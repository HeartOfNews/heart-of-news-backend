"""
Factory for creating scraper instances based on source configuration
"""

import logging
from typing import Dict, Any, Optional

from app.services.scraper.base import BaseScraper
from app.services.scraper.rss_scraper import RSSFeedScraper
from app.services.scraper.web_scraper import WebScraper

logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory for creating appropriate scraper instances"""
    
    SCRAPER_TYPES = {
        'rss': RSSFeedScraper,
        'web': WebScraper,
    }
    
    @classmethod
    def create_scraper(cls, source_config: Dict[str, Any]) -> Optional[BaseScraper]:
        """
        Create a scraper instance based on source configuration
        
        Args:
            source_config: Dictionary containing source configuration including:
                - scraper_type: Type of scraper to use ('rss', 'web')
                - Other scraper-specific configuration
        
        Returns:
            Scraper instance or None if creation fails
        """
        scraper_type = source_config.get('scraper_type', 'rss')
        
        if scraper_type not in cls.SCRAPER_TYPES:
            logger.error(f"Unknown scraper type: {scraper_type}")
            return None
        
        try:
            scraper_class = cls.SCRAPER_TYPES[scraper_type]
            return scraper_class(source_config)
        except Exception as e:
            logger.error(f"Failed to create {scraper_type} scraper: {str(e)}")
            return None
    
    @classmethod
    def get_available_scraper_types(cls) -> list[str]:
        """Get list of available scraper types"""
        return list(cls.SCRAPER_TYPES.keys())


class ScraperManager:
    """Manager for handling multiple scrapers"""
    
    def __init__(self):
        self.active_scrapers = {}
    
    def add_source(self, source_id: str, source_config: Dict[str, Any]) -> bool:
        """
        Add a new source and create its scraper
        
        Returns:
            True if scraper was created successfully, False otherwise
        """
        scraper = ScraperFactory.create_scraper(source_config)
        if scraper:
            self.active_scrapers[source_id] = scraper
            logger.info(f"Added scraper for source {source_id}")
            return True
        else:
            logger.error(f"Failed to create scraper for source {source_id}")
            return False
    
    def remove_source(self, source_id: str) -> bool:
        """Remove a source and its scraper"""
        if source_id in self.active_scrapers:
            del self.active_scrapers[source_id]
            logger.info(f"Removed scraper for source {source_id}")
            return True
        return False
    
    def get_scraper(self, source_id: str) -> Optional[BaseScraper]:
        """Get scraper for a specific source"""
        return self.active_scrapers.get(source_id)
    
    def get_all_scrapers(self) -> Dict[str, BaseScraper]:
        """Get all active scrapers"""
        return self.active_scrapers.copy()
    
    async def scrape_source(self, source_id: str, limit: int = 10):
        """Scrape articles from a specific source"""
        scraper = self.get_scraper(source_id)
        if not scraper:
            logger.error(f"No scraper found for source {source_id}")
            return []
        
        try:
            articles = await scraper.fetch_articles(limit=limit)
            logger.info(f"Scraped {len(articles)} articles from source {source_id}")
            return articles
        except Exception as e:
            logger.error(f"Error scraping source {source_id}: {str(e)}")
            return []
    
    async def scrape_all_sources(self, limit: int = 10):
        """Scrape articles from all active sources"""
        all_articles = []
        
        for source_id, scraper in self.active_scrapers.items():
            try:
                articles = await scraper.fetch_articles(limit=limit)
                all_articles.extend(articles)
                logger.info(f"Scraped {len(articles)} articles from {source_id}")
            except Exception as e:
                logger.error(f"Error scraping source {source_id}: {str(e)}")
        
        logger.info(f"Total scraped articles: {len(all_articles)}")
        return all_articles


# Global scraper manager instance
scraper_manager = ScraperManager()