from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ResultSynthesizer:
    """Integrate analysis results and derive insights"""
    
    def __init__(self):
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
    def synthesize(self, engine_results: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate multiple engine results to derive final insights"""
        try:
            primary_insights = self._extract_primary_insights(engine_results)
            supporting_evidence = self._gather_supporting_evidence(engine_results)
            confidence_scores = self._calculate_confidence_scores(engine_results)
            
            synthesis = {
                'insights': primary_insights,
                'evidence': supporting_evidence,
                'confidence': confidence_scores,
                'recommendations': self._generate_recommendations(
                    primary_insights,
                    supporting_evidence,
                    confidence_scores
                ),
                'metadata': {
                    'analysis_timestamp': datetime.now().isoformat(),
                    'analysis_components': list(engine_results.keys()),
                    'data_quality': self._assess_data_quality(engine_results)
                }
            }
            
            # Add low confidence warnings
            if self._has_low_confidence(confidence_scores):
                synthesis['warnings'] = self._generate_warnings(confidence_scores)
                
            return synthesis
            
        except Exception as e:
            logger.error(f"Result synthesis failed: {e}")
            return {
                'error': 'Synthesis failed',
                'message': str(e),
                'partial_results': engine_results
            }
            
    def _extract_primary_insights(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract primary insights"""
        insights = []
        
        for engine_type, engine_result in results.items():
            if isinstance(engine_result, dict) and 'data' in engine_result:
                engine_insights = self._process_engine_insights(
                    engine_type,
                    engine_result['data']
                )
                insights.extend(engine_insights)
                
        return sorted(insights, key=lambda x: x.get('significance', 0), reverse=True)
        
    def _gather_supporting_evidence(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect supporting evidence"""
        evidence = {
            'metrics': self._collect_metrics(results),
            'trends': self._collect_trends(results),
            'correlations': self._collect_correlations(results),
            'anomalies': self._detect_anomalies(results)
        }
        return evidence
        
    def _calculate_confidence_scores(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores"""
        confidence_scores = {}
        
        for engine_type, result in results.items():
            if isinstance(result, dict) and 'data' in result:
                confidence_scores[engine_type] = self._calculate_single_confidence(
                    result['data']
                )
                
        return confidence_scores
        
    def _generate_recommendations(self, insights: List[Dict[str, Any]],
                                evidence: Dict[str, Any],
                                confidence: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate recommendations"""
        recommendations = []
        
        # Use only high confidence insights
        high_confidence_insights = [
            insight for insight in insights
            if confidence.get(insight['source'], 0) >= self.confidence_thresholds['medium']
        ]
        
        for insight in high_confidence_insights:
            recommendation = self._create_recommendation(
                insight,
                evidence,
                confidence.get(insight['source'], 0)
            )
            if recommendation:
                recommendations.append(recommendation)
                
        return sorted(recommendations, key=lambda x: x['priority'], reverse=True)
        
    def _assess_data_quality(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess data quality"""
        quality_metrics = {
            'completeness': self._calculate_completeness(results),
            'consistency': self._check_consistency(results),
            'reliability': self._assess_reliability(results)
        }
        return quality_metrics
        
    def _has_low_confidence(self, confidence_scores: Dict[str, float]) -> bool:
        """Check if any low confidence"""
        return any(
            score < self.confidence_thresholds['medium']
            for score in confidence_scores.values()
        )
        
    def _generate_warnings(self, confidence_scores: Dict[str, float]) -> List[str]:
        """Generate warning messages"""
        warnings = []
        
        for component, score in confidence_scores.items():
            if score < self.confidence_thresholds['low']:
                warnings.append(
                    f"Very low confidence in {component} analysis (score: {score:.2f})"
                )
            elif score < self.confidence_thresholds['medium']:
                warnings.append(
                    f"Moderate confidence in {component} analysis (score: {score:.2f})"
                )
                
        return warnings
        
    def _process_engine_insights(self, engine_type: str, 
                               data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process engine insights"""
        insights = []
        
        if 'primary_insights' in data:
            for insight in data['primary_insights']:
                processed_insight = {
                    'source': engine_type,
                    'type': insight.get('type', 'unknown'),
                    'finding': insight.get('finding', ''),
                    'significance': insight.get('significance', 0),
                    'confidence': insight.get('confidence', 0)
                }
                insights.append(processed_insight)
                
        return insights
        
    def _create_recommendation(self, insight: Dict[str, Any],
                             evidence: Dict[str, Any],
                             confidence: float) -> Optional[Dict[str, Any]]:
        """Generate recommendations"""
        if confidence < self.confidence_thresholds['medium']:
            return None
            
        return {
            'source_insight': insight['finding'],
            'recommendation': self._generate_recommendation_text(insight, evidence),
            'priority': self._calculate_priority(insight, confidence),
            'confidence': confidence,
            'supporting_evidence': self._get_relevant_evidence(insight, evidence)
        }
        
    def _calculate_priority(self, insight: Dict[str, Any], 
                          confidence: float) -> float:
        """Calculate priority"""
        significance = insight.get('significance', 0)
        return significance * confidence
        
    def _get_relevant_evidence(self, insight: Dict[str, Any],
                             evidence: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant evidence"""
        relevant_evidence = {}
        
        insight_type = insight.get('type', '')
        
        if 'metrics' in evidence:
            relevant_evidence['metrics'] = {
                k: v for k, v in evidence['metrics'].items()
                if insight_type in k
            }
            
        if 'trends' in evidence:
            relevant_evidence['trends'] = {
                k: v for k, v in evidence['trends'].items()
                if insight_type in k
            }
            
        return relevant_evidence 

    def _collect_metrics(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect metric data"""
        metrics = {}
        
        for engine_type, result in results.items():
            if isinstance(result, dict) and 'data' in result:
                engine_metrics = result['data'].get('metrics', {})
                for metric_name, value in engine_metrics.items():
                    metrics[f"{engine_type}_{metric_name}"] = value
                    
        return metrics
        
    def _collect_trends(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect trend data"""
        trends = {}
        
        for engine_type, result in results.items():
            if isinstance(result, dict) and 'data' in result:
                engine_trends = result['data'].get('trends', {})
                for trend_name, data in engine_trends.items():
                    trends[f"{engine_type}_{trend_name}"] = {
                        'direction': data.get('direction', 'unknown'),
                        'magnitude': data.get('magnitude', 0),
                        'period': data.get('period', 'unknown'),
                        'confidence': data.get('confidence', 0)
                    }
                    
        return trends
        
    def _collect_correlations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Collect correlation data"""
        correlations = {}
        
        for engine_type, result in results.items():
            if isinstance(result, dict) and 'data' in result:
                engine_correlations = result['data'].get('correlations', {})
                for var1, var2_data in engine_correlations.items():
                    for var2, corr_data in var2_data.items():
                        key = f"{engine_type}_{var1}_{var2}"
                        correlations[key] = {
                            'coefficient': corr_data.get('coefficient', 0),
                            'significance': corr_data.get('significance', 0),
                            'sample_size': corr_data.get('sample_size', 0)
                        }
                        
        return correlations
        
    def _detect_anomalies(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies"""
        anomalies = {}
        
        for engine_type, result in results.items():
            if isinstance(result, dict) and 'data' in result:
                engine_anomalies = result['data'].get('anomalies', {})
                for metric_name, anomaly_data in engine_anomalies.items():
                    key = f"{engine_type}_{metric_name}"
                    anomalies[key] = {
                        'severity': anomaly_data.get('severity', 0),
                        'description': anomaly_data.get('description', ''),
                        'timestamp': anomaly_data.get('timestamp', ''),
                        'value': anomaly_data.get('value', None)
                    }
                    
        return anomalies
        
    def _calculate_single_confidence(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score for single result"""
        confidence_factors = [
            self._assess_data_completeness(data),
            self._assess_data_consistency(data),
            self._assess_sample_size(data),
            self._assess_time_relevance(data)
        ]
        
        # Calculate weighted average
        weights = [0.4, 0.3, 0.2, 0.1]  # Weights for each factor
        weighted_sum = sum(f * w for f, w in zip(confidence_factors, weights))
        
        return min(1.0, max(0.0, weighted_sum))
        
    def _assess_data_completeness(self, data: Dict[str, Any]) -> float:
        """Assess data completeness"""
        if not data:
            return 0.0
            
        required_fields = {'metrics', 'trends', 'correlations', 'anomalies'}
        present_fields = set(data.keys())
        completeness_ratio = len(present_fields & required_fields) / len(required_fields)
        
        return completeness_ratio
        
    def _assess_data_consistency(self, data: Dict[str, Any]) -> float:
        """Assess data consistency"""
        consistency_score = 1.0
        
        if 'metrics' in data and 'trends' in data:
            metrics = data['metrics']
            trends = data['trends']
            
            # Check consistency between metrics and trends
            for metric_name, metric_value in metrics.items():
                if metric_name in trends:
                    trend_direction = trends[metric_name].get('direction', 'unknown')
                    if not self._is_consistent_with_trend(metric_value, trend_direction):
                        consistency_score *= 0.8
                        
        return consistency_score
        
    def _assess_sample_size(self, data: Dict[str, Any]) -> float:
        """Assess sample size"""
        if 'metadata' not in data or 'sample_size' not in data['metadata']:
            return 0.5  # Default value
            
        sample_size = data['metadata']['sample_size']
        min_sample = 30  # Minimum sample size
        optimal_sample = 1000  # Optimal sample size
        
        if sample_size < min_sample:
            return 0.3
        elif sample_size >= optimal_sample:
            return 1.0
        else:
            # Linear scaling
            return 0.3 + 0.7 * (sample_size - min_sample) / (optimal_sample - min_sample)
            
    def _assess_time_relevance(self, data: Dict[str, Any]) -> float:
        """Assess time relevance"""
        if 'metadata' not in data or 'timestamp' not in data['metadata']:
            return 0.5  # Default value
            
        timestamp = datetime.fromisoformat(data['metadata']['timestamp'])
        now = datetime.now()
        age_days = (now - timestamp).days
        
        if age_days <= 7:  # Within 1 week
            return 1.0
        elif age_days <= 30:  # Within 1 month
            return 0.8
        elif age_days <= 90:  # Within 3 months
            return 0.6
        elif age_days <= 180:  # Within 6 months
            return 0.4
        else:
            return 0.2
            
    def _is_consistent_with_trend(self, value: float, trend_direction: str) -> bool:
        """Check consistency between value and trend direction"""
        if trend_direction == 'increasing' and value < 0:
            return False
        elif trend_direction == 'decreasing' and value > 0:
            return False
        return True
        
    def _calculate_completeness(self, results: Dict[str, Any]) -> float:
        """Calculate completeness of overall results"""
        if not results:
            return 0.0
            
        completeness_scores = []
        for result in results.values():
            if isinstance(result, dict) and 'data' in result:
                completeness_scores.append(self._assess_data_completeness(result['data']))
                
        return sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
        
    def _check_consistency(self, results: Dict[str, Any]) -> float:
        """Check consistency of overall results"""
        if not results:
            return 0.0
            
        consistency_scores = []
        for result in results.values():
            if isinstance(result, dict) and 'data' in result:
                consistency_scores.append(self._assess_data_consistency(result['data']))
                
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
        
    def _assess_reliability(self, results: Dict[str, Any]) -> float:
        """Assess reliability of overall results"""
        if not results:
            return 0.0
            
        reliability_scores = []
        for result in results.values():
            if isinstance(result, dict) and 'data' in result:
                sample_size_score = self._assess_sample_size(result['data'])
                time_relevance_score = self._assess_time_relevance(result['data'])
                reliability_scores.append((sample_size_score + time_relevance_score) / 2)
                
        return sum(reliability_scores) / len(reliability_scores) if reliability_scores else 0.0
        
    def _generate_recommendation_text(self, insight: Dict[str, Any],
                                   evidence: Dict[str, Any]) -> str:
        """Generate recommendation text"""
        insight_type = insight.get('type', '')
        finding = insight.get('finding', '')
        
        # Extract relevant metrics and trends
        relevant_metrics = evidence.get('metrics', {})
        relevant_trends = evidence.get('trends', {})
        
        recommendation_text = f"Based on the {insight_type} analysis finding that {finding}, "
        
        # Metric-based recommendations
        if relevant_metrics:
            metric_insights = self._analyze_metrics(relevant_metrics)
            recommendation_text += f"and considering the metrics showing {metric_insights}, "
            
        # Trend-based recommendations
        if relevant_trends:
            trend_insights = self._analyze_trends(relevant_trends)
            recommendation_text += f"with trends indicating {trend_insights}, "
            
        recommendation_text += "we recommend the following actions:\n"
        
        # Generate specific recommendations for insight type
        specific_recommendations = self._get_specific_recommendations(
            insight_type,
            finding,
            relevant_metrics,
            relevant_trends
        )
        
        recommendation_text += "\n".join(f"- {rec}" for rec in specific_recommendations)
        
        return recommendation_text
        
    def _analyze_metrics(self, metrics: Dict[str, Any]) -> str:
        """Analyze metrics and generate text"""
        if not metrics:
            return "insufficient metric data"
            
        significant_metrics = {
            k: v for k, v in metrics.items()
            if abs(float(v)) > 0.1  # Significant change threshold
        }
        
        if not significant_metrics:
            return "no significant metric changes"
            
        metric_descriptions = []
        for metric, value in significant_metrics.items():
            description = f"{metric.replace('_', ' ')} of {value:.2f}"
            metric_descriptions.append(description)
            
        return ", ".join(metric_descriptions)
        
    def _analyze_trends(self, trends: Dict[str, Any]) -> str:
        """Analyze trends and generate text"""
        if not trends:
            return "no clear trends"
            
        significant_trends = {
            k: v for k, v in trends.items()
            if v.get('confidence', 0) > 0.6  # Select only high confidence trends
        }
        
        if not significant_trends:
            return "no significant trends"
            
        trend_descriptions = []
        for trend_name, trend_data in significant_trends.items():
            description = (
                f"{trend_name.replace('_', ' ')} is {trend_data['direction']} "
                f"with {trend_data['magnitude']:.1f}% change over {trend_data['period']}"
            )
            trend_descriptions.append(description)
            
        return "; ".join(trend_descriptions)
        
    def _get_specific_recommendations(self, insight_type: str,
                                    finding: str,
                                    metrics: Dict[str, Any],
                                    trends: Dict[str, Any]) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if insight_type == "market_analysis":
            recommendations.extend(self._get_market_recommendations(finding, metrics, trends))
        elif insight_type == "risk_analysis":
            recommendations.extend(self._get_risk_recommendations(finding, metrics, trends))
        elif insight_type == "customer_analysis":
            recommendations.extend(self._get_customer_recommendations(finding, metrics, trends))
        elif insight_type == "product_analysis":
            recommendations.extend(self._get_product_recommendations(finding, metrics, trends))
        else:
            recommendations.append(
                "Conduct further analysis to determine specific action items"
            )
            
        return recommendations
        
    def _get_market_recommendations(self, finding: str,
                                  metrics: Dict[str, Any],
                                  trends: Dict[str, Any]) -> List[str]:
        """Market analysis-based recommendations"""
        recommendations = []
        
        # Market growth-related recommendations
        market_growth = self._extract_growth_trend(trends)
        if market_growth > 0.1: 
            recommendations.append(
                "Increase market presence through targeted marketing campaigns"
            )
            recommendations.append(
                "Develop new products to capture growing market segments"
            )
        elif market_growth < -0.1:  
            recommendations.append(
                "Focus on customer retention and cost optimization"
            )
            recommendations.append(
                "Explore adjacent markets for diversification"
            )
            
        # Competition intensity-related recommendations
        competition_intensity = metrics.get('competition_intensity', 0)
        if competition_intensity > 0.7:  
            recommendations.append(
                "Differentiate products through unique features or service quality"
            )
            recommendations.append(
                "Strengthen customer relationships through improved service"
            )
            
        return recommendations
        
    def _get_risk_recommendations(self, finding: str,
                                metrics: Dict[str, Any],
                                trends: Dict[str, Any]) -> List[str]:
        """Risk analysis-based recommendations"""
        recommendations = []
        
        # Claim frequency-related recommendations
        claim_frequency = metrics.get('claim_frequency', 0)
        if claim_frequency > 0.15:  
            recommendations.append(
                "Implement stricter risk assessment procedures"
            )
            recommendations.append(
                "Review and adjust pricing models based on claim patterns"
            )
            
        # Loss ratio-related recommendations
        loss_ratio = metrics.get('loss_ratio', 0)
        if loss_ratio > 0.7:  
            recommendations.append(
                "Enhance fraud detection mechanisms"
            )
            recommendations.append(
                "Revise underwriting guidelines for high-risk segments"
            )
            
        return recommendations
        
    def _get_customer_recommendations(self, finding: str,
                                    metrics: Dict[str, Any],
                                    trends: Dict[str, Any]) -> List[str]:
        """Customer analysis-based recommendations"""
        recommendations = []
        
        # Customer satisfaction-related recommendations
        satisfaction = metrics.get('customer_satisfaction', 0)
        if satisfaction < 0.7:  
            recommendations.append(
                "Improve customer service response times and quality"
            )
            recommendations.append(
                "Implement regular customer feedback collection and analysis"
            )
            
        # Churn rate-related recommendations
        churn_rate = metrics.get('churn_rate', 0)
        if churn_rate > 0.1:  
            recommendations.append(
                "Develop customer retention programs with targeted incentives"
            )
            recommendations.append(
                "Analyze churn patterns to identify at-risk customers early"
            )
            
        return recommendations
        
    def _get_product_recommendations(self, finding: str,
                                   metrics: Dict[str, Any],
                                   trends: Dict[str, Any]) -> List[str]:
        """Product analysis-based recommendations"""
        recommendations = []
        
        # Product performance-related recommendations
        performance = metrics.get('product_performance', 0)
        if performance < 0.6:  
            recommendations.append(
                "Review and optimize product features based on usage patterns"
            )
            recommendations.append(
                "Consider product bundling or unbundling strategies"
            )
            
        # Price competitiveness-related recommendations
        price_competitiveness = metrics.get('price_competitiveness', 0)
        if price_competitiveness < 0.5:  
            recommendations.append(
                "Analyze cost structure for optimization opportunities"
            )
            recommendations.append(
                "Evaluate pricing strategy against market benchmarks"
            )
            
        return recommendations
        
    def _extract_growth_trend(self, trends: Dict[str, Any]) -> float:
        """Extract growth trends"""
        growth_trends = {
            k: v for k, v in trends.items()
            if 'growth' in k.lower() or 'market_size' in k.lower()
        }
        
        if not growth_trends:
            return 0.0
            
        # Calculate weighted average
        weighted_sum = 0
        total_weight = 0
        
        for trend_data in growth_trends.values():
            confidence = trend_data.get('confidence', 0)
            magnitude = trend_data.get('magnitude', 0)
            
            weighted_sum += magnitude * confidence
            total_weight += confidence
            
        return weighted_sum / total_weight if total_weight > 0 else 0.0 