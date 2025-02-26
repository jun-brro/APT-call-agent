INSURANCE_TYPE_MAPPING = {
    # Direct mappings
    'injury': 'injury',
    'disease': 'disease',
    'expense_damage': 'expense_damage',
    'injury_and_disease': 'injury_and_disease',
    
    # Extended mappings
    'mental_health': 'disease',
    'dental': 'disease',
    'critical_illness': 'disease',
    'long_term_care': 'disease',
    'cyber': 'expense_damage',
    'disability': 'injury_and_disease',
    'cancer': 'disease',
    'parametric': 'expense_damage',
    'wellness': 'disease',
    'hospital_cash': 'disease',
    'income_protection': 'injury_and_disease',
    'auto': 'expense_damage',
    'telehealth': 'disease',
    'chronic_care': 'disease'
}

# Data loading column mappings
DATA_COLUMN_MAPPINGS = {
    # Common columns
    'year': 'year',
    'insurance_category': 'insurance_category',
    'insurance_type': 'insurance_type',
    
    # Claims by amount
    'claims_under_10m': 'claims_under_10m',
    'payment_under_10m': 'payment_under_10m',
    'claims_under_50m': 'claims_under_50m',
    'payment_under_50m': 'payment_under_50m',
    'claims_under_100m': 'claims_under_100m',
    'payment_under_100m': 'payment_under_100m',
    'claims_over_100m': 'claims_over_100m',
    'payment_over_100m': 'payment_over_100m',
    'total_claims': 'total_claims',
    'total_payment': 'total_payment',

    # Claims by period
    'claims_under_1y': 'claims_under_1y',
    'payment_under_1y': 'payment_under_1y',
    'claims_under_3y': 'claims_under_3y',
    'payment_under_3y': 'payment_under_3y',
    'claims_under_5y': 'claims_under_5y',
    'payment_under_5y': 'payment_under_5y',
    'claims_under_7y': 'claims_under_7y',
    'payment_under_7y': 'payment_under_7y',
    'claims_over_7y': 'claims_over_7y',
    'payment_over_7y': 'payment_over_7y',

    # Quarterly data
    'q1_claims': 'q1_claims',
    'q1_payment': 'q1_payment',
    'q2_claims': 'q2_claims',
    'q2_payment': 'q2_payment',
    'q3_claims': 'q3_claims',
    'q3_payment': 'q3_payment',
    'q4_claims': 'q4_claims',
    'q4_payment': 'q4_payment',

    # Contract performance
    'q1_contracts': 'q1_contracts',
    'q1_risk_premium': 'q1_risk_premium',
    'q2_contracts': 'q2_contracts',
    'q2_risk_premium': 'q2_risk_premium',
    'q3_contracts': 'q3_contracts',
    'q3_risk_premium': 'q3_risk_premium',
    'q4_contracts': 'q4_contracts',
    'q4_risk_premium': 'q4_risk_premium',
    'total_contracts': 'total_contracts',
    'total_risk_premium': 'total_risk_premium',

    # Age-based data
    'contracts_under_10': 'contracts_under_10',
    'risk_premium_under_10': 'risk_premium_under_10',
    'contracts_10_to_20': 'contracts_10_to_20',
    'risk_premium_10_to_20': 'risk_premium_10_to_20',
    'contracts_20_to_30': 'contracts_20_to_30',
    'risk_premium_20_to_30': 'risk_premium_20_to_30',
    'contracts_30_to_40': 'contracts_30_to_40',
    'risk_premium_30_to_40': 'risk_premium_30_to_40',
    'contracts_40_to_50': 'contracts_40_to_50',
    'risk_premium_40_to_50': 'risk_premium_40_to_50',
    'contracts_50_to_60': 'contracts_50_to_60',
    'risk_premium_50_to_60': 'risk_premium_50_to_60',
    'contracts_over_60': 'contracts_over_60',
    'risk_premium_over_60': 'risk_premium_over_60',

    # Health insurance
    'region': 'region',
    'occupation_type': 'occupation_type',

    # Product returns
    'product_returns_and_fees': 'product_returns_and_fees'
}

# TODO: Replace with actual Korean column names from your data source
# Format: 'korean_column_name': 'english_column_name'
KOREAN_TO_ENGLISH_COLUMNS = {
    'TODO_YEAR': 'year',
    'TODO_INSURANCE_CATEGORY': 'insurance_category',
    'TODO_INSURANCE_TYPE': 'insurance_type',
    
    # Claims by amount
    'TODO_CLAIMS_UNDER_10M': 'claims_under_10m',
    'TODO_PAYMENT_UNDER_10M': 'payment_under_10m',
    'TODO_CLAIMS_UNDER_50M': 'claims_under_50m',
    'TODO_PAYMENT_UNDER_50M': 'payment_under_50m',
    'TODO_CLAIMS_UNDER_100M': 'claims_under_100m',
    'TODO_PAYMENT_UNDER_100M': 'payment_under_100m',
    'TODO_CLAIMS_OVER_100M': 'claims_over_100m',
    'TODO_PAYMENT_OVER_100M': 'payment_over_100m',
    'TODO_TOTAL_CLAIMS': 'total_claims',
    'TODO_TOTAL_PAYMENT': 'total_payment',

    # Claims by period
    'TODO_CLAIMS_UNDER_1Y': 'claims_under_1y',
    'TODO_PAYMENT_UNDER_1Y': 'payment_under_1y',
    'TODO_CLAIMS_UNDER_3Y': 'claims_under_3y',
    'TODO_PAYMENT_UNDER_3Y': 'payment_under_3y',
    'TODO_CLAIMS_UNDER_5Y': 'claims_under_5y',
    'TODO_PAYMENT_UNDER_5Y': 'payment_under_5y',
    'TODO_CLAIMS_UNDER_7Y': 'claims_under_7y',
    'TODO_PAYMENT_UNDER_7Y': 'payment_under_7y',
    'TODO_CLAIMS_OVER_7Y': 'claims_over_7y',
    'TODO_PAYMENT_OVER_7Y': 'payment_over_7y',

    # Quarterly data
    'TODO_Q1_CLAIMS': 'q1_claims',
    'TODO_Q1_PAYMENT': 'q1_payment',
    'TODO_Q2_CLAIMS': 'q2_claims',
    'TODO_Q2_PAYMENT': 'q2_payment',
    'TODO_Q3_CLAIMS': 'q3_claims',
    'TODO_Q3_PAYMENT': 'q3_payment',
    'TODO_Q4_CLAIMS': 'q4_claims',
    'TODO_Q4_PAYMENT': 'q4_payment',

    # Contract performance
    'TODO_Q1_CONTRACTS': 'q1_contracts',
    'TODO_Q1_RISK_PREMIUM': 'q1_risk_premium',
    'TODO_Q2_CONTRACTS': 'q2_contracts',
    'TODO_Q2_RISK_PREMIUM': 'q2_risk_premium',
    'TODO_Q3_CONTRACTS': 'q3_contracts',
    'TODO_Q3_RISK_PREMIUM': 'q3_risk_premium',
    'TODO_Q4_CONTRACTS': 'q4_contracts',
    'TODO_Q4_RISK_PREMIUM': 'q4_risk_premium',
    'TODO_TOTAL_CONTRACTS': 'total_contracts',
    'TODO_TOTAL_RISK_PREMIUM': 'total_risk_premium',

    # Age-based data
    'TODO_CONTRACTS_UNDER_10': 'contracts_under_10',
    'TODO_RISK_PREMIUM_UNDER_10': 'risk_premium_under_10',
    'TODO_CONTRACTS_10_TO_20': 'contracts_10_to_20',
    'TODO_RISK_PREMIUM_10_TO_20': 'risk_premium_10_to_20',
    'TODO_CONTRACTS_20_TO_30': 'contracts_20_to_30',
    'TODO_RISK_PREMIUM_20_TO_30': 'risk_premium_20_to_30',
    'TODO_CONTRACTS_30_TO_40': 'contracts_30_to_40',
    'TODO_RISK_PREMIUM_30_TO_40': 'risk_premium_30_to_40',
    'TODO_CONTRACTS_40_TO_50': 'contracts_40_to_50',
    'TODO_RISK_PREMIUM_40_TO_50': 'risk_premium_40_to_50',
    'TODO_CONTRACTS_50_TO_60': 'contracts_50_to_60',
    'TODO_RISK_PREMIUM_50_TO_60': 'risk_premium_50_to_60',
    'TODO_CONTRACTS_OVER_60': 'contracts_over_60',
    'TODO_RISK_PREMIUM_OVER_60': 'risk_premium_over_60',

    # Health insurance
    'TODO_REGION': 'region',
    'TODO_OCCUPATION_TYPE': 'occupation_type',

    # Product returns
    'TODO_PRODUCT_RETURNS_AND_FEES': 'product_returns_and_fees'
}

# TODO: Replace with actual Korean value names from your data source
# Format: 'korean_value': 'english_value'
KOREAN_TO_ENGLISH_VALUES = {
    'TODO_YEAR_SUBTOTAL': 'year_subtotal',
    'TODO_INSURANCE_CATEGORY_SUBTOTAL': 'insurance_category_subtotal',
    'TODO_DISEASE': 'disease',
    'TODO_INJURY': 'injury',
    'TODO_INJURY_AND_DISEASE': 'injury_and_disease',
    'TODO_LIABILITY_DAMAGE': 'liability_damage',
    'TODO_EXPENSE_DAMAGE': 'expense_damage',
    'TODO_PROPERTY_DAMAGE': 'property_damage',
    'TODO_OTHERS': 'others',
    
    # Detailed insurance classifications
    'TODO_GENERAL_INJURY': 'general_injury',
    'TODO_TRAFFIC_INJURY': 'traffic_injury',
    'TODO_DRIVING_INJURY': 'driving_injury',
    'TODO_WORK_INJURY': 'work_injury',
    'TODO_LEISURE_INJURY': 'leisure_injury',
    'TODO_DISEASE_DEATH': 'disease_death',
    'TODO_DISEASE_HOSPITALIZATION': 'disease_hospitalization',
    'TODO_DISEASE_SURGERY': 'disease_surgery'
}

# TODO: Replace with actual data file names from your data source
# Format: 'table_name': 'file_name.csv'
DATA_FILE_MAPPINGS = {
    'insurance_claims_by_amount': 'TODO_CLAIMS_BY_AMOUNT.csv',
    'insurance_claims_by_period': 'TODO_CLAIMS_BY_PERIOD.csv',
    'health_insurance_premium': 'TODO_HEALTH_INSURANCE_PREMIUM.csv',
    'insurance_claims_by_quarter': 'TODO_CLAIMS_BY_QUARTER.csv',
    'insurance_contracts_by_quarter': 'TODO_CONTRACTS_BY_QUARTER.csv',
    'product_returns_and_fees': 'TODO_PRODUCT_RETURNS.csv',
    'insurance_contracts_by_age': 'TODO_CONTRACTS_BY_AGE.csv'
}

# Analysis keywords
ANALYSIS_KEYWORDS = {
    # Actuarial analysis keywords
    'actuarial': {
        'loss_ratio', 'claim', 'premium', 'cost', 'risk', 'mortality',
        'morbidity', 'survival', 'utilization', 'frequency', 'severity',
        'recovery', 'progression', 'treatment', 'hospitalization',
        'disability', 'pricing', 'profitability', 'expense', 'reserve',
        'underwriting', 'reinsurance', 'portfolio', 'exposure'
    },
    # Market analysis keywords
    'market': {
        'market', 'demand', 'trend', 'competition', 'segment',
        'distribution', 'penetration', 'growth', 'opportunity',
        'customer', 'behavior', 'preference', 'adoption', 'channel',
        'region', 'demographic', 'satisfaction', 'retention', 'churn',
        'acquisition', 'digital', 'innovation', 'ecosystem'
    },
    # Product design keywords
    'product': {
        'coverage', 'benefit', 'design', 'feature', 'structure',
        'exclusion', 'waiting', 'limit', 'eligibility', 'underwriting',
        'wellness', 'program', 'service', 'option', 'rider',
        'parametric', 'hybrid', 'bundling', 'customization', 'flexibility',
        'integration', 'platform', 'experience', 'journey'
    }
}

# Result templates
RESULT_TEMPLATES = {
    'actuarial': {
        'metrics': [
            'loss_ratio', 'combined_ratio', 'expense_ratio',
            'mortality_rate', 'morbidity_rate', 'recovery_rate',
            'claim_frequency', 'claim_severity', 'reserve_adequacy'
        ],
        'trends': [
            'claim_trend', 'premium_trend', 'expense_trend',
            'mortality_trend', 'morbidity_trend', 'utilization_trend'
        ],
        'risk_factors': [
            'underwriting_risk', 'pricing_risk', 'reserve_risk',
            'operational_risk', 'market_risk', 'credit_risk'
        ]
    },
    'market': {
        'metrics': [
            'market_size', 'market_share', 'growth_rate',
            'penetration_rate', 'customer_satisfaction',
            'retention_rate', 'acquisition_cost', 'lifetime_value'
        ],
        'trends': [
            'market_trend', 'competition_trend', 'channel_trend',
            'customer_trend', 'digital_trend', 'innovation_trend'
        ],
        'segments': [
            'age_group', 'income_level', 'occupation',
            'region', 'lifestyle', 'health_status'
        ]
    },
    'product': {
        'metrics': [
            'product_performance', 'coverage_ratio',
            'benefit_utilization', 'service_adoption',
            'customer_satisfaction', 'profitability'
        ],
        'features': [
            'core_coverage', 'additional_benefits',
            'service_integration', 'digital_features',
            'wellness_programs', 'value_added_services'
        ],
        'innovations': [
            'parametric_triggers', 'hybrid_solutions',
            'ecosystem_integration', 'personalization',
            'prevention_services', 'digital_engagement'
        ]
    }
} 