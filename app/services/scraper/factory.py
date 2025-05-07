"""
Factory for creating appropriate scrapers based on source configuration
"""

import logging
from typing import Dict, Any, Optional, List, Type

from app.services.scraper.base import BaseScraper
from app.services.scraper.rss_scraper import RssScraper
from app.services.scraper.web_scraper import WebScraper

logger = logging.getLogger(__name__)

class ScraperFactory:
    """
    Factory for creating scrapers based on source configuration
    """
    
    _scraper_types = {
        "rss": RssScraper,
        "web": WebScraper,
    }
    
    @classmethod
    def register_scraper_type(cls, type_name: str, scraper_class: Type[BaseScraper]) -> None:
        """
        Register a new scraper type
        
        Args:
            type_name: Name of the scraper type
            scraper_class: Class of the scraper
        """
        cls._scraper_types[type_name] = scraper_class
        logger.info(f"Registered scraper type: {type_name}")
    
    @classmethod
    def create_scraper(cls, source_config: Dict[str, Any]) -> Optional[BaseScraper]:
        """
        Create a scraper based on source configuration
        
        Args:
            source_config: Source configuration
            
        Returns:
            BaseScraper instance or None if creation failed
        """
        try:
            scraper_type = source_config.get("type", "web")
            
            # Auto-detect scraper type if not specified
            if scraper_type == "auto":
                scraper_type = cls._detect_scraper_type(source_config)
            
            if scraper_type in cls._scraper_types:
                scraper_class = cls._scraper_types[scraper_type]
                return scraper_class(source_config)
            else:
                logger.error(f"Unknown scraper type: {scraper_type}")
                return None
        except Exception as e:
            logger.error(f"Error creating scraper: {e}")
            return None
    
    @classmethod
    def _detect_scraper_type(cls, source_config: Dict[str, Any]) -> str:
        """
        Detect the appropriate scraper type based on source configuration
        
        Args:
            source_config: Source configuration
            
        Returns:
            Detected scraper type
        """
        # If feed_url is provided, use RSS scraper
        if "feed_url" in source_config:
            return "rss"
        
        # Default to web scraper
        return "web"
    
    @classmethod
    def create_scrapers_for_sources(cls, sources: List[Dict[str, Any]]) -> Dict[str, BaseScraper]:
        """
        Create scrapers for multiple sources
        
        Args:
            sources: List of source configurations
            
        Returns:
            Dictionary mapping source IDs to scraper instances
        """
        scrapers = {}
        
        for source in sources:
            source_id = source.get("id")
            if not source_id:
                logger.warning(f"Source missing ID, skipping: {source}")
                continue
            
            scraper = cls.create_scraper(source)
            if scraper:
                scrapers[source_id] = scraper
            else:
                logger.warning(f"Failed to create scraper for source: {source_id}")
        
        return scrapers