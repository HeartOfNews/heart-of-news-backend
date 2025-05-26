"""
Configuration for news sources
"""

import uuid
from typing import Dict, List, Any

# Default sources configuration - Focus on EU and USA political news
DEFAULT_SOURCES = [
    # === USA POLITICAL NEWS ===
    
    # Associated Press - USA Politics
    {
        "id": str(uuid.uuid4()),
        "name": "Associated Press - US Politics",
        "url": "https://apnews.com/hub/politics",
        "type": "rss",
        "feed_url": "https://apnews.com/index.rss",
        "article_selector": ".FeedCard a, .CardHeadline a",
        "content_selector": ".Article, article, .RichTextStoryBody",
        "reliability_score": 0.95,
        "bias_score": 0.0,
        "categories": ["Politics", "USA"],
        "priority": "high"
    },
    
    # Reuters - US Politics
    {
        "id": str(uuid.uuid4()),
        "name": "Reuters - US Politics",
        "url": "https://www.reuters.com/world/us/",
        "type": "rss",
        "feed_url": "https://www.reuters.com/politics/feed/",
        "article_selector": "article, .StandardArticle_content",
        "reliability_score": 0.9,
        "bias_score": 0.0,
        "categories": ["Politics", "USA"],
        "priority": "high"
    },
    
    # Politico - US Politics
    {
        "id": str(uuid.uuid4()),
        "name": "Politico",
        "url": "https://www.politico.com",
        "type": "rss",
        "feed_url": "https://www.politico.com/rss/politicopicks.xml",
        "article_selector": ".story-text",
        "reliability_score": 0.85,
        "bias_score": -0.1,
        "categories": ["Politics", "USA"],
        "priority": "high"
    },
    
    # The Hill - US Politics
    {
        "id": str(uuid.uuid4()),
        "name": "The Hill",
        "url": "https://thehill.com/news/",
        "type": "rss",
        "feed_url": "https://thehill.com/news/feed/",
        "article_selector": ".field-name-body",
        "reliability_score": 0.8,
        "bias_score": 0.0,
        "categories": ["Politics", "USA"],
        "priority": "high"
    },
    
    # === EUROPEAN UNION NEWS ===
    
    # Euronews
    {
        "id": str(uuid.uuid4()),
        "name": "Euronews",
        "url": "https://www.euronews.com",
        "type": "rss",
        "feed_url": "https://www.euronews.com/rss?format=mrss",
        "article_selector": ".c-article-content",
        "reliability_score": 0.85,
        "bias_score": 0.0,
        "categories": ["Politics", "European Union", "Europe"],
        "priority": "high"
    },
    
    # Politico Europe
    {
        "id": str(uuid.uuid4()),
        "name": "Politico Europe",
        "url": "https://www.politico.eu",
        "type": "rss",
        "feed_url": "https://www.politico.eu/feed/",
        "article_selector": ".story-text",
        "reliability_score": 0.85,
        "bias_score": 0.0,
        "categories": ["Politics", "European Union", "Europe"],
        "priority": "high"
    },
    
    # EurActiv
    {
        "id": str(uuid.uuid4()),
        "name": "EurActiv",
        "url": "https://www.euractiv.com",
        "type": "rss",
        "feed_url": "https://www.euractiv.com/feed/",
        "article_selector": ".ea-article-body",
        "reliability_score": 0.8,
        "bias_score": 0.0,
        "categories": ["Politics", "European Union", "Europe"],
        "priority": "high"
    },
    
    # EU Observer
    {
        "id": str(uuid.uuid4()),
        "name": "EU Observer",
        "url": "https://euobserver.com",
        "type": "rss",
        "feed_url": "https://euobserver.com/rss",
        "article_selector": ".article-content",
        "reliability_score": 0.8,
        "bias_score": 0.0,
        "categories": ["Politics", "European Union", "Europe"],
        "priority": "high"
    },
    
    # === GLOBAL POLITICAL CONTEXT ===
    
    # BBC News - Politics
    {
        "id": str(uuid.uuid4()),
        "name": "BBC News - Politics",
        "url": "https://www.bbc.com/news/politics",
        "type": "rss",
        "feed_url": "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "article_selector": ".article__body-content",
        "reliability_score": 0.9,
        "bias_score": 0.0,
        "categories": ["Politics", "Global"],
        "priority": "medium"
    },
    
    # Financial Times - Politics
    {
        "id": str(uuid.uuid4()),
        "name": "Financial Times - Politics",
        "url": "https://www.ft.com/world/us",
        "type": "rss",
        "feed_url": "https://www.ft.com/politics?format=rss",
        "article_selector": ".article__content-body",
        "reliability_score": 0.9,
        "bias_score": 0.0,
        "categories": ["Politics", "Economics"],
        "priority": "medium"
    },
    
    # CNN Politics
    {
        "id": str(uuid.uuid4()),
        "name": "CNN Politics",
        "url": "https://www.cnn.com/politics",
        "type": "rss",
        "feed_url": "http://rss.cnn.com/rss/edition.rss",
        "article_selector": ".zn-body__paragraph",
        "reliability_score": 0.75,
        "bias_score": -0.2,
        "categories": ["Politics", "USA"],
        "priority": "medium"
    }
]

def get_default_sources() -> List[Dict[str, Any]]:
    """
    Get the default sources configuration
    
    Returns:
        List of source configurations
    """
    return DEFAULT_SOURCES

def get_sources_by_bias(bias_range: tuple = None) -> List[Dict[str, Any]]:
    """
    Get sources filtered by bias score range
    
    Args:
        bias_range: Tuple of (min_bias, max_bias)
            Bias scores range from -1.0 (extreme left) to 1.0 (extreme right)
            
    Returns:
        List of source configurations
    """
    if bias_range is None:
        return DEFAULT_SOURCES
    
    min_bias, max_bias = bias_range
    
    return [
        source for source in DEFAULT_SOURCES
        if min_bias <= source.get("bias_score", 0) <= max_bias
    ]

def get_sources_by_reliability(min_reliability: float = 0.0) -> List[Dict[str, Any]]:
    """
    Get sources filtered by minimum reliability score
    
    Args:
        min_reliability: Minimum reliability score (0.0 to 1.0)
            
    Returns:
        List of source configurations
    """
    return [
        source for source in DEFAULT_SOURCES
        if source.get("reliability_score", 0) >= min_reliability
    ]