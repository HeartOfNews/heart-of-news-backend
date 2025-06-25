"""
Sentiment analysis service using transformers (Mock implementation for demo)
"""

import logging
import re
import random
from typing import Dict, List, Optional, Tuple
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Mock sentiment analysis for demo (simplified rule-based implementation)
    """
    
    def __init__(self, model_name: str = "mock-sentiment-model"):
        """
        Initialize the sentiment analyzer
        
        Args:
            model_name: Mock model name for demo
        """
        self.model_name = model_name
        self._positive_words = [
            'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic',
            'positive', 'love', 'like', 'enjoy', 'happy', 'pleased', 'satisfied'
        ]
        self._negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate', 'dislike', 'angry',
            'sad', 'disappointed', 'frustrated', 'annoyed', 'upset', 'worried'
        ]
        
    async def _load_models(self):
        """Mock model loading"""
        logger.info(f"Mock sentiment analysis model loaded: {self.model_name}")
        await asyncio.sleep(0.1)  # Simulate loading time
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text (mock implementation)
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores (negative, neutral, positive)
        """
        await self._load_models()
        
        try:
            text_lower = text.lower()
            words = text_lower.split()
            
            positive_count = sum(1 for word in words if word in self._positive_words)
            negative_count = sum(1 for word in words if word in self._negative_words)
            total_sentiment_words = positive_count + negative_count
            
            if total_sentiment_words == 0:
                # Neutral text
                return {'negative': 0.2, 'neutral': 0.6, 'positive': 0.2}
            
            # Calculate basic sentiment scores
            positive_ratio = positive_count / len(words)
            negative_ratio = negative_count / len(words)
            
            # Normalize scores
            base_neutral = 0.4
            positive_score = min(positive_ratio * 3, 0.8)
            negative_score = min(negative_ratio * 3, 0.8)
            neutral_score = max(base_neutral - (positive_score + negative_score) / 2, 0.1)
            
            # Ensure scores sum to approximately 1
            total = positive_score + negative_score + neutral_score
            return {
                'positive': round(positive_score / total, 3),
                'negative': round(negative_score / total, 3),
                'neutral': round(neutral_score / total, 3)
            }
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            return {'negative': 0.33, 'neutral': 0.34, 'positive': 0.33}
    
    async def analyze_emotional_intensity(self, text: str) -> float:
        """
        Analyze emotional intensity of text
        
        Returns:
            Float between 0.0 (neutral) and 1.0 (highly emotional)
        """
        sentiment_scores = await self.analyze_sentiment(text)
        
        # Calculate emotional intensity as deviation from neutral
        neutral_score = sentiment_scores.get('neutral', 0.0)
        emotional_intensity = 1.0 - neutral_score
        
        return min(max(emotional_intensity, 0.0), 1.0)
    
    async def detect_emotional_language_patterns(self, text: str) -> Dict[str, float]:
        """
        Detect specific emotional language patterns
        
        Returns:
            Dictionary with scores for different emotional categories
        """
        # Emotional keywords and phrases
        emotional_patterns = {
            'anger': [
                'outrageous', 'disgusting', 'appalling', 'furious', 'rage',
                'infuriating', 'shocking', 'scandal', 'betrayal', 'corrupt'
            ],
            'fear': [
                'terrifying', 'dangerous', 'threat', 'crisis', 'disaster',
                'catastrophe', 'panic', 'alarming', 'scary', 'devastating'
            ],
            'excitement': [
                'amazing', 'incredible', 'fantastic', 'extraordinary', 'breakthrough',
                'revolutionary', 'spectacular', 'thrilling', 'stunning', 'remarkable'
            ],
            'urgency': [
                'urgent', 'immediate', 'critical', 'emergency', 'must',
                'now', 'quickly', 'deadline', 'hurry', 'rush'
            ]
        }
        
        text_lower = text.lower()
        word_count = len(text.split())
        
        pattern_scores = {}
        for category, keywords in emotional_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower)
            # Normalize by text length
            pattern_scores[category] = min(matches / max(word_count / 100, 1), 1.0)
        
        return pattern_scores


class EmotionalLanguageDetector:
    """
    Specialized detector for emotional vs factual language
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        
    async def analyze_emotional_language(self, text: str) -> float:
        """
        Analyze how emotional vs factual the language is
        
        Returns:
            Float between 0.0 (purely factual) and 1.0 (highly emotional)
        """
        # Get sentiment analysis
        sentiment_scores = await self.sentiment_analyzer.analyze_sentiment(text)
        emotional_patterns = await self.sentiment_analyzer.detect_emotional_language_patterns(text)
        
        # Calculate base emotional score from sentiment deviation
        neutral_score = sentiment_scores.get('neutral', 0.0)
        sentiment_emotionality = 1.0 - neutral_score
        
        # Calculate pattern-based emotional score
        pattern_emotionality = sum(emotional_patterns.values()) / len(emotional_patterns)
        
        # Detect factual language indicators
        factual_indicators = self._detect_factual_language(text)
        
        # Combine scores with weights
        emotional_score = (
            sentiment_emotionality * 0.4 +
            pattern_emotionality * 0.4 +
            (1.0 - factual_indicators) * 0.2
        )
        
        return min(max(emotional_score, 0.0), 1.0)
    
    def _detect_factual_language(self, text: str) -> float:
        """
        Detect factual language patterns
        
        Returns:
            Float between 0.0 (not factual) and 1.0 (highly factual)
        """
        factual_patterns = [
            # Numbers and statistics
            r'\d+%', r'\d+\.\d+', r'\$\d+', r'\d+ million', r'\d+ billion',
            # Dates and times
            r'\d{4}', r'january|february|march|april|may|june|july|august|september|october|november|december',
            # Attribution and sources
            r'according to', r'reported by', r'study shows', r'research indicates',
            r'data suggests', r'survey found', r'analysis reveals',
            # Factual connectors
            r'because', r'therefore', r'as a result', r'due to', r'caused by',
            # Objective language
            r'the report', r'the study', r'the analysis', r'the data'
        ]
        
        import re
        text_lower = text.lower()
        word_count = len(text.split())
        
        factual_matches = 0
        for pattern in factual_patterns:
            matches = len(re.findall(pattern, text_lower))
            factual_matches += matches
        
        # Normalize by text length
        factual_score = min(factual_matches / max(word_count / 50, 1), 1.0)
        
        return factual_score