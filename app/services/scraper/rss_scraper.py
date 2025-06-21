"""
RSS feed scraper implementation
"""

import logging
import aiohttp
import feedparser
from datetime import datetime
from typing import Dict, List, Optional, Any
from dateutil import parser as date_parser

from app.services.scraper.base import BaseScraper, ArticleData

logger = logging.getLogger(__name__)


class RSSFeedScraper(BaseScraper):
    """Scraper for RSS/Atom feeds"""
    
    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url")
        if not self.feed_url:
            raise ValueError("RSS scraper requires feed_url in source config")
    
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """Fetch articles from RSS feed"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch RSS feed {self.feed_url}: {response.status}")
                        return []
                    
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    articles = []
                    for entry in feed.entries[:limit]:
                        article_data = self._parse_rss_entry(entry)
                        if article_data:
                            articles.append(article_data)
                    
                    logger.info(f"Fetched {len(articles)} articles from {self.name}")
                    return articles
                    
        except Exception as e:
            logger.error(f"Error fetching articles from {self.name}: {str(e)}")
            return []
    
    async def fetch_article_content(self, article_url: str) -> Optional[ArticleData]:
        """Fetch full content for a specific article"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(article_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch article {article_url}: {response.status}")
                        return None
                    
                    content = await response.text()
                    # Here you would parse the HTML content to extract the article text
                    # For now, return basic data
                    return ArticleData(
                        url=article_url,
                        title="Article Title",  # Would be extracted from HTML
                        content=self._clean_html(content),
                        summary=None,
                        published_at=datetime.utcnow(),
                        author=None,
                        image_url=None,
                        tags=None,
                        metadata={"scraped_at": datetime.utcnow().isoformat()}
                    )
                    
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {str(e)}")
            return None
    
    def _parse_rss_entry(self, entry) -> Optional[ArticleData]:
        """Parse a single RSS entry into ArticleData"""
        try:
            # Extract basic information
            title = getattr(entry, 'title', 'No Title')
            url = getattr(entry, 'link', '')
            summary = getattr(entry, 'summary', getattr(entry, 'description', ''))
            
            if not url:
                logger.warning(f"RSS entry missing URL: {title}")
                return None
            
            # Parse published date
            published_at = None
            if hasattr(entry, 'published'):
                try:
                    published_at = date_parser.parse(entry.published)
                except Exception as e:
                    logger.warning(f"Failed to parse date {entry.published}: {e}")
            elif hasattr(entry, 'updated'):
                try:
                    published_at = date_parser.parse(entry.updated)
                except Exception as e:
                    logger.warning(f"Failed to parse date {entry.updated}: {e}")
            
            # Extract author
            author = None
            if hasattr(entry, 'author'):
                author = entry.author
            elif hasattr(entry, 'authors') and entry.authors:
                author = entry.authors[0].get('name', '')
            
            # Extract image URL
            image_url = None
            if hasattr(entry, 'media_content') and entry.media_content:
                image_url = entry.media_content[0].get('url')
            elif hasattr(entry, 'enclosures') and entry.enclosures:
                for enclosure in entry.enclosures:
                    if enclosure.type and enclosure.type.startswith('image/'):
                        image_url = enclosure.href
                        break
            
            # Extract tags
            tags = []
            if hasattr(entry, 'tags'):
                tags = [tag.term for tag in entry.tags]
            
            return ArticleData(
                url=url,
                title=title,
                content=None,  # Will be fetched separately if needed
                summary=summary,
                published_at=published_at,
                author=author,
                image_url=image_url,
                tags=tags,
                metadata={
                    "source": self.name,
                    "source_id": self.source_id,
                    "scraped_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error parsing RSS entry: {str(e)}")
            return None