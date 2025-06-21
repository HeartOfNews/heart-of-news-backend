"""
Propaganda technique detection using NLP and pattern matching
"""

import logging
import re
import asyncio
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
import spacy

logger = logging.getLogger(__name__)


class PropagandaTechniqueDetector:
    """
    Detect propaganda techniques in news articles based on established taxonomies
    """
    
    def __init__(self):
        self._nlp = None
        self._propaganda_patterns = self._load_propaganda_patterns()
        
    async def _load_models(self):
        """Load NLP models for propaganda detection"""
        if self._nlp is None:
            try:
                loop = asyncio.get_event_loop()
                self._nlp = await loop.run_in_executor(
                    None,
                    lambda: spacy.load("en_core_web_sm")
                )
            except OSError:
                logger.warning("spaCy model not found. Some features will be limited.")
                self._nlp = None
    
    def _load_propaganda_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Load patterns for detecting propaganda techniques"""
        return {
            'loaded_language': {
                'description': 'Using words/phrases with strong positive or negative connotations',
                'patterns': [
                    # Negative loaded terms
                    r'\b(terrorist|thug|criminal|extremist|radical|fanatic)\b',
                    r'\b(corrupt|crooked|dishonest|lying|fake)\b',
                    r'\b(destroy|devastate|attack|assault|invasion)\b',
                    
                    # Positive loaded terms
                    r'\b(hero|patriot|defender|champion|savior)\b',
                    r'\b(brilliant|genius|outstanding|exceptional)\b',
                    r'\b(freedom|liberty|justice|democracy)\b'
                ],
                'severity': 'medium'
            },
            
            'name_calling': {
                'description': 'Using negative labels to discredit opponents',
                'patterns': [
                    r'\b(socialist|communist|fascist|nazi)\b(?! party)',
                    r'\b(libtard|conservatard|trumptard)\b',
                    r'\b(snowflake|deplorable|elite|establishment)\b',
                    r'\b(puppet|stooge|shill|mouthpiece)\b'
                ],
                'severity': 'high'
            },
            
            'glittering_generalities': {
                'description': 'Using vague, emotionally appealing words without substance',
                'patterns': [
                    r'\b(freedom|liberty|democracy|justice)\b.*\b(for all|always|never)\b',
                    r'\b(real|true|authentic)\b.*\b(american|patriot|citizen)\b',
                    r'\b(common sense|traditional values|family values)\b',
                    r'\b(hope and change|make.*great again)\b'
                ],
                'severity': 'medium'
            },
            
            'transfer': {
                'description': 'Associating something with positive/negative symbols or concepts',
                'patterns': [
                    r'\b(founding fathers|constitution|flag)\b',
                    r'\b(hitler|nazi|stalin|communist)\b.*\b(like|similar|reminiscent)\b',
                    r'\b(godless|ungodly|evil|satanic)\b',
                    r'\b(blessed|righteous|holy|sacred)\b'
                ],
                'severity': 'medium'
            },
            
            'fear_appeal': {
                'description': 'Creating fear to persuade audience',
                'patterns': [
                    r'\b(crisis|disaster|catastrophe|emergency)\b',
                    r'\b(dangerous|threat|risk|peril|doom)\b',
                    r'\b(destroy|annihilate|eliminate|wipe out)\b',
                    r'\b(if we don\'t|unless we|before it\'s too late)\b'
                ],
                'severity': 'high'
            },
            
            'bandwagon': {
                'description': 'Appealing to the desire to follow the crowd',
                'patterns': [
                    r'\b(everyone knows|everybody agrees|most people)\b',
                    r'\b(join the movement|be part of|don\'t be left behind)\b',
                    r'\b(all Americans|every citizen|the people demand)\b',
                    r'\b(overwhelming support|massive backing|unprecedented)\b'
                ],
                'severity': 'medium'
            },
            
            'plain_folks': {
                'description': 'Appealing to ordinary people',
                'patterns': [
                    r'\b(ordinary people|working families|common folk)\b',
                    r'\b(just like you|one of us|regular guy)\b',
                    r'\b(hardworking|middle class|everyday)\b',
                    r'\b(Main Street|small town|grassroots)\b'
                ],
                'severity': 'low'
            },
            
            'card_stacking': {
                'description': 'Presenting only evidence that supports one side',
                'patterns': [
                    r'\b(studies show|experts agree|science proves)\b(?!.*but|however|although)',
                    r'\b(clearly|obviously|undoubtedly|without question)\b',
                    r'\b(the facts are|the truth is|reality is)\b',
                    r'\b(all evidence|every study|unanimous)\b'
                ],
                'severity': 'high'
            },
            
            'testimonial': {
                'description': 'Using celebrity or authority endorsements',
                'patterns': [
                    r'\b(endorsed by|supported by|backed by)\b.*\b(celebrity|star|famous)\b',
                    r'\b(expert|professor|doctor)\b.*\b(says|believes|supports)\b',
                    r'\b(Nobel Prize|PhD|credentials)\b'
                ],
                'severity': 'low'
            },
            
            'false_dilemma': {
                'description': 'Presenting only two options when more exist',
                'patterns': [
                    r'\b(either.*or|you\'re either|only two choices)\b',
                    r'\b(with us or against us|love it or leave it)\b',
                    r'\b(black and white|no middle ground|simple choice)\b'
                ],
                'severity': 'medium'
            },
            
            'red_herring': {
                'description': 'Introducing irrelevant information to distract',
                'patterns': [
                    r'\b(but what about|speaking of|by the way)\b',
                    r'\b(the real issue|more importantly|meanwhile)\b',
                    r'\b(let\'s not forget|remember when|years ago)\b'
                ],
                'severity': 'medium'
            },
            
            'ad_hominem': {
                'description': 'Attacking the person rather than their argument',
                'patterns': [
                    r'\b(hypocrite|liar|fraud|incompetent)\b',
                    r'\b(can\'t be trusted|history of|track record)\b',
                    r'\b(personal life|private affairs|character flaws)\b'
                ],
                'severity': 'high'
            },
            
            'appeal_to_authority': {
                'description': 'Using authority figures to support claims',
                'patterns': [
                    r'\b(according to experts|scientists say|doctors recommend)\b',
                    r'\b(government officials|authorities|specialists)\b',
                    r'\b(leading researchers|top scientists|renowned)\b'
                ],
                'severity': 'low'
            }
        }
    
    async def detect_propaganda_techniques(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect propaganda techniques in text
        
        Returns:
            List of detected techniques with details
        """
        await self._load_models()
        
        detected_techniques = []
        text_lower = text.lower()
        
        for technique_name, technique_data in self._propaganda_patterns.items():
            matches = []
            
            for pattern in technique_data['patterns']:
                regex_matches = list(re.finditer(pattern, text_lower, re.IGNORECASE))
                for match in regex_matches:
                    matches.append({
                        'text': text[match.start():match.end()],
                        'start': match.start(),
                        'end': match.end(),
                        'context': self._extract_context(text, match.start(), match.end())
                    })
            
            if matches:
                detected_techniques.append({
                    'technique': technique_name,
                    'description': technique_data['description'],
                    'severity': technique_data['severity'],
                    'matches': matches,
                    'count': len(matches),
                    'confidence': self._calculate_confidence(technique_name, matches, text)
                })
        
        # Sort by severity and count
        severity_order = {'high': 3, 'medium': 2, 'low': 1}
        detected_techniques.sort(
            key=lambda x: (severity_order.get(x['severity'], 0), x['count']),
            reverse=True
        )
        
        return detected_techniques
    
    def _extract_context(self, text: str, start: int, end: int, context_size: int = 50) -> str:
        """Extract context around a match"""
        context_start = max(0, start - context_size)
        context_end = min(len(text), end + context_size)
        context = text[context_start:context_end]
        
        # Add ellipsis if truncated
        if context_start > 0:
            context = "..." + context
        if context_end < len(text):
            context = context + "..."
        
        return context.strip()
    
    def _calculate_confidence(self, technique: str, matches: List[Dict], text: str) -> float:
        """Calculate confidence score for detected technique"""
        if not matches:
            return 0.0
        
        # Base confidence on pattern strength and context
        base_confidence = 0.6
        
        # Adjust based on number of matches
        match_bonus = min(len(matches) * 0.1, 0.3)
        
        # Adjust based on text length (more reliable in longer texts)
        length_factor = min(len(text) / 1000, 1.0) * 0.1
        
        # Technique-specific adjustments
        technique_adjustments = {
            'name_calling': 0.2,
            'fear_appeal': 0.15,
            'card_stacking': 0.1,
            'ad_hominem': 0.2,
            'plain_folks': -0.1,  # Common in legitimate news too
            'testimonial': -0.05
        }
        
        technique_adjustment = technique_adjustments.get(technique, 0.0)
        
        confidence = base_confidence + match_bonus + length_factor + technique_adjustment
        return min(max(confidence, 0.0), 1.0)
    
    async def analyze_propaganda_density(self, text: str) -> Dict[str, Any]:
        """
        Analyze overall propaganda density in text
        
        Returns comprehensive propaganda analysis
        """
        techniques = await self.detect_propaganda_techniques(text)
        
        if not techniques:
            return {
                'overall_score': 0.0,
                'risk_level': 'low',
                'technique_count': 0,
                'high_severity_count': 0,
                'recommendations': []
            }
        
        # Calculate overall propaganda score
        total_score = 0
        severity_weights = {'high': 1.0, 'medium': 0.6, 'low': 0.3}
        
        high_severity_count = 0
        for technique in techniques:
            weight = severity_weights.get(technique['severity'], 0.5)
            confidence = technique['confidence']
            count = min(technique['count'], 5)  # Cap to prevent single technique dominance
            
            technique_score = weight * confidence * (1 + count * 0.2)
            total_score += technique_score
            
            if technique['severity'] == 'high':
                high_severity_count += 1
        
        # Normalize score
        max_possible_score = len(self._propaganda_patterns) * 1.5
        overall_score = min(total_score / max_possible_score, 1.0)
        
        # Determine risk level
        if overall_score < 0.2:
            risk_level = 'low'
        elif overall_score < 0.5:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # Generate recommendations
        recommendations = self._generate_recommendations(techniques, overall_score)
        
        return {
            'overall_score': overall_score,
            'risk_level': risk_level,
            'technique_count': len(techniques),
            'high_severity_count': high_severity_count,
            'techniques_detected': [t['technique'] for t in techniques[:5]],  # Top 5
            'recommendations': recommendations
        }
    
    def _generate_recommendations(self, techniques: List[Dict], overall_score: float) -> List[str]:
        """Generate recommendations based on detected propaganda"""
        recommendations = []
        
        if overall_score > 0.7:
            recommendations.append("High propaganda content detected. Exercise extreme caution.")
        elif overall_score > 0.4:
            recommendations.append("Moderate propaganda techniques detected. Verify claims independently.")
        
        # Technique-specific recommendations
        technique_counts = defaultdict(int)
        for technique in techniques:
            technique_counts[technique['technique']] += 1
        
        if technique_counts['fear_appeal'] > 0:
            recommendations.append("Fear-based appeals detected. Consider emotional manipulation.")
        
        if technique_counts['card_stacking'] > 0:
            recommendations.append("One-sided evidence presentation detected. Seek alternative perspectives.")
        
        if technique_counts['name_calling'] > 0:
            recommendations.append("Ad hominem attacks detected. Focus on facts rather than personal attacks.")
        
        if technique_counts['false_dilemma'] > 0:
            recommendations.append("False choices presented. Look for additional options and nuance.")
        
        if not recommendations:
            recommendations.append("Low propaganda content. Article appears relatively objective.")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    async def get_technique_explanations(self) -> Dict[str, str]:
        """Get explanations of all propaganda techniques"""
        return {
            name: data['description'] 
            for name, data in self._propaganda_patterns.items()
        }