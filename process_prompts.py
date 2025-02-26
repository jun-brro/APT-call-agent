import json
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any, Tuple, Optional, Set
import logging
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from src.core.engines.insurance import InsuranceEngine
from src.config import (
    DEFAULT_MODEL_PATH,
    DEFAULT_RESPONSE_MODEL_PATH,
    DB_CONFIG,
    ACTUARIAL_CONFIG,
    PRODUCT_CONFIG,
    MARKET_CONFIG,
    MODEL_CONFIG,
    VALID_INSURANCE_TYPES,
    VALID_ACTUARIAL_ANALYSIS_TYPES,
    VALID_MARKET_ANALYSIS_TYPES,
    VALID_PRODUCT_DESIGN_TYPES
)
from src.templates import SYSTEM_PROMPT_TEMPLATE, ANALYSIS_CONTEXT_TEMPLATE, TOOLS
from src.mappings import INSURANCE_TYPE_MAPPING, ANALYSIS_KEYWORDS, RESULT_TEMPLATES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return super().default(obj)

class PromptProcessor:
    def __init__(self, prompt_file: str):
        self.prompt_file = prompt_file
        self.results = []
        self.tool_model = None
        self.response_model = None
        self.tool_tokenizer = None
        self.response_tokenizer = None
        self.insurance_engine = None
        
        # Initialize models
        self.TOOL_MODEL_PATH = os.getenv('MODEL_PATH', DEFAULT_MODEL_PATH)
        self.RESPONSE_MODEL_PATH = os.getenv('RESPONSE_MODEL_PATH', DEFAULT_RESPONSE_MODEL_PATH)
        
        # Initialize system prompt
        self.system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            insurance_types=VALID_INSURANCE_TYPES,
            actuarial_types=VALID_ACTUARIAL_ANALYSIS_TYPES,
            product_types=VALID_PRODUCT_DESIGN_TYPES,
            market_types=VALID_MARKET_ANALYSIS_TYPES
        )
        
        self.initialize()
        
    def initialize(self):
        """Initialize required components"""
        try:
            logger.info(f"Initializing {self.TOOL_MODEL_PATH} model for tool calls...")
            self.tool_tokenizer = AutoTokenizer.from_pretrained(self.TOOL_MODEL_PATH)
            self.tool_model = AutoModelForCausalLM.from_pretrained(
                self.TOOL_MODEL_PATH,
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True
            )
            
            logger.info(f"Initializing {self.RESPONSE_MODEL_PATH} model for response generation...")
            
            config = AutoConfig.from_pretrained(self.RESPONSE_MODEL_PATH)
            self.response_tokenizer = AutoTokenizer.from_pretrained(
                self.RESPONSE_MODEL_PATH,
                padding_side="left",
                truncation_side="left"
            )
            
            if self.response_tokenizer.pad_token is None:
                logger.info("Adding PAD token to tokenizer...")
                special_tokens_dict = {'pad_token': '[PAD]'}
                num_added_tokens = self.response_tokenizer.add_special_tokens(special_tokens_dict)
                logger.info(f"Added {num_added_tokens} special tokens: {special_tokens_dict}")
            
            self.response_model = AutoModelForCausalLM.from_pretrained(
                self.RESPONSE_MODEL_PATH,
                config=config,
                device_map="auto",
                torch_dtype=torch.float16,
                low_cpu_mem_usage=True,
                offload_folder="offload",
                offload_state_dict=True
            )
            
            self.response_model.resize_token_embeddings(
                len(self.response_tokenizer),
                mean_resizing=False
            )
            
            logger.info(f"Model device: {next(self.response_model.parameters()).device}")
            logger.info(f"Tokenizer vocabulary size: {len(self.response_tokenizer)}")
            
            self.insurance_engine = InsuranceEngine({
                'db_config': DB_CONFIG,
                'actuarial_config': ACTUARIAL_CONFIG,
                'product_config': PRODUCT_CONFIG,
                'market_config': MARKET_CONFIG
            })
            logger.info("Initialization complete")
            
        except Exception as e:
            logger.error(f"Initialization failed: {e}", exc_info=True)
            raise

    def validate_tool_parameters(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, str]:
        """Validate tool parameters and return error message if invalid"""
        tool_def = next((tool for tool in TOOLS if tool["name"] == tool_name), None)
        if not tool_def:
            return {"error": f"Invalid tool name: {tool_name}"}
            
        required_params = tool_def["arguments"]["required"]
        missing_params = [param for param in required_params if param not in params]
        if missing_params:
            return {"error": f"Missing required parameters: {', '.join(missing_params)}"}
            
        # Validate enum values
        for param_name, param_value in params.items():
            if param_name in tool_def["arguments"]["properties"]:
                prop = tool_def["arguments"]["properties"][param_name]
                if "enum" in prop and param_value not in prop["enum"]:
                    return {"error": f"Invalid {param_name}: {param_value}. Must be one of: {', '.join(prop['enum'])}"}
                    
        return {}

    def parse_model_output(self, output: str) -> Tuple[List[Dict[str, Any]], str]:
        """Parse the model output to extract tool calls and final response.
        
        Args:
            output (str): Raw model output
            
        Returns:
            Tuple[List[Dict[str, Any]], str]: Tuple of (tool calls, final response)
        """
        tool_calls = []
        
        tool_pattern = r'\[(\w+)\s*\(((?:[^()[\]{}]+|{[^{}]*})*)\)\]'
        matches = re.finditer(tool_pattern, output)
        
        for match in matches:
            tool_name = match.group(1).strip()
            params_str = match.group(2).strip()
            
            try:
                params = {}
                if params_str.startswith('{') and params_str.endswith('}'):
                    params = json.loads(params_str)
                else:
                    param_pattern = r'(\w+)\s*=\s*("[^"]*"|\'[^\']*\'|\{[^}]*\}|[^,\s]+)'
                    for param_match in re.finditer(param_pattern, params_str):
                        key = param_match.group(1)
                        value = self._parse_value(param_match.group(2))
                        params[key] = value
                
                validation_result = self.validate_tool_parameters(tool_name, params)
                if validation_result:
                    logger.warning(f"Tool validation failed: {validation_result}")
                    continue
                
                tool_calls.append({"tool": tool_name, "parameters": params})
                
            except Exception as e:
                logger.error(f"Failed to parse tool parameters: {e}")
                continue
                
        final_response = output
        if tool_calls:
            last_tool_end = max(match.end() for match in re.finditer(tool_pattern, output))
            final_response = output[last_tool_end:].strip()
            
        return tool_calls, final_response

    def execute_tool_call(self, tool_call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call with validation and flexible mapping"""
        try:
            tool_name = tool_call.get('name') or tool_call.get('tool')  # Handle both 'name' and 'tool' keys
            if not tool_name:
                raise ValueError("Missing tool name in tool call")
                
            parameters = tool_call['parameters']
            
            # Map insurance type if needed
            if 'insurance_type' in parameters:
                orig_type = parameters['insurance_type'].lower()
                if orig_type in self.insurance_type_mapping:
                    parameters['insurance_type'] = self.insurance_type_mapping[orig_type]
                else:
                    # Default to 'disease' if unknown type
                    parameters['insurance_type'] = 'disease'
                    logger.warning(f"Unknown insurance type '{orig_type}', defaulting to 'disease'")
            
            # Validate parameters
            validation_error = self.validate_tool_parameters(tool_name, parameters)
            if validation_error:
                return validation_error
            
            # Map tool names to request types and prepare parameters
            if tool_name == 'actuarial_analysis':
                processed_parameters = {
                    'request_type': 'actuarial',
                    'parameters': {
                        'analysis_type': parameters['analysis_type'],
                        'insurance_type': parameters['insurance_type'],
                        'data': parameters.get('data', {
                            'claims': [100, 200, 300],  # Default values if none provided
                            'premiums': [150, 300, 450]
                        })
                    }
                }
            elif tool_name == 'product_design':
                processed_parameters = {
                    'request_type': 'product',
                    'parameters': {
                        'design_type': parameters['design_type'],
                        'insurance_type': parameters['insurance_type'],
                        'parameters': parameters.get('parameters', {
                            'coverage_type': 'basic',
                            'target_segment': 'age_31_40'
                        })
                    }
                }
            elif tool_name == 'market_analysis':
                processed_parameters = {
                    'request_type': 'market',
                    'parameters': {
                        'analysis_type': parameters['analysis_type'],
                        'insurance_type': parameters['insurance_type'],
                        'segment': parameters.get('segment', 'age_31_40')
                    }
                }
            else:
                return {"error": f"Unknown tool: {tool_name}"}
            
            # Add table mapping information
            processed_parameters['table_mapping'] = {
                'contracts': 'quarterly_insurance_contracts',
                'claims': 'quarterly_insurance_claims',
                'market': 'market_research'
            }
            
            # Execute the request
            return self.insurance_engine.process(processed_parameters)
                
        except Exception as e:
            logger.error(f"Error executing tool call: {e}")
            return {"error": str(e)}

    def generate_analysis_response(self, prompt: str, results: Dict[str, Any]) -> str:
        """Generate detailed analysis response with explanations"""
        try:
            context = self._create_analysis_context(prompt, results)
            
            # Format results by domain
            response_parts = []
            
            # Add actuarial analysis explanation
            if 'actuarial' in results:
                actuarial_explanation = self._format_actuarial_results(results['actuarial'])
                if actuarial_explanation:
                    response_parts.append("Actuarial Analysis:\n" + actuarial_explanation)
            
            # Add market analysis explanation
            if 'market' in results:
                market_explanation = self._format_market_results(results['market'])
                if market_explanation:
                    response_parts.append("Market Analysis:\n" + market_explanation)
            
            # Add product analysis explanation
            if 'product' in results:
                product_explanation = self._format_product_results(results['product'])
                if product_explanation:
                    response_parts.append("Product Analysis:\n" + product_explanation)
            
            # Add insights and recommendations
            if 'insights' in results:
                insights_text = "\nKey Insights:\n"
                for insight in results['insights']:
                    insights_text += f"- {insight}\n"
                response_parts.append(insights_text)
            
            if 'recommendations' in results:
                recommendations_text = "\nRecommendations:\n"
                for rec in results['recommendations']:
                    recommendations_text += f"- {rec}\n"
                response_parts.append(recommendations_text)
            
            # Add confidence information
            if 'confidence_scores' in results.get('metadata', {}):
                confidence_text = "\nAnalysis Confidence:\n"
                for domain, score in results['metadata']['confidence_scores'].items():
                    confidence_text += f"- {domain}: {score:.2%}\n"
                response_parts.append(confidence_text)
            
            # Combine all parts
            final_response = "\n\n".join(response_parts)
            
            # Add warnings if any
            if 'warnings' in results:
                warnings_text = "\nWarnings:\n"
                for warning in results['warnings']:
                    warnings_text += f"! {warning}\n"
                final_response += "\n" + warnings_text
            
            return final_response
            
        except Exception as e:
            logger.error(f"Failed to generate analysis response: {e}")
            return "Failed to generate detailed analysis response."

    def _format_actuarial_results(self, results: Dict[str, Any]) -> str:
        """Format actuarial analysis results"""
        if not results:
            return ""
            
        explanation = []
        
        # Loss ratio analysis
        if 'loss_ratio' in results:
            explanation.append(f"Loss Ratio: {results['loss_ratio']:.2%}")
            
        # Risk metrics
        if 'risk_metrics' in results:
            metrics = results['risk_metrics']
            explanation.append("Risk Metrics:")
            explanation.append(f"- Expected Loss: {metrics.get('expected_loss', 0):.2f}")
            explanation.append(f"- Standard Deviation: {metrics.get('std_dev', 0):.2f}")
            explanation.append(f"- VaR (95%): {metrics.get('var_95', 0):.2f}")
            
        return "\n".join(explanation)

    def _format_market_results(self, results: Dict[str, Any]) -> str:
        """Format market analysis results"""
        if not results:
            return ""
            
        explanation = []
        
        # Market size
        if 'market_size' in results:
            explanation.append(f"Market Size: {results['market_size']:,}")
            
        # Market share
        if 'market_share' in results:
            explanation.append(f"Market Share: {results['market_share']:.2%}")
            
        # Growth potential
        if 'growth_potential' in results:
            explanation.append(f"Growth Potential: {results['growth_potential']:.2%}")
            
        return "\n".join(explanation)

    def _format_product_results(self, results: Dict[str, Any]) -> str:
        """Format product analysis results"""
        if not results:
            return ""
            
        explanation = []
        
        # Product design
        if 'design' in results:
            explanation.append("Product Design:")
            explanation.append(f"- Coverage Type: {results['design'].get('coverage_type', 'N/A')}")
            explanation.append(f"- Benefit Structure: {results['design'].get('benefit_structure', 'N/A')}")
            
        # Pricing
        if 'pricing' in results:
            explanation.append("Pricing Strategy:")
            explanation.append(f"- Base Premium: {results['pricing'].get('base_premium', 0):,.2f}")
            explanation.append(f"- Risk Loading: {results['pricing'].get('risk_loading', 0):.2%}")
            
        return "\n".join(explanation)

    def _create_analysis_context(self, prompt: str, results: Dict[str, Any]) -> str:
        """Create analysis context"""
        context = f"User Question: {prompt}\n\n"
        context += "Analysis Results:\n"
        
        # Actuarial Analysis Results
        if 'actuarial' in results:
            context += "\nActuarial Analysis:\n"
            context += self._format_actuarial_results(results['actuarial'])
        
        # Market Analysis Results
        if 'market' in results:
            context += "\nMarket Analysis:\n"
            context += self._format_market_results(results['market'])
        
        # Product Analysis Results
        if 'product' in results:
            context += "\nProduct Analysis:\n"
            context += self._format_product_results(results['product'])
        
        context += "\n\n위 분석 결과를 바탕으로 통찰력 있고 실행 가능한 추천사항을 제시해주세요."
        
        return context

    def _detect_required_tools(self, prompt: str) -> List[str]:
        """Analyze prompt and detect required tools"""
        required_tools = set()
        
        # 1. Keyword-based analysis
        prompt_lower = prompt.lower()
        for tool_type, keywords in self.analysis_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                if tool_type == 'actuarial':
                    required_tools.add('actuarial_analysis')
                elif tool_type == 'market':
                    required_tools.add('market_analysis')
                elif tool_type == 'product':
                    required_tools.add('product_design')
        
        # 2. Insurance type-specific required tools
        insurance_type = self._detect_insurance_type(prompt)
        if insurance_type:
            required_tools.update(self._get_required_tools_for_insurance(insurance_type))
        
        # 3. Always include at least one tool
        if not required_tools:
            required_tools.add('actuarial_analysis')
            
        return list(required_tools)

    def _detect_insurance_type(self, prompt: str) -> str:
        """Detect insurance type from prompt"""
        prompt_lower = prompt.lower()
        
        # Direct insurance type mention check
        for insurance_type in self.insurance_type_mapping.keys():
            if insurance_type.replace('_', ' ') in prompt_lower:
                return insurance_type
        
        # Keyword-based insurance type inference
        keywords_to_type = {
            'mental': 'mental_health',
            'dental': 'dental',
            'critical illness': 'critical_illness',
            'cancer': 'cancer',
            'cyber': 'cyber',
            'disability': 'disability',
            'wellness': 'wellness',
            'hospital': 'hospital_cash',
            'income': 'income_protection',
            'auto': 'auto',
            'telehealth': 'telehealth',
            'chronic': 'chronic_care'
        }
        
        for keyword, insurance_type in keywords_to_type.items():
            if keyword in prompt_lower:
                return insurance_type
                
        return 'disease'  # Default value

    def _get_required_tools_for_insurance(self, insurance_type: str) -> Set[str]:
        """Insurance type-specific required analysis tools"""
        insurance_tools = {
            'mental_health': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'dental': {'actuarial_analysis', 'product_design', 'market_analysis'},
            'critical_illness': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'long_term_care': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'cyber': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'disability': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'cancer': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'parametric': {'actuarial_analysis', 'product_design'},
            'wellness': {'market_analysis', 'product_design', 'actuarial_analysis'},
            'hospital_cash': {'actuarial_analysis', 'product_design'},
            'income_protection': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'auto': {'actuarial_analysis', 'market_analysis', 'product_design'},
            'telehealth': {'market_analysis', 'product_design', 'actuarial_analysis'},
            'chronic_care': {'actuarial_analysis', 'product_design', 'market_analysis'}
        }
        
        return insurance_tools.get(insurance_type, {'actuarial_analysis', 'market_analysis'})

    def _create_tool_calls(self, prompt: str) -> List[Dict[str, Any]]:
        """Create tool calls"""
        tool_calls = []
        insurance_type = self._detect_insurance_type(prompt)
        required_tools = self._detect_required_tools(prompt)
        
        for tool in required_tools:
            if tool == 'actuarial_analysis':
                tool_calls.extend(self._create_actuarial_tool_calls(insurance_type))
            elif tool == 'market_analysis':
                tool_calls.extend(self._create_market_tool_calls(insurance_type))
            elif tool == 'product_design':
                tool_calls.extend(self._create_product_tool_calls(insurance_type))
        
        return tool_calls

    def _create_actuarial_tool_calls(self, insurance_type: str) -> List[Dict[str, Any]]:
        """Create actuarial analysis tool calls"""
        calls = []
        
        # Basic loss ratio analysis
        calls.append({
            'name': 'actuarial_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'loss_ratio',
                'data': {
                    'claims': [100, 200, 150, 300],
                    'premiums': [150, 300, 180, 360]
                }
            }
        })
        
        # Risk metrics analysis
        calls.append({
            'name': 'actuarial_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'risk_metrics',
                'data': {
                    'exposure': 1000,
                    'claims_history': [80, 120, 90, 150]
                }
            }
        })
        
        # Cost analysis
        calls.append({
            'name': 'actuarial_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'cost_analysis',
                'data': {
                    'administrative_costs': [50, 60, 55, 65],
                    'acquisition_costs': [30, 35, 32, 38]
                }
            }
        })
        
        return calls

    def _create_market_tool_calls(self, insurance_type: str) -> List[Dict[str, Any]]:
        """Create market analysis tool calls"""
        calls = []
        
        # Market size analysis
        calls.append({
            'name': 'market_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'market_size',
                'segment': 'age_31_40'
            }
        })
        
        # Competition analysis
        calls.append({
            'name': 'market_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'competition_analysis',
                'segment': 'all'
            }
        })
        
        # Customer behavior analysis
        calls.append({
            'name': 'market_analysis',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'analysis_type': 'customer_behavior',
                'segment': 'all'
            }
        })
        
        return calls

    def _create_product_tool_calls(self, insurance_type: str) -> List[Dict[str, Any]]:
        """Create product design tool calls"""
        calls = []
        
        # Basic product design
        calls.append({
            'name': 'product_design',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'design_type': 'coverage',
                'parameters': {
                    'coverage_type': 'comprehensive',
                    'target_segment': 'age_31_40'
                }
            }
        })
        
        # Innovation product design
        calls.append({
            'name': 'product_design',
            'parameters': {
                'insurance_type': self.insurance_type_mapping.get(insurance_type, 'disease'),
                'design_type': 'hybrid_product',
                'parameters': {
                    'core_coverage': 'standard',
                    'additional_features': ['wellness', 'telehealth']
                }
            }
        })
        
        return calls

    def process_prompt(self, prompt: str, prompt_number: int) -> Dict[str, Any]:
        """Process a single prompt"""
        try:
            logger.info(f"Starting to process prompt {prompt_number}: {prompt[:100]}...")  # 프롬프트 처리 시작
            
            # 1. Create tool calls
            logger.info(f"Generating tool calls for prompt {prompt_number}...")
            tool_calls = self._create_tool_calls(prompt)
            logger.info(f"Generated {len(tool_calls)} tool calls")
            
            # 2. Execute tool calls and aggregate results
            logger.info(f"Executing tool calls for prompt {prompt_number}...")
            domain_results = {}
            for i, call in enumerate(tool_calls, 1):
                logger.info(f"Executing tool call {i}/{len(tool_calls)}")
                result = self.execute_tool_call(call)
                domain_results.update(result)
            
            # 3. Generate comprehensive response using Mistral
            logger.info(f"Generating Mistral response for prompt {prompt_number}...")
            final_response = self._generate_mistral_response(prompt, domain_results)
            
            logger.info(f"Completed processing prompt {prompt_number}")
            
            # 4. Calculate quality metrics
            quality_metrics = {
                'completeness': self._calculate_completeness(domain_results),
                'consistency': self._check_consistency(domain_results),
                'reliability': self._assess_reliability(domain_results)
            }
            
            return {
                'prompt_number': prompt_number,
                'prompt': prompt,
                'tool_calls': tool_calls,
                'domain_results': domain_results,
                'quality_metrics': quality_metrics,
                'execution_status': 'completed',
                'final_response': final_response
            }
            
        except Exception as e:
            logger.error(f"Error processing prompt {prompt_number}: {e}")
            return {
                'prompt_number': prompt_number,
                'prompt': prompt,
                'error': str(e),
                'execution_status': 'failed'
            }

    def _generate_mistral_response(self, prompt: str, domain_results: Dict[str, Any]) -> str:
        try:
            context = self._prepare_mistral_context(prompt, domain_results)
            logger.info("Context prepared for Mistral, length: %d", len(context))
            
            inputs = self.response_tokenizer(
                context,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )
            
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            input_ids = inputs["input_ids"].to(device)
            attention_mask = inputs["attention_mask"].to(device)
            
            gen_kwargs = {
                "max_length": 4096,  # 출력 길이 조정
                "num_beams": 1,
                "temperature": 0.9,
                "top_p": 0.9,
                "pad_token_id": self.response_tokenizer.pad_token_id,
                "eos_token_id": self.response_tokenizer.eos_token_id,
                "do_sample": True
            }
            
            torch.cuda.empty_cache()
            
            with torch.no_grad(), torch.amp.autocast('cuda'):
                outputs = self.response_model.generate(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    **gen_kwargs
                )
            
            torch.cuda.empty_cache()
            
            response = self.response_tokenizer.decode(outputs[0], skip_special_tokens=True)
            response = response.strip()
            
            if '--- FINAL RESPONSE STARTS BELOW ---' in response:
                response = response.split('--- FINAL RESPONSE STARTS BELOW ---')[-1].strip()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate Mistral response: {str(e)}", exc_info=True)
            return f"Failed to generate detailed analysis response. Error: {str(e)}"

    def _prepare_mistral_context(self, prompt: str, domain_results: Dict[str, Any]) -> str:
        """Prepare context for Mistral model"""
        context_parts = [
            "You are an expert insurance analyst.",
            "Based on the provided analysis results, produce the analysis and suggestions with detailed insights and actionable recommendations.",
            "You MUST explain your analysis with specific numeric reasons or specific details.",
            "If you suggest something, you MUST explain with quantitative reasons or numeric data from the given data.",
            "DO NOT include the original request in your final answer.",
            "\nFor reference only (do not use in final answer):",
            
            f"Original Request: {prompt}\n\n",
            
            "Analysis Results:\n",
            
            "1. Actuarial Analysis:",
            self._format_actuarial_results(domain_results.get('actuarial', {})),
            
            "\n2. Market Analysis:",
            self._format_market_results(domain_results.get('market', {})),
            
            "\n3. Product Analysis:",
            self._format_product_results(domain_results.get('product', {})),
            
            "\nPlease provide a detailed response that includes:\n",
            "- Key findings and insights from the analysis\n",
            "- Cross-domain relationships and implications\n",
            "- Specific, actionable recommendations\n",
            "- Potential risks and mitigation strategies\n",
            "- Implementation considerations\n"
            "\n--- FINAL RESPONSE STARTS BELOW ---\n"
        ]
        
        return "\n".join(filter(None, context_parts))

    def process_all(self):
        """Process all prompts"""
        prompts = self.read_prompts()
        for i, prompt in enumerate(prompts, 1):
            try:
                result = self.process_prompt(prompt, i)
                self.results.append(result)
            except Exception as e:
                logger.error(f"Failed to process prompt {i}: {e}")
                self.results.append({
                    "prompt_number": i,
                    "error": str(e),
                    "prompt": prompt,
                    "timestamp": datetime.now().isoformat(),
                    "execution_status": "failed"
                })
        
        self.save_results()

    def save_results(self, output_file: str = "results.json"):
        """Save results to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, cls=CustomJSONEncoder, ensure_ascii=False, indent=2)
            logger.info(f"Results saved to {output_file}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    def read_prompts(self) -> List[str]:
        """Read prompts from file, combining lines between [PROMPT] markers"""
        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Split by [PROMPT] markers and filter out empty strings
            prompts = []
            parts = content.split('[PROMPT')
            
            for part in parts:
                if not part.strip():
                    continue
                    
                # Handle numbered prompts [PROMPT N] format
                if part.startswith(' '):
                    # Remove the prompt number and closing bracket
                    prompt_text = part.split(']', 1)[1].strip()
                else:
                    prompt_text = part.strip()
                
                if prompt_text:
                    prompts.append(prompt_text)
            
            logger.info(f"Read {len(prompts)} prompts from file")
            return prompts
            
        except Exception as e:
            logger.error(f"Failed to read prompts: {e}")
            return []

    def _calculate_completeness(self, domain_results: Dict[str, Any]) -> float:
        """Calculate completeness score of the analysis results"""
        expected_fields = {
            'actuarial': {'loss_ratio', 'risk_metrics', 'cost_analysis'},
            'market': {'market_size', 'competition_analysis', 'customer_behavior'},
            'product': {'design', 'pricing', 'features'}
        }
        
        total_fields = sum(len(fields) for fields in expected_fields.values())
        found_fields = 0
        
        for domain, fields in expected_fields.items():
            if domain in domain_results:
                found_fields += sum(1 for field in fields if field in domain_results[domain])
                
        return found_fields / total_fields if total_fields > 0 else 0.0
        
    def _check_consistency(self, domain_results: Dict[str, Any]) -> float:
        """Check consistency of analysis results across domains"""
        consistency_score = 1.0
        
        # Check if market size aligns with actuarial projections
        if ('market' in domain_results and 'actuarial' in domain_results and
            'market_size' in domain_results['market'] and 'risk_metrics' in domain_results['actuarial']):
            market_size = float(domain_results['market']['market_size'])
            exposure = float(domain_results['actuarial']['risk_metrics'].get('exposure', 0))
            if market_size > 0 and exposure > 0:
                ratio = min(exposure / market_size, market_size / exposure)
                consistency_score *= ratio
        
        # Check if pricing aligns with market analysis
        if ('product' in domain_results and 'market' in domain_results and
            'pricing' in domain_results['product'] and 'market_size' in domain_results['market']):
            consistency_score *= 0.8  # Simplified check
            
        return consistency_score
        
    def _assess_reliability(self, domain_results: Dict[str, Any]) -> float:
        """Assess reliability of the analysis results"""
        reliability_scores = []
        
        # Check data presence and quality for each domain
        for domain, results in domain_results.items():
            if not results:
                continue
                
            # Check for required fields based on domain
            if domain == 'actuarial':
                if 'loss_ratio' in results and 'risk_metrics' in results:
                    reliability_scores.append(0.9)
                else:
                    reliability_scores.append(0.5)
                    
            elif domain == 'market':
                if 'market_size' in results and 'competition_analysis' in results:
                    reliability_scores.append(0.85)
                else:
                    reliability_scores.append(0.4)
                    
            elif domain == 'product':
                if 'design' in results and 'pricing' in results:
                    reliability_scores.append(0.95)
                else:
                    reliability_scores.append(0.6)
        
        return sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0

def main():
    processor = PromptProcessor("prompt.txt")
    processor.process_all()

if __name__ == "__main__":
    main() 