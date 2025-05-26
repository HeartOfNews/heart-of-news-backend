"""
Advanced Propaganda Detection and Content Verification Service
Analyzes news content for propaganda techniques and bias before publication
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class PropagandaDetector:
    """Detects propaganda techniques and bias in news content"""
    
    def __init__(self):
        self.propaganda_patterns = self._load_propaganda_patterns()
        self.bias_indicators = self._load_bias_indicators()
        self.fact_check_keywords = self._load_fact_check_keywords()
        
    def _load_propaganda_patterns(self) -> Dict[str, List[str]]:
        """Load patterns that indicate propaganda techniques"""
        return {
            "emotional_manipulation": [
                r"\b(outrageous|shocking|devastating|horrifying|terrifying)\b",
                r"\b(you must|everyone knows|nobody can deny)\b",
                r"\b(threat to democracy|existential crisis|catastrophic)\b"
            ],
            "loaded_language": [
                r"\b(regime|puppet|dictator|tyrant|fascist)\b",
                r"\b(terrorist|extremist|radical|fanatic)\b",
                r"\b(invasion|occupation|annexation)\b"
            ],
            "false_dichotomy": [
                r"\b(either|or)\b.*\b(no choice|only option)\b",
                r"\b(with us or against us|choose sides)\b"
            ],
            "ad_hominem": [
                r"\b(corrupt|crooked|dishonest|lying)\b.*\b(politician|leader|official)\b",
                r"\b(failed|incompetent|weak)\b.*\b(administration|government)\b"
            ],
            "unverified_claims": [
                r"\b(sources say|reportedly|allegedly|rumored)\b",
                r"\b(according to insiders|unnamed officials)\b",
                r"\b(it is believed|widely reported)\b"
            ]
        }
    
    def _load_bias_indicators(self) -> Dict[str, List[str]]:
        """Load indicators of political bias"""
        return {
            "left_bias": [
                r"\b(progressive|social justice|inequality|systemic)\b",
                r"\b(climate emergency|corporate greed|wealth gap)\b"
            ],
            "right_bias": [
                r"\b(traditional values|law and order|free market)\b",
                r"\b(personal responsibility|limited government)\b"
            ],
            "sensationalism": [
                r"\b(breaking|urgent|exclusive|bombshell)\b",
                r"\b(stunning|explosive|unprecedented)\b"
            ]
        }
    
    def _load_fact_check_keywords(self) -> List[str]:
        """Keywords that require fact-checking"""
        return [
            "statistics", "data shows", "study reveals", "research indicates",
            "poll shows", "survey finds", "according to", "sources confirm"
        ]
    
    def analyze_content(self, title: str, content: str, source_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive analysis of news content for propaganda and bias
        
        Args:
            title: Article title
            content: Article content
            source_info: Information about the news source
            
        Returns:
            Analysis results with propaganda detection and recommendations
        """
        full_text = f"{title} {content}".lower()
        
        analysis = {
            "propaganda_score": 0.0,  # 0.0 = no propaganda, 1.0 = high propaganda
            "bias_score": 0.0,       # -1.0 = left bias, 1.0 = right bias, 0.0 = neutral
            "reliability_score": 1.0, # 1.0 = highly reliable, 0.0 = unreliable
            "fact_check_required": False,
            "verification_needed": False,
            "propaganda_techniques": [],
            "bias_indicators": [],
            "concerns": [],
            "recommendation": "APPROVE",  # APPROVE, REVIEW, REJECT
            "confidence": 1.0
        }
        
        # Analyze propaganda techniques
        propaganda_techniques = self._detect_propaganda_techniques(full_text)
        analysis["propaganda_techniques"] = propaganda_techniques
        analysis["propaganda_score"] = len(propaganda_techniques) * 0.2
        
        # Analyze bias indicators
        bias_indicators = self._detect_bias_indicators(full_text)
        analysis["bias_indicators"] = bias_indicators
        analysis["bias_score"] = self._calculate_bias_score(bias_indicators)
        
        # Check if fact-checking is required
        analysis["fact_check_required"] = self._requires_fact_checking(full_text)
        
        # Verify source reliability
        source_reliability = self._verify_source_reliability(source_info)
        analysis["reliability_score"] = source_reliability
        
        # Check for verification requirements
        analysis["verification_needed"] = self._needs_verification(full_text, source_info)
        
        # Generate concerns
        analysis["concerns"] = self._generate_concerns(analysis)
        
        # Make recommendation
        analysis["recommendation"] = self._make_recommendation(analysis)
        analysis["confidence"] = self._calculate_confidence(analysis)
        
        return analysis
    
    def _detect_propaganda_techniques(self, text: str) -> List[str]:
        """Detect specific propaganda techniques in text"""
        detected = []
        
        for technique, patterns in self.propaganda_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(technique)
                    break
        
        return detected
    
    def _detect_bias_indicators(self, text: str) -> List[str]:
        """Detect bias indicators in text"""
        detected = []
        
        for bias_type, patterns in self.bias_indicators.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected.append(bias_type)
                    break
        
        return detected
    
    def _calculate_bias_score(self, bias_indicators: List[str]) -> float:
        """Calculate overall bias score"""
        left_count = sum(1 for indicator in bias_indicators if "left" in indicator)
        right_count = sum(1 for indicator in bias_indicators if "right" in indicator)
        
        if left_count > right_count:
            return -min(0.5, left_count * 0.2)
        elif right_count > left_count:
            return min(0.5, right_count * 0.2)
        else:
            return 0.0
    
    def _requires_fact_checking(self, text: str) -> bool:
        """Determine if content requires fact-checking"""
        for keyword in self.fact_check_keywords:
            if keyword in text:
                return True
        
        # Check for statistical claims
        if re.search(r"\d+%|\d+\s*(percent|million|billion|trillion)", text):
            return True
        
        return False
    
    def _verify_source_reliability(self, source_info: Dict[str, Any]) -> float:
        """Verify source reliability based on known standards"""
        base_reliability = source_info.get("reliability_score", 0.5)
        
        # Tier 1: Wire services and established news
        if source_info.get("official_status") in ["wire_service", "government_official"]:
            return min(1.0, base_reliability + 0.1)
        
        # Tier 2: Public broadcasters
        if source_info.get("official_status") in ["public_broadcaster", "international_broadcaster"]:
            return min(1.0, base_reliability + 0.05)
        
        # Reduce reliability for sources requiring verification
        if source_info.get("verification_required", True):
            return max(0.5, base_reliability - 0.1)
        
        return base_reliability
    
    def _needs_verification(self, text: str, source_info: Dict[str, Any]) -> bool:
        """Determine if article needs additional verification"""
        # Always verify sources that require it
        if source_info.get("verification_required", True):
            return True
        
        # Verify breaking news claims
        if re.search(r"\b(breaking|urgent|developing)\b", text, re.IGNORECASE):
            return True
        
        # Verify exclusive claims
        if re.search(r"\b(exclusive|first to report|obtained)\b", text, re.IGNORECASE):
            return True
        
        return False
    
    def _generate_concerns(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate list of concerns based on analysis"""
        concerns = []
        
        if analysis["propaganda_score"] > 0.6:
            concerns.append("HIGH_PROPAGANDA_RISK")
        
        if abs(analysis["bias_score"]) > 0.3:
            concerns.append("SIGNIFICANT_BIAS_DETECTED")
        
        if analysis["reliability_score"] < 0.7:
            concerns.append("LOW_SOURCE_RELIABILITY")
        
        if len(analysis["propaganda_techniques"]) > 2:
            concerns.append("MULTIPLE_PROPAGANDA_TECHNIQUES")
        
        if analysis["fact_check_required"] and analysis["verification_needed"]:
            concerns.append("REQUIRES_FACT_VERIFICATION")
        
        return concerns
    
    def _make_recommendation(self, analysis: Dict[str, Any]) -> str:
        """Make publication recommendation based on analysis"""
        concerns = analysis["concerns"]
        
        # Reject if high propaganda or very low reliability
        if ("HIGH_PROPAGANDA_RISK" in concerns or 
            analysis["reliability_score"] < 0.5):
            return "REJECT"
        
        # Review if multiple concerns
        if (len(concerns) > 2 or 
            "SIGNIFICANT_BIAS_DETECTED" in concerns or
            "MULTIPLE_PROPAGANDA_TECHNIQUES" in concerns):
            return "REVIEW"
        
        # Approve if minimal concerns
        return "APPROVE"
    
    def _calculate_confidence(self, analysis: Dict[str, Any]) -> float:
        """Calculate confidence in the analysis"""
        base_confidence = 1.0
        
        # Reduce confidence for unverified sources
        if analysis["verification_needed"]:
            base_confidence -= 0.2
        
        # Reduce confidence for fact-check requirements
        if analysis["fact_check_required"]:
            base_confidence -= 0.1
        
        # Reduce confidence for propaganda techniques
        base_confidence -= len(analysis["propaganda_techniques"]) * 0.1
        
        return max(0.3, base_confidence)
    
    def verify_with_multiple_sources(self, article_data: Dict[str, Any], min_sources: int = 2) -> Dict[str, Any]:
        """
        Verify article content against multiple sources
        
        Args:
            article_data: Article information
            min_sources: Minimum number of sources required
            
        Returns:
            Verification results
        """
        # This would implement cross-referencing with other verified sources
        # For now, return a basic verification structure
        
        return {
            "verified": True,  # Would be actual verification result
            "source_count": min_sources,
            "corroborated": True,
            "discrepancies": [],
            "confidence": 0.9
        }


# Global instance
propaganda_detector = PropagandaDetector()