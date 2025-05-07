"""
Tests for the bias detector service
"""

import os
import unittest
import asyncio
from typing import Dict, List, Any

import pytest

from app.services.ai.bias_detector import BiasDetector

# Sample texts for testing various bias detection algorithms
POLITICAL_TEXTS = {
    "left_leaning": """
        The new progressive agenda aims to address social inequality through increased 
        regulations on corporations and expanded welfare programs. Social justice advocates 
        argue that marginalized communities need more support through public initiatives that
        promote diversity and inclusion. Workers' unions are pushing for climate action and
        sustainable policies to protect future generations.
    """,
    "right_leaning": """
        Conservative values and individual freedom must be protected to maintain our 
        constitutional rights. The free market economy thrives with deregulation and tax cuts
        that allow entrepreneurs to create jobs. Traditional family values and patriotism
        are essential to our national sovereignty, along with a strong military defense
        and fiscal responsibility.
    """,
    "neutral": """
        The city council voted on the infrastructure proposal yesterday. Roads and bridges
        will be repaired starting next month according to the schedule. The project is
        expected to be completed within the fiscal year. Several community members
        expressed their opinions during the public comment period.
    """
}

EMOTIONAL_TEXTS = {
    "emotional": """
        This is absolutely the most incredible achievement ever! I am completely amazed
        by the fantastic, wonderful results. It's extremely exciting and definitely the
        best outcome we could have hoped for! I'm utterly thrilled about this incredibly
        brilliant development!!!
    """,
    "factual": """
        The experiment resulted in a 15% increase in efficiency. Data shows that the new
        method requires 20 minutes less processing time. According to measurements taken
        during the trial period, energy consumption decreased by 120 kilowatt-hours per day.
        The team recorded all results in the attached spreadsheet.
    """
}

PROPAGANDA_TEXTS = {
    "propaganda_rich": """
        Everyone knows that our opponents are lazy and corrupt extremists. Their ideas are
        a disaster that will lead to catastrophic consequences for our nation. Either we
        choose freedom or we accept tyranny - there is no middle ground. The American people
        stand with us because all patriotic citizens can see through these so-called experts.
    """,
    "propaganda_free": """
        The research paper examined multiple perspectives on the issue. Various outcomes
        were considered based on different initial assumptions. The study found correlations
        between several variables, although causation could not be definitively established.
        Further research is recommended to explore additional factors.
    """
}


class TestBiasDetector(unittest.TestCase):
    """Test suite for BiasDetector service"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.detector = BiasDetector()
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
    def test_initialization(self):
        """Test that detector initializes correctly"""
        assert self.detector is not None
        assert self.detector.political_keywords is not None
        assert len(self.detector.political_keywords["left"]) > 0
        assert len(self.detector.political_keywords["right"]) > 0
    
    def test_analyze_political_bias(self):
        """Test political bias detection"""
        results = {}
        
        # Run the async functions in a loop
        for key, text in POLITICAL_TEXTS.items():
            results[key] = asyncio.run(self.detector.analyze_political_bias(text))
        
        # Left-leaning text should have negative score
        assert results["left_leaning"] < -0.3
        
        # Right-leaning text should have positive score
        assert results["right_leaning"] > 0.3
        
        # Neutral text should be close to zero
        assert abs(results["neutral"]) < 0.2
        
        # Left should be more negative than neutral
        assert results["left_leaning"] < results["neutral"]
        
        # Right should be more positive than neutral
        assert results["right_leaning"] > results["neutral"]
    
    def test_analyze_emotional_language(self):
        """Test emotional language detection"""
        emotional_score = asyncio.run(
            self.detector.analyze_emotional_language(EMOTIONAL_TEXTS["emotional"])
        )
        factual_score = asyncio.run(
            self.detector.analyze_emotional_language(EMOTIONAL_TEXTS["factual"])
        )
        
        # Emotional text should have high score
        assert emotional_score > 0.6
        
        # Factual text should have low score
        assert factual_score < 0.4
        
        # Emotional should be higher than factual
        assert emotional_score > factual_score
    
    def test_detect_propaganda_techniques(self):
        """Test propaganda technique detection"""
        propaganda_results = asyncio.run(
            self.detector.detect_propaganda_techniques(PROPAGANDA_TEXTS["propaganda_rich"])
        )
        clean_results = asyncio.run(
            self.detector.detect_propaganda_techniques(PROPAGANDA_TEXTS["propaganda_free"])
        )
        
        # Propaganda-rich text should have multiple techniques detected
        assert len(propaganda_results) > 3
        
        # Clean text should have few or no techniques detected
        assert len(clean_results) < 2
        
        if propaganda_results:
            # Each result should have required fields
            first_result = propaganda_results[0]
            assert "technique" in first_result
            assert "span" in first_result
            assert "text" in first_result
            assert "confidence" in first_result
            assert "explanation" in first_result
            
            # Confidence should be between 0 and 1
            assert 0 <= first_result["confidence"] <= 1.0
    
    def test_calculate_fact_opinion_ratio(self):
        """Test fact vs opinion ratio calculation"""
        factual_ratio = asyncio.run(
            self.detector.calculate_fact_opinion_ratio(EMOTIONAL_TEXTS["factual"])
        )
        opinion_ratio = asyncio.run(
            self.detector.calculate_fact_opinion_ratio(EMOTIONAL_TEXTS["emotional"])
        )
        
        # Factual text should have high fact ratio
        assert factual_ratio > 0.6
        
        # Emotional/opinion text should have low fact ratio
        assert opinion_ratio < 0.5
        
        # Factual ratio should be higher than opinion ratio
        assert factual_ratio > opinion_ratio
    
    def test_get_full_bias_analysis(self):
        """Test full bias analysis"""
        # Test with different texts
        neutral_analysis = asyncio.run(
            self.detector.get_full_bias_analysis(POLITICAL_TEXTS["neutral"])
        )
        biased_analysis = asyncio.run(
            self.detector.get_full_bias_analysis(PROPAGANDA_TEXTS["propaganda_rich"])
        )
        
        # Check that all required fields are present
        for analysis in [neutral_analysis, biased_analysis]:
            assert "political_bias" in analysis
            assert "emotional_language" in analysis
            assert "propaganda_techniques" in analysis
            assert "fact_opinion_ratio" in analysis
            assert "overall_bias_score" in analysis
        
        # Biased text should have higher overall bias score
        assert biased_analysis["overall_bias_score"] > neutral_analysis["overall_bias_score"]
        
        # Biased text should have more propaganda techniques
        assert len(biased_analysis["propaganda_techniques"]) > len(neutral_analysis["propaganda_techniques"])
        
        # Overall bias score should be between 0 and 1
        assert 0 <= neutral_analysis["overall_bias_score"] <= 1.0
        assert 0 <= biased_analysis["overall_bias_score"] <= 1.0


if __name__ == "__main__":
    unittest.main()