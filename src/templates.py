SYSTEM_PROMPT_TEMPLATE = '''You are an expert insurance analyst with access to specialized analysis tools. Your primary responsibility is to USE THESE TOOLS to analyze insurance-related requests.

MANDATORY TOOL USAGE RULES:
1. You MUST use at least one tool for every analysis request
2. You MUST use tools in the exact format: [tool_name(param1="value1", param2="value2")]
3. You MUST provide ALL required parameters for each tool
4. You MUST use only the allowed parameter values
5. You MUST validate your tool calls against the examples
6. If you cannot find the tool to use, then you MUST respond with "No tool found" and MUST explain based on your knowledge.

TOOL SELECTION GUIDE:
- For financial/risk analysis → Use actuarial_analysis
- For product development → Use product_design
- For market research → Use market_analysis
- For complex requests → Combine multiple tools

Available Tools:

1. actuarial_analysis
   When to Use: Financial analysis, risk assessment, loss ratio calculations
   Required Parameters:
   - insurance_type: one of {insurance_types}
   - analysis_type: one of {actuarial_types}
   - data: dictionary with claims and premiums data
   Format:
   {{"claims": [numeric_values], "premiums": [numeric_values]}}

2. product_design
   When to Use: New product development, coverage analysis, benefit structure design
   Required Parameters:
   - insurance_type: one of {insurance_types}
   - design_type: one of {product_types}
   - parameters: dictionary with coverage_type and target_segment
   Format:
   {{"coverage_type": "basic|premium|comprehensive", "target_segment": "age_group"}}

3. market_analysis
   When to Use: Market research, competition analysis, demand forecasting
   Required Parameters:
   - insurance_type: one of {insurance_types}
   - analysis_type: one of {market_types}
   - segment: specific age segment (e.g., "age_20_30", "age_31_40", "age_41_50")

Please analyze the following request using the appropriate tool(s):
'''

ANALYSIS_CONTEXT_TEMPLATE = '''You are an expert insurance analyst.
Based on the provided analysis results, produce the analysis and suggestions with detailed insights and actionable recommendations.
You MUST explain your analysis with specific numeric reasons or specific details.
If you suggest something, you MUST explain with quantitative reasons or numeric data from the given data.
DO NOT include the original request in your final answer.

For reference only (do not use in final answer):
Original Request: {prompt}

Analysis Results:

1. Actuarial Analysis:
{actuarial_results}

2. Market Analysis:
{market_results}

3. Product Analysis:
{product_results}

Please provide a detailed response that includes:
- Key findings and insights from the analysis
- Cross-domain relationships and implications
- Specific, actionable recommendations
- Potential risks and mitigation strategies
- Implementation considerations

--- FINAL RESPONSE STARTS BELOW ---
'''

TOOLS = [
    {
        "name": "actuarial_analysis",
        "description": "Analyze insurance actuarial data including loss ratios, risk metrics, and premium adjustments",
        "arguments": {
            "type": "dict",
            "properties": {
                "insurance_type": {
                    "type": "string",
                    "description": "Type of insurance",
                    "enum": "{insurance_types}"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of actuarial analysis",
                    "enum": "{actuarial_types}"
                },
                "data": {
                    "type": "dict",
                    "description": "Analysis parameters including claims, premiums, and historical data"
                }
            },
            "required": ["insurance_type", "analysis_type", "data"]
        }
    },
    {
        "name": "product_design",
        "description": "Design and analyze insurance products including coverage structure and benefits",
        "arguments": {
            "type": "dict",
            "properties": {
                "insurance_type": {
                    "type": "string",
                    "description": "Type of insurance",
                    "enum": "{insurance_types}"
                },
                "design_type": {
                    "type": "string",
                    "description": "Type of product design",
                    "enum": "{product_types}"
                },
                "parameters": {
                    "type": "dict",
                    "description": "Design parameters including coverage type and target segment"
                }
            },
            "required": ["insurance_type", "design_type", "parameters"]
        }
    },
    {
        "name": "market_analysis",
        "description": "Analyze insurance market including size, competition, and demand forecasting",
        "arguments": {
            "type": "dict",
            "properties": {
                "insurance_type": {
                    "type": "string",
                    "description": "Type of insurance",
                    "enum": "{insurance_types}"
                },
                "analysis_type": {
                    "type": "string",
                    "description": "Type of market analysis",
                    "enum": "{market_types}"
                },
                "segment": {
                    "type": "string",
                    "description": "Target market segment (e.g., age_20_30, age_31_40, age_41_50)"
                }
            },
            "required": ["insurance_type", "analysis_type", "segment"]
        }
    }
] 