"""
Sentiment analysis service using transformers
"""

import logging
from typing import Dict, List, Optional, Tuple
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import asyncio
from functools import lru_cache

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Advanced sentiment analysis using pre-trained transformer models
    """
    
    def __init__(self, model_name: str = "cardiffnlp/twitter-roberta-base-sentiment-latest"):
        """
        Initialize the sentiment analyzer
        
        Args:
            model_name: HuggingFace model name for sentiment analysis
        """
        self.model_name = model_name
        self.device = 0 if torch.cuda.is_available() else -1
        self._pipeline = None
        self._tokenizer = None
        
    async def _load_models(self):
        """Load models asynchronously"""
        if self._pipeline is None:
            logger.info(f"Loading sentiment analysis model: {self.model_name}")
            
            # Run model loading in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            self._pipeline = await loop.run_in_executor(
                None,
                lambda: pipeline(
                    "sentiment-analysis",
                    model=self.model_name,
                    device=self.device,
                    return_all_scores=True
                )
            )
            
            self._tokenizer = await loop.run_in_executor(
                None,
                lambda: AutoTokenizer.from_pretrained(self.model_name)
            )
            
            logger.info("Sentiment analysis model loaded successfully")
    
    async def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with sentiment scores (negative, neutral, positive)
        """
        await self._load_models()
        
        try:
            # Truncate text if too long for the model
            max_length = self._tokenizer.model_max_length - 2  # Account for special tokens
            tokens = self._tokenizer.encode(text, add_special_tokens=False)
            if len(tokens) > max_length:
                tokens = tokens[:max_length]
                text = self._tokenizer.decode(tokens)
            
            # Run inference in thread pool
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                None,
                lambda: self._pipeline(text)
            )
            
            # Convert results to standardized format
            sentiment_scores = {}
            for result in results[0]:  # Pipeline returns list of lists
                label = result['label'].lower()
                score = result['score']
                
                # Map common label variants to standard names
                if label in ['negative', 'neg']:
                    sentiment_scores['negative'] = score
                elif label in ['positive', 'pos']:
                    sentiment_scores['positive'] = score
                elif label in ['neutral', 'neu']:
                    sentiment_scores['neutral'] = score
            
            # Ensure all required keys exist
            for key in ['negative', 'neutral', 'positive']:
                if key not in sentiment_scores:
                    sentiment_scores[key] = 0.0
            
            return sentiment_scores
            
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