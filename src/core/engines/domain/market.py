from typing import Dict, Any, List, Optional, Set
import pandas as pd
import numpy as np
from datetime import datetime
from ..base import BaseEngine
from ....data.connectors.db_connector import DBConnector
from ....data.processors.query_manager import QueryManager
from ...analyzers.market_analyzer import MarketAnalyzer
import logging

logger = logging.getLogger(__name__)

class MarketEngine(BaseEngine):
    """Market analysis engine - market trends and competition analysis"""
    
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
        super()._initialize()
        self.data_source = self.config.get('market_data_source', 'default')
        self.period = self.config.get('analysis_period', 12)
        self.default_segments = ['injury', 'disease', 'expense_damage', 'injury_and_disease']
        
        # Initialize MarketAnalyzer
        self.market_analyzer = MarketAnalyzer(self.config)
        
        # Add analysis type mapping
        self.analysis_types = {
            'market_size': self.analyze_market_size,
            'competition': self.analyze_competition,
            'forecast': self.forecast_demand,
            'customer_behavior': self.analyze_customer_behavior,
            'distribution': self.analyze_distribution_channels,
            'regulatory': self.analyze_regulatory_impact,
            'trend': self.analyze_market_trends,
            'penetration': self.analyze_market_penetration,
            'growth': self.analyze_growth_potential,
            'age_group': self.analyze_age_group_distribution,
            'premium_trend': self.analyze_premium_trends,
            'quarterly_comparison': self.analyze_quarterly_comparison,
            'regional_performance': self.analyze_regional_performance,
            'product_mix': self.analyze_product_mix,
            'segment': self.analyze_market_segment,
            'full': self._perform_full_analysis
        }
    
    def process(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Market analysis processing"""
        try:
            analysis_type = parameters.get('analysis_type', 'full')
            target_segment = parameters.get('target_segment', 'injury')
            
            # Map analysis type
            analysis_type = self._map_analysis_type(analysis_type)
            
            if analysis_type in self.analysis_types:
                result = self.analysis_types[analysis_type](target_segment)
            else:
                result = self._perform_full_analysis(target_segment)
                
            return self.format_response(result)
        except Exception as e:
            logger.error(f"Market analysis failed: {e}")
            raise
    
    def _map_analysis_type(self, input_type: str) -> str:
        """Flexible mapping of analysis types"""
        mapping = {
            'size': 'market_size',
            'competitive': 'competition',
            'prediction': 'forecast',
            'customer': 'customer_behavior',
            'channel': 'distribution',
            'regulation': 'regulatory',
            'segmentation': 'segment',
            'tendency': 'trend',
            'market_share': 'penetration',
            'potential': 'growth',
            'age': 'age_group',
            'premium': 'premium_trend',
            'quarterly': 'quarterly_comparison',
            'regional': 'regional_performance',
            'products': 'product_mix'
        }
        return mapping.get(input_type.lower(), input_type)
    
    def _perform_full_analysis(self, segment: str) -> Dict[str, Any]:
        """Perform full market analysis"""
        return {
            'market_size': self.analyze_market_size(segment),
            'competition': self.analyze_competition(segment),
            'forecast': self.forecast_demand(segment),
            'customer_behavior': self.analyze_customer_behavior(segment),
            'distribution': self.analyze_distribution_channels(),
            'trends': self.analyze_market_trends(segment)
        }
    
    def analyze_market_size(self, segment: str) -> Dict[str, Any]:
        """Market size analysis"""
        market_data = self.query_manager.get_market_data(segment)
        quarterly_trends = self.query_manager.get_quarterly_trends(segment)
        
        return {
            'total_market_size': market_data.get('total_contracts', 0),
            'total_premium': market_data.get('total_premium', 0),
            'quarterly_average': market_data.get('avg_quarterly_contracts', 0),
            'trends': quarterly_trends.to_dict('records') if not quarterly_trends.empty else []
        }
    
    def analyze_market_size(self, segment: str) -> Dict[str, Any]:
        market_data = self.query_manager.get_market_data(segment)
        market_analysis = self.market_analyzer.analyze_market_demand(segment)
        
        return {
            'total_market_size': market_data.get('total_contracts', 0),
            'total_premium': market_data.get('total_premium', 0),
            'quarterly_average': market_data.get('avg_quarterly_contracts', 0),
            'market_analysis': market_analysis
        }

    def analyze_competition(self, segment: str) -> Dict[str, Any]:
        """Competitor analysis"""
        market_share = self.query_manager.get_market_share(segment)
        competition_analysis = self.market_analyzer.analyze_competition(segment)
        
        return {
            'market_share': market_share,
            'competition_analysis': competition_analysis
        }

    def forecast_demand(self, segment: str) -> Dict[str, Any]:
        """Demand forecast"""
        forecast_data = self.market_analyzer.forecast_demand(segment)
        quarterly_data = self.query_manager.get_quarterly_trends(segment)
        
        return {
            'historical_data': quarterly_data.to_dict('records') if not quarterly_data.empty else [],
            'forecast': forecast_data
        }

    def analyze_market_trends(self, segment: str) -> Dict[str, Any]:
        """Market trends analysis"""
        market_data = self.query_manager.get_market_data(segment)
        trend_analysis = self.market_analyzer.analyze_market_trends({'segment': segment, 'market_data': market_data})
        
        return trend_analysis
    
    def _generate_forecast(self, historical_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """Generate forecast"""
        if historical_data.empty:
            return []
            
        # Basic time series forecast logic
        latest_year = historical_data['year'].max()
        latest_data = historical_data[historical_data['year'] == latest_year].iloc[0]
        
        growth_rate = 0.05  # Default growth rate
        forecast_periods = 4  # 4 quarters forecast
        
        forecast = []
        base_q1 = latest_data['q1_contracts']
        base_q2 = latest_data['q2_contracts']
        base_q3 = latest_data['q3_contracts']
        base_q4 = latest_data['q4_contracts']
        
        for i in range(forecast_periods):
            forecast.append({
                'period': f'Q{i+1}',
                'forecast_contracts': int([base_q1, base_q2, base_q3, base_q4][i] * (1 + growth_rate)),
                'growth_rate': growth_rate
            })
        
        return forecast
    
    def _identify_growth_factors(self, segment: str) -> List[Dict[str, str]]:
        """Identify growth factors"""
        return [
            {'factor': 'Population aging', 'impact': 'high'},
            {'factor': 'Increased health awareness', 'impact': 'medium'},
            {'factor': 'Economic situation', 'impact': 'medium'}
        ]
    
    def _calculate_market_concentration(self, segment: str) -> float:
        """Calculate market concentration"""
        market_share = self.query_manager.get_market_share(segment)
        return market_share.get('contract_share', 0)
    
    def analyze_customer_behavior(self, segment: str) -> Dict[str, Any]:
        """Customer behavior analysis"""
        return {
            'behavior_patterns': self._analyze_patterns(segment),
            'preference_analysis': self._analyze_preferences(),
            'loyalty_factors': self._identify_loyalty_factors()
        }
    
    def analyze_distribution_channels(self) -> Dict[str, Any]:
        """Distribution channel analysis"""
        return {
            'channel_performance': self._analyze_channel_performance(),
            'cost_efficiency': self._analyze_channel_costs(),
            'optimization_opportunities': self._identify_channel_opportunities()
        }
    
    def analyze_regulatory_impact(self) -> Dict[str, Any]:
        """Regulatory impact analysis"""
        return {
            'regulatory_changes': self._track_regulatory_changes(),
            'compliance_requirements': self._analyze_compliance_requirements(),
            'business_impact': self._assess_regulatory_impact()
        }
    
    def _calculate_market_size(self, segment: str) -> Dict[str, float]:
        """Calculate market size"""
        base_size = self.base_market_sizes.get(segment, self.base_market_sizes['general'])
        
        return {
            'current_size': base_size,
            'potential_size': base_size * 1.5,
            'addressable_market': base_size * 0.3
        }
    
    def _calculate_growth_rate(self, segment: str) -> Dict[str, float]:
        """Calculate growth rate"""
        base_growth = self.base_growth_rates.get(segment, self.base_growth_rates['general'])
        
        return {
            'historical_growth': base_growth,
            'projected_growth': base_growth * 1.2,
            'industry_average': 0.08
        }
    
    def _analyze_patterns(self, segment: str) -> Dict[str, Any]:
        """Behavior pattern analysis"""
        return {
            'purchase_frequency': self._calculate_purchase_frequency(segment),
            'channel_preference': self._analyze_channel_preference(segment),
            'price_sensitivity': self._analyze_price_sensitivity(segment)
        }
    
    def _analyze_channel_performance(self) -> Dict[str, Any]:
        """Channel performance analysis"""
        channels = ['direct', 'agency', 'bancassurance', 'digital']
        performance = {}
        
        for channel in channels:
            performance[channel] = {
                'revenue': np.random.normal(1000000, 100000),
                'cost': np.random.normal(500000, 50000),
                'conversion_rate': np.random.normal(0.15, 0.02),
                'customer_satisfaction': np.random.normal(4.0, 0.3)
            }
            
        return performance
    
    def _calculate_market_share(self, segment: str) -> Dict[str, float]:
        """Calculate market share"""
        total_share = sum(comp['market_share'] for comp in self._analyze_competitors('general'))
        return {
            'company_share': 0.15,
            'total_market': 1.0,
            'market_concentration': total_share
        }
    
    def _calculate_segment_share(self, segment: str) -> Dict[str, float]:
        """Calculate segment share"""
        total_market_size = sum(self.base_market_sizes.values())
        segment_size = self.base_market_sizes.get(segment, self.base_market_sizes['general'])
        
        return {
            'segment_share': segment_size / total_market_size,
            'relative_growth': self.base_growth_rates.get(segment, self.base_growth_rates['general']) / self.base_growth_rates['general'],
            'market_potential': segment_size * (1 + self.base_growth_rates.get(segment, self.base_growth_rates['general']))
        }
    
    def _identify_advantages(self) -> List[str]:
        """Identify competitive advantages"""
        return [
            'innovative_products',
            'strong_distribution_network',
            'efficient_claims_processing'
        ]
    
    def _identify_demand_drivers(self) -> List[str]:
        """Identify demand prediction factors"""
        return [
            'aging_population',
            'increasing_health_awareness',
            'digital_transformation'
        ]
    
    def _analyze_scenarios(self) -> List[Dict[str, Any]]:
        """Analyze scenarios"""
        return [
            {
                'scenario': 'Optimistic',
                'demand_forecast': self._generate_forecast('general', 12)[-1]['demand'] * 1.2
            },
            {
                'scenario': 'Pessimistic',
                'demand_forecast': self._generate_forecast('general', 12)[-1]['demand'] * 0.8
            }
        ]
    
    def _analyze_preferences(self) -> Dict[str, Any]:
        """Customer preference analysis"""
        return {
            'health_insurance': 0.7,
            'life_insurance': 0.3
        }
    
    def _identify_loyalty_factors(self) -> List[str]:
        """Identify customer moments"""
        return [
            'trust',
            'convenience',
            'price'
        ]
    
    def _analyze_channel_costs(self) -> Dict[str, float]:
        """Analyze channel costs"""
        channels = ['direct', 'agency', 'bancassurance', 'digital']
        costs = {}
        
        for channel in channels:
            costs[channel] = {
                'cost': np.random.normal(500000, 50000),
                'efficiency': np.random.normal(0.8, 0.1)
            }
        
        return costs
    
    def _identify_channel_opportunities(self) -> List[str]:
        """Identify channel optimization opportunities"""
        return [
            'digital_transformation',
            'agency_partnership',
            'bancassurance_expansion'
        ]
    
    def _track_regulatory_changes(self) -> List[str]:
        """Track regulatory changes"""
        return [
            'new_regulation_introduced',
            'existing_regulation_amended'
        ]
    
    def _analyze_compliance_requirements(self) -> Dict[str, Any]:
        """Analyze compliance requirements"""
        return {
            'required_compliance_documents': ['Act', 'Regulation'],
            'compliance_deadlines': ['30 days', '60 days'],
            'penalties': ['fine', 'license suspension']
        }
    
    def _assess_regulatory_impact(self) -> Dict[str, Any]:
        """Assess regulatory impact"""
        return {
            'impact_on_business': 'moderate',
            'strategic_adjustments': ['compliance_strategy', 'risk_management']
        }
    
    def analyze_age_group_distribution(self, segment: str) -> Dict[str, Any]:
        """Analyze age group distribution"""
        age_data = self.query_manager.get_age_distribution(segment)
        
        if age_data.empty:
            return {'error': 'No age distribution data available'}
            
        total_contracts = age_data['total_contracts'].sum()
        total_premium = age_data['total_premium'].sum()
        
        age_groups = []
        for _, row in age_data.iterrows():
            age_groups.append({
                'age_group': row['age_group'],
                'contract_share': (row['total_contracts'] / total_contracts) * 100,
                'premium_share': (row['total_premium'] / total_premium) * 100,
                'avg_premium': row['total_premium'] / row['total_contracts'] if row['total_contracts'] > 0 else 0
            })
            
        return {
            'age_distribution': age_groups,
            'dominant_age_group': max(age_groups, key=lambda x: x['contract_share']),
            'premium_metrics': {
                'highest_avg_premium': max(age_groups, key=lambda x: x['avg_premium']),
                'lowest_avg_premium': min(age_groups, key=lambda x: x['avg_premium'])
            }
        }

    def analyze_premium_trends(self, segment: str) -> Dict[str, Any]:
        """Analyze premium trends"""
        quarterly_data = self.query_manager.get_quarterly_trends(segment)
        
        if quarterly_data.empty:
            return {'error': 'No premium trend data available'}
            
        premium_trends = []
        for year in quarterly_data['year'].unique():
            year_data = quarterly_data[quarterly_data['year'] == year]
            premium_trends.append({
                'year': year,
                'q1_premium': year_data['q1_risk_premium'].iloc[0],
                'q2_premium': year_data['q2_risk_premium'].iloc[0],
                'q3_premium': year_data['q3_risk_premium'].iloc[0],
                'q4_premium': year_data['q4_risk_premium'].iloc[0],
                'total_premium': year_data['total_risk_premium'].iloc[0],
                'yoy_growth': self._calculate_yoy_growth(year_data, quarterly_data)
            })
            
        return {
            'premium_trends': premium_trends,
            'trend_analysis': {
                'overall_growth': self._calculate_overall_growth(premium_trends),
                'seasonal_pattern': self._analyze_seasonal_pattern(premium_trends),
                'latest_trend': premium_trends[-1] if premium_trends else None
            }
        }

    def analyze_quarterly_comparison(self, segment: str) -> Dict[str, Any]:
        """Analyze quarterly performance comparison"""
        contracts_data = self.query_manager.get_quarterly_trends(segment)
        claims_data = self.query_manager.get_loss_ratio(segment)
        
        if contracts_data.empty:
            return {'error': 'No quarterly comparison data available'}
            
        latest_year = contracts_data['year'].max()
        latest_data = contracts_data[contracts_data['year'] == latest_year].iloc[0]
        
        quarters = ['q1', 'q2', 'q3', 'q4']
        quarterly_metrics = []
        
        for q in quarters:
            quarterly_metrics.append({
                'quarter': q,
                'contracts': latest_data[f'{q}_contracts'],
                'premium': latest_data[f'{q}_risk_premium'],
                'avg_premium': (latest_data[f'{q}_risk_premium'] / latest_data[f'{q}_contracts'] 
                              if latest_data[f'{q}_contracts'] > 0 else 0)
            })
            
        return {
            'quarterly_metrics': quarterly_metrics,
            'best_performing_quarter': max(quarterly_metrics, key=lambda x: x['contracts']),
            'premium_efficiency': max(quarterly_metrics, key=lambda x: x['avg_premium']),
            'year_over_year': self._calculate_quarterly_yoy(contracts_data, latest_year)
        }

    def analyze_regional_performance(self, segment: str) -> Dict[str, Any]:
        """Analyze regional performance"""
        # Assuming there is regional data and getting data from query manager
        market_data = self.query_manager.get_market_data(segment)
        
        # Assuming there is no regional data and using total market data
        total_market = market_data.get('total_contracts', 0)
        total_premium = market_data.get('total_premium', 0)
        
        return {
            'market_concentration': {
                'total_market_size': total_market,
                'total_premium': total_premium,
                'market_density': total_market / self.period if self.period > 0 else 0
            },
            'regional_metrics': {
                'market_penetration': total_market / 10000,  # 인구 1만명당 계약 수
                'premium_density': total_premium / total_market if total_market > 0 else 0
            }
        }

    def analyze_product_mix(self, segment: str) -> Dict[str, Any]:
        """Analyze product mix"""
        contracts_data = self.query_manager.get_market_data(segment)
        age_data = self.query_manager.get_age_distribution(segment)
        
        if not contracts_data:
            return {'error': 'No product mix data available'}
            
        total_contracts = contracts_data.get('total_contracts', 0)
        total_premium = contracts_data.get('total_premium', 0)
        
        product_metrics = {
            'contract_density': total_contracts / self.period if self.period > 0 else 0,
            'premium_per_contract': total_premium / total_contracts if total_contracts > 0 else 0,
            'age_group_distribution': age_data.to_dict('records') if not age_data.empty else []
        }
        
        return {
            'product_metrics': product_metrics,
            'market_position': {
                'total_market_share': contracts_data.get('market_share', {}).get('contract_share', 0),
                'premium_share': total_premium / (total_contracts * product_metrics['premium_per_contract'])
                               if total_contracts > 0 and product_metrics['premium_per_contract'] > 0 else 0
            }
        }

    def _calculate_yoy_growth(self, current_data: pd.Series, all_data: pd.DataFrame) -> float:
        """Calculate annual growth rate"""
        current_year = current_data['year'].iloc[0]
        previous_year_data = all_data[all_data['year'] == current_year - 1]
        
        if previous_year_data.empty:
            return 0.0
            
        current_total = current_data['total_risk_premium'].iloc[0]
        previous_total = previous_year_data['total_risk_premium'].iloc[0]
        
        return ((current_total - previous_total) / previous_total * 100) if previous_total > 0 else 0.0

    def _calculate_overall_growth(self, trends: List[Dict[str, Any]]) -> float:
        """Calculate overall growth rate"""
        if len(trends) < 2:
            return 0.0
            
        first_year = trends[0]['total_premium']
        last_year = trends[-1]['total_premium']
        
        return ((last_year - first_year) / first_year * 100) if first_year > 0 else 0.0

    def _analyze_seasonal_pattern(self, trends: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyzelseasonalepatterneasonal pattern"""
        if not trends:
            return {}
            
        q1_avg = sum(t['q1_premium'] for t in trends) / len(trends)
        q2_avg = sum(t['q2_premium'] for t in trends) / len(trends)
        q3_avg = sum(t['q3_premium'] for t in trends) / len(trends)
        q4_avg = sum(t['q4_premium'] for t in trends) / len(trends)
        
        total_avg = (q1_avg + q2_avg + q3_avg + q4_avg) / 4
        
        return {
            'q1_index': (q1_avg / total_avg * 100) if total_avg > 0 else 0,
            'q2_index': (q2_avg / total_avg * 100) if total_avg > 0 else 0,
            'q3_index': (q3_avg / total_avg * 100) if total_avg > 0 else 0,
            'q4_index': (q4_avg / total_avg * 100) if total_avg > 0 else 0
        }

    def _calculate_quarterly_yoy(self, data: pd.DataFrame, current_year: int) -> List[Dict[str, float]]:
        """Calculate quarterly year-over-year growth"""
        previous_year = data[data['year'] == current_year - 1]
        current_year_data = data[data['year'] == current_year]
        
        if previous_year.empty or current_year_data.empty:
            return []
            
        quarters = ['q1', 'q2', 'q3', 'q4']
        yoy_growth = []
        
        for q in quarters:
            current_contracts = current_year_data[f'{q}_contracts'].iloc[0]
            previous_contracts = previous_year[f'{q}_contracts'].iloc[0]
            
            growth = ((current_contracts - previous_contracts) / previous_contracts * 100 
                     if previous_contracts > 0 else 0)
            
            yoy_growth.append({
                'quarter': q,
                'growth_rate': growth
            })
            
        return yoy_growth

    def analyze_market_segment(self, segment: str) -> Dict[str, Any]:
        """Analyze market segment"""
        try:
            market_data = self.query_manager.get_market_data(segment)
            age_distribution = self.query_manager.get_age_distribution(segment)
            
            if not market_data:
                return {'error': 'No market data available for segment'}
                
            return {
                'market_size': {
                    'total_contracts': market_data.get('total_contracts', 0),
                    'total_premium': market_data.get('total_premium', 0),
                    'avg_premium': market_data.get('avg_premium', 0)
                },
                'age_distribution': age_distribution.to_dict('records') if not age_distribution.empty else [],
                'segment_metrics': {
                    'market_share': market_data.get('market_share', {}).get('contract_share', 0),
                    'premium_density': market_data.get('total_premium', 0) / market_data.get('total_contracts', 1)
                }
            }
            
        except Exception as e:
            logger.error(f"Market segment analysis failed: {e}")
            return {'error': str(e)}

    def analyze_market_penetration(self, segment: str) -> Dict[str, Any]:
        """Analyze market penetration"""
        market_data = self.query_manager.get_market_data(segment)
        age_distribution = self.query_manager.get_age_distribution(segment)
        market_share = self.query_manager.get_market_share(segment)
        
        # Use MarketAnalyzer's analysis results
        market_demand = self.market_analyzer.analyze_market_demand(segment)
        
        total_contracts = market_data.get('total_contracts', 0)
        total_premium = market_data.get('total_premium', 0)
        
        return {
            'penetration_metrics': {
                'market_share': market_share.get('contract_share', 0),
                'premium_share': total_premium / (market_demand.get('market_size', {}).get('total_market', 1)),
                'customer_reach': total_contracts / 10000  # 인구 1만명당 계약 수
            },
            'segment_analysis': {
                'age_distribution': age_distribution.to_dict('records') if not age_distribution.empty else [],
                'market_opportunities': market_demand.get('opportunities', []),
                'competition_level': market_demand.get('competition', {}).get('market_concentration', 0)
            },
            'growth_potential': {
                'untapped_market': market_demand.get('market_size', {}).get('potential_size', 0) - total_contracts,
                'market_saturation': total_contracts / market_demand.get('market_size', {}).get('potential_size', 1)
            }
        }

    def analyze_growth_potential(self, segment: str) -> Dict[str, Any]:
        """Analyze growth potential"""
        market_data = self.query_manager.get_market_data(segment)
        quarterly_trends = self.query_manager.get_quarterly_trends(segment)
        
        # Use MarketAnalyzer's demand forecast and market analysis results
        forecast_data = self.market_analyzer.forecast_demand(segment)
        market_demand = self.market_analyzer.analyze_market_demand(segment)
        
        # Calculate growth rate
        if not quarterly_trends.empty:
            latest_year = quarterly_trends['year'].max()
            previous_year = latest_year - 1
            latest_data = quarterly_trends[quarterly_trends['year'] == latest_year]
            previous_data = quarterly_trends[quarterly_trends['year'] == previous_year]
            
            if not previous_data.empty and not latest_data.empty:
                yoy_growth = ((latest_data['total_contracts'].iloc[0] - previous_data['total_contracts'].iloc[0]) / 
                             previous_data['total_contracts'].iloc[0] * 100 if previous_data['total_contracts'].iloc[0] > 0 else 0)
            else:
                yoy_growth = 0
        else:
            yoy_growth = 0
        
        return {
            'current_metrics': {
                'total_contracts': market_data.get('total_contracts', 0),
                'total_premium': market_data.get('total_premium', 0),
                'yoy_growth': yoy_growth
            },
            'growth_forecast': {
                'forecast': forecast_data.get('forecast', []),
                'trend': forecast_data.get('trend', {}),
                'confidence_interval': forecast_data.get('confidence_interval', {})
            },
            'market_potential': {
                'opportunities': market_demand.get('opportunities', []),
                'addressable_market': market_demand.get('market_size', {}).get('addressable_market', 0),
                'growth_drivers': self._identify_growth_factors(segment)
            },
            'competitive_landscape': {
                'market_share': self.query_manager.get_market_share(segment).get('contract_share', 0),
                'competitor_analysis': market_demand.get('competition', {}),
                'market_position': self._analyze_competitive_position(segment)
            }
        }

    def _get_expected_fields(self, request_type: str) -> Set[str]:
        """
        Expected fields for market analysis request type
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
            'market_size': {
                'data.total_market_size',
                'data.growth_rate',
                'data.market_segments',
                'data.market_share'
            },
            'competition': {
                'data.competitor_analysis',
                'data.market_concentration',
                'data.competitive_advantages',
                'data.market_position'
            },
            'demand': {
                'data.demand_forecast',
                'data.growth_drivers',
                'data.market_potential',
                'data.customer_segments'
            },
            'trends': {
                'data.market_trends',
                'data.emerging_opportunities',
                'data.risk_factors',
                'data.future_outlook'
            },
            'market_penetration': {
                'data.current_penetration',
                'data.target_segments',
                'data.growth_opportunities',
                'data.entry_barriers'
            },
            'growth_potential': {
                'data.market_metrics',
                'data.growth_forecast',
                'data.market_potential',
                'data.competitive_landscape'
            },
            'market_segment': {
                'data.segment_analysis',
                'data.segment_growth',
                'data.segment_profitability',
                'data.segment_opportunities'
            },
            'age_group_distribution': {
                'data.age_groups',
                'data.distribution_metrics',
                'data.trend_analysis',
                'data.segment_preferences'
            },
            'premium_trends': {
                'data.premium_analysis',
                'data.trend_metrics',
                'data.pricing_strategy',
                'data.competitive_pricing'
            },
            'quarterly_comparison': {
                'data.quarterly_metrics',
                'data.seasonal_patterns',
                'data.growth_trends',
                'data.performance_indicators'
            },
            'regional_performance': {
                'data.regional_metrics',
                'data.market_share',
                'data.growth_opportunities',
                'data.competitive_position'
            },
            'product_mix': {
                'data.product_portfolio',
                'data.performance_metrics',
                'data.optimization_opportunities',
                'data.market_fit'
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