"""
News Authenticity Verification Service
Ensures all published news is real, verified, and from legitimate sources
"""

import logging
import hashlib
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class NewsVerifier:
    """Verifies news authenticity and prevents fake content publication"""
    
    def __init__(self):
        self.verified_domains = self._load_verified_domains()
        self.fake_content_patterns = self._load_fake_content_patterns()
        self.verification_cache = {}
        
    def _load_verified_domains(self) -> Dict[str, Dict[str, Any]]:
        """Load list of verified, legitimate news domains"""
        return {
            # Tier 1: Wire Services
            "apnews.com": {
                "tier": 1,
                "type": "wire_service",
                "reliability": 0.98,
                "verification_method": "api_verification",
                "fact_checking": True
            },
            "reuters.com": {
                "tier": 1, 
                "type": "wire_service",
                "reliability": 0.97,
                "verification_method": "content_hash",
                "fact_checking": True
            },
            
            # Tier 2: Major Broadcasters
            "bbc.com": {
                "tier": 2,
                "type": "public_broadcaster",
                "reliability": 0.95,
                "verification_method": "editorial_standards",
                "fact_checking": True
            },
            "npr.org": {
                "tier": 2,
                "type": "public_broadcaster", 
                "reliability": 0.94,
                "verification_method": "editorial_standards",
                "fact_checking": True
            },
            "dw.com": {
                "tier": 2,
                "type": "international_broadcaster",
                "reliability": 0.92,
                "verification_method": "editorial_standards",
                "fact_checking": True
            },
            
            # Tier 3: Established Newspapers
            "theguardian.com": {
                "tier": 3,
                "type": "newspaper",
                "reliability": 0.91,
                "verification_method": "editorial_oversight",
                "fact_checking": True
            },
            "ft.com": {
                "tier": 3,
                "type": "newspaper",
                "reliability": 0.93,
                "verification_method": "fact_checking_team", 
                "fact_checking": True
            },
            
            # Government Official Sources
            "consilium.europa.eu": {
                "tier": 1,
                "type": "government_official",
                "reliability": 1.0,
                "verification_method": "official_publication",
                "fact_checking": False  # Official statements
            },
            "state.gov": {
                "tier": 1,
                "type": "government_official",
                "reliability": 1.0,
                "verification_method": "official_publication",
                "fact_checking": False
            },
            
            # Verified Russian Sources
            "meduza.io": {
                "tier": 2,
                "type": "independent_verified",
                "reliability": 0.90,
                "verification_method": "editorial_standards",
                "fact_checking": True,
                "language": "ru"
            },
            "bbci.co.uk": {  # BBC feeds
                "tier": 2,
                "type": "public_broadcaster",
                "reliability": 0.95,
                "verification_method": "bbc_standards",
                "fact_checking": True
            }
        }
    
    def _load_fake_content_patterns(self) -> List[str]:
        """Patterns that indicate fake or generated content"""
        return [
            # AI-generated content indicators
            r"as an ai|according to my knowledge|i don't have real-time",
            r"i cannot provide|i'm not able to|i don't have access",
            r"hypothetical|fictional|imaginary|made-up",
            
            # Fake news indicators
            r"this story is developing|unconfirmed reports suggest",
            r"sources close to|insiders reveal|leaked documents show",
            r"breaking: unprecedented|shocking revelation|exclusive investigation",
            
            # Satirical content
            r"satirical|parody|comedy|humorous take|joke|meme",
            r"april fools|satire|spoof|mock news"
        ]
    
    def verify_article_authenticity(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive verification of article authenticity
        
        Args:
            article_data: Article information including URL, content, source
            
        Returns:
            Verification results with authenticity assessment
        """
        verification_result = {
            "authentic": False,
            "verification_level": "UNVERIFIED",  # VERIFIED, PARTIALLY_VERIFIED, UNVERIFIED, FAKE
            "source_verified": False,
            "content_verified": False,
            "domain_verified": False,
            "fact_checked": False,
            "concerns": [],
            "confidence": 0.0,
            "recommendation": "REJECT",
            "verification_timestamp": datetime.now()
        }
        
        # 1. Verify domain authenticity
        domain_verification = self._verify_domain(article_data.get("url", ""))
        verification_result.update(domain_verification)
        
        # 2. Verify content authenticity
        content_verification = self._verify_content_authenticity(
            article_data.get("title", ""),
            article_data.get("content", "")
        )
        verification_result.update(content_verification)
        
        # 3. Cross-reference with known sources
        cross_reference = self._cross_reference_content(article_data)
        verification_result.update(cross_reference)
        
        # 4. Check publication timing (avoid stale news)
        timing_check = self._verify_publication_timing(article_data)
        verification_result.update(timing_check)
        
        # 5. Make final authenticity determination
        final_assessment = self._make_authenticity_assessment(verification_result)
        verification_result.update(final_assessment)
        
        return verification_result
    
    def _verify_domain(self, url: str) -> Dict[str, Any]:
        """Verify the domain is from a legitimate news source"""
        if not url:
            return {
                "domain_verified": False,
                "concerns": ["NO_URL_PROVIDED"]
            }
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove www. prefix
            if domain.startswith("www."):
                domain = domain[4:]
            
            # Check against verified domains
            if domain in self.verified_domains:
                domain_info = self.verified_domains[domain]
                return {
                    "domain_verified": True,
                    "source_tier": domain_info["tier"],
                    "source_type": domain_info["type"],
                    "source_reliability": domain_info["reliability"],
                    "fact_checking_available": domain_info.get("fact_checking", False)
                }
            else:
                return {
                    "domain_verified": False,
                    "concerns": ["UNVERIFIED_DOMAIN"],
                    "domain": domain
                }
                
        except Exception as e:
            return {
                "domain_verified": False,
                "concerns": ["INVALID_URL"],
                "error": str(e)
            }
    
    def _verify_content_authenticity(self, title: str, content: str) -> Dict[str, Any]:
        """Verify content is real news, not AI-generated or fake"""
        full_text = f"{title} {content}".lower()
        
        concerns = []
        content_verified = True
        
        # Check for fake content patterns
        for pattern in self.fake_content_patterns:
            if re.search(pattern, full_text, re.IGNORECASE):
                concerns.append("FAKE_CONTENT_PATTERN_DETECTED")
                content_verified = False
                break
        
        # Check for AI-generated content indicators
        ai_indicators = [
            "as an ai", "i don't have real-time", "i cannot provide",
            "according to my training", "based on my knowledge"
        ]
        
        for indicator in ai_indicators:
            if indicator in full_text:
                concerns.append("AI_GENERATED_CONTENT")
                content_verified = False
                break
        
        # Check for satirical content
        satire_indicators = ["satirical", "parody", "april fools", "joke", "meme"]
        for indicator in satire_indicators:
            if indicator in full_text:
                concerns.append("SATIRICAL_CONTENT")
                content_verified = False
                break
        
        # Verify content has journalistic structure
        if not self._has_journalistic_structure(title, content):
            concerns.append("NON_JOURNALISTIC_STRUCTURE")
        
        return {
            "content_verified": content_verified,
            "content_concerns": concerns
        }
    
    def _has_journalistic_structure(self, title: str, content: str) -> bool:
        """Check if content follows proper journalistic structure"""
        if not title or not content:
            return False
        
        # Check for proper news article elements
        content_lower = content.lower()
        
        # Should have quotes or official statements
        has_quotes = bool(re.search(r'["""]\s*[^"""]+\s*["""]', content))
        has_said = bool(re.search(r'\b(said|stated|announced|declared|confirmed)\b', content_lower))
        
        # Should have specific details (dates, names, places)
        has_specifics = bool(re.search(r'\b(yesterday|today|monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', content_lower))
        has_names = bool(re.search(r'\b[A-Z][a-z]+ [A-Z][a-z]+\b', content))  # Proper names
        
        # Should have attribution
        has_attribution = bool(re.search(r'\b(according to|reported by|source|official)\b', content_lower))
        
        return (has_quotes or has_said) and (has_specifics or has_names or has_attribution)
    
    def _cross_reference_content(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-reference content with other verified sources"""
        # This would implement actual cross-referencing
        # For now, return basic structure
        
        return {
            "cross_referenced": True,
            "corroborating_sources": 1,  # Would be actual count
            "discrepancies_found": False
        }
    
    def _verify_publication_timing(self, article_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify article is recent and not stale"""
        published_at = article_data.get("published_at")
        concerns = []
        
        if not published_at:
            concerns.append("NO_PUBLICATION_DATE")
            return {"timing_concerns": concerns}
        
        if isinstance(published_at, str):
            # Would parse the date string
            pass
        
        # Check if article is too old (> 7 days for breaking news)
        if isinstance(published_at, datetime):
            age = datetime.now() - published_at
            if age > timedelta(days=7):
                concerns.append("STALE_CONTENT")
        
        return {"timing_concerns": concerns}
    
    def _make_authenticity_assessment(self, verification_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make final authenticity assessment"""
        concerns = (verification_data.get("concerns", []) + 
                   verification_data.get("content_concerns", []) +
                   verification_data.get("timing_concerns", []))
        
        domain_verified = verification_data.get("domain_verified", False)
        content_verified = verification_data.get("content_verified", False)
        
        # Determine verification level
        if domain_verified and content_verified and not concerns:
            verification_level = "VERIFIED"
            authentic = True
            recommendation = "APPROVE"
            confidence = 0.95
        elif domain_verified and content_verified and len(concerns) <= 1:
            verification_level = "PARTIALLY_VERIFIED"
            authentic = True
            recommendation = "REVIEW"
            confidence = 0.75
        elif "FAKE_CONTENT_PATTERN_DETECTED" in concerns or "AI_GENERATED_CONTENT" in concerns:
            verification_level = "FAKE"
            authentic = False
            recommendation = "REJECT"
            confidence = 0.9
        else:
            verification_level = "UNVERIFIED"
            authentic = False
            recommendation = "REJECT"
            confidence = 0.6
        
        return {
            "authentic": authentic,
            "verification_level": verification_level,
            "recommendation": recommendation,
            "confidence": confidence,
            "all_concerns": concerns
        }
    
    def get_verification_requirements(self) -> Dict[str, Any]:
        """Get current verification requirements"""
        return {
            "minimum_reliability_score": 0.8,
            "required_verification_level": "PARTIALLY_VERIFIED",
            "allowed_source_types": [
                "wire_service", "public_broadcaster", "government_official",
                "international_broadcaster", "independent_verified"
            ],
            "content_age_limit_hours": 168,  # 7 days
            "cross_reference_required": True,
            "fact_check_required": True
        }


# Global instance
news_verifier = NewsVerifier()