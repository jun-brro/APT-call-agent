from typing import Dict, Any, List, Optional, Set
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from ..base import BaseEngine
from ....data.connectors.db_connector import DBConnector
from ....data.processors.query_manager import QueryManager
import logging

logger = logging.getLogger(__name__)

class ActuarialEngine(BaseEngine):
    """Actuarial Engine - Insurance actuarial analysis and calculations"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.db = DBConnector(config.get('db_config'))
        self.table_mapping = config.get('table_mapping', {
            'contracts': 'quarterly_insurance_contracts',
            'claims': 'quarterly_insurance_claims',
            'market': 'market_research',
            'products': 'product_templates',
            'pricing': 'pricing_models'
        })
        self.query_manager = QueryManager(self.db, self.table_mapping)
        self._initialize()
    
    def _initialize(self) -> None:
        """Actuarial Engine Initialization"""
        super()._initialize()
        # Actuarial Basic Settings
        self.mortality_table = self.config.get('mortality_table', 'standard_2023')
        self.expense_inflation = self.config.get('expense_inflation', 0.02)
        self.interest_rate = self.config.get('interest_rate', 0.025)
        
        # Loss Ratio Related Settings
        self.target_loss_ratios = {
            'injury': 0.75,
            'disease': 0.70,
            'expense_damage': 0.65,
            'injury_and_disease': 0.68
        }
        
        # Risk Measurement Settings
        self.var_confidence_levels = {
            'standard': 0.95,
            'conservative': 0.99,
            'aggressive': 0.90
        }
        
        # Premium Adjustment Limits
        self.premium_adjustment_limits = {
            'min_factor': 0.7,
            'max_factor': 1.3,
            'standard_step': 0.05
        }

        # Flexible analysis_type mapping
        self.analysis_types = {
            'loss_ratio': self._calculate_loss_ratio,
            'risk_metrics': self._calculate_risk_metrics,
            'mortality': self._analyze_mortality_patterns,
            'morbidity': self._analyze_morbidity_patterns,
            'treatment_cost': self._analyze_treatment_costs,
            'utilization': self._analyze_utilization_patterns,
            'stage_progression': self._analyze_stage_progression,
            'recovery_pattern': self._analyze_recovery_patterns,
            'disability_duration': self._analyze_disability_duration,
            'early_detection': self._analyze_early_detection_impact,
            'prevention_impact': self._analyze_prevention_impact,
            'claim_severity': self._analyze_claim_severity,
            'benefit_utilization': self._analyze_benefit_utilization,
            'age_specific_loss': self.analyze_age_specific_loss_ratio,
            'quarterly_risk': self.analyze_quarterly_risk_metrics,
            'claim_pattern': self.analyze_claim_patterns,
            'expense_analysis': self.analyze_expense_ratios,
            'retention_metrics': self.analyze_retention_metrics,
            'full': self._perform_full_analysis
        }
    
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Actuarial Analysis Processing"""
        try:
            analysis_type = parameters.get('analysis_type', 'full')
            insurance_type = parameters.get('insurance_type', 'injury')
            
            # Flexible insurance_type mapping
            insurance_type = self._map_insurance_type(insurance_type)
            
            # Flexible analysis_type mapping
            analysis_type = self._map_analysis_type(analysis_type)
            
            if analysis_type in self.analysis_types:
                result = self.analysis_types[analysis_type](parameters)
            else:
                result = self._perform_full_analysis(parameters)
            
            return self.format_response(result)
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            raise
    
    def _calculate_loss_ratio(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Loss Ratio Calculation"""
        insurance_type = data.get('insurance_type', 'injury')
        loss_ratio_data = self.query_manager.get_loss_ratio(insurance_type)
        
        if not loss_ratio_data:
            return {
                'loss_ratio': 0.0,
                'adjusted_loss_ratio': 0.0,
                'target_ratio': self.target_loss_ratios.get(insurance_type, 0.7),
                'total_claims': 0,
                'total_premiums': 0
            }
        
        base_loss_ratio = loss_ratio_data.get('loss_ratio', 0)
        adjusted_loss_ratio = base_loss_ratio * (1 + self.expense_inflation)
        target_ratio = self.target_loss_ratios.get(insurance_type, 0.7)
        
        return {
            'loss_ratio': base_loss_ratio,
            'adjusted_loss_ratio': adjusted_loss_ratio,
            'target_ratio': target_ratio,
            'deviation_from_target': ((base_loss_ratio - target_ratio) / target_ratio) * 100 if target_ratio > 0 else 0,
            'total_claims': loss_ratio_data.get('total_claims', 0),
            'total_premiums': loss_ratio_data.get('total_premium', 0)
        }
    
    def _calculate_risk_metrics(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Risk Metrics Calculation"""
        insurance_type = data.get('insurance_type', 'injury')
        quarterly_data = self.query_manager.get_quarterly_trends(insurance_type)
        
        if quarterly_data.empty:
            return {
                'var_95': 0.0,
                'var_99': 0.0,
                'expected_loss': 0.0
            }
        
        # Loss Calculation (using total_premium)
        if 'total_premium' in quarterly_data.columns:
            losses = quarterly_data['total_premium'].values
        else:
            logger.warning("total_premium column not found, using default values")
            losses = data.get('premiums', [0.0])
            
        return {
            'var_95': float(np.percentile(losses, 95)) if len(losses) > 0 else 0.0,
            'var_99': float(np.percentile(losses, 99)) if len(losses) > 0 else 0.0,
            'expected_loss': float(np.mean(losses)) if len(losses) > 0 else 0.0
        }
    
    def _calculate_premium_adjustments(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Premium Adjustment Calculation"""
        insurance_type = data.get('insurance_type', 'injury')
        loss_ratio_data = self._calculate_loss_ratio({'insurance_type': insurance_type})
        
        current_loss_ratio = loss_ratio_data['loss_ratio']
        target_loss_ratio = self.target_loss_ratios.get(insurance_type, 0.7)
        
        if current_loss_ratio <= 0 or target_loss_ratio <= 0:
            return {
                'adjustment_factor': 1.0,
                'recommended_change': 0.0
            }
        
        # Adjustment Factor Calculation
        raw_adjustment = target_loss_ratio / current_loss_ratio
        
        # Adjustment Limit Application
        adjustment_factor = max(
            min(raw_adjustment, self.premium_adjustment_limits['max_factor']),
            self.premium_adjustment_limits['min_factor']
        )
        
        return {
            'adjustment_factor': adjustment_factor,
            'recommended_change': (adjustment_factor - 1) * 100
        }
    
    def analyze_age_specific_trends(self, age_range: tuple, period: tuple) -> Dict[str, Any]:
        """Age-specific trend analysis"""
        start_age, end_age = age_range
        start_date, end_date = period
        
        return {
            'age_bands': self._calculate_age_bands(start_age, end_age),
            'quarterly_trends': self._calculate_quarterly_trends(start_date, end_date),
            'risk_factors': self._analyze_risk_factors()
        }

    def analyze_preexisting_conditions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analysis of existing conditions impact"""
        return {
            'condition_prevalence': self._calculate_condition_prevalence(),
            'impact_on_claims': self._analyze_condition_impact(),
            'trend_analysis': self._analyze_condition_trends()
        }

    def calculate_premium_adjustments(self, target_ratio: float) -> Dict[str, Any]:
        """Premium Adjustment Calculation"""
        return {
            'current_ratio': self._calculate_current_ratio(),
            'required_adjustment': self._calculate_required_adjustment(target_ratio),
            'impact_analysis': self._analyze_adjustment_impact()
        }

    def analyze_treatment_costs(self, condition_type: str) -> Dict[str, Any]:
        """Treatment Costs Analysis"""
        return {
            'average_cost': self._calculate_average_cost(condition_type),
            'cost_progression': self._analyze_cost_progression(),
            'future_projections': self._project_future_costs()
        }

    def analyze_survival_rates(self, condition_type: str) -> Dict[str, Any]:
        """Survival Rates Analysis"""
        return {
            'survival_curves': self._calculate_survival_curves(),
            'treatment_impact': self._analyze_treatment_impact(),
            'age_specific_rates': self._calculate_age_specific_rates()
        }

    def analyze_hospitalization_patterns(self, diagnosis_type: str) -> Dict[str, Any]:
        """Hospitalization Patterns Analysis"""
        return {
            'length_of_stay': self._analyze_length_of_stay(),
            'readmission_rates': self._calculate_readmission_rates(),
            'cost_patterns': self._analyze_cost_patterns()
        }

    def analyze_disability_patterns(self, occupation_class: str) -> Dict[str, Any]:
        """Disability Patterns Analysis"""
        return {
            'duration_analysis': self._analyze_disability_duration(),
            'recovery_rates': self._calculate_recovery_rates(),
            'occupation_impact': self._analyze_occupation_impact()
        }

    def _calculate_age_bands(self, start_age: int, end_age: int) -> List[Dict[str, Any]]:
        age_bands = []
        for age in range(start_age, end_age, 5):
            age_bands.append({
                'age_range': f"{age}-{age+4}",
                'claim_frequency': np.random.normal(0.1, 0.02),
                'average_claim': np.random.normal(50000, 10000)
            })
        return age_bands

    def _calculate_quarterly_trends(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        trends = []
        current_date = start_date
        while current_date <= end_date:
            trends.append({
                'quarter': current_date.strftime("%Y-Q%q"),
                'loss_ratio': np.random.normal(0.7, 0.05),
                'claim_count': int(np.random.normal(1000, 100))
            })
            current_date += timedelta(days=90)
        return trends

    def _analyze_risk_factors(self) -> List[Dict[str, Any]]:
        risk_factors = [
            {'factor': 'age', 'weight': 0.3},
            {'factor': 'gender', 'weight': 0.15},
            {'factor': 'smoking', 'weight': 0.25},
            {'factor': 'bmi', 'weight': 0.2},
            {'factor': 'family_history', 'weight': 0.1}
        ]
        return risk_factors

    def _map_insurance_type(self, input_type: str) -> str:
        """Insurance Type Flexible Mapping"""
        mapping = {
            'mental_health': 'disease',
            'dental': 'disease',
            'critical_illness': 'disease',
            'cancer': 'disease',
            'accident': 'injury',
            'disability': 'injury',
            'medical': 'disease',
            'long_term_care': 'disease',
            'parametric': 'disease'
        }
        return mapping.get(input_type.lower(), input_type)

    def _map_analysis_type(self, input_type: str) -> str:
        """Analysis Type Flexible Mapping"""
        mapping = {
            'loss': 'loss_ratio',
            'risk': 'risk_metrics',
            'death': 'mortality',
            'illness': 'morbidity',
            'cost': 'treatment_cost',
            'usage': 'utilization',
            'progression': 'stage_progression',
            'recovery': 'recovery_pattern',
            'disability': 'disability_duration',
            'detection': 'early_detection',
            'prevention': 'prevention_impact',
            'severity': 'claim_severity',
            'benefit': 'benefit_utilization',
            'age_loss': 'age_specific_loss',
            'quarterly': 'quarterly_risk',
            'claims': 'claim_pattern',
            'expense': 'expense_analysis',
            'retention': 'retention_metrics'
        }
        return mapping.get(input_type.lower(), input_type)

    def _analyze_mortality_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Mortality Patterns Analysis"""
        return {
            'mortality_rates': self._calculate_mortality_rates(data),
            'trend_analysis': self._analyze_mortality_trends(data),
            'age_factors': self._analyze_age_impact(data)
        }

    def _analyze_morbidity_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Disease Incidence Patterns Analysis"""
        return {
            'incidence_rates': self._calculate_incidence_rates(data),
            'progression_analysis': self._analyze_disease_progression(data),
            'risk_factors': self._identify_risk_factors(data)
        }

    def _analyze_treatment_costs(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Treatment Costs Analysis"""
        return {
            'cost_by_stage': self._calculate_stage_costs(data),
            'trend_analysis': self._analyze_cost_trends(data),
            'cost_drivers': self._identify_cost_drivers(data)
        }

    def _analyze_utilization_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Utilization Patterns Analysis"""
        return {
            'service_utilization': self._calculate_utilization_rates(data),
            'frequency_analysis': self._analyze_claim_frequency(data),
            'seasonal_patterns': self._identify_seasonal_patterns(data)
        }

    def _analyze_stage_progression(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Stage Progression Analysis"""
        return {
            'progression_rates': self._calculate_progression_rates(data),
            'stage_duration': self._analyze_stage_duration(data),
            'intervention_impact': self._analyze_intervention_effect(data)
        }

    def _analyze_recovery_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recovery Patterns Analysis"""
        return {
            'recovery_rates': self._calculate_recovery_rates(data),
            'duration_analysis': self._analyze_recovery_duration(data),
            'success_factors': self._identify_success_factors(data)
        }

    def _analyze_disability_duration(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Disability Duration Analysis"""
        return {
            'duration_patterns': self._calculate_disability_patterns(data),
            'return_rates': self._analyze_return_to_work_rates(data),
            'influencing_factors': self._identify_duration_factors(data)
        }

    def _analyze_early_detection_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Early Detection Impact Analysis"""
        return {
            'detection_rates': self._calculate_detection_rates(data),
            'survival_impact': self._analyze_survival_impact(data),
            'cost_benefit': self._analyze_detection_cost_benefit(data)
        }

    def _analyze_prevention_impact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prevention Impact Analysis"""
        return {
            'prevention_rates': self._calculate_prevention_rates(data),
            'cost_savings': self._analyze_prevention_savings(data),
            'program_effectiveness': self._evaluate_program_effectiveness(data)
        }

    def _analyze_claim_severity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Claim Severity Analysis"""
        return {
            'severity_levels': self._calculate_severity_levels(data),
            'cost_distribution': self._analyze_cost_distribution(data),
            'trend_analysis': self._analyze_severity_trends(data)
        }

    def _analyze_benefit_utilization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Benefit Utilization Analysis"""
        return {
            'utilization_rates': self._calculate_benefit_utilization(data),
            'pattern_analysis': self._analyze_utilization_patterns(data),
            'optimization_opportunities': self._identify_optimization_opportunities(data)
        }

    def _perform_full_analysis(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Full Analysis Execution"""
        return {
            'mortality': self._analyze_mortality_patterns(data),
            'morbidity': self._analyze_morbidity_patterns(data),
            'treatment_cost': self._analyze_treatment_costs(data),
            'utilization': self._analyze_utilization_patterns(data),
            'prevention': self._analyze_prevention_impact(data)
        }

    def analyze_age_specific_loss_ratio(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Age-specific loss ratio analysis"""
        insurance_type = data.get('insurance_type', 'injury')
        age_data = self.query_manager.get_age_distribution(insurance_type)
        loss_ratio_data = self.query_manager.get_loss_ratio(insurance_type)
        
        if age_data.empty:
            return {'error': 'No age distribution data available'}
            
        age_specific_ratios = []
        for _, row in age_data.iterrows():
            age_group = row['age_group']
            contracts = row['total_contracts']
            premium = row['total_premium']
            
            # Age-specific loss ratio calculation
            age_loss_ratio = (loss_ratio_data.get('total_claims', 0) * contracts / 
                            loss_ratio_data.get('total_contracts', 1)) / premium if premium > 0 else 0
                            
            age_specific_ratios.append({
                'age_group': age_group,
                'loss_ratio': age_loss_ratio,
                'contracts': contracts,
                'premium': premium
            })
            
        return {
            'age_specific_ratios': age_specific_ratios,
            'summary': {
                'highest_ratio': max(age_specific_ratios, key=lambda x: x['loss_ratio']),
                'lowest_ratio': min(age_specific_ratios, key=lambda x: x['loss_ratio']),
                'average_ratio': sum(x['loss_ratio'] for x in age_specific_ratios) / len(age_specific_ratios)
            }
        }

    def analyze_quarterly_risk_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Quarterly risk metrics analysis"""
        insurance_type = data.get('insurance_type', 'injury')
        quarterly_data = self.query_manager.get_quarterly_trends(insurance_type)
        
        if quarterly_data.empty:
            return {'error': 'No quarterly risk data available'}
            
        latest_year = quarterly_data['year'].max()
        latest_data = quarterly_data[quarterly_data['year'] == latest_year].iloc[0]
        
        quarters = ['q1', 'q2', 'q3', 'q4']
        quarterly_metrics = []
        
        for q in quarters:
            contracts = latest_data[f'{q}_contracts']
            premium = latest_data[f'{q}_risk_premium']
            
            quarterly_metrics.append({
                'quarter': q,
                'risk_exposure': premium / contracts if contracts > 0 else 0,
                'contracts': contracts,
                'premium': premium
            })
            
        return {
            'quarterly_metrics': quarterly_metrics,
            'risk_trends': {
                'highest_exposure': max(quarterly_metrics, key=lambda x: x['risk_exposure']),
                'lowest_exposure': min(quarterly_metrics, key=lambda x: x['risk_exposure']),
                'trend_direction': 'increasing' if quarterly_metrics[-1]['risk_exposure'] > quarterly_metrics[0]['risk_exposure'] else 'decreasing'
            }
        }

    def analyze_claim_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Claim Patterns Analysis"""
        insurance_type = data.get('insurance_type', 'injury')
        quarterly_data = self.query_manager.get_quarterly_trends(insurance_type)
        loss_ratio_data = self.query_manager.get_loss_ratio(insurance_type)
        
        if quarterly_data.empty:
            return {'error': 'No claim pattern data available'}
            
        latest_year = quarterly_data['year'].max()
        latest_data = quarterly_data[quarterly_data['year'] == latest_year].iloc[0]
        
        quarters = ['q1', 'q2', 'q3', 'q4']
        claim_patterns = []
        
        for q in quarters:
            claim_patterns.append({
                'quarter': q,
                'claim_frequency': latest_data[f'{q}_accident_count'] / latest_data[f'{q}_contracts'] if latest_data[f'{q}_contracts'] > 0 else 0,
                'average_claim_size': latest_data[f'{q}_claims'] / latest_data[f'{q}_accident_count'] if latest_data[f'{q}_accident_count'] > 0 else 0
            })
            
        return {
            'claim_patterns': claim_patterns,
            'pattern_analysis': {
                'peak_frequency': max(claim_patterns, key=lambda x: x['claim_frequency']),
                'peak_severity': max(claim_patterns, key=lambda x: x['average_claim_size']),
                'overall_loss_ratio': loss_ratio_data.get('loss_ratio', 0)
            }
        }

    def analyze_expense_ratios(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Expense Ratios Analysis"""
        insurance_type = data.get('insurance_type', 'injury')
        contracts_data = self.query_manager.get_market_data(insurance_type)
        
        if not contracts_data:
            return {'error': 'No expense data available'}
            
        total_premium = contracts_data.get('total_premium', 0)
        total_contracts = contracts_data.get('total_contracts', 0)
        
        # Expense Components Calculation
        acquisition_cost = total_premium * 0.15  # Acquisition Cost
        maintenance_cost = total_premium * 0.05  # Maintenance Cost
        claim_handling_cost = total_premium * 0.03  # Claim Handling Cost
        
        return {
            'expense_components': {
                'acquisition_ratio': (acquisition_cost / total_premium * 100) if total_premium > 0 else 0,
                'maintenance_ratio': (maintenance_cost / total_premium * 100) if total_premium > 0 else 0,
                'claim_handling_ratio': (claim_handling_cost / total_premium * 100) if total_premium > 0 else 0
            },
            'efficiency_metrics': {
                'cost_per_contract': (acquisition_cost + maintenance_cost) / total_contracts if total_contracts > 0 else 0,
                'total_expense_ratio': ((acquisition_cost + maintenance_cost + claim_handling_cost) / total_premium * 100) 
                                     if total_premium > 0 else 0
            }
        }

    def analyze_retention_metrics(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Contract Retention Metrics Analysis"""
        insurance_type = data.get('insurance_type', 'injury')
        quarterly_data = self.query_manager.get_quarterly_trends(insurance_type)
        
        if quarterly_data.empty:
            return {'error': 'No retention data available'}
            
        retention_metrics = []
        years = sorted(quarterly_data['year'].unique())
        
        for i in range(1, len(years)):
            current_year = quarterly_data[quarterly_data['year'] == years[i]].iloc[0]
            previous_year = quarterly_data[quarterly_data['year'] == years[i-1]].iloc[0]
            
            retention_rate = (current_year['total_contracts'] / previous_year['total_contracts'] * 100 
                            if previous_year['total_contracts'] > 0 else 0)
            
            retention_metrics.append({
                'year': years[i],
                'retention_rate': retention_rate,
                'contracts_retained': current_year['total_contracts'],
                'premium_retention': (current_year['total_risk_premium'] / previous_year['total_risk_premium'] * 100 
                                   if previous_year['total_risk_premium'] > 0 else 0)
            })
            
        return {
            'retention_metrics': retention_metrics,
            'summary': {
                'average_retention': sum(x['retention_rate'] for x in retention_metrics) / len(retention_metrics) if retention_metrics else 0,
                'latest_retention': retention_metrics[-1] if retention_metrics else None,
                'trend': 'improving' if retention_metrics and retention_metrics[-1]['retention_rate'] > retention_metrics[0]['retention_rate'] else 'declining'
            }
        }

    def _get_expected_fields(self, request_type: str) -> Set[str]:
        """
        Actuarial Analysis Request Type Expected Fields
        Args:
            request_type: Analysis Type
        Returns:
            Expected Fields Set
        """
        # Basic Common Fields
        common_fields = {
            'metadata.timestamp',
            'metadata.engine',
            'metadata.config',
            'status'
        }

        # Analysis Type-specific Fields
        type_specific_fields = {
            'loss_ratio': {
                'data.loss_ratio',
                'data.adjusted_loss_ratio',
                'data.target_ratio',
                'data.total_claims',
                'data.total_premiums'
            },
            'risk_metrics': {
                'data.var_95',
                'data.var_99',
                'data.expected_loss',
                'data.std_dev'
            },
            'mortality': {
                'data.mortality_rates',
                'data.trend_analysis',
                'data.age_factors'
            },
            'morbidity': {
                'data.incidence_rates',
                'data.progression_analysis',
                'data.risk_factors'
            },
            'treatment_cost': {
                'data.cost_by_stage',
                'data.trend_analysis',
                'data.cost_drivers'
            },
            'utilization': {
                'data.service_utilization',
                'data.frequency_analysis',
                'data.seasonal_patterns'
            },
            'stage_progression': {
                'data.progression_rates',
                'data.stage_duration',
                'data.intervention_impact'
            },
            'recovery_pattern': {
                'data.recovery_rates',
                'data.duration_analysis',
                'data.success_factors'
            },
            'disability_duration': {
                'data.duration_patterns',
                'data.return_rates',
                'data.influencing_factors'
            },
            'early_detection': {
                'data.detection_rates',
                'data.survival_impact',
                'data.cost_benefit'
            },
            'prevention_impact': {
                'data.prevention_rates',
                'data.cost_savings',
                'data.program_effectiveness'
            },
            'claim_severity': {
                'data.severity_levels',
                'data.cost_distribution',
                'data.trend_analysis'
            },
            'benefit_utilization': {
                'data.utilization_rates',
                'data.pattern_analysis',
                'data.optimization_opportunities'
            },
            'age_specific_loss': {
                'data.age_specific_ratios',
                'data.summary.highest_ratio',
                'data.summary.lowest_ratio',
                'data.summary.average_ratio'
            },
            'quarterly_risk': {
                'data.quarterly_metrics',
                'data.risk_trends.highest_exposure',
                'data.risk_trends.lowest_exposure',
                'data.risk_trends.trend_direction'
            },
            'claim_pattern': {
                'data.claim_patterns',
                'data.pattern_analysis.peak_frequency',
                'data.pattern_analysis.peak_severity',
                'data.pattern_analysis.overall_loss_ratio'
            },
            'expense_analysis': {
                'data.expense_components',
                'data.efficiency_metrics'
            },
            'retention_metrics': {
                'data.retention_metrics',
                'data.summary.average_retention',
                'data.summary.latest_retention',
                'data.summary.trend'
            }
        }

        # Analysis Type-specific Fields Combination
        expected_fields = common_fields
        if request_type in type_specific_fields:
            expected_fields = expected_fields.union(type_specific_fields[request_type])
        elif request_type == 'full':
            # full analysis case includes all fields
            for fields in type_specific_fields.values():
                expected_fields = expected_fields.union(fields)

        return expected_fields 
        