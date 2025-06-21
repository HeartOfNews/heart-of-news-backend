"""
Comprehensive bias detection service for analyzing news articles
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any, Tuple

from app.services.ai.sentiment_analyzer import SentimentAnalyzer, EmotionalLanguageDetector
from app.services.ai.political_bias_detector import PoliticalBiasDetector
from app.services.ai.fact_opinion_classifier import FactOpinionClassifier
from app.services.ai.propaganda_detector import PropagandaTechniqueDetector

logger = logging.getLogger(__name__)

class BiasDetector:
    """
    Comprehensive service for detecting various types of bias in news articles
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the bias detector with AI models
        """
        self.model_path = model_path
        self.sentiment_analyzer = SentimentAnalyzer()
        self.emotional_detector = EmotionalLanguageDetector()
        self.political_detector = PoliticalBiasDetector()
        self.fact_opinion_classifier = FactOpinionClassifier()
        self.propaganda_detector = PropagandaTechniqueDetector()
        
    async def analyze_political_bias(self, text: str) -> float:
        """
        Analyze text for political bias
        
        Returns a float between -1.0 (left-leaning) and 1.0 (right-leaning)
        with 0.0 being neutral
        """
        return await self.political_detector.analyze_political_bias(text)
    
    async def analyze_emotional_language(self, text: str) -> float:
        """
        Analyze text for emotional vs. factual language
        
        Returns a float between 0.0 (completely factual) and 
        1.0 (highly emotional)
        """
        return await self.emotional_detector.analyze_emotional_language(text)
    
    async def detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect specific propaganda techniques in the text
        
        Returns a list of detected techniques with confidence scores
        and text spans
        """
        return await self.propaganda_detector.detect_propaganda_techniques(text)
    
    async def calculate_fact_opinion_ratio(self, text: str) -> float:
        """
        Calculate the ratio of factual statements to opinions
        
        Returns a float between 0.0 (all opinions) and 
        1.0 (all factual statements)
        """
        return await self.fact_opinion_classifier.calculate_fact_opinion_ratio(text)
    
    async def get_full_bias_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform a complete bias analysis of the text
        
        Returns a dictionary with multiple bias metrics
        """
        # Run all analyses concurrently for better performance
        political_bias_task = asyncio.create_task(self.analyze_political_bias(text))
        emotional_language_task = asyncio.create_task(self.analyze_emotional_language(text))
        propaganda_techniques_task = asyncio.create_task(self.detect_propaganda_techniques(text))
        fact_opinion_ratio_task = asyncio.create_task(self.calculate_fact_opinion_ratio(text))
        sentiment_task = asyncio.create_task(self.sentiment_analyzer.analyze_sentiment(text))
        
        # Additional detailed analyses
        propaganda_density_task = asyncio.create_task(self.propaganda_detector.analyze_propaganda_density(text))
        bias_indicators_task = asyncio.create_task(self.political_detector.detect_bias_indicators(text))
        fact_detail_task = asyncio.create_task(self.fact_opinion_classifier.get_detailed_analysis(text))
        
        # Wait for all tasks to complete
        political_bias = await political_bias_task
        emotional_language = await emotional_language_task
        propaganda_techniques = await propaganda_techniques_task
        fact_opinion_ratio = await fact_opinion_ratio_task
        sentiment_scores = await sentiment_task
        propaganda_density = await propaganda_density_task
        bias_indicators = await bias_indicators_task
        fact_detail = await fact_detail_task
        
        overall_bias_score = self._calculate_overall_bias(
            political_bias, 
            emotional_language, 
            len(propaganda_techniques), 
            fact_opinion_ratio
        )
        
        return {
            "political_bias": political_bias,
            "emotional_language": emotional_language,
            "propaganda_techniques": propaganda_techniques,
            "fact_opinion_ratio": fact_opinion_ratio,
            "overall_bias_score": overall_bias_score,
            "sentiment_scores": sentiment_scores,
            "propaganda_density": propaganda_density,
            "bias_indicators": bias_indicators,
            "fact_analysis": fact_detail,
            "risk_assessment": self._assess_risk_level(overall_bias_score, propaganda_density),
            "recommendations": self._generate_recommendations(
                overall_bias_score, 
                political_bias, 
                emotional_language, 
                propaganda_techniques,
                fact_opinion_ratio
            )
        }
    
    def _calculate_overall_bias(
        self,
        political_bias: float,
        emotional_language: float,
        propaganda_count: int,
        fact_opinion_ratio: float
    ) -> float:
        """
        Calculate an overall bias score from individual metrics
        
        Returns a float between 0.0 (unbiased) and 1.0 (highly biased)
        """
        # This would combine individual metrics into an overall score
        # For now, use a simple weighted average
        political_weight = 0.3
        emotional_weight = 0.3
        propaganda_weight = 0.2
        factual_weight = 0.2
        
        # Normalize political bias to 0-1 range
        political_score = abs(political_bias)
        
        # Normalize propaganda count (assuming max of 5 techniques)
        propaganda_score = min(propaganda_count / 5.0, 1.0)
        
        # Invert fact-opinion ratio so higher means more biased
        factual_score = 1.0 - fact_opinion_ratio
        
        return (
            political_score * political_weight +
            emotional_language * emotional_weight +
            propaganda_score * propaganda_weight +
            factual_score * factual_weight
        )
    
    def _assess_risk_level(self, overall_bias_score: float, propaganda_density: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall risk level of the content"""
        risk_factors = []
        
        # Overall bias score assessment
        if overall_bias_score > 0.7:
            risk_level = "high"
            risk_factors.append("High overall bias score")
        elif overall_bias_score > 0.4:
            risk_level = "medium"
            risk_factors.append("Moderate bias detected")
        else:
            risk_level = "low"
        
        # Propaganda density assessment
        if propaganda_density.get("risk_level") == "high":
            if risk_level != "high":
                risk_level = "high"
            risk_factors.append("High propaganda technique usage")
        elif propaganda_density.get("risk_level") == "medium":
            if risk_level == "low":
                risk_level = "medium"
            risk_factors.append("Moderate propaganda techniques detected")
        
        # High severity propaganda techniques
        if propaganda_density.get("high_severity_count", 0) > 2:
            risk_level = "high"
            risk_factors.append("Multiple high-severity propaganda techniques")
        
        return {
            "level": risk_level,
            "factors": risk_factors,
            "score": overall_bias_score,
            "confidence": 0.8  # Could be made more sophisticated
        }
    
    def _generate_recommendations(
        self, 
        overall_bias_score: float, 
        political_bias: float, 
        emotional_language: float, 
        propaganda_techniques: List[Dict[str, Any]],
        fact_opinion_ratio: float
    ) -> List[str]:
        """Generate actionable recommendations based on bias analysis"""
        recommendations = []
        
        # Overall bias recommendations
        if overall_bias_score > 0.6:
            recommendations.append("This content shows significant bias. Seek multiple sources for balanced perspective.")
        elif overall_bias_score > 0.3:
            recommendations.append("Some bias detected. Consider cross-referencing with other sources.")
        
        # Political bias recommendations
        if abs(political_bias) > 0.5:
            direction = "conservative" if political_bias > 0 else "liberal"
            recommendations.append(f"Strong {direction} political leaning detected. Seek opposing viewpoints.")
        
        # Emotional language recommendations
        if emotional_language > 0.6:
            recommendations.append("High emotional language detected. Focus on factual claims rather than emotional appeals.")
        
        # Propaganda technique recommendations
        high_severity_techniques = [t for t in propaganda_techniques if t.get('severity') == 'high']
        if len(high_severity_techniques) > 1:
            recommendations.append("Multiple propaganda techniques detected. Be cautious of manipulation attempts.")
        
        # Fact/opinion ratio recommendations
        if fact_opinion_ratio < 0.3:
            recommendations.append("Content is heavily opinion-based. Look for factual evidence and data.")
        elif fact_opinion_ratio > 0.8:
            recommendations.append("Content is very factual but may lack context or analysis.")
        
        # Limit to most important recommendations
        return recommendations[:4]