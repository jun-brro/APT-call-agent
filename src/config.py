import os
from pathlib import Path

# Default paths
DEFAULT_MODEL_PATH = os.getenv('MODEL_PATH', 'models/watt-tool-8B')
DEFAULT_RESPONSE_MODEL_PATH = os.getenv('RESPONSE_MODEL_PATH', 'models/Mistral-Small-24B-Instruct-2501')

# Valid types
VALID_INSURANCE_TYPES = ["injury", "disease", "expense_damage", "injury_and_disease"]

VALID_ACTUARIAL_ANALYSIS_TYPES = [
    "loss_ratio", "risk_metrics", "utilization_pattern", "cost_analysis",
    "risk_assessment", "progression_analysis", "treatment_cost", "survival_rate",
    "mortality_analysis", "morbidity_analysis", "claim_pattern", "expense_ratio"
]

VALID_MARKET_ANALYSIS_TYPES = [
    "market_size", "market_share", "full", "demand_projection",
    "service_utilization", "segment_analysis", "telehealth_impact",
    "competition_analysis", "customer_behavior", "distribution_channel",
    "market_penetration", "growth_potential", "regional_performance"
]

VALID_PRODUCT_DESIGN_TYPES = [
    "coverage", "benefits", "pricing", "benefit_structure",
    "coverage_limit", "waiting_period", "wellness_program",
    "parametric_trigger", "mental_health", "chronic_care",
    "telehealth_service", "hybrid_product"
]

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432)),
    'database': os.getenv('DB_NAME', 'insurance_db'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

# Analysis configuration
ACTUARIAL_CONFIG = {
    'mortality_table': 'standard_2023',
    'expense_inflation': 0.025,
    'interest_rate': 0.025
}

PRODUCT_CONFIG = {
    'min_premium': 1000,
    'max_coverage': 1000000000
}

MARKET_CONFIG = {
    'market_data_source': 'external_api',
    'analysis_period': 12
}

# Model configuration
MODEL_CONFIG = {
    'max_length': 4096,
    'num_beams': 1,
    'temperature': 0.9,
    'top_p': 0.9,
    'do_sample': True
} 