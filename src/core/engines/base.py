from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set
import logging
from ...data.connectors.db_connector import DBConnector
from ...data.processors.query_manager import QueryManager

logger = logging.getLogger(__name__)

class BaseEngine(ABC):
    """Base engine class"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.db = None
        self.query_manager = None
        self.table_mapping = None
        self._validate_config()  # Validate config first
        self._initialize_common()
        self._initialize()
    
    def _initialize_common(self) -> None:
        """Initialize common components for all engines"""
        try:
            # Initialize database connection
            db_config = self.config.get('db_config', {})
            self.db = DBConnector(db_config)
            
            # Initialize table mapping
            self.table_mapping = self.config.get('table_mapping', {
                'contracts': 'quarterly_insurance_contracts',
                'claims': 'quarterly_insurance_claims',
                'market': 'market_research',
                'products': 'product_templates',
                'pricing': 'pricing_models'
            })
            
            # Initialize query manager
            self.query_manager = QueryManager(self.db, self.table_mapping)
            
        except Exception as e:
            logger.error(f"Failed to initialize engine: {e}")
            raise
    
    def _validate_config(self) -> None:
        """Validate engine configuration"""
        try:
            required_config = {
                'db_config': ['host', 'port', 'database', 'user', 'password'],
                'table_mapping': ['contracts', 'claims', 'market']
            }
            
            for section, fields in required_config.items():
                config_section = self.config.get(section, {})
                if not config_section and section == 'db_config':
                    raise ValueError(f"Missing required section: {section}")
                    
                for field in fields:
                    if section == 'db_config' and field not in config_section:
                        raise ValueError(f"Missing required configuration: {section}.{field}")
                        
            logger.info("Configuration validation successful")
            
        except Exception as e:
            logger.error(f"Configuration validation failed: {str(e)}")
            raise ValueError(f"Configuration validation failed: {str(e)}")
    
    def format_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format engine response with metadata"""
        return {
            'status': 'success',
            'data': data,
            'metadata': {
                'engine_type': self.__class__.__name__,
                'config_version': self.config.get('version', 'unknown'),
                'database_status': self._get_database_status()
            }
        }
    
    def _get_database_status(self) -> Dict[str, Any]:
        """Get current database status"""
        try:
            return {
                'active_connections': self.db.get_active_connections(),
                'table_sizes': self.db.get_table_sizes(),
                'slow_queries': len(self.db.get_slow_queries())
            }
        except Exception as e:
            logger.error(f"Failed to get database status: {e}")
            return {}
    
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle engine errors with context"""
        error_info = {
            'error_type': error.__class__.__name__,
            'error_message': str(error),
            'context': context
        }
        logger.error(f"Engine error: {error_info}")
        
        return {
            'status': 'error',
            'error': error_info,
            'metadata': {
                'engine_type': self.__class__.__name__,
                'recovery_suggestion': self._get_recovery_suggestion(error)
            }
        }
    
    def _get_recovery_suggestion(self, error: Exception) -> str:
        """Get recovery suggestion based on error type"""
        suggestions = {
            'DatabaseError': "Check database connection and schema",
            'ValueError': "Validate input parameters",
            'KeyError': "Check configuration keys",
            'Exception': "Contact system administrator"
        }
        return suggestions.get(error.__class__.__name__, "Unknown error")
    
    def cleanup(self) -> None:
        """Cleanup engine resources"""
        try:
            if self.db:
                self.db.disconnect()
            logger.info(f"Engine {self.__class__.__name__} cleaned up successfully")
        except Exception as e:
            logger.error(f"Failed to cleanup engine: {e}")
    
    @abstractmethod
    def _initialize(self) -> None:
        """Initialize engine"""
        pass
    
    @abstractmethod
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process request"""
        pass
    
    def _initialize(self) -> None:
        pass

    def _decompose_request(self, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Decompose request into smaller units"""
        decomposed = []
        main_request = parameters.get('request_type')
        
        # Decomposition logic by request type
        decomposition_map = {
            'mental_health': ['utilization', 'cost_comparison', 'demand_projection', 'risk_assessment'],
            'dental': ['procedure_frequency', 'preventive_impact', 'cost_trend', 'utilization'],
            'critical_illness': ['diagnosis_trend', 'survival_rate', 'treatment_cost', 'risk_factors'],
            'long_term_care': ['care_cost', 'progression_rate', 'cognitive_impact', 'physical_impact'],
            'cyber': ['attack_frequency', 'severity_analysis', 'recovery_cost', 'security_impact']
        }
        
        sub_types = decomposition_map.get(main_request, [main_request])
        for sub_type in sub_types:
            sub_request = parameters.copy()
            sub_request['analysis_type'] = sub_type
            sub_request['original_request'] = main_request
            decomposed.append(sub_request)
            
        return decomposed

    def _synthesize_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple analysis results"""
        if not results:
            return {'error': 'No results to synthesize'}
            
        synthesized = {
            'primary_insights': self._extract_primary_insights(results),
            'supporting_data': self._organize_supporting_data(results),
            'recommendations': self._generate_recommendations(results),
            'metadata': {
                'analysis_components': list(results.keys()),
                'confidence_scores': self._calculate_confidence_scores(results),
                'data_completeness': self._assess_data_completeness(results)
            }
        }
        
        # Add warnings if confidence scores are low
        if any(score < 0.6 for score in synthesized['metadata']['confidence_scores'].values()):
            synthesized['warnings'] = self._generate_confidence_warnings(results)
            
        return synthesized

    def _extract_primary_insights(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract primary insights"""
        insights = []
        for analysis_type, result in results.items():
            if isinstance(result, dict):
                if 'error' in result:
                    continue
                    
                insight = {
                    'type': analysis_type,
                    'key_findings': self._extract_key_findings(result),
                    'significance': self._assess_significance(result),
                    'confidence': self._calculate_single_confidence(result)
                }
                insights.append(insight)
                
        return sorted(insights, key=lambda x: x['significance'], reverse=True)

    def _organize_supporting_data(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Organize supporting data"""
        supporting_data = {}
        for analysis_type, result in results.items():
            if isinstance(result, dict) and 'error' not in result:
                supporting_data[analysis_type] = {
                    'metrics': self._extract_metrics(result),
                    'trends': self._extract_trends(result),
                    'correlations': self._extract_correlations(result)
                }
        return supporting_data

    def _calculate_confidence_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for results"""
        confidence_scores = {}
        for analysis_type, result in results.items():
            if isinstance(result, dict) and 'error' not in result:
                data_completeness = self._assess_data_completeness(result)
                statistical_significance = self._assess_statistical_significance(result)
                sample_size = self._assess_sample_size(result)
                
                confidence_scores[analysis_type] = (
                    data_completeness * 0.4 +
                    statistical_significance * 0.4 +
                    sample_size * 0.2
                )
        return confidence_scores

    def _assess_data_completeness(self, results: Dict[str, Any]) -> float:
        """Assess data completeness"""
        if not isinstance(results, dict):
            return 0.0
            
        expected_fields = self._get_expected_fields(results.get('original_request', ''))
        available_fields = set(self._flatten_dict_keys(results))
        
        if not expected_fields:
            return 1.0
            
        return len(available_fields.intersection(expected_fields)) / len(expected_fields)

    def _generate_recommendations(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on analysis results"""
        recommendations = []
        insights = self._extract_primary_insights(results)
        
        for insight in insights:
            if insight['confidence'] >= 0.7:  # Use insights with high confidence
                recommendations.extend(self._generate_insight_recommendations(insight))
                
        return sorted(recommendations, key=lambda x: x.get('priority', 0), reverse=True)

    def _generate_confidence_warnings(self, results: Dict[str, Any]) -> List[str]:
        """Generate confidence related warnings"""
        warnings = []
        confidence_scores = self._calculate_confidence_scores(results)
        
        for analysis_type, score in confidence_scores.items():
            if score < 0.4:
                warnings.append(f"Very low confidence in {analysis_type} analysis results")
            elif score < 0.6:
                warnings.append(f"Moderate confidence in {analysis_type} analysis results")
                
        return warnings

    @abstractmethod
    def _get_expected_fields(self, request_type: str) -> Set[str]:
        """Expected fields for request type"""
        pass

    def _flatten_dict_keys(self, d: Dict[str, Any], parent_key: str = '') -> Set[str]:
        """Flatten all keys of a dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}.{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict_keys(v, new_key))
            else:
                items.append(new_key)
        return set(items) 