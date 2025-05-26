"""
Verified Official News Sources Configuration
Only includes legitimate, verified news organizations with high reliability
"""

import uuid
from typing import Dict, List, Any

# VERIFIED OFFICIAL NEWS SOURCES - Only legitimate news organizations
VERIFIED_SOURCES = [
    # === TIER 1: WIRE SERVICES (Highest Reliability) ===
    
    # Associated Press (Primary wire service)
    {
        "id": str(uuid.uuid4()),
        "name": "Associated Press",
        "url": "https://apnews.com",
        "type": "rss",
        "feed_url": "https://apnews.com/index.rss",
        "api_endpoint": "https://apnews.com/api/v2/search",
        "verification_required": True,
        "reliability_score": 0.98,
        "bias_score": 0.0,  # Neutral
        "categories": ["Politics", "International", "Breaking"],
        "fact_check_required": True,
        "official_status": "wire_service",
        "verification_method": "api_key_required"
    },
    
    # Reuters (International wire service)
    {
        "id": str(uuid.uuid4()),
        "name": "Reuters",
        "url": "https://www.reuters.com",
        "type": "rss", 
        "feed_url": "https://www.reuters.com/politics/feed/",
        "verification_required": True,
        "reliability_score": 0.97,
        "bias_score": 0.0,
        "categories": ["Politics", "International", "Economics"],
        "fact_check_required": True,
        "official_status": "wire_service",
        "verification_method": "content_verification"
    },
    
    # === TIER 2: MAJOR BROADCASTERS ===
    
    # BBC News (British public broadcaster)
    {
        "id": str(uuid.uuid4()),
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "type": "rss",
        "feed_url": "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "verification_required": True,
        "reliability_score": 0.95,
        "bias_score": 0.0,
        "categories": ["Politics", "International"],
        "fact_check_required": True,
        "official_status": "public_broadcaster",
        "verification_method": "editorial_standards"
    },
    
    # NPR (US public radio)
    {
        "id": str(uuid.uuid4()),
        "name": "NPR",
        "url": "https://www.npr.org",
        "type": "rss",
        "feed_url": "https://feeds.npr.org/1001/rss.xml",
        "verification_required": True,
        "reliability_score": 0.94,
        "bias_score": -0.1,  # Slight left lean but factual
        "categories": ["Politics", "USA"],
        "fact_check_required": True,
        "official_status": "public_broadcaster",
        "verification_method": "editorial_standards"
    },
    
    # === TIER 3: ESTABLISHED NEWSPAPERS ===
    
    # The Guardian (UK)
    {
        "id": str(uuid.uuid4()),
        "name": "The Guardian",
        "url": "https://www.theguardian.com",
        "type": "rss",
        "feed_url": "https://www.theguardian.com/world/rss",
        "verification_required": True,
        "reliability_score": 0.92,
        "bias_score": -0.2,  # Left-leaning but factual
        "categories": ["Politics", "International"],
        "fact_check_required": True,
        "official_status": "established_newspaper",
        "verification_method": "editorial_oversight"
    },
    
    # Financial Times (UK business)
    {
        "id": str(uuid.uuid4()),
        "name": "Financial Times",
        "url": "https://www.ft.com",
        "type": "rss",
        "feed_url": "https://www.ft.com/politics?format=rss",
        "verification_required": True,
        "reliability_score": 0.93,
        "bias_score": 0.1,  # Slight business-conservative lean
        "categories": ["Politics", "Economics"],
        "fact_check_required": True,
        "official_status": "established_newspaper",
        "verification_method": "fact_checking_team"
    },
    
    # === GOVERNMENT SOURCES (Official Statements Only) ===
    
    # European Council
    {
        "id": str(uuid.uuid4()),
        "name": "European Council",
        "url": "https://www.consilium.europa.eu",
        "type": "rss",
        "feed_url": "https://www.consilium.europa.eu/en/press/press-releases/rss/",
        "verification_required": False,  # Official government source
        "reliability_score": 1.0,  # Official statements
        "bias_score": 0.0,  # Factual but institutional perspective
        "categories": ["Politics", "European Union"],
        "fact_check_required": False,  # Official source
        "official_status": "government_official",
        "verification_method": "official_publication"
    },
    
    # US State Department
    {
        "id": str(uuid.uuid4()),
        "name": "US State Department",
        "url": "https://www.state.gov",
        "type": "rss",
        "feed_url": "https://www.state.gov/rss/",
        "verification_required": False,  # Official government source
        "reliability_score": 1.0,
        "bias_score": 0.0,  # US government perspective
        "categories": ["Politics", "USA", "International"],
        "fact_check_required": False,
        "official_status": "government_official",
        "verification_method": "official_publication"
    }
]

# RUSSIAN VERIFIED SOURCES
VERIFIED_RUSSIAN_SOURCES = [
    # === INDEPENDENT VERIFIED SOURCES ===
    
    # Meduza (Latvia-based, verified independent)
    {
        "id": str(uuid.uuid4()),
        "name": "Медуза",
        "name_en": "Meduza",
        "url": "https://meduza.io",
        "type": "rss",
        "feed_url": "https://meduza.io/rss/all",
        "verification_required": True,
        "reliability_score": 0.90,
        "bias_score": -0.1,
        "categories": ["Политика", "Россия"],
        "fact_check_required": True,
        "official_status": "independent_verified",
        "verification_method": "editorial_standards",
        "language": "ru"
    },
    
    # BBC Russian Service (Verified international)
    {
        "id": str(uuid.uuid4()),
        "name": "BBC Русская служба",
        "name_en": "BBC Russian",
        "url": "https://www.bbc.com/russian",
        "type": "rss", 
        "feed_url": "https://feeds.bbci.co.uk/russian/rss.xml",
        "verification_required": True,
        "reliability_score": 0.95,
        "bias_score": 0.0,
        "categories": ["Политика", "Международные отношения"],
        "fact_check_required": True,
        "official_status": "international_broadcaster",
        "verification_method": "bbc_editorial_standards",
        "language": "ru"
    },
    
    # Deutsche Welle Russian (Verified international)
    {
        "id": str(uuid.uuid4()),
        "name": "Deutsche Welle на русском",
        "name_en": "DW Russian",
        "url": "https://www.dw.com/ru",
        "type": "rss",
        "feed_url": "https://rss.dw.com/rdf/rss-ru-all",
        "verification_required": True,
        "reliability_score": 0.92,
        "bias_score": 0.0,
        "categories": ["Политика", "Европа"],
        "fact_check_required": True,
        "official_status": "international_broadcaster",
        "verification_method": "dw_editorial_standards",
        "language": "ru"
    }
]

def get_verified_sources() -> List[Dict[str, Any]]:
    """Get only verified, legitimate news sources"""
    return VERIFIED_SOURCES

def get_verified_russian_sources() -> List[Dict[str, Any]]:
    """Get only verified Russian-language sources"""
    return VERIFIED_RUSSIAN_SOURCES

def get_tier_one_sources() -> List[Dict[str, Any]]:
    """Get highest reliability sources (wire services)"""
    return [
        source for source in VERIFIED_SOURCES
        if source.get("official_status") == "wire_service"
    ]

def get_government_sources() -> List[Dict[str, Any]]:
    """Get official government sources only"""
    return [
        source for source in VERIFIED_SOURCES
        if source.get("official_status") == "government_official"
    ]

def get_sources_requiring_verification() -> List[Dict[str, Any]]:
    """Get sources that require additional fact-checking"""
    return [
        source for source in VERIFIED_SOURCES + VERIFIED_RUSSIAN_SOURCES
        if source.get("verification_required", True)
    ]

# Content verification patterns
PROPAGANDA_INDICATORS = [
    # Emotional manipulation
    "sensational_language", "emotional_appeals", "fear_mongering",
    # Logical fallacies
    "ad_hominem", "strawman", "false_dichotomy", "cherry_picking",
    # Bias indicators
    "loaded_language", "selective_facts", "omitted_context",
    # Misinformation patterns
    "unverified_claims", "anonymous_sources", "correlation_causation"
]

VERIFICATION_REQUIREMENTS = {
    "minimum_sources": 2,  # Require corroboration
    "fact_check_apis": [
        "factcheck.org",
        "snopes.com", 
        "politifact.com"
    ],
    "cross_reference_required": True,
    "government_verification": True,
    "bias_score_threshold": 0.3  # Maximum acceptable bias
}