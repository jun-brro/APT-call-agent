from typing import Dict, Any, List, Optional, Set
from ..base import BaseEngine
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from ....data.connectors.db_connector import DBConnector
from ....data.processors.query_manager import QueryManager

logger = logging.getLogger(__name__)

class ProductEngine(BaseEngine):
    """Product Engine - Insurance product development and management"""
    
    def __init__(self, config: Dict[str, Any]):
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
        self.min_premium = config.get('min_premium', 1000)
        self.max_coverage = config.get('max_coverage', 1000000)
        self.test_mode = config.get('test_mode', False)
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize product engine"""
        super()._initialize()
        self.min_premium = self.config.get('min_premium', 10000)
        self.max_coverage = self.config.get('max_coverage', 1000000000)
        
        # Product design type mapping
        self.design_types = {
            'wellness': self._design_wellness_product,
            'mental_health': self._design_mental_health_coverage,
            'telehealth': self._design_telehealth_service,
            'chronic_care': self._design_chronic_care_product,
            'hybrid': self._design_hybrid_product,
            'standard': self._design_standard_product,
            'full': self._perform_full_design
        }
        
        # Additional mapping for flexible mapping
        self.design_type_mapping = {
            'health': 'wellness',
            'remote': 'telehealth',
            'chronic': 'chronic_care',
            'combined': 'hybrid',
            'basic': 'standard'
        }
        
        # Default coverage structure settings
        self.coverage_structures = {
            'basic': ['death', 'disability'],
            'standard': ['death', 'disability', 'critical_illness'],
            'premium': ['death', 'disability', 'critical_illness', 'accident']
        }
        
        # Default benefit structure settings
        self.benefit_structures = {
            'young_professionals': {
                'death': 1.0,
                'disability': 1.2,
                'critical_illness': 0.8
            },
            'families': {
                'death': 1.5,
                'disability': 1.0,
                'critical_illness': 1.0
            },
            'senior_citizens': {
                'death': 0.8,
                'disability': 0.7,
                'critical_illness': 1.5
            }
        }
        
        # Risk factor weight settings
        self.risk_weights = {
            'age': 0.3,
            'health': 0.4,
            'occupation': 0.2,
            'lifestyle': 0.1
        }
    
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process product design request"""
        try:
            design_type = parameters.get('design_type', 'full')
            
            # Design type mapping
            design_type = self._map_design_type(design_type)
            
            if design_type in self.design_types:
                result = self.design_types[design_type](parameters)
            else:
                result = self._perform_full_design(parameters)
            
            return self.format_response(result)
        except Exception as e:
            logger.error(f"Product design failed: {e}")
            raise
    
    def _map_design_type(self, input_type: str) -> str:
        """Flexible design type mapping"""
        if not input_type:
            return 'standard'
            
        input_type = input_type.lower()
        
        # If directly mapped type, return it
        if input_type in self.design_types:
            return input_type
            
        # Apply flexible mapping
        return self.design_type_mapping.get(input_type, 'standard')
    
    def _design_coverage(self, parameters: Dict[str, Any]) -> Dict[str, float]:
        """Design coverage structure"""
        coverage_type = parameters.get('coverage_type', 'basic')
        if isinstance(coverage_type, dict):
            coverage_type = coverage_type.get('type', 'basic')
            
        # Default coverage structure
        if coverage_type == 'basic':
            return {
                'death': 1.0,
                'disability': 0.5
            }
        elif coverage_type == 'premium':
            return {
                'death': 1.0,
                'disability': 0.7,
                'critical_illness': 0.5
            }
        else:
            return {
                'death': 1.0,
                'disability': 0.6,
                'critical_illness': 0.4,
                'medical': 0.3
            }
    
    def _calculate_pricing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate insurance premium"""
        coverage = self._design_coverage(parameters)
        base_premium = self.min_premium
        
        # Apply weighted premium by coverage type
        weighted_premium = base_premium * sum(coverage.values())
        
        # Adjust by target segment
        segment = parameters.get('target_segment', 'general')
        if segment == 'young_adults':
            weighted_premium *= 0.9
        elif segment == 'seniors':
            weighted_premium *= 1.3
            
        return {
            'base_premium': base_premium,
            'final_premium': weighted_premium,
            'premium_factors': {
                'coverage_weight': sum(coverage.values()),
                'segment_factor': 0.9 if segment == 'young_adults' else 1.3 if segment == 'seniors' else 1.0
            }
        }
    
    def _get_test_data(self, design_type: str, coverage_type: str) -> Dict[str, Any]:
        """Create test data"""
        result = {
            'coverage': {
                'death': 1.0,
                'disability': 0.5
            },
            'max_coverage': self.max_coverage,
            'coverage_type': coverage_type
        }
        
        if design_type in ['pricing', 'full']:
            result.update({
                'base_premium': self.min_premium,
                'final_premium': self.min_premium * 1.5,
                'premium_factors': {
                    'coverage_weight': 1.5,
                    'segment_factor': 1.0
                }
            })
        
        return {
            'status': 'success',
            'data': result,
            'config': self.config
        }
    
    def _design_coverage_structure(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Design coverage structure"""
        coverage_type = parameters.get('coverage_type', 'basic')
        return {
            'coverage': self.default_coverage_types.get(coverage_type, self.default_coverage_types['basic']),
            'max_coverage': self.max_coverage,
            'coverage_type': coverage_type
        }
    
    def _design_benefits(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Design benefits"""
        target_segment = data.get('target_segment', 'general')
        coverage_type = data.get('coverage_type', 'basic')
        
        base_benefits = [
            {'type': 'death_benefit', 'amount': self.max_coverage},
            {'type': 'disability_benefit', 'amount': self.max_coverage * 0.5}
        ]
        
        if coverage_type == 'comprehensive':
            base_benefits.append(
                {'type': 'critical_illness_benefit', 'amount': self.max_coverage * 0.3}
            )
        
        return base_benefits
    
    def _develop_pricing_strategy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Develop pricing strategy"""
        base_premium = self._calculate_base_premium(data)
        risk_factors = self._identify_risk_factors(data)
        
        return {
            'base_premium': base_premium,
            'risk_adjustments': risk_factors,
            'premium_range': {
                'min': max(self.min_premium, base_premium * 0.8),
                'max': base_premium * 1.2
            }
        }
    
    def _define_exclusions(self, data: Dict[str, Any]) -> List[str]:
        """Define exclusions"""
        coverage_type = data.get('coverage_type', 'basic')
        base_exclusions = [
            'intentional_self_harm',
            'war_and_terrorism',
            'pre_existing_conditions'
        ]
        
        if coverage_type == 'comprehensive':
            base_exclusions.extend([
                'high_risk_activities',
                'professional_sports'
            ])
        
        return base_exclusions
    
    def _calculate_base_premium(self, data: Dict[str, Any]) -> float:
        """Calculate base insurance premium"""
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        risk_level = data.get('risk_level', 1.0)
        return (coverage_amount * 0.001) * risk_level
    
    def _identify_risk_factors(self, data: Dict[str, Any]) -> Dict[str, float]:
        """Identify risk factors"""
        return {
            'age_factor': self._calculate_age_factor(data.get('age', 30)),
            'health_factor': self._calculate_health_factor(data.get('health_score', 1.0)),
            'occupation_factor': self._calculate_occupation_factor(data.get('occupation_class', 1))
        }
    
    def _calculate_age_factor(self, age: int) -> float:
        """Calculate age factor"""
        return 1.0 + max(0, (age - 20) * 0.01)
    
    def _calculate_health_factor(self, health_score: float) -> float:
        """Calculate health factor"""
        return 2.0 - health_score if health_score <= 1.0 else 1.0
    
    def _calculate_occupation_factor(self, occupation_class: int) -> float:
        """Calculate occupation factor"""
        return 1.0 + (occupation_class - 1) * 0.2

    def design_coverage_structure(self, coverage_type: str, target_segment: str) -> Dict[str, Any]:
        """Design product coverage structure"""
        return {
            'coverage_levels': self._define_coverage_levels(coverage_type),
            'benefit_structure': self._design_benefit_structure(target_segment),
            'exclusions': self._define_exclusions(coverage_type),
            'waiting_periods': self._define_waiting_periods(coverage_type)
        }
        
    def design_wellness_program(self, target_segment: str) -> Dict[str, Any]:
        """Design wellness program"""
        return {
            'activity_targets': self._define_activity_targets(target_segment),
            'reward_structure': self._design_reward_structure(),
            'monitoring_metrics': self._define_monitoring_metrics()
        }
        
    def analyze_benefit_utilization(self, product_type: str) -> Dict[str, Any]:
        """Analyze benefit utilization"""
        return {
            'utilization_patterns': self._analyze_utilization_patterns(product_type),
            'cost_drivers': self._identify_cost_drivers(),
            'optimization_opportunities': self._identify_optimization_opportunities()
        }
        
    def design_parametric_triggers(self, risk_type: str) -> Dict[str, Any]:
        """Design parametric insurance triggers"""
        return {
            'trigger_conditions': self._define_trigger_conditions(risk_type),
            'payout_structure': self._design_payout_structure(),
            'monitoring_requirements': self._define_monitoring_requirements()
        }
        
    def analyze_telehealth_impact(self) -> Dict[str, Any]:
        """Analyze telemedicine impact"""
        return {
            'utilization_comparison': self._compare_utilization(),
            'cost_efficiency': self._analyze_cost_efficiency(),
            'quality_metrics': self._analyze_quality_metrics()
        }
        
    def design_mental_health_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design mental health coverage"""
        return {
            'coverage_structure': self._design_mental_health_structure(data),
            'service_network': self._design_provider_network(data),
            'treatment_limits': self._define_treatment_limits(data)
        }
        
    # Private helper methods
    def _define_coverage_levels(self, coverage_type: str) -> List[Dict[str, Any]]:
        """Define coverage levels"""
        base_coverage = {
            'comprehensive': 1000000,
            'standard': 500000,
            'basic': 250000
        }.get(coverage_type, 500000)
        
        return [
            {'level': 'Bronze', 'coverage': base_coverage * 0.5},
            {'level': 'Silver', 'coverage': base_coverage},
            {'level': 'Gold', 'coverage': base_coverage * 2},
            {'level': 'Platinum', 'coverage': base_coverage * 4}
        ]
        
    def _design_benefit_structure(self, target_segment: str) -> Dict[str, Any]:
        """Design benefit structure"""
        return {
            'primary_benefits': self._define_primary_benefits(target_segment),
            'riders': self._define_riders(target_segment),
            'limitations': self._define_limitations()
        }
        
    def _define_exclusions(self, coverage_type: str) -> List[str]:
        """Define exclusions"""
        base_exclusions = [
            "pre-existing conditions",
            "intentional self-injury",
            "war and terrorism",
            "illegal activities"
        ]
        
        specific_exclusions = {
            'critical_illness': [
                "cosmetic surgery",
                "experimental treatments"
            ],
            'disability': [
                "mental health conditions",
                "substance abuse"
            ],
            'accident': [
                "professional sports",
                "extreme sports"
            ]
        }
        
        return base_exclusions + specific_exclusions.get(coverage_type, [])
        
    def _define_waiting_periods(self, coverage_type: str) -> Dict[str, int]:
        """Define waiting periods"""
        return {
            'initial': 30,  # days
            'specific_conditions': 180,
            'pre_existing_conditions': 365
        }
        
    def _define_activity_targets(self, target_segment: str) -> Dict[str, Any]:
        """Define activity targets"""
        return {
            'daily_steps': 10000,
            'exercise_minutes': 150,
            'sleep_hours': 7,
            'stress_management': 'meditation_sessions'
        }
        
    def _design_reward_structure(self) -> Dict[str, Any]:
        """Design reward structure"""
        return {
            'premium_discounts': {'max_discount': 0.15},
            'cash_rewards': {'annual_max': 500},
            'benefit_enhancements': {'coverage_boost': 0.1}
        }
        
    def _define_monitoring_metrics(self) -> List[Dict[str, Any]]:
        """Define monitoring metrics"""
        return [
            {'metric': 'activity_completion', 'weight': 0.4},
            {'metric': 'health_screening', 'weight': 0.3},
            {'metric': 'preventive_care', 'weight': 0.3}
        ]

    def _design_parametric_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design parametric insurance"""
        return {
            'trigger_conditions': self._define_trigger_conditions(data),
            'payout_structure': self._design_payout_structure(data),
            'risk_transfer': self._design_risk_transfer(data)
        }

    def _design_mental_health_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design mental health coverage structure"""
        return {
            'outpatient': {'visits': 20, 'coverage_rate': 0.8},
            'inpatient': {'days': 30, 'coverage_rate': 0.9},
            'medication': {'coverage_rate': 0.7}
        }

    def _design_provider_network(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design medical institution network"""
        return {
            'specialists': ['psychiatrist', 'psychologist', 'counselor'],
            'facilities': ['hospitals', 'clinics', 'centers'],
            'coverage_rates': {'in_network': 0.8, 'out_network': 0.5}
        }

    def _define_treatment_limits(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Define treatment limits"""
        return {
            'annual_visits': 24,
            'lifetime_maximum': 1000000,
            'session_duration': 50
        }

    def _design_special_features(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design special features"""
        return {
            'telemedicine': self._design_telehealth_service(data),
            'wellness': self._design_wellness_product(data),
            'chronic_care': self._design_chronic_care_product(data)
        }

    def _design_wellness_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design wellness product"""
        base_premium = data.get('base_premium', self.min_premium)
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        
        # Wellness program configuration
        wellness_features = {
            'health_screening': {
                'annual_checkup': True,
                'coverage': min(coverage_amount * 0.05, 1000000)
            },
            'fitness_benefits': {
                'gym_membership': True,
                'annual_limit': min(base_premium * 0.1, 300000)
            },
            'preventive_care': {
                'vaccinations': True,
                'coverage_ratio': 0.8
            }
        }
        
        # Insurance premium discount structure
        discount_structure = {
            'activity_tracking': {
                'steps_goal': {'daily_target': 10000, 'discount': 0.05},
                'exercise_minutes': {'weekly_target': 150, 'discount': 0.03}
            },
            'health_metrics': {
                'bmi_range': {'target': (18.5, 25), 'discount': 0.02},
                'blood_pressure': {'target': (120, 80), 'discount': 0.02}
            }
        }
        
        return {
            'product_type': 'wellness',
            'base_premium': base_premium,
            'coverage_amount': coverage_amount,
            'wellness_features': wellness_features,
            'discount_structure': discount_structure,
            'max_total_discount': 0.15
        }

    def _design_mental_health_coverage(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design mental health coverage product"""
        base_premium = data.get('base_premium', self.min_premium)
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        
        # Coverage content configuration
        coverage_structure = {
            'counseling': {
                'sessions_per_year': 12,
                'coverage_per_session': min(coverage_amount * 0.002, 200000)
            },
            'psychiatric_treatment': {
                'inpatient_coverage': min(coverage_amount * 0.3, 30000000),
                'outpatient_coverage': min(coverage_amount * 0.1, 10000000)
            },
            'medication': {
                'annual_limit': min(coverage_amount * 0.05, 5000000),
                'coverage_ratio': 0.7
            }
        }
        
        # Additional services
        additional_services = {
            'teletherapy': True,
            'crisis_hotline': True,
            'support_group_access': True
        }
        
        return {
            'product_type': 'mental_health',
            'base_premium': base_premium,
            'coverage_amount': coverage_amount,
            'coverage_structure': coverage_structure,
            'additional_services': additional_services,
            'waiting_period': 60  # 60 days
        }

    def _design_telehealth_service(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design telemedicine service product"""
        base_premium = data.get('base_premium', self.min_premium)
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        
        # Service configuration
        service_structure = {
            'video_consultation': {
                'monthly_limit': 4,
                'coverage_per_session': min(coverage_amount * 0.001, 100000)
            },
            'prescription_delivery': {
                'delivery_coverage': True,
                'medication_coverage_ratio': 0.6
            },
            'remote_monitoring': {
                'device_subsidy': min(coverage_amount * 0.02, 500000),
                'data_transmission_coverage': True
            }
        }
        
        # Specialist network
        specialist_network = {
            'general_physician': True,
            'dermatologist': True,
            'psychiatrist': True,
            'nutritionist': True
        }
        
        return {
            'product_type': 'telehealth',
            'base_premium': base_premium,
            'coverage_amount': coverage_amount,
            'service_structure': service_structure,
            'specialist_network': specialist_network,
            'response_time_guarantee': 30  # 30 minutes
        }

    def _design_chronic_care_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design chronic care product"""
        base_premium = data.get('base_premium', self.min_premium)
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        
        # Condition-based coverage structure
        coverage_by_condition = {
            'diabetes': {
                'supplies_coverage': min(coverage_amount * 0.1, 5000000),
                'medication_coverage': min(coverage_amount * 0.2, 10000000),
                'specialist_visits': 12
            },
            'hypertension': {
                'medication_coverage': min(coverage_amount * 0.15, 7500000),
                'monitoring_equipment': min(coverage_amount * 0.05, 1000000)
            },
            'respiratory': {
                'medication_coverage': min(coverage_amount * 0.2, 10000000),
                'equipment_coverage': min(coverage_amount * 0.1, 5000000)
            }
        }
        
        # Management program
        management_program = {
            'regular_checkups': True,
            'nutrition_counseling': True,
            'lifestyle_coaching': True,
            'emergency_support': True
        }
        
        return {
            'product_type': 'chronic_care',
            'base_premium': base_premium,
            'coverage_amount': coverage_amount,
            'coverage_by_condition': coverage_by_condition,
            'management_program': management_program,
            'renewal_guarantee': True
        }

    def _design_hybrid_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design hybrid product"""
        base_premium = data.get('base_premium', self.min_premium)
        coverage_amount = data.get('coverage_amount', self.max_coverage)
        
        # Basic coverage structure
        base_coverage = {
            'accident': min(coverage_amount * 0.4, 100000000),
            'illness': min(coverage_amount * 0.3, 50000000),
            'disability': min(coverage_amount * 0.2, 30000000)
        }
        
        # Investment component
        investment_component = {
            'minimum_guarantee': base_premium * 1.5,
            'investment_options': ['conservative', 'balanced', 'aggressive'],
            'fund_allocation': {'equity': 0.3, 'bond': 0.5, 'cash': 0.2}
        }
        
        # Healthcare services
        healthcare_services = {
            'annual_checkup': True,
            'telemedicine': True,
            'fitness_tracking': True,
            'mental_health_support': True
        }
        
        return {
            'product_type': 'hybrid',
            'base_premium': base_premium,
            'coverage_amount': coverage_amount,
            'base_coverage': base_coverage,
            'investment_component': investment_component,
            'healthcare_services': healthcare_services,
            'premium_flexibility': True
        }

    def _design_standard_product(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design standard insurance product"""
        coverage_type = data.get('coverage_type', 'basic')
        target_segment = data.get('target_segment', 'general')
        
        coverage_structure = self._design_coverage_structure({
            'coverage_type': coverage_type,
            'target_segment': target_segment
        })
        
        benefit_structure = self._design_benefit_structure(target_segment)
        pricing_strategy = self._develop_pricing_strategy({
            'coverage_type': coverage_type,
            'target_segment': target_segment,
            'benefit_structure': benefit_structure
        })
        
        return {
            'product_type': 'standard',
            'coverage_structure': coverage_structure,
            'benefit_structure': benefit_structure,
            'pricing_strategy': pricing_strategy,
            'exclusions': self._define_exclusions(coverage_type),
            'waiting_periods': self._define_waiting_periods(coverage_type),
            'metadata': {
                'target_segment': target_segment,
                'coverage_type': coverage_type,
                'design_date': datetime.now().isoformat()
            }
        }

    def _perform_full_design(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Design full insurance product"""
        return {
            'core_coverage': self._design_coverage_structure(data),
            'pricing': self._develop_pricing_strategy(data),
            'benefits': self._design_benefits(data),
            'wellness': self._design_wellness_product(data),
            'special_features': self._design_special_features(data)
        }

    def _get_expected_fields(self, request_type: str) -> Set[str]:
        """
        Return expected fields for product analysis request type
        Args:
            request_type: Analysis type
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

        # Analysis type-specific fields
        type_specific_fields = {
            'design': {
                'data.coverage_structure',
                'data.benefit_design',
                'data.exclusions',
                'data.waiting_periods'
            },
            'pricing': {
                'data.base_premium',
                'data.risk_factors',
                'data.adjustment_factors',
                'data.pricing_strategy'
            },
            'coverage': {
                'data.coverage_levels',
                'data.benefit_limits',
                'data.covered_events',
                'data.exclusions'
            },
            'benefits': {
                'data.benefit_structure',
                'data.payment_terms',
                'data.claim_conditions',
                'data.value_added_services'
            },
            'wellness_program': {
                'data.activity_targets',
                'data.reward_structure',
                'data.monitoring_metrics',
                'data.program_benefits'
            },
            'parametric_product': {
                'data.trigger_events',
                'data.payout_structure',
                'data.risk_parameters',
                'data.monitoring_system'
            },
            'mental_health': {
                'data.coverage_structure',
                'data.provider_network',
                'data.treatment_limits',
                'data.special_features'
            },
            'telehealth': {
                'data.service_structure',
                'data.provider_integration',
                'data.access_methods',
                'data.quality_metrics'
            },
            'chronic_care': {
                'data.care_pathways',
                'data.monitoring_plan',
                'data.intervention_protocols',
                'data.support_services'
            },
            'hybrid_product': {
                'data.component_integration',
                'data.flexibility_options',
                'data.customization_rules',
                'data.pricing_model'
            }
        }

        # Combine fields based on analysis type
        expected_fields = common_fields
        if request_type in type_specific_fields:
            expected_fields = expected_fields.union(type_specific_fields[request_type])
        elif request_type == 'full':
            # For full analysis, include all fields
            for fields in type_specific_fields.values():
                expected_fields = expected_fields.union(fields)

        return expected_fields 