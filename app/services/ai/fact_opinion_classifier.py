"""
Fact vs Opinion classification using simple rule-based logic (Mock implementation for demo)
"""

import logging
import asyncio
import re
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class FactOpinionClassifier:
    """
    Classify text segments as factual statements or opinions (Mock implementation for demo)
    """
    
    def __init__(self):
        self._fact_indicators = self._load_fact_indicators()
        self._opinion_indicators = self._load_opinion_indicators()
        
    async def _load_models(self):
        """Mock model loading - no actual models needed"""
        logger.info("Mock fact/opinion classification models loaded")
        await asyncio.sleep(0.1)  # Simulate loading time
    
    def _load_fact_indicators(self) -> Dict[str, List[str]]:
        """Load indicators that suggest factual content"""
        return {
            'verifiable_claims': [
                # Numbers and statistics
                r'\d+%', r'\d+\.\d+%', r'\$\d+', r'\d+ million', r'\d+ billion',
                r'\d+ thousand', r'\d+ percent', r'rate of \d+',
                
                # Dates and times
                r'\d{4}', r'in \d{4}', r'since \d{4}', r'by \d{4}',
                r'january|february|march|april|may|june|july|august|september|october|november|december',
                r'monday|tuesday|wednesday|thursday|friday|saturday|sunday',
                
                # Measurements
                r'\d+ degrees', r'\d+ miles', r'\d+ kilometers', r'\d+ hours',
                r'\d+ minutes', r'\d+ seconds', r'\d+ years', r'\d+ months'
            ],
            'attribution_phrases': [
                'according to', 'reported by', 'study shows', 'research indicates',
                'data suggests', 'survey found', 'analysis reveals', 'statistics show',
                'census data', 'government report', 'official statement', 'court documents',
                'police report', 'medical records', 'scientific study', 'peer-reviewed'
            ],
            'factual_verbs': [
                'occurred', 'happened', 'took place', 'resulted in', 'caused',
                'led to', 'produced', 'created', 'established', 'founded',
                'built', 'constructed', 'developed', 'discovered', 'invented',
                'announced', 'declared', 'stated', 'confirmed', 'verified'
            ],
            'objective_language': [
                'the report states', 'the document shows', 'the evidence indicates',
                'the investigation found', 'the analysis concluded', 'the study determined',
                'measurements indicate', 'observations show', 'records demonstrate'
            ]
        }
    
    def _load_opinion_indicators(self) -> Dict[str, List[str]]:
        """Load indicators that suggest opinion content"""
        return {
            'subjective_language': [
                'i think', 'i believe', 'i feel', 'in my opinion', 'it seems',
                'appears to be', 'looks like', 'sounds like', 'feels like',
                'my view', 'my perspective', 'personally', 'subjectively'
            ],
            'evaluative_adjectives': [
                'good', 'bad', 'excellent', 'terrible', 'amazing', 'awful',
                'wonderful', 'horrible', 'great', 'poor', 'outstanding', 'disappointing',
                'impressive', 'disgusting', 'beautiful', 'ugly', 'smart', 'stupid',
                'brilliant', 'foolish', 'wise', 'naive', 'sophisticated', 'primitive'
            ],
            'modal_verbs': [
                'should', 'would', 'could', 'might', 'may', 'must',
                'ought to', 'supposed to', 'expected to', 'likely to'
            ],
            'opinion_starters': [
                'arguably', 'presumably', 'supposedly', 'allegedly', 'apparently',
                'seemingly', 'probably', 'possibly', 'potentially', 'conceivably',
                'theoretically', 'hypothetically', 'presumably', 'ostensibly'
            ],
            'value_judgments': [
                'important', 'significant', 'crucial', 'essential', 'vital',
                'necessary', 'unnecessary', 'pointless', 'worthwhile', 'valuable',
                'worthless', 'meaningful', 'meaningless', 'relevant', 'irrelevant'
            ]
        }
    
    async def calculate_fact_opinion_ratio(self, text: str) -> float:
        """
        Calculate the ratio of factual content to opinion content
        
        Returns:
            Float between 0.0 (all opinion) and 1.0 (all factual)
        """
        await self._load_models()
        
        # Split text into sentences for analysis
        sentences = self._split_into_sentences(text)
        if not sentences:
            return 0.5  # Neutral if no sentences
        
        factual_scores = []
        for sentence in sentences:
            score = await self._classify_sentence(sentence)
            factual_scores.append(score)
        
        # Calculate average factual score
        avg_factual_score = sum(factual_scores) / len(factual_scores)
        
        return max(0.0, min(1.0, avg_factual_score))
    
    async def _classify_sentence(self, sentence: str) -> float:
        """
        Classify a single sentence as factual or opinion
        
        Returns:
            Float between 0.0 (opinion) and 1.0 (factual)
        """
        # Combine multiple classification approaches
        pattern_score = self._analyze_linguistic_patterns(sentence)
        structure_score = self._analyze_sentence_structure(sentence)
        content_score = await self._analyze_content_features(sentence)
        
        # Weighted combination
        combined_score = (
            pattern_score * 0.4 +
            structure_score * 0.3 +
            content_score * 0.3
        )
        
        return max(0.0, min(1.0, combined_score))
    
    def _analyze_linguistic_patterns(self, sentence: str) -> float:
        """Analyze linguistic patterns that indicate facts vs opinions"""
        sentence_lower = sentence.lower()
        word_count = len(sentence.split())
        
        # Count fact indicators
        fact_score = 0
        for category, patterns in self._fact_indicators.items():
            for pattern in patterns:
                if isinstance(pattern, str):
                    if pattern in sentence_lower:
                        fact_score += 1
                else:  # regex pattern
                    matches = len(re.findall(pattern, sentence_lower))
                    fact_score += matches
        
        # Count opinion indicators
        opinion_score = 0
        for category, patterns in self._opinion_indicators.items():
            for pattern in patterns:
                if pattern in sentence_lower:
                    opinion_score += 1
        
        # Normalize scores
        total_score = fact_score + opinion_score
        if total_score == 0:
            return 0.5  # Neutral
        
        # Return ratio of fact indicators to total indicators
        return fact_score / total_score
    
    def _analyze_sentence_structure(self, sentence: str) -> float:
        """Analyze sentence structure for factual vs opinion indicators (simplified mock)"""
        sentence_lower = sentence.lower()
        
        factual_features = 0
        opinion_features = 0
        
        # Simple pattern matching instead of spaCy
        # Numbers and dates indicate factual content
        import re
        if re.search(r'\d+', sentence):
            factual_features += 1
        if re.search(r'\b\d{4}\b', sentence):  # Years
            factual_features += 1
        if re.search(r'\$\d+', sentence):  # Money
            factual_features += 1
        
        # First person pronouns indicate opinion
        if re.search(r'\bi\b|\bmy\b|\bme\b', sentence_lower):
            opinion_features += 1
        
        # Modal verbs indicate opinion
        if re.search(r'\bshould\b|\bwould\b|\bcould\b|\bmight\b|\bmay\b', sentence_lower):
            opinion_features += 1
        
        # Evaluative adjectives indicate opinion
        evaluative_adj = ['good', 'bad', 'excellent', 'terrible', 'amazing', 'awful', 'great', 'poor']
        for adj in evaluative_adj:
            if adj in sentence_lower:
                opinion_features += 1
                break
        
        # Calculate ratio
        total_features = factual_features + opinion_features
        if total_features == 0:
            return 0.5
        
        return factual_features / total_features
    
    async def _analyze_content_features(self, sentence: str) -> float:
        """Analyze content-level features using simple pattern matching"""
        try:
            sentence_lower = sentence.lower()
            
            # Check for objective reporting language
            objective_patterns = [
                'said', 'stated', 'announced', 'reported', 'according to',
                'confirmed', 'revealed', 'showed', 'indicated', 'found'
            ]
            
            # Check for subjective language
            subjective_patterns = [
                'believe', 'think', 'feel', 'seem', 'appear', 'look',
                'probably', 'likely', 'possibly', 'should', 'would'
            ]
            
            objective_count = sum(1 for pattern in objective_patterns if pattern in sentence_lower)
            subjective_count = sum(1 for pattern in subjective_patterns if pattern in sentence_lower)
            
            if objective_count + subjective_count == 0:
                return 0.5
            
            return objective_count / (objective_count + subjective_count)
            
        except Exception as e:
            logger.warning(f"Error in content analysis: {str(e)}")
            return 0.5
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences for individual analysis"""
        # Simple sentence splitting - could be improved with better tokenization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
        return sentences
    
    async def get_detailed_analysis(self, text: str) -> Dict[str, any]:
        """
        Get detailed fact/opinion analysis of text
        
        Returns comprehensive breakdown of factual vs opinion content
        """
        await self._load_models()
        
        sentences = self._split_into_sentences(text)
        
        analysis = {
            'overall_ratio': 0.0,
            'sentence_breakdown': [],
            'fact_indicators': {
                'verifiable_claims': 0,
                'attribution_phrases': 0,
                'objective_language': 0,
                'dates_numbers': 0
            },
            'opinion_indicators': {
                'subjective_language': 0,
                'evaluative_adjectives': 0,
                'modal_verbs': 0,
                'first_person': 0
            },
            'recommendations': []
        }
        
        sentence_scores = []
        
        for i, sentence in enumerate(sentences):
            score = await self._classify_sentence(sentence)
            sentence_scores.append(score)
            
            analysis['sentence_breakdown'].append({
                'sentence': sentence,
                'factual_score': score,
                'classification': 'factual' if score > 0.6 else 'opinion' if score < 0.4 else 'mixed'
            })
        
        # Calculate overall ratio
        if sentence_scores:
            analysis['overall_ratio'] = sum(sentence_scores) / len(sentence_scores)
        
        # Count specific indicators
        text_lower = text.lower()
        
        for category, patterns in self._fact_indicators.items():
            count = 0
            for pattern in patterns:
                if isinstance(pattern, str):
                    count += text_lower.count(pattern)
                else:
                    count += len(re.findall(pattern, text_lower))
            analysis['fact_indicators'][category] = count
        
        for category, patterns in self._opinion_indicators.items():
            count = sum(1 for pattern in patterns if pattern in text_lower)
            analysis['opinion_indicators'][category] = count
        
        # Generate recommendations
        if analysis['overall_ratio'] < 0.3:
            analysis['recommendations'].append("Article is heavily opinion-based. Consider adding more factual evidence.")
        elif analysis['overall_ratio'] > 0.8:
            analysis['recommendations'].append("Article is very factual. Consider if context or analysis would be helpful.")
        
        return analysis