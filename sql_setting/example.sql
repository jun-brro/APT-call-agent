-- Market Analysis
CREATE TABLE market_research (
    id SERIAL PRIMARY KEY,
    research_date DATE,
    target_segment JSONB,
    segment VARCHAR(100),
    market_size DECIMAL(15,2),
    competitor_analysis JSONB,
    demand_forecast JSONB
);

-- Product Design
CREATE TABLE product_templates (
    template_id SERIAL PRIMARY KEY,
    coverage_type VARCHAR(50),
    target_market JSONB,
    benefit_structure JSONB,
    rider_options JSONB,
    underwriting_rules JSONB,
    created_date DATE,
    last_modified DATE
);

-- Pricing Models
CREATE TABLE pricing_models (
    model_id SERIAL PRIMARY KEY,
    product_template_id INTEGER REFERENCES product_templates(template_id),
    base_rate DECIMAL(10,6),
    adjustment_factors JSONB,
    profitability_metrics JSONB,
    market_constraints JSONB,
    effective_date DATE
);

-- Risk Scenarios
CREATE TABLE risk_scenarios (
    scenario_id SERIAL PRIMARY KEY,
    scenario_name VARCHAR(100),
    scenario_type VARCHAR(50),
    parameters JSONB,
    stress_factors JSONB
);

-- Simulation Results
CREATE TABLE simulation_results (
    simulation_id SERIAL PRIMARY KEY,
    product_template_id INTEGER REFERENCES product_templates(template_id),
    scenario_id INTEGER REFERENCES risk_scenarios(scenario_id),
    simulation_date DATE,
    results JSONB,
    key_metrics JSONB
);

-- Regulatory Requirements
CREATE TABLE regulatory_requirements (
    requirement_id SERIAL PRIMARY KEY,
    jurisdiction VARCHAR(50),
    product_type VARCHAR(50),
    requirement_type VARCHAR(50),
    details JSONB,
    effective_date DATE,
    expiry_date DATE
);

-- Product Development Workflow
CREATE TABLE development_projects (
    project_id SERIAL PRIMARY KEY,
    product_template_id INTEGER REFERENCES product_templates(template_id),
    project_status VARCHAR(50),
    timeline JSONB,
    stakeholders JSONB,
    current_stage VARCHAR(50),
    documentation JSONB
);

-- Views for Analysis
CREATE VIEW product_performance_metrics AS
SELECT 
    pt.template_id,
    pt.coverage_type,
    pm.base_rate,
    sr.results->'performance_metrics' as performance_metrics,
    sr.key_metrics
FROM product_templates pt
JOIN pricing_models pm ON pt.template_id = pm.product_template_id
JOIN simulation_results sr ON pt.template_id = sr.product_template_id
WHERE sr.scenario_id = (
    SELECT scenario_id 
    FROM risk_scenarios 
    WHERE scenario_type = 'base'
);

CREATE VIEW regulatory_compliance_status AS
SELECT 
    dp.project_id,
    pt.coverage_type,
    rr.jurisdiction,
    rr.requirement_type,
    dp.documentation->'compliance_status' as compliance_status
FROM development_projects dp
JOIN product_templates pt ON dp.product_template_id = pt.template_id
CROSS JOIN regulatory_requirements rr
WHERE rr.product_type = pt.coverage_type
AND CURRENT_DATE BETWEEN rr.effective_date AND COALESCE(rr.expiry_date, '9999-12-31');

-- Indexes for Performance
CREATE INDEX idx_product_templates_coverage ON product_templates(coverage_type);
CREATE INDEX idx_pricing_models_dates ON pricing_models(effective_date);
CREATE INDEX idx_simulation_results_dates ON simulation_results(simulation_date);
CREATE INDEX idx_regulatory_requirements_jurisdiction ON regulatory_requirements(jurisdiction, product_type);

-- Create insurance data tables
CREATE TABLE quarterly_insurance_contracts (
    year INTEGER,
    insurance_category VARCHAR(100),
    q1_contracts INTEGER,
    q2_contracts INTEGER,
    q3_contracts INTEGER,
    q4_contracts INTEGER,
    q1_risk_premium DECIMAL(15,2),
    q2_risk_premium DECIMAL(15,2),
    q3_risk_premium DECIMAL(15,2),
    q4_risk_premium DECIMAL(15,2),
    total_contracts INTEGER,
    total_risk_premium DECIMAL(15,2),
    total_premium DECIMAL(15,2)
);

CREATE TABLE quarterly_insurance_claims (
    year INTEGER,
    insurance_category VARCHAR(100),
    q1_accident_count INTEGER,
    q1_claims DECIMAL(15,2),
    q2_accident_count INTEGER,
    q2_claims DECIMAL(15,2),
    q3_accident_count INTEGER,
    q3_claims DECIMAL(15,2),
    q4_accident_count INTEGER,
    q4_claims DECIMAL(15,2),
    total_accident_count INTEGER,
    total_claims DECIMAL(15,2)
);

CREATE TABLE insurance_contracts_by_age (
    insurance_category VARCHAR(100),
    age_group VARCHAR(50),
    total_contracts INTEGER,
    total_premium DECIMAL(15,2)
);

-- Create mapping for insurance categories
CREATE TABLE IF NOT EXISTS insurance_category_mapping (
    korean_category VARCHAR(100),
    english_category VARCHAR(100),
    PRIMARY KEY (korean_category)
);

-- Insert category mappings
INSERT INTO insurance_category_mapping (korean_category, english_category) 
VALUES 
    ('상해', 'injury'),
    ('질병', 'disease'),
    ('비용손해', 'expense_damage'),
    ('상해및질병', 'injury_and_disease'),
    ('배상책임손해', 'liability_damage'),
    ('재물손해', 'property_damage')
ON CONFLICT (korean_category) DO UPDATE 
SET english_category = EXCLUDED.english_category;

-- Create raw data tables for CSV import with TEXT columns
CREATE TABLE insurance_accident_results (
    year TEXT,
    보험대분류 TEXT,
    보험분류 TEXT,
    q1_accident_count TEXT,
    q1_claims TEXT,
    q2_accident_count TEXT,
    q2_claims TEXT,
    q3_accident_count TEXT,
    q3_claims TEXT,
    q4_accident_count TEXT,
    q4_claims TEXT,
    total_accident_count TEXT,
    total_claims TEXT
);

CREATE TABLE insurance_contract_results (
    year TEXT,
    보험대분류 TEXT,
    보험분류 TEXT,
    q1_contracts TEXT,
    q1_risk_premium TEXT,
    q2_contracts TEXT,
    q2_risk_premium TEXT,
    q3_contracts TEXT,
    q3_risk_premium TEXT,
    q4_contracts TEXT,
    q4_risk_premium TEXT,
    total_contracts TEXT,
    total_risk_premium TEXT
);

CREATE TABLE age_based_contract_results (
    year TEXT,
    보험대분류 TEXT,
    보험분류 TEXT,
    under_10_contracts TEXT,
    under_10_premium TEXT,
    age_10_20_contracts TEXT,
    age_10_20_premium TEXT,
    age_20_30_contracts TEXT,
    age_20_30_premium TEXT,
    age_30_40_contracts TEXT,
    age_30_40_premium TEXT,
    age_40_50_contracts TEXT,
    age_40_50_premium TEXT,
    age_50_60_contracts TEXT,
    age_50_60_premium TEXT,
    over_60_contracts TEXT,
    over_60_premium TEXT,
    total_contracts TEXT,
    total_premium TEXT
);

-- Load CSV data
\COPY insurance_accident_results FROM 'your-file.csv' WITH CSV HEADER;
\COPY insurance_contract_results FROM 'your-file.csv' WITH CSV HEADER;
\COPY age_based_contract_results FROM 'your-file.csv' WITH CSV HEADER;

-- Insert processed data into final tables with data type conversion
INSERT INTO quarterly_insurance_claims 
SELECT 
    year::INTEGER,
    m.english_category,
    REPLACE(q1_accident_count, ',', '')::INTEGER,
    REPLACE(q1_claims, ',', '')::DECIMAL,
    REPLACE(q2_accident_count, ',', '')::INTEGER,
    REPLACE(q2_claims, ',', '')::DECIMAL,
    REPLACE(q3_accident_count, ',', '')::INTEGER,
    REPLACE(q3_claims, ',', '')::DECIMAL,
    REPLACE(q4_accident_count, ',', '')::INTEGER,
    REPLACE(q4_claims, ',', '')::DECIMAL,
    REPLACE(total_accident_count, ',', '')::INTEGER,
    REPLACE(total_claims, ',', '')::DECIMAL
FROM insurance_accident_results r
AND r.year IS NOT NULL;

INSERT INTO quarterly_insurance_contracts 
SELECT 
    year::INTEGER,
    m.english_category,
    REPLACE(q1_contracts, ',', '')::INTEGER,
    REPLACE(q2_contracts, ',', '')::INTEGER,
    REPLACE(q3_contracts, ',', '')::INTEGER,
    REPLACE(q4_contracts, ',', '')::INTEGER,
    REPLACE(q1_risk_premium, ',', '')::DECIMAL,
    REPLACE(q2_risk_premium, ',', '')::DECIMAL,
    REPLACE(q3_risk_premium, ',', '')::DECIMAL,
    REPLACE(q4_risk_premium, ',', '')::DECIMAL,
    REPLACE(total_contracts, ',', '')::INTEGER,
    REPLACE(total_risk_premium, ',', '')::DECIMAL,
    REPLACE(total_risk_premium, ',', '')::DECIMAL
FROM insurance_contract_results r
AND r.year IS NOT NULL;

INSERT INTO insurance_contracts_by_age
SELECT 
    m.english_category,
    age_group,
    contracts::INTEGER,
    premium::DECIMAL
FROM (
    SELECT 
        보험대분류,
        '0-10' as age_group,
        REPLACE(under_10_contracts, ',', '') as contracts,
        REPLACE(under_10_premium, ',', '') as premium
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '10-20',
        REPLACE(age_10_20_contracts, ',', ''),
        REPLACE(age_10_20_premium, ',', '')
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '20-30',
        REPLACE(age_20_30_contracts, ',', ''),
        REPLACE(age_20_30_premium, ',', '')
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '30-40',
        REPLACE(age_30_40_contracts, ',', ''),
        REPLACE(age_30_40_premium, ',', '')
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '40-50',
        REPLACE(age_40_50_contracts, ',', ''),
        REPLACE(age_40_50_premium, ',', '')
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '50-60',
        REPLACE(age_50_60_contracts, ',', ''),
        REPLACE(age_50_60_premium, ',', '')
    FROM age_based_contract_results
    UNION ALL
    SELECT 
        보험대분류,
        '60+',
        REPLACE(over_60_contracts, ',', ''),
        REPLACE(over_60_premium, ',', '')
    FROM age_based_contract_results
) a

-- Clean up raw data tables
DROP TABLE insurance_accident_results;
DROP TABLE insurance_contract_results;
DROP TABLE age_based_contract_results;

-- Create statistical views
CREATE OR REPLACE VIEW insurance_statistics AS
SELECT 
    ic.year,
    ic.insurance_category,
    ic.total_contracts,
    ic.total_risk_premium,
    icl.total_claims,
    ROUND((icl.total_claims / ic.total_risk_premium * 100)::numeric, 2) as loss_ratio,
    ROUND(((ic.total_risk_premium - icl.total_claims) / ic.total_risk_premium * 100)::numeric, 2) as profit_margin
FROM quarterly_insurance_contracts ic
LEFT JOIN quarterly_insurance_claims icl 
    ON ic.year = icl.year 
    AND ic.insurance_category = icl.insurance_category;

CREATE OR REPLACE VIEW age_distribution_analysis AS
SELECT 
    insurance_category,
    age_group,
    total_contracts,
    total_premium,
    ROUND((total_contracts::float / SUM(total_contracts) OVER (PARTITION BY insurance_category) * 100)::numeric, 2) as contracts_percentage,
    ROUND((total_premium::float / SUM(total_premium) OVER (PARTITION BY insurance_category) * 100)::numeric, 2) as premium_percentage
FROM insurance_contracts_by_age;

CREATE OR REPLACE VIEW quarterly_trend_analysis AS
SELECT 
    year,
    insurance_category,
    ROUND(((q4_contracts - q1_contracts)::float / q1_contracts * 100)::numeric, 2) as contracts_growth_rate,
    ROUND(((q4_risk_premium - q1_risk_premium)::float / q1_risk_premium * 100)::numeric, 2) as premium_growth_rate
FROM quarterly_insurance_contracts;

-- Create indexes for performance
CREATE INDEX idx_quarterly_contracts_year ON quarterly_insurance_contracts(year);
CREATE INDEX idx_quarterly_contracts_category ON quarterly_insurance_contracts(insurance_category);
CREATE INDEX idx_quarterly_claims_year ON quarterly_insurance_claims(year);
CREATE INDEX idx_quarterly_claims_category ON quarterly_insurance_claims(insurance_category);
CREATE INDEX idx_contracts_age_category ON insurance_contracts_by_age(insurance_category);

-- Create query metrics table for monitoring
CREATE TABLE query_metrics (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    execution_time FLOAT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    query_plan JSONB,
    rows_affected INTEGER
);

CREATE INDEX idx_query_metrics_execution_time ON query_metrics(execution_time);
CREATE INDEX idx_query_metrics_timestamp ON query_metrics(timestamp);
