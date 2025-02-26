from typing import Dict, Any, List, Optional
import pandas as pd
from datetime import datetime, timedelta

class MarketAnalyzer:
    """
    Market Analyzer - A class for analyzing market trends and competition
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize Market Analyzer"""
        self.market_data_source = self.config.get('market_data_source', 'default')
        self.analysis_period = self.config.get('analysis_period', 12)  # months
    
    def analyze_market_demand(self, target_segment: str) -> Dict[str, Any]:
        """Analyze Market Demand"""
        market_size = self._calculate_market_size(target_segment)
        growth_rate = self._calculate_growth_rate(target_segment)
        competition = self._analyze_competition(target_segment)
        
        return {
            'market_size': market_size,
            'growth_rate': growth_rate,
            'competition': competition,
            'opportunities': self._identify_opportunities(target_segment),
            'threats': self._identify_threats(target_segment)
        }
    
    def analyze_market_trends(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Market Trends"""
        return {
            'market_growth': self._calculate_market_growth(data),
            'competition_analysis': self._analyze_competition(data),
            'risk_factors': self._identify_risk_factors(data)
        }
    
    def analyze_competition(self, target_segment: str) -> Dict[str, Any]:
        """Analyze Competitors"""
        competitors = self._get_competitors(target_segment)
        market_share = self._calculate_market_share(competitors)
        product_comparison = self._compare_products(competitors)
        
        return {
            'competitors': competitors,
            'market_share': market_share,
            'product_comparison': product_comparison,
            'competitive_advantages': self._identify_competitive_advantages(competitors)
        }
    
    def forecast_demand(self, target_segment: str, forecast_period: int = 12) -> Dict[str, Any]:
        """Forecast Demand"""
        historical_data = self._get_historical_data(target_segment)
        trend = self._analyze_trend(historical_data)
        seasonality = self._analyze_seasonality(historical_data)
        
        return {
            'forecast': self._generate_forecast(historical_data, forecast_period),
            'trend': trend,
            'seasonality': seasonality,
            'confidence_interval': self._calculate_confidence_interval(historical_data)
        }
    
    def _calculate_market_size(self, target_segment: str) -> Dict[str, float]:
        """Calculate Market Size"""
        return {
            'total_premium': 1000000000, # example value
            'number_of_policies': 10000,
            'average_premium': 100000
        }
    
    def _calculate_growth_rate(self, target_segment: str) -> Dict[str, float]:
        """Calculate Growth Rate"""
        return {
            'yoy_growth': 0.05, # example value
            'cagr_3year': 0.07,
            'cagr_5year': 0.06
        }
    
    def _analyze_competition(self, target_segment: str) -> Dict[str, Any]:
        """Analyze Competition"""
        return {
            'number_of_competitors': 5,
            'market_concentration': 0.75,
            'price_competition_level': 'high'
        }
    
    def _identify_opportunities(self, target_segment: str) -> List[str]:
        """Identify Opportunities"""
        return [
            'aging_population',
            'increasing_health_awareness',
            'digital_transformation'
        ]
    
    def _identify_threats(self, target_segment: str) -> List[str]:
        """Identify Threats"""
        return [
            'regulatory_changes',
            'new_market_entrants',
            'economic_uncertainty'
        ]
    
    def _get_competitors(self, target_segment: str) -> List[Dict[str, Any]]:
        """Get Competitors Information"""
        return [
            {'name': 'Competitor A', 'market_share': 0.3},
            {'name': 'Competitor B', 'market_share': 0.25},
            {'name': 'Competitor C', 'market_share': 0.2}
        ]
    
    def _calculate_market_share(self, competitors: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate Market Share"""
        total_share = sum(comp['market_share'] for comp in competitors)
        return {
            'company_share': 0.15,
            'total_market': 1.0,
            'market_concentration': total_share
        }
    
    def _compare_products(self, competitors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Compare Products"""
        return [
            {
                'competitor': comp['name'],
                'product_features': ['feature1', 'feature2'],
                'price_position': 'premium',
                'strengths': ['strong_brand', 'wide_network'],
                'weaknesses': ['high_premium', 'limited_coverage']
            }
            for comp in competitors
        ]
    
    def _identify_competitive_advantages(self, competitors: List[Dict[str, Any]]) -> List[str]:
        """Identify Competitive Advantages"""
        return [
            'innovative_products',
            'strong_distribution_network',
            'efficient_claims_processing'
        ]
    
    def _get_historical_data(self, target_segment: str) -> pd.DataFrame:
        """Get Historical Data"""
        # In actual implementation, data should be fetched from a database or external source
        dates = pd.date_range(end=datetime.now(), periods=self.analysis_period, freq='M')
        data = pd.DataFrame({
            'date': dates,
            'demand': [100 + i * 10 for i in range(self.analysis_period)]
        })
        return data
    
    def _analyze_trend(self, data: pd.DataFrame) -> Dict[str, float]:
        """Analyze Trend"""
        return {
            'slope': 10.0,  # example value
            'r_squared': 0.85
        }
    
    def _analyze_seasonality(self, data: pd.DataFrame) -> Dict[str, List[float]]:
        """Analyze Seasonality"""
        return {
            'seasonal_factors': [1.1, 0.9, 1.0, 1.2],  # example value
            'seasonal_strength': 0.15
        }
    
    def _generate_forecast(self, data: pd.DataFrame, forecast_period: int) -> List[Dict[str, Any]]:
        """Generate Forecast"""
        last_value = data['demand'].iloc[-1]
        trend = 10  # example value
        
        forecast = []
        for i in range(forecast_period):
            forecast.append({
                'period': i + 1,
                'forecast_value': last_value + trend * (i + 1),
                'confidence_low': last_value + trend * (i + 1) * 0.9,
                'confidence_high': last_value + trend * (i + 1) * 1.1
            })
        
        return forecast
    
    def _calculate_confidence_interval(self, data: pd.DataFrame) -> Dict[str, float]:
        """Calculate Confidence Interval"""
        return {
            'lower_bound': 0.9,  # example value
            'upper_bound': 1.1,
            'confidence_level': 0.95
        }
    
    def _calculate_market_growth(self, data: Dict[str, Any]) -> float:
        """Calculate Market Growth
        
        Args:
            data (Dict[str, Any]): Dictionary containing market data with keys:
                - current_period_value: Current period market value
                - previous_period_value: Previous period market value
                - periods: List of period values for trend analysis
                - segment_growth: Dictionary of growth rates by segment
                
        Returns:
            float: Calculated market growth rate
        """
        try:
            # Extract basic growth rate if available
            if 'current_period_value' in data and 'previous_period_value' in data:
                current_value = float(data['current_period_value'])
                previous_value = float(data['previous_period_value'])
                if previous_value > 0:
                    basic_growth = (current_value - previous_value) / previous_value
                else:
                    basic_growth = 0.0
            else:
                basic_growth = 0.0
            
            # Calculate weighted segment growth if available
            segment_growth = 0.0
            if 'segment_growth' in data:
                segment_weights = {
                    'premium': 0.4,
                    'standard': 0.35,
                    'basic': 0.25
                }
                for segment, growth in data['segment_growth'].items():
                    weight = segment_weights.get(segment, 0.33)
                    segment_growth += float(growth) * weight
            
            # Calculate trend-based growth if period data available
            trend_growth = 0.0
            if 'periods' in data and len(data['periods']) >= 2:
                periods = data['periods']
                growth_rates = [(periods[i] - periods[i-1])/periods[i-1] 
                              for i in range(1, len(periods))]
                trend_growth = sum(growth_rates) / len(growth_rates)
            
            # Combine different growth indicators with weights
            final_growth = (basic_growth * 0.5 + 
                          segment_growth * 0.3 + 
                          trend_growth * 0.2)
            
            return round(final_growth, 4)
            
        except Exception as e:
            print(f"Error calculating market growth: {str(e)}")
            return 0.0
    
    def _identify_risk_factors(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify Risk Factors in the market
        
        Args:
            data (Dict[str, Any]): Dictionary containing market data with keys:
                - market_volatility: Market volatility metrics
                - competitor_actions: Recent competitor activities
                - regulatory_changes: Recent or upcoming regulatory changes
                - economic_indicators: Economic health indicators
                - technology_trends: Technological disruption indicators
                
        Returns:
            Dict[str, Any]: Identified risk factors with their severity and impact
        """
        risk_factors = {}
        
        try:
            # Market volatility risks
            if 'market_volatility' in data:
                volatility = data.get('market_volatility', {})
                risk_factors['market_volatility'] = {
                    'severity': self._calculate_risk_severity(volatility),
                    'factors': {
                        'premium_volatility': volatility.get('premium_volatility', 'low'),
                        'demand_fluctuation': volatility.get('demand_fluctuation', 'low'),
                        'claims_volatility': volatility.get('claims_volatility', 'low')
                    }
                }
            
            # Competitive risks
            if 'competitor_actions' in data:
                competitor_data = data.get('competitor_actions', {})
                risk_factors['competitive_risks'] = {
                    'severity': 'high' if len(competitor_data) > 3 else 'medium',
                    'factors': {
                        'new_entrants': competitor_data.get('new_entrants', 0),
                        'pricing_pressure': competitor_data.get('pricing_pressure', 'low'),
                        'product_innovation': competitor_data.get('innovation_level', 'low')
                    }
                }
            
            # Regulatory risks
            if 'regulatory_changes' in data:
                reg_changes = data.get('regulatory_changes', [])
                risk_factors['regulatory_risks'] = {
                    'severity': 'high' if len(reg_changes) > 2 else 'medium',
                    'upcoming_changes': reg_changes,
                    'compliance_impact': self._assess_compliance_impact(reg_changes)
                }
            
            # Economic risks
            if 'economic_indicators' in data:
                economic_data = data.get('economic_indicators', {})
                risk_factors['economic_risks'] = {
                    'severity': self._assess_economic_risk_severity(economic_data),
                    'factors': {
                        'inflation_risk': economic_data.get('inflation', 'low'),
                        'interest_rate_risk': economic_data.get('interest_rate', 'low'),
                        'currency_risk': economic_data.get('currency', 'low')
                    }
                }
            
            # Technology risks
            if 'technology_trends' in data:
                tech_trends = data.get('technology_trends', {})
                risk_factors['technology_risks'] = {
                    'severity': 'high' if tech_trends.get('disruption_level', 'low') == 'high' else 'medium',
                    'factors': {
                        'digital_disruption': tech_trends.get('digital_disruption', 'low'),
                        'cybersecurity': tech_trends.get('cybersecurity_threat', 'low'),
                        'tech_adoption_gap': tech_trends.get('adoption_gap', 'low')
                    }
                }
            
            # Add risk mitigation suggestions
            risk_factors['mitigation_strategies'] = self._generate_mitigation_strategies(risk_factors)
            
            return risk_factors
            
        except Exception as e:
            print(f"Error identifying risk factors: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_risk_severity(self, volatility_data: Dict[str, Any]) -> str:
        """Calculate risk severity based on volatility data"""
        severity_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        total_score = sum(severity_scores.get(level, 1) 
                         for level in volatility_data.values())
        avg_score = total_score / len(volatility_data) if volatility_data else 1
        
        if avg_score >= 2.5:
            return 'high'
        elif avg_score >= 1.5:
            return 'medium'
        return 'low'
    
    def _assess_compliance_impact(self, regulatory_changes: List[str]) -> str:
        """Assess the impact of regulatory changes"""
        high_impact_keywords = ['mandatory', 'penalty', 'immediate', 'strict']
        medium_impact_keywords = ['recommended', 'guideline', 'proposed']
        
        high_impact_count = sum(1 for change in regulatory_changes 
                              if any(keyword in change.lower() 
                                    for keyword in high_impact_keywords))
        
        medium_impact_count = sum(1 for change in regulatory_changes 
                                if any(keyword in change.lower() 
                                      for keyword in medium_impact_keywords))
        
        if high_impact_count > 1:
            return 'high'
        elif high_impact_count == 1 or medium_impact_count > 1:
            return 'medium'
        return 'low'
    
    def _assess_economic_risk_severity(self, economic_data: Dict[str, Any]) -> str:
        """Assess severity of economic risks"""
        risk_scores = {
            'high': 3,
            'medium': 2,
            'low': 1
        }
        
        total_score = sum(risk_scores.get(level, 1) 
                         for level in economic_data.values())
        avg_score = total_score / len(economic_data) if economic_data else 1
        
        if avg_score >= 2.5:
            return 'high'
        elif avg_score >= 1.5:
            return 'medium'
        return 'low'
    
    def _generate_mitigation_strategies(self, risk_factors: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate mitigation strategies for identified risks"""
        strategies = []
        
        # Market volatility mitigation
        if 'market_volatility' in risk_factors and risk_factors['market_volatility']['severity'] == 'high':
            strategies.append({
                'risk_type': 'market_volatility',
                'strategy': 'Implement dynamic pricing and risk assessment models',
                'priority': 'high'
            })
        
        # Competitive risk mitigation
        if 'competitive_risks' in risk_factors and risk_factors['competitive_risks']['severity'] == 'high':
            strategies.append({
                'risk_type': 'competitive_risks',
                'strategy': 'Enhance product differentiation and customer service',
                'priority': 'high'
            })
        
        # Regulatory risk mitigation
        if 'regulatory_risks' in risk_factors and risk_factors['regulatory_risks']['severity'] == 'high':
            strategies.append({
                'risk_type': 'regulatory_risks',
                'strategy': 'Strengthen compliance framework and monitoring',
                'priority': 'high'
            })
        
        # Economic risk mitigation
        if 'economic_risks' in risk_factors and risk_factors['economic_risks']['severity'] == 'high':
            strategies.append({
                'risk_type': 'economic_risks',
                'strategy': 'Diversify investment portfolio and hedge currency exposure',
                'priority': 'high'
            })
        
        # Technology risk mitigation
        if 'technology_risks' in risk_factors and risk_factors['technology_risks']['severity'] == 'high':
            strategies.append({
                'risk_type': 'technology_risks',
                'strategy': 'Accelerate digital transformation and enhance cybersecurity',
                'priority': 'high'
            })
        
        return strategies 