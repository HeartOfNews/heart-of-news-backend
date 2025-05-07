"""
Manager for handling scraping operations
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set

from app.models.article import Article
from app.models.source import Source
from app.services.scraper.base import BaseScraper, ArticleData
from app.services.scraper.factory import ScraperFactory

logger = logging.getLogger(__name__)

class ScraperManager:
    """
    Manager for coordinating scraping operations
    """
    
    def __init__(self, db=None):
        """
        Initialize the scraper manager
        
        Args:
            db: Database session (optional)
        """
        self.db = db
        self.scrapers = {}
        self.last_run = {}
        
    async def initialize_scrapers(self, sources: List[Dict[str, Any]] = None) -> None:
        """
        Initialize scrapers from sources
        
        Args:
            sources: List of source configurations (optional)
        """
        if not sources and self.db:
            # Load sources from database
            sources = await self._get_sources_from_db()
        
        if not sources:
            logger.warning("No sources provided or found in database")
            return
        
        self.scrapers = ScraperFactory.create_scrapers_for_sources(sources)
        logger.info(f"Initialized {len(self.scrapers)} scrapers")
    
    async def _get_sources_from_db(self) -> List[Dict[str, Any]]:
        """
        Get sources from database
        
        Returns:
            List of source configurations
        """
        if not self.db:
            logger.error("No database session provided")
            return []
        
        try:
            # This is a placeholder for actual database query
            # In real implementation, this would use the ORM to fetch sources
            sources = []
            # Example: sources = await db.query(Source).filter(Source.active == True).all()
            
            # Convert to dictionaries
            source_configs = []
            for source in sources:
                config = {
                    "id": str(source.id),
                    "name": source.name,
                    "url": source.url,
                    "type": source.scraper_type,
                }
                
                # Add scraper-specific configurations
                if source.scraper_config:
                    config.update(source.scraper_config)
                
                source_configs.append(config)
            
            return source_configs
        except Exception as e:
            logger.error(f"Error getting sources from database: {e}")
            return []
    
    async def scrape_all_sources(self, limit_per_source: int = 10) -> Dict[str, List[ArticleData]]:
        """
        Scrape articles from all sources
        
        Args:
            limit_per_source: Maximum number of articles to fetch per source
            
        Returns:
            Dictionary mapping source IDs to lists of ArticleData
        """
        results = {}
        tasks = []
        
        for source_id, scraper in self.scrapers.items():
            tasks.append(self._scrape_source(source_id, scraper, limit_per_source))
        
        # Run scraping tasks concurrently
        source_results = await asyncio.gather(*tasks)
        
        # Combine results
        for source_id, articles in source_results:
            results[source_id] = articles
        
        return results
    
    async def _scrape_source(self, source_id: str, scraper: BaseScraper, limit: int) -> tuple[str, List[ArticleData]]:
        """
        Scrape articles from a specific source
        
        Args:
            source_id: ID of the source
            scraper: Scraper instance
            limit: Maximum number of articles to fetch
            
        Returns:
            Tuple of (source_id, list of ArticleData)
        """
        try:
            logger.info(f"Scraping source: {scraper.name} (ID: {source_id})")
            articles = await scraper.fetch_articles(limit=limit)
            
            # Update last run timestamp
            self.last_run[source_id] = datetime.utcnow()
            
            logger.info(f"Scraped {len(articles)} articles from {scraper.name}")
            return source_id, articles
        except Exception as e:
            logger.error(f"Error scraping source {source_id}: {e}")
            return source_id, []
    
    async def save_articles_to_db(self, articles_by_source: Dict[str, List[ArticleData]]) -> Dict[str, int]:
        """
        Save scraped articles to the database
        
        Args:
            articles_by_source: Dictionary mapping source IDs to lists of ArticleData
            
        Returns:
            Dictionary mapping source IDs to number of articles saved
        """
        if not self.db:
            logger.error("No database session provided")
            return {}
        
        results = {}
        
        for source_id, articles in articles_by_source.items():
            try:
                # Track how many were saved
                saved_count = 0
                
                for article_data in articles:
                    # Check if article already exists by URL
                    existing = None
                    # Example: existing = await db.query(Article).filter(Article.original_url == article_data.url).first()
                    
                    if existing:
                        # Skip existing articles
                        continue
                    
                    # Create new article
                    new_article = Article(
                        original_url=article_data.url,
                        title=article_data.title,
                        summary=article_data.summary,
                        content=article_data.content,
                        published_at=article_data.published_at,
                        source_id=source_id,
                        entities={"author": article_data.author} if article_data.author else {},
                        topics={"tags": article_data.tags} if article_data.tags else {},
                        status="draft"
                    )
                    
                    # Save to database
                    # Example: db.add(new_article)
                    # Example: await db.commit()
                    
                    saved_count += 1
                
                results[source_id] = saved_count
                logger.info(f"Saved {saved_count} new articles from source {source_id}")
                
            except Exception as e:
                logger.error(f"Error saving articles from source {source_id}: {e}")
                results[source_id] = 0
        
        return results
    
    async def run_scheduled_scrape(self, limit_per_source: int = 10) -> Dict[str, int]:
        """
        Run a scheduled scrape for all sources
        
        Args:
            limit_per_source: Maximum number of articles to fetch per source
            
        Returns:
            Dictionary mapping source IDs to number of articles saved
        """
        # Scrape all sources
        scraped_articles = await self.scrape_all_sources(limit_per_source=limit_per_source)
        
        # Save to database
        saved_counts = await self.save_articles_to_db(scraped_articles)
        
        return saved_counts
    
    async def get_source_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics for each source
        
        Returns:
            Dictionary mapping source IDs to stats
        """
        stats = {}
        
        for source_id, scraper in self.scrapers.items():
            last_run = self.last_run.get(source_id)
            
            stats[source_id] = {
                "name": scraper.name,
                "url": scraper.source_url,
                "last_run": last_run.isoformat() if last_run else None,
                "scraper_type": scraper.__class__.__name__,
            }
        
        return stats