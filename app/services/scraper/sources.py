"""
Configuration for news sources
"""

import uuid
from typing import Dict, List, Any

# Default sources configuration
DEFAULT_SOURCES = [
    # Example of an RSS-based source
    {
        "id": str(uuid.uuid4()),
        "name": "Reuters",
        "url": "https://www.reuters.com",
        "type": "rss",
        "feed_url": "https://www.reuters.com/sitemap_news.xml",
        "article_selector": "article, .StandardArticle_content, .ArticleBody_body",
        "reliability_score": 0.85,
        "bias_score": 0.1,  # 0 = neutral
    },
    
    # Example of another RSS-based source
    {
        "id": str(uuid.uuid4()),
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "type": "rss",
        "feed_url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "article_selector": ".article__body-content, .story-body__inner",
        "reliability_score": 0.9,
        "bias_score": 0.05,  # slightly left-leaning but fairly neutral
    },
    
    # Example of a web-based source
    {
        "id": str(uuid.uuid4()),
        "name": "The Associated Press",
        "url": "https://apnews.com",
        "type": "web",
        "article_selector": ".cards a, .FeedCard a, .CardHeadline a",
        "content_selector": ".Article, article, .RichTextStoryBody",
        "title_selector": "h1",
        "date_selector": "time, .Timestamp",
        "reliability_score": 0.95,
        "bias_score": 0.0,  # very neutral
    },
    
    # Example of another web-based source
    {
        "id": str(uuid.uuid4()),
        "name": "The Washington Post",
        "url": "https://www.washingtonpost.com",
        "type": "web",
        "article_selector": ".story-headline a, .headline a, .card-heading a",
        "content_selector": ".article-content, .article-body",
        "title_selector": "h1[data-qa='headline'], h1.font--headline",
        "date_selector": ".display-date",
        "author_selector": ".author-name, .author-names",
        "reliability_score": 0.8,
        "bias_score": -0.3,  # somewhat left-leaning
    },
    
    # Example of a right-leaning source
    {
        "id": str(uuid.uuid4()),
        "name": "Fox News",
        "url": "https://www.foxnews.com",
        "type": "rss",
        "feed_url": "https://moxie.foxnews.com/feedburner/latest.xml",
        "article_selector": ".article-body, .article-content",
        "reliability_score": 0.7,
        "bias_score": 0.4,  # right-leaning
    },
    
    # Example of a left-leaning source
    {
        "id": str(uuid.uuid4()),
        "name": "MSNBC",
        "url": "https://www.msnbc.com",
        "type": "web",
        "article_selector": ".article a, .cd__headline a",
        "content_selector": ".article-body, .article__body",
        "reliability_score": 0.7,
        "bias_score": -0.4,  # left-leaning
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