"""
Bias detection service for analyzing news articles
"""

import logging
import re
import json
import math
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

# Define numpy-like functions to avoid dependency
def sigmoid(x):
    return 1.0 / (1.0 + math.exp(-x))

logger = logging.getLogger(__name__)

class BiasDetector:
    """
    Service for detecting various types of bias in news articles
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize the bias detector with optional pre-trained model
        """
        self.model_path = model_path or str(Path(__file__).parent / "models")
        self.political_keywords = self._load_political_keywords()
        self.propaganda_patterns = self._load_propaganda_patterns()
        
        # Initialize sentiment word lists
        self.positive_words = set(self._load_word_list("positive_words.txt"))
        self.negative_words = set(self._load_word_list("negative_words.txt"))
        
        logger.info(f"BiasDetector initialized with model path: {self.model_path}")
        
    async def analyze_political_bias(self, text: str) -> float:
        """
        Analyze text for political bias
        
        Returns a float between -1.0 (left-leaning) and 1.0 (right-leaning)
        with 0.0 being neutral
        """
        # Normalize and clean text
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        if word_count == 0:
            return 0.0
            
        # Count occurrences of politically charged terms
        left_count = sum(words.count(word) for word in self.political_keywords["left"])
        right_count = sum(words.count(word) for word in self.political_keywords["right"])
        
        # Calculate normalized scores
        left_score = left_count / word_count
        right_score = right_count / word_count
        
        # Calculate bias as difference between right and left
        # Positive = right leaning, Negative = left leaning
        raw_bias = right_score - left_score
        
        # Apply sigmoid-like function to constrain between -1 and 1
        normalized_bias = 2 * sigmoid(5 * raw_bias) - 1
        
        logger.debug(f"Political bias analysis: {normalized_bias:.2f} (raw={raw_bias:.4f})")
        return normalized_bias
    
    async def analyze_emotional_language(self, text: str) -> float:
        """
        Analyze text for emotional vs. factual language
        
        Returns a float between 0.0 (completely factual) and 
        1.0 (highly emotional)
        """
        # Tokenize and normalize text
        text = text.lower()
        words = re.findall(r'\b\w+\b', text)
        word_count = len(words)
        
        if word_count == 0:
            return 0.5
            
        # Count emotional words (both positive and negative)
        emotional_words = sum(1 for word in words if word in self.positive_words or word in self.negative_words)
        
        # Count intensifiers and superlatives
        intensifiers = sum(words.count(word) for word in [
            "very", "extremely", "incredibly", "absolutely", "completely",
            "totally", "utterly", "really", "definitely", "certainly"
        ])
        
        # Count exclamation marks
        exclamations = text.count('!')
        
        # Calculate emotion score based on multiple factors
        emotional_ratio = emotional_words / word_count
        intensifier_factor = min(1.0, intensifiers / (word_count * 0.05))
        exclamation_factor = min(1.0, exclamations / (word_count * 0.01))
        
        # Combine factors with weights
        emotion_score = (
            emotional_ratio * 0.6 +
            intensifier_factor * 0.25 +
            exclamation_factor * 0.15
        )
        
        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, emotion_score))
    
    async def detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect specific propaganda techniques in the text
        
        Returns a list of detected techniques with confidence scores
        and text spans
        """
        results = []
        
        # Check each propaganda pattern
        for technique, patterns in self.propaganda_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern["regex"], text, re.IGNORECASE)
                
                for match in matches:
                    start, end = match.span()
                    span_text = text[start:end]
                    
                    # Calculate confidence based on match quality and context
                    base_confidence = pattern["base_confidence"]
                    
                    # Adjust confidence based on span length (penalize very short matches)
                    length_factor = min(1.0, len(span_text) / 20.0)
                    
                    # Adjust confidence based on technique prevalence
                    results.append({
                        "technique": technique,
                        "span": (start, end),
                        "text": span_text,
                        "confidence": base_confidence * length_factor,
                        "explanation": pattern["explanation"]
                    })
        
        # Sort by confidence
        results.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Take top 10 most confident matches
        return results[:10]
    
    async def calculate_fact_opinion_ratio(self, text: str) -> float:
        """
        Calculate the ratio of factual statements to opinions
        
        Returns a float between 0.0 (all opinions) and 
        1.0 (all factual statements)
        """
        # Split text into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        if not sentences:
            return 0.5
            
        fact_count = 0
        opinion_count = 0
        
        # Opinion indicators
        opinion_starters = [
            "i think", "i believe", "in my opinion", "i feel", "arguably",
            "probably", "likely", "seems", "appears to", "may be", "might be",
            "could be", "i suspect", "suggests that", "indicates that"
        ]
        
        # Factual indicators
        factual_indicators = [
            "according to", "data shows", "research indicates", "evidence suggests",
            "study found", "reported that", "confirmed that", "revealed that",
            "announced that", "statistics show", "experts state", "demonstrated that"
        ]
        
        for sentence in sentences:
            sentence = sentence.lower().strip()
            
            # Skip very short sentences
            if len(sentence) < 10:
                continue
                
            # Check for opinion indicators
            if any(indicator in sentence for indicator in opinion_starters):
                opinion_count += 1
                continue
                
            # Check for factual indicators
            if any(indicator in sentence for indicator in factual_indicators):
                fact_count += 1
                continue
                
            # Check for first-person pronouns (often indicate opinions)
            if re.search(r'\b(i|we|our|us|my)\b', sentence):
                opinion_count += 0.7
                continue
                
            # Default scoring based on presence of statistics, quotes, etc.
            has_numbers = bool(re.search(r'\d+', sentence))
            has_quotes = bool(re.search(r'["""].*["""]', sentence))
            
            if has_numbers or has_quotes:
                fact_count += 0.8
            else:
                # Assume somewhat factual by default, but less confidence
                fact_count += 0.6
        
        total_scored = fact_count + opinion_count
        if total_scored == 0:
            return 0.5
            
        return fact_count / total_scored
    
    async def get_full_bias_analysis(self, text: str) -> Dict[str, Any]:
        """
        Perform a complete bias analysis of the text
        
        Returns a dictionary with multiple bias metrics
        """
        political_bias = await self.analyze_political_bias(text)
        emotional_language = await self.analyze_emotional_language(text)
        propaganda_techniques = await self.detect_propaganda_techniques(text)
        fact_opinion_ratio = await self.calculate_fact_opinion_ratio(text)
        
        return {
            "political_bias": political_bias,
            "emotional_language": emotional_language,
            "propaganda_techniques": propaganda_techniques,
            "fact_opinion_ratio": fact_opinion_ratio,
            "overall_bias_score": self._calculate_overall_bias(
                political_bias, 
                emotional_language, 
                len(propaganda_techniques), 
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
        political_weight = 0.25
        emotional_weight = 0.25
        propaganda_weight = 0.3
        factual_weight = 0.2
        
        # Normalize political bias to 0-1 range
        political_score = abs(political_bias)
        
        # Apply non-linear scaling to propaganda count
        # Few propaganda techniques -> low score
        # Many propaganda techniques -> high score, but with diminishing returns
        propaganda_score = 1.0 - (1.0 / (1.0 + 0.5 * propaganda_count))
        
        # Invert fact-opinion ratio so higher means more biased
        factual_score = 1.0 - fact_opinion_ratio
        
        # Calculate weighted score
        weighted_score = (
            political_score * political_weight +
            emotional_language * emotional_weight +
            propaganda_score * propaganda_weight +
            factual_score * factual_weight
        )
        
        # Apply sigmoid function to emphasize differences in the middle range
        # and de-emphasize differences at the extremes
        normalized_score = sigmoid(5 * (weighted_score - 0.5))
        
        return normalized_score
        
    def _load_political_keywords(self) -> Dict[str, List[str]]:
        """
        Load political keywords from data files
        """
        try:
            # In a production environment, these would be loaded from files
            # For now, define them inline for development
            return {
                "left": [
                    "progressive", "liberal", "socialism", "equity", "welfare", 
                    "social justice", "regulation", "workers", "union", "public", 
                    "collective", "marginalized", "diversity", "reform", "inclusion",
                    "reproductive rights", "green", "climate", "sustainable"
                ],
                "right": [
                    "conservative", "traditional", "freedom", "liberty", "capitalism",
                    "deregulation", "tax cuts", "private", "individual", "faith",
                    "patriot", "values", "free market", "constitutional", "moral",
                    "defense", "military", "sovereign", "fiscal", "entrepreneur"
                ]
            }
        except Exception as e:
            logger.error(f"Failed to load political keywords: {e}")
            return {"left": [], "right": []}
    
    def _load_propaganda_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Load propaganda detection patterns
        """
        try:
            # In a production environment, these would be loaded from files
            # For now, define them inline for development
            return {
                "name_calling": [
                    {
                        "regex": r'\b(stupid|idiot|dumb|crazy|lazy|corrupt|radical|extremist|fanatic|evil)\b',
                        "base_confidence": 0.7,
                        "explanation": "Uses negative labels to discredit without addressing substance"
                    }
                ],
                "loaded_language": [
                    {
                        "regex": r'\b(disaster|crisis|threat|danger|catastrophe|chaos|devastating|alarming)\b',
                        "base_confidence": 0.6,
                        "explanation": "Uses emotional language to influence audience"
                    }
                ],
                "false_dilemma": [
                    {
                        "regex": r'(either|choose between|only two)\s+.{5,40}\s+(or)\s+.{5,40}',
                        "base_confidence": 0.7,
                        "explanation": "Presents complex issue as having only two possible options"
                    }
                ],
                "bandwagon": [
                    {
                        "regex": r'\b(everyone|everybody|all|most people|the majority)\s+(knows|believes|agrees|thinks|supports|wants)\b',
                        "base_confidence": 0.65,
                        "explanation": "Appeals to popularity rather than merit"
                    }
                ],
                "flag_waving": [
                    {
                        "regex": r'\b(patriotic|patriot|american values|our country|our nation|american people)\b',
                        "base_confidence": 0.5,
                        "explanation": "Appeals to patriotism to justify actions or positions"
                    }
                ],
                "doubt_casting": [
                    {
                        "regex": r'\b(allegedly|so-called|claims to|supposedly|purported)\b',
                        "base_confidence": 0.5,
                        "explanation": "Suggests information is unreliable without evidence"
                    }
                ]
            }
        except Exception as e:
            logger.error(f"Failed to load propaganda patterns: {e}")
            return {}
            
    def _load_word_list(self, filename: str) -> List[str]:
        """
        Load a word list from a file
        """
        try:
            # In a production environment, these would be loaded from files
            # For now, return a small sample list
            if filename == "positive_words.txt":
                return [
                    "good", "great", "excellent", "amazing", "wonderful", "best", 
                    "fantastic", "terrific", "outstanding", "superb", "brilliant", 
                    "perfect", "impressive", "remarkable", "exceptional"
                ]
            elif filename == "negative_words.txt":
                return [
                    "bad", "terrible", "awful", "horrible", "worst", "poor", 
                    "unpleasant", "disappointing", "mediocre", "miserable", "dreadful", 
                    "atrocious", "appalling", "abysmal", "disastrous"
                ]
            else:
                return []
        except Exception as e:
            logger.error(f"Failed to load word list {filename}: {e}")
            return []