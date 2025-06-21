"""
Political bias detection using NLP and machine learning
"""

import logging
import asyncio
import re
from typing import Dict, List, Tuple, Optional
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np

logger = logging.getLogger(__name__)


class PoliticalBiasDetector:
    """
    Detect political bias in news articles using multiple approaches
    """
    
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self._emotion_classifier = None
        self._tokenizer = None
        self._bias_keywords = self._load_bias_keywords()
        self._political_entities = self._load_political_entities()
        
    async def _load_models(self):
        """Load transformer models for bias detection"""
        if self._emotion_classifier is None:
            logger.info("Loading political bias detection models...")
            
            loop = asyncio.get_event_loop()
            
            # Load emotion classifier which can help detect biased language
            self._emotion_classifier = await loop.run_in_executor(
                None,
                lambda: pipeline(
                    "text-classification",
                    model="j-hartmann/emotion-english-distilroberta-base",
                    device=self.device,
                    return_all_scores=True
                )
            )
            
            logger.info("Political bias detection models loaded")
    
    def _load_bias_keywords(self) -> Dict[str, List[str]]:
        """Load political bias keywords categorized by leaning"""
        return {
            'conservative_positive': [
                'traditional values', 'law and order', 'personal responsibility',
                'free market', 'constitutional rights', 'family values',
                'fiscal responsibility', 'strong defense', 'limited government'
            ],
            'conservative_negative': [
                'liberal agenda', 'big government', 'tax and spend',
                'activist judges', 'welfare state', 'political correctness',
                'mainstream media bias', 'government overreach'
            ],
            'liberal_positive': [
                'social justice', 'equality', 'progressive values',
                'civil rights', 'environmental protection', 'healthcare for all',
                'worker rights', 'diversity and inclusion', 'social safety net'
            ],
            'liberal_negative': [
                'corporate greed', 'income inequality', 'systemic racism',
                'climate denial', 'voter suppression', 'right-wing extremism',
                'corporate welfare', 'plutocracy'
            ],
            'loaded_language': [
                'radical', 'extremist', 'socialist', 'fascist', 'communist',
                'terrorist', 'thug', 'elite', 'establishment', 'corrupt',
                'crooked', 'rigged', 'fake news', 'alternative facts'
            ]
        }
    
    def _load_political_entities(self) -> Dict[str, str]:
        """Load political entities and their general associations"""
        return {
            # Political parties
            'democratic party': 'left',
            'republican party': 'right',
            'democrats': 'left',
            'republicans': 'right',
            'gop': 'right',
            
            # Political figures (examples - would be expanded)
            'joe biden': 'left',
            'donald trump': 'right',
            'nancy pelosi': 'left',
            'mitch mcconnell': 'right',
            
            # Media outlets
            'fox news': 'right',
            'cnn': 'left',
            'msnbc': 'left',
            'breitbart': 'right',
            'huffington post': 'left',
            'wall street journal': 'center-right',
            'new york times': 'center-left',
            
            # Think tanks and organizations
            'heritage foundation': 'right',
            'cato institute': 'right',
            'aclu': 'left',
            'nra': 'right',
            'planned parenthood': 'left'
        }
    
    async def analyze_political_bias(self, text: str) -> float:
        """
        Analyze political bias in text
        
        Returns:
            Float between -1.0 (left-leaning) and 1.0 (right-leaning), 0.0 is neutral
        """
        await self._load_models()
        
        # Combine multiple bias detection methods
        keyword_bias = self._analyze_keyword_bias(text)
        entity_bias = self._analyze_entity_bias(text)
        language_bias = await self._analyze_language_patterns(text)
        emotional_bias = await self._analyze_emotional_bias(text)
        
        # Weighted combination of different approaches
        combined_bias = (
            keyword_bias * 0.3 +
            entity_bias * 0.2 +
            language_bias * 0.3 +
            emotional_bias * 0.2
        )
        
        # Ensure result is within bounds
        return max(-1.0, min(1.0, combined_bias))
    
    def _analyze_keyword_bias(self, text: str) -> float:
        """Analyze bias based on political keywords"""
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Count occurrences of different keyword categories
        conservative_positive = sum(1 for phrase in self._bias_keywords['conservative_positive'] 
                                  if phrase in text_lower)
        conservative_negative = sum(1 for phrase in self._bias_keywords['conservative_negative'] 
                                  if phrase in text_lower)
        liberal_positive = sum(1 for phrase in self._bias_keywords['liberal_positive'] 
                             if phrase in text_lower)
        liberal_negative = sum(1 for phrase in self._bias_keywords['liberal_negative'] 
                             if phrase in text_lower)
        loaded_language = sum(1 for phrase in self._bias_keywords['loaded_language'] 
                            if phrase in text_lower)
        
        # Calculate bias scores
        conservative_score = (conservative_positive + liberal_negative) / max(word_count / 100, 1)
        liberal_score = (liberal_positive + conservative_negative) / max(word_count / 100, 1)
        
        # Apply penalty for loaded language
        loaded_penalty = loaded_language / max(word_count / 100, 1)
        
        # Calculate net bias
        net_bias = (conservative_score - liberal_score) * (1 + loaded_penalty * 0.5)
        
        return max(-1.0, min(1.0, net_bias))
    
    def _analyze_entity_bias(self, text: str) -> float:
        """Analyze bias based on political entities mentioned"""
        text_lower = text.lower()
        
        left_mentions = 0
        right_mentions = 0
        
        for entity, leaning in self._political_entities.items():
            if entity in text_lower:
                # Analyze context around the entity
                context_sentiment = self._analyze_entity_context(text_lower, entity)
                
                if leaning == 'left':
                    left_mentions += context_sentiment
                elif leaning == 'right':
                    right_mentions += context_sentiment
                elif leaning == 'center-left':
                    left_mentions += context_sentiment * 0.5
                elif leaning == 'center-right':
                    right_mentions += context_sentiment * 0.5
        
        total_mentions = abs(left_mentions) + abs(right_mentions)
        if total_mentions == 0:
            return 0.0
        
        # Calculate bias based on mention sentiment
        entity_bias = (right_mentions - left_mentions) / total_mentions
        
        return max(-1.0, min(1.0, entity_bias))
    
    def _analyze_entity_context(self, text: str, entity: str) -> float:
        """Analyze sentiment context around political entities"""
        # Find entity position in text
        entity_pos = text.find(entity)
        if entity_pos == -1:
            return 0.0
        
        # Extract context window (50 characters before and after)
        start = max(0, entity_pos - 50)
        end = min(len(text), entity_pos + len(entity) + 50)
        context = text[start:end]
        
        # Simple sentiment analysis of context
        positive_words = ['praised', 'successful', 'effective', 'strong', 'good', 'excellent']
        negative_words = ['criticized', 'failed', 'weak', 'bad', 'terrible', 'corrupt']
        
        positive_count = sum(1 for word in positive_words if word in context)
        negative_count = sum(1 for word in negative_words if word in context)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)
    
    async def _analyze_language_patterns(self, text: str) -> float:
        """Analyze language patterns that indicate bias"""
        # Check for biased language patterns
        patterns = {
            'right_leaning': [
                r'liberal\s+media', r'mainstream\s+media', r'fake\s+news',
                r'radical\s+left', r'socialist\s+agenda', r'deep\s+state',
                r'law\s+and\s+order', r'traditional\s+values'
            ],
            'left_leaning': [
                r'right[\s-]wing\s+extremism', r'corporate\s+greed', r'systemic\s+racism',
                r'climate\s+change\s+denial', r'voter\s+suppression',
                r'social\s+justice', r'income\s+inequality'
            ]
        }
        
        text_lower = text.lower()
        right_patterns = sum(1 for pattern in patterns['right_leaning'] 
                           if re.search(pattern, text_lower))
        left_patterns = sum(1 for pattern in patterns['left_leaning'] 
                          if re.search(pattern, text_lower))
        
        total_patterns = right_patterns + left_patterns
        if total_patterns == 0:
            return 0.0
        
        return (right_patterns - left_patterns) / total_patterns
    
    async def _analyze_emotional_bias(self, text: str) -> float:
        """Analyze emotional language that might indicate bias"""
        try:
            # Truncate text for model
            max_length = 512
            if len(text.split()) > max_length:
                text = ' '.join(text.split()[:max_length])
            
            # Get emotion classification
            loop = asyncio.get_event_loop()
            emotions = await loop.run_in_executor(
                None,
                lambda: self._emotion_classifier(text)
            )
            
            # Map emotions to potential bias indicators
            emotion_scores = {emotion['label']: emotion['score'] for emotion in emotions[0]}
            
            # Anger and disgust often indicate bias
            bias_emotions = emotion_scores.get('anger', 0) + emotion_scores.get('disgust', 0)
            neutral_emotions = emotion_scores.get('neutral', 0) + emotion_scores.get('joy', 0)
            
            # Higher emotional charge suggests potential bias
            emotional_bias_strength = bias_emotions - neutral_emotions
            
            # This doesn't indicate direction, just presence of emotional bias
            # Direction would need additional context analysis
            return emotional_bias_strength * 0.5  # Scale down the impact
            
        except Exception as e:
            logger.error(f"Error in emotional bias analysis: {str(e)}")
            return 0.0
    
    async def detect_bias_indicators(self, text: str) -> Dict[str, any]:
        """
        Detect specific bias indicators in text
        
        Returns detailed analysis of bias indicators found
        """
        await self._load_models()
        
        indicators = {
            'loaded_language': [],
            'political_entities': [],
            'emotional_language': False,
            'one_sided_sources': [],
            'opinion_vs_fact_ratio': 0.0
        }
        
        text_lower = text.lower()
        
        # Find loaded language
        for phrase in self._bias_keywords['loaded_language']:
            if phrase in text_lower:
                indicators['loaded_language'].append(phrase)
        
        # Find political entities
        for entity, leaning in self._political_entities.items():
            if entity in text_lower:
                indicators['political_entities'].append({
                    'entity': entity,
                    'leaning': leaning,
                    'context_sentiment': self._analyze_entity_context(text_lower, entity)
                })
        
        # Check for emotional language
        try:
            emotions = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._emotion_classifier(text[:512])
            )
            emotion_scores = {emotion['label']: emotion['score'] for emotion in emotions[0]}
            indicators['emotional_language'] = (
                emotion_scores.get('anger', 0) + emotion_scores.get('disgust', 0) > 0.3
            )
        except:
            pass
        
        # Check for one-sided source attribution
        source_patterns = [
            r'according to.*democrats?', r'according to.*republicans?',
            r'democrats? said', r'republicans? said',
            r'liberal.*claims?', r'conservative.*claims?'
        ]
        
        for pattern in source_patterns:
            if re.search(pattern, text_lower):
                indicators['one_sided_sources'].append(pattern)
        
        return indicators