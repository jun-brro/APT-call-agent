from typing import Dict, Any, Optional, Callable, List, Set
from .base import BaseEngine
from .domain.actuarial import ActuarialEngine
from .domain.product import ProductEngine
from .domain.market import MarketEngine
import logging
from datetime import datetime
from .result_synthesizer import ResultSynthesizer

logger = logging.getLogger(__name__)

class InsuranceEngine(BaseEngine):
    """Integrated Insurance Engine - Coordinates all domain engines"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize insurance engine
        Args:
            config: Configuration dictionary
        Raises:
            ValueError: Invalid configuration
        """
        if not config:
            raise ValueError("Invalid configuration: Configuration dictionary cannot be empty")
        super().__init__(config)
        self.result_synthesizer = ResultSynthesizer()
        self._initialize()
            
    def _initialize(self) -> None:
        """Initialize domain engines"""
        try:
            # Extract common database configuration
            db_config = self.config['db_config']
            
            # Define default table mappings
            default_table_mapping = {
                'contracts': 'quarterly_insurance_contracts',
                'claims': 'quarterly_insurance_claims',
                'market': 'market_research',
                'products': 'product_templates',
                'pricing': 'pricing_models',
                'development': 'development_projects',
                'regulatory': 'regulatory_requirements',
                'risk': 'risk_scenarios',
                'simulation': 'simulation_results'
            }
            
            # Initialize domain configurations with database config and table mapping
            actuarial_config = self.config.get('actuarial_config', {}).copy()
            actuarial_config.update({
                'db_config': db_config,
                'table_mapping': default_table_mapping
            })
            
            product_config = self.config.get('product_config', {}).copy()
            product_config.update({
                'db_config': db_config,
                'table_mapping': default_table_mapping
            })
            
            market_config = self.config.get('market_config', {}).copy()
            market_config.update({
                'db_config': db_config,
                'table_mapping': default_table_mapping
            })
            
            # Store table mapping for future use
            self.table_mapping = default_table_mapping
            
            # Initialize domain engines
            try:
                self.actuarial_engine = ActuarialEngine(actuarial_config)
                self.product_engine = ProductEngine(product_config)
                self.market_engine = MarketEngine(market_config)
            except Exception as e:
                if 'invalid_host' in str(e).lower():
                    raise Exception("Failed to connect to database")
                raise ValueError({
                    'error_code': 'INITIALIZATION_ERROR',
                    'message': str(e),
                    'details': {'config': self.config}
                })
            
            # Set up engine mapping
            self.engine_map = {
                'actuarial': self.actuarial_engine.process,
                'product': self.product_engine.process,
                'market': self.market_engine.process,
                'integrated': self._process_integrated_analysis
            }
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            if 'Failed to connect to database' in str(e):
                raise Exception("Failed to connect to database")
            raise ValueError({
                'error_code': 'INITIALIZATION_ERROR',
                'message': str(e),
                'details': {'config': self.config}
            })
            
    def _validate_config(self) -> None:
        """Validate configuration"""
        if not isinstance(self.config, dict):
            raise ValueError({
                'error_code': 'INVALID_CONFIGURATION',
                'message': "Configuration must be a dictionary",
                'details': {'provided_type': str(type(self.config))}
            })
            
        try:
            # Check required domain configs
            required_configs = ['actuarial_config', 'product_config', 'market_config']
            for required in required_configs:
                if required not in self.config:
                    raise ValueError({
                        'error_code': 'INVALID_CONFIGURATION',
                        'message': f"Missing {required}",
                        'details': {'missing_config': required}
                    })
                    
                sub_config = self.config[required]
                if not isinstance(sub_config, dict):
                    raise ValueError({
                        'error_code': 'INVALID_CONFIGURATION',
                        'message': f"{required} must be a dictionary",
                        'details': {'provided_type': str(type(sub_config))}
                    })
                    
                # Validate required settings for each domain
                if required == 'actuarial_config':
                    required_fields = ['mortality_table', 'expense_inflation', 'interest_rate']
                    for field in required_fields:
                        if field not in sub_config:
                            raise ValueError({
                                'error_code': 'INVALID_CONFIGURATION',
                                'message': f"Missing {field} in {required}",
                                'details': {'missing_field': field}
                            })
                        # mortality_table is allowed to be empty in test mode
                        if field == 'mortality_table':
                            test_mode = sub_config.get('test_mode', False)  # default to False
                            if not sub_config[field] and not test_mode:  # test_mode is False and mortality_table is empty
                                raise ValueError({
                                    'error_code': 'INVALID_CONFIGURATION',
                                    'message': "mortality_table cannot be empty when not in test mode",
                                    'details': {'field': 'mortality_table', 'test_mode': test_mode}
                                })
                        elif not sub_config[field] and sub_config[field] != 0:
                            raise ValueError({
                                'error_code': 'INVALID_CONFIGURATION',
                                'message': f"{field} cannot be empty in {required}",
                                'details': {'field': field}
                            })
                            
            # Check database config
            if 'db_config' not in self.config:
                raise ValueError("Invalid configuration: Missing database configuration")
                
            db_config = self.config['db_config']
            if not isinstance(db_config, dict):
                raise ValueError("Invalid configuration: Database configuration must be a dictionary")
                
            required_db_fields = ['host', 'port', 'database', 'user', 'password']
            for field in required_db_fields:
                if field not in db_config:
                    raise ValueError(f"Invalid configuration: Missing {field} in database configuration")
                if not db_config[field] and field != 'password':
                    raise ValueError(f"Invalid configuration: {field} cannot be empty in database configuration")
                    
        except ValueError as e:
            raise ValueError(str(e))
            
    def _map_cross_domain_parameters(self, request_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Map parameters between domains"""
        mapped_params = params.copy()
        
        if request_type == 'actuarial' and 'target_segment' in params:
            # Map market segment to insurance type
            segment_to_insurance = {
                'young_adults': 'injury',
                'middle_age': 'health',
                'seniors': 'life'
            }
            mapped_params['insurance_type'] = segment_to_insurance.get(
                params['target_segment'], 'general'
            )
            
        return mapped_params
        
    def _validate_request(self, parameters: Dict[str, Any]) -> None:
        """Validate request"""
        # Validate basic parameters
        if not isinstance(parameters, dict):
            error_info = {
                'error_code': 'INVALID_REQUEST',
                'message': "Request must be a dictionary",
                'details': {'provided_type': str(type(parameters))}
            }
            raise ValueError(error_info)
        
        # Validate request_type
        request_type = parameters.get('request_type')
        if not request_type:
            error_info = {
                'error_code': 'MISSING_REQUEST_TYPE',
                'message': "Missing required field: request_type",
                'details': {'parameters': parameters}
            }
            raise ValueError(error_info)
            
        if not isinstance(request_type, str):
            error_info = {
                'error_code': 'INVALID_REQUEST_TYPE',
                'message': "request_type must be a string",
                'details': {'provided_type': str(type(request_type))}
            }
            raise ValueError(error_info)
            
        # Validate valid request types
        valid_types = ['actuarial', 'product', 'market', 'integrated']
        if request_type not in valid_types:
            error_info = {
                'error_code': 'INVALID_REQUEST_TYPE',
                'message': f"Unknown request type: {request_type}",
                'details': {
                    'provided_type': request_type,
                    'valid_types': valid_types
                }
            }
            raise ValueError(error_info)
            
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process request"""
        try:
            # Validate basic request structure
            self._validate_request(parameters)
            
            request_type = parameters['request_type']
            params = parameters.get('parameters', {})
            
            # Decompose request into smaller units
            decomposed_requests = self._decompose_request(parameters)
            
            # Perform analysis for each sub-request
            analysis_results = {}
            for sub_request in decomposed_requests:
                sub_type = sub_request['analysis_type']
                analysis_results[sub_type] = self._perform_sub_analysis(sub_request)
            
            # Use ResultSynthesizer to synthesize results and derive insights
            synthesized_results = self.result_synthesizer.synthesize(analysis_results)
            
            # If results are insufficient, perform additional analysis
            if self._needs_additional_analysis(synthesized_results):
                additional_results = self._perform_additional_analysis(synthesized_results, parameters)
                synthesized_results = self.result_synthesizer.synthesize({**analysis_results, **additional_results})
            
            return self.format_response(synthesized_results)
            
        except ValueError as e:
            if isinstance(e.args[0], dict):
                raise
            raise ValueError({
                'error_code': 'VALIDATION_ERROR',
                'message': str(e),
                'details': {'parameters': parameters}
            })
    
    def _perform_sub_analysis(self, sub_request: Dict[str, Any]) -> Dict[str, Any]:
        """Perform analysis for sub-request"""
        results = {}
        
        # Perform analysis for each engine
        try:
            if self._should_run_actuarial(sub_request):
                results['actuarial'] = self.actuarial_engine.process(sub_request)
        except Exception as e:
            logger.warning(f"Actuarial analysis failed: {e}")
            
        try:
            if self._should_run_market(sub_request):
                results['market'] = self.market_engine.process(sub_request)
        except Exception as e:
            logger.warning(f"Market analysis failed: {e}")
            
        try:
            if self._should_run_product(sub_request):
                results['product'] = self.product_engine.process(sub_request)
        except Exception as e:
            logger.warning(f"Product analysis failed: {e}")
            
        return results
        
    def _needs_additional_analysis(self, results: Dict[str, Any]) -> bool:
        """Evaluate if additional analysis is needed"""
        if not results or 'metadata' not in results:
            return True
            
        confidence_scores = results['metadata'].get('confidence_scores', {})
        data_completeness = results['metadata'].get('data_completeness', 0)
        
        return (
            any(score < 0.6 for score in confidence_scores.values()) or
            data_completeness < 0.7
        )
        
    def _perform_additional_analysis(self, current_results: Dict[str, Any], 
                                   original_parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform additional analysis"""
        additional_results = {}
        
        # Identify missing aspects
        missing_aspects = self._identify_missing_aspects(current_results)
        
        # Perform additional analysis for each missing aspect
        for aspect in missing_aspects:
            analysis_params = self._create_additional_analysis_params(
                aspect, 
                original_parameters,
                current_results
            )
            
            try:
                if aspect in self.engine_map:
                    additional_results[f"additional_{aspect}"] = self.engine_map[aspect](analysis_params)
            except Exception as e:
                logger.warning(f"Additional analysis for {aspect} failed: {e}")
                
        return additional_results
        
    def _identify_missing_aspects(self, results: Dict[str, Any]) -> List[str]:
        """Identify missing analysis aspects"""
        missing_aspects = []
        confidence_scores = results.get('metadata', {}).get('confidence_scores', {})
        
        for aspect, score in confidence_scores.items():
            if score < 0.6:
                missing_aspects.append(aspect)
                
        return missing_aspects
        
    def _create_additional_analysis_params(self, aspect: str, 
                                         original_params: Dict[str, Any],
                                         current_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create parameters for additional analysis"""
        params = original_params.copy()
        params['analysis_type'] = aspect
        params['previous_results'] = current_results
        params['is_additional_analysis'] = True
        
        return params
        
    def _should_run_actuarial(self, request: Dict[str, Any]) -> bool:
        """Check if actuarial analysis is needed"""
        actuarial_types = {'risk_metrics', 'loss_ratio', 'mortality', 'morbidity'}
        return request['analysis_type'] in actuarial_types
        
    def _should_run_market(self, request: Dict[str, Any]) -> bool:
        """Check if market analysis is needed"""
        market_types = {'market_size', 'competition', 'demand', 'trends'}
        return request['analysis_type'] in market_types
        
    def _should_run_product(self, request: Dict[str, Any]) -> bool:
        """Check if product analysis is needed"""
        product_types = {'design', 'pricing', 'coverage', 'benefits'}
        return request['analysis_type'] in product_types
    
    def _validate_parameters(self, request_type: str, parameters: Dict[str, Any]) -> None:
        """Validate parameters"""
        if request_type == 'actuarial':
            required = ['analysis_type', 'insurance_type']
            valid_analysis_types = ['loss_ratio', 'risk_metrics', 'full']
        elif request_type == 'product':
            required = ['design_type']
            valid_design_types = ['pricing', 'coverage', 'full']
        elif request_type == 'market':
            required = ['analysis_type']
            valid_analysis_types = ['market_size', 'market_share', 'full']
        elif request_type == 'integrated':
            required = ['target_segment']
        else:
            return
            
        # Validate required parameters
        missing = [param for param in required if param not in parameters]
        if missing:
            error_info = {
                'error_code': 'MISSING_REQUIRED_PARAMETERS',
                'message': f"Missing required parameters: {', '.join(missing)}",
                'details': {
                    'missing_parameters': missing,
                    'provided_parameters': list(parameters.keys())
                }
            }
            raise ValueError(error_info)
            
        # Validate parameter values
        for key, value in parameters.items():
            # Validate empty strings
            if isinstance(value, str) and not value.strip():
                error_info = {
                    'error_code': 'INVALID_PARAMETER_VALUE',
                    'message': f"Invalid parameter value: {key} cannot be empty",
                    'details': {
                        'parameter': key,
                        'value': value
                    }
                }
                raise ValueError(error_info)
                
            # Validate None values
            if value is None:
                error_info = {
                    'error_code': 'INVALID_PARAMETER_VALUE',
                    'message': f"Invalid parameter value: {key} cannot be None",
                    'details': {
                        'parameter': key,
                        'value': value
                    }
                }
                raise ValueError(error_info)
                
            # Validate numerical values
            if isinstance(value, (int, float)) and value < 0:
                error_info = {
                    'error_code': 'INVALID_NUMERICAL_VALUE',
                    'message': f"Invalid numerical value for {key}: must be non-negative",
                    'details': {
                        'parameter': key,
                        'value': value
                    }
                }
                raise ValueError(error_info)
                
        # Validate analysis types
        if request_type in ['actuarial', 'market'] and 'analysis_type' in parameters:
            analysis_type = parameters['analysis_type']
            if analysis_type not in valid_analysis_types:
                error_info = {
                    'error_code': 'INVALID_ANALYSIS_TYPE',
                    'message': f"Invalid analysis type: {analysis_type}",
                    'details': {
                        'provided_type': analysis_type,
                        'valid_types': valid_analysis_types
                    }
                }
                raise ValueError(error_info)
                
        # Validate product design types
        if request_type == 'product' and 'design_type' in parameters:
            design_type = parameters['design_type']
            if design_type not in valid_design_types:
                error_info = {
                    'error_code': 'INVALID_DESIGN_TYPE',
                    'message': f"Invalid design type: {design_type}",
                    'details': {
                        'provided_type': design_type,
                        'valid_types': valid_design_types
                    }
                }
                raise ValueError(error_info)
    
    def format_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Format response"""
        if not result:
            return {
                'status': 'success',
                'engine': self.__class__.__name__,
                'data': {},
                'metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'config': self.config
                }
            }
            
        # Enhance metadata
        metadata = result.get('metadata', {})
        metadata.update({
            'timestamp': datetime.now().isoformat(),
            'engine': self.__class__.__name__,
            'config': self.config
        })
        
        return {
            'status': 'success',
            'data': {
                'insights': result.get('insights', []),
                'evidence': result.get('evidence', {}),
                'recommendations': result.get('recommendations', []),
                'warnings': result.get('warnings', [])
            },
            'metadata': metadata
        }
    
    def _process_integrated_analysis(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process integrated analysis"""
        try:
            # Ensure table mapping is included in parameters
            table_mapping = parameters.get('table_mapping', self.table_mapping)
            
            # Market analysis
            market_params = {
                'analysis_type': 'full',
                'target_segment': parameters.get('target_segment', 'general'),
                'table_mapping': table_mapping
            }
            market_result = self.market_engine.process(market_params)
            
            # Product analysis
            product_params = {
                'design_type': 'full',
                'coverage_type': parameters.get('coverage_type', 'basic'),
                'target_segment': parameters.get('target_segment', 'general'),
                'table_mapping': table_mapping
            }
            product_result = self.product_engine.process(product_params)
            
            # Actuarial analysis
            actuarial_params = {
                'analysis_type': 'full',
                'insurance_type': parameters.get('insurance_type', 'injury'),
                'period': parameters.get('period', 'latest'),
                'table_mapping': table_mapping
            }
            actuarial_result = self.actuarial_engine.process(actuarial_params)
            
            # Validate results
            if not market_result.get('data') or not product_result.get('data') or not actuarial_result.get('data'):
                raise ValueError("Required analysis data not found")
                
            # Generate integrated results
            result = {
                'data': {
                    'market_analysis': market_result['data'],
                    'product_analysis': product_result['data'],
                    'actuarial_analysis': actuarial_result['data'],
                    'target_segment': parameters.get('target_segment', 'general')
                },
                'metadata': {
                    'parameters': parameters
                }
            }
            
            # Generate recommendations
            result['data']['recommendations'] = self._generate_recommendations(
                market_result['data'],
                product_result['data'],
                actuarial_result['data']
            )
            
            return result
        except Exception as e:
            error_info = {
                'error_code': 'INTEGRATION_ERROR',
                'message': str(e),
                'details': parameters
            }
            raise ValueError(error_info)
    
    def _generate_recommendations(
        self,
        market_analysis: Dict[str, Any],
        product_analysis: Dict[str, Any],
        actuarial_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on integrated analysis
        Args:
            market_analysis: Market analysis results
            product_analysis: Product analysis results
            actuarial_analysis: Actuarial analysis results
        Returns:
            Recommendations
        """
        recommendations = []
        
        # Market-based recommendations
        if market_opportunities := market_analysis.get('opportunities', []):
            recommendations.append({
                'type': 'market_opportunity',
                'description': f"Market opportunities identified: {', '.join(market_opportunities)}",
                'priority': 'high'
            })
        
        # Product-based recommendations
        if product_pricing := product_analysis.get('pricing', {}):
            recommendations.append({
                'type': 'product_pricing',
                'description': f"Recommended premium range: {product_pricing.get('premium_range', {})}",
                'priority': 'medium'
            })
        
        # Actuarial-based recommendations
        if loss_ratio := actuarial_analysis.get('loss_ratio', {}):
            recommendations.append({
                'type': 'risk_management',
                'description': f"Loss ratio adjustment needed: {loss_ratio.get('adjusted_loss_ratio', 0):.2%}",
                'priority': 'high' if loss_ratio.get('loss_ratio', 0) > 0.8 else 'medium'
            })
        
        return {
            'recommendations': recommendations,
            'priority_summary': self._summarize_priorities(recommendations)
        }
    
    def _summarize_priorities(self, recommendations: list) -> Dict[str, int]:
        """
        Summarize recommendations by priority
        Args:
            recommendations: List of recommendations
        Returns:
            Priority counts
        """
        priority_count = {'high': 0, 'medium': 0, 'low': 0}
        for rec in recommendations:
            priority_count[rec['priority']] += 1
        return priority_count

    def _get_expected_fields(self, request_type: str) -> Set[str]:
        """
        Return expected fields for request type
        Args:
            request_type: Request type
        Returns:
            Expected fields set
        """
        # Basic common fields
        common_fields = {
            'metadata.timestamp',
            'metadata.engine',
            'metadata.config',
            'status'
        }

        # Type-specific fields
        type_specific_fields = {
            'actuarial': {
                'data.risk_metrics',
                'data.loss_ratio',
                'data.mortality_analysis',
                'data.morbidity_analysis'
            },
            'market': {
                'data.market_size',
                'data.competition_analysis',
                'data.demand_forecast',
                'data.market_trends'
            },
            'product': {
                'data.product_design',
                'data.pricing_strategy',
                'data.coverage_analysis',
                'data.benefit_structure'
            },
            'integrated': {
                'data.market_analysis',
                'data.product_analysis',
                'data.actuarial_analysis',
                'data.recommendations',
                'data.target_segment'
            }
        }

        # ResultSynthesizer-related fields
        synthesizer_fields = {
            'insights',
            'evidence',
            'recommendations',
            'warnings',
            'metadata.confidence_scores',
            'metadata.data_completeness'
        }

        # Combine fields based on request type
        expected_fields = common_fields.union(synthesizer_fields)
        if request_type in type_specific_fields:
            expected_fields = expected_fields.union(type_specific_fields[request_type])

        return expected_fields 