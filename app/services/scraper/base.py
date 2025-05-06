"""
Base scraper service for retrieving news articles
"""

import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)

class ArticleData(BaseModel):
    """Data structure for scraped articles"""
    url: HttpUrl
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.name = source_config.get("name", "Unknown Source")
        self.source_url = source_config.get("url")
        self.source_id = source_config.get("id")
    
    @abstractmethod
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """Fetch articles from the source"""
        pass
    
    @abstractmethod
    async def fetch_article_content(self, article_url: str) -> Optional[ArticleData]:
        """Fetch full content for a specific article"""
        pass
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content by removing ads, navigation, etc."""
        # This would contain HTML cleaning logic
        # For now it's a placeholder
        return html_content
    
    def _extract_published_date(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract and parse published date from various formats"""
        # This would contain date parsing logic
        # For now it's a placeholder
        return datetime.utcnow()