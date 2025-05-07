"""
Celery worker for background tasks
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from celery import Celery
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import SessionLocal
from app.crud import article, source
from app.models.article import Article
from app.models.source import Source
from app.services.ai.bias_detector import BiasDetector
from app.services.scraper.factory import ScraperFactory
from app.services.scraper.manager import ScraperManager
from app.services.scraper.sources import get_default_sources

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "heart_of_news_worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)

# Configure Celery
celery_app.conf.task_routes = {
    "app.worker.scrape_sources": {"queue": "scraper"},
    "app.worker.analyze_articles": {"queue": "analyzer"},
    "app.worker.publish_articles": {"queue": "publisher"},
}

celery_app.conf.beat_schedule = {
    "scrape-sources": {
        "task": "app.worker.scrape_sources",
        "schedule": 60 * 60,  # every hour
    },
    "analyze-articles": {
        "task": "app.worker.analyze_articles",
        "schedule": 15 * 60,  # every 15 minutes
    },
    "publish-articles": {
        "task": "app.worker.publish_articles",
        "schedule": 30 * 60,  # every 30 minutes
    },
}

# Helper function to get database session
def get_db() -> Session:
    """
    Get a database session
    
    Returns:
        Database session
    """
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise

# Define Celery tasks

@celery_app.task
def scrape_sources(
    limit_per_source: int = 10,
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Scrape articles from sources and save to database
    
    Args:
        limit_per_source: Maximum number of articles to fetch per source
        source_ids: Optional list of source IDs to scrape (if None, scrapes sources based on crawl frequency)
        
    Returns:
        Dictionary with results
    """
    logger.info("Starting scrape_sources task")
    
    try:
        db = get_db()
        
        if source_ids:
            # Scrape specific sources
            sources_to_scrape = []
            for source_id in source_ids:
                db_source = source.get(db=db, id=source_id)
                if db_source:
                    sources_to_scrape.append(db_source)
        else:
            # Scrape sources based on crawl frequency
            sources_to_scrape = source.get_sources_for_crawling(db=db, limit=5)
        
        if not sources_to_scrape:
            logger.info("No sources to scrape")
            return {"status": "success", "message": "No sources to scrape", "results": {}}
        
        # Create source configurations
        source_configs = []
        for db_source in sources_to_scrape:
            config = {
                "id": str(db_source.id),
                "name": db_source.name,
                "url": db_source.url,
                "feed_url": db_source.feed_url
            }
            
            # Add scraper config if available
            if db_source.scraper_config:
                config.update(db_source.scraper_config)
                
            source_configs.append(config)
        
        # Run the scraper synchronously (Celery doesn't support asyncio directly)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create scraper manager
        manager = ScraperManager(db=db)
        
        # Initialize scrapers
        loop.run_until_complete(manager.initialize_scrapers(source_configs))
        
        # Run the scrape operation
        results = loop.run_until_complete(
            manager.scrape_all_sources(limit_per_source=limit_per_source)
        )
        
        # Save results to database
        saved_counts = loop.run_until_complete(
            manager.save_articles_to_db(results)
        )
        
        # Update last_crawled_at for each source
        for db_source in sources_to_scrape:
            source.update_crawl_timestamp(db=db, db_obj=db_source)
        
        # Clean up the loop
        loop.close()
        
        logger.info(f"Completed scrape_sources task: {saved_counts}")
        
        return {
            "status": "success",
            "message": f"Scraped {sum(saved_counts.values())} new articles",
            "results": saved_counts
        }
        
    except Exception as e:
        logger.error(f"Error in scrape_sources task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()

@celery_app.task
def analyze_articles(limit: int = 20) -> Dict[str, Any]:
    """
    Analyze draft articles for bias and update their metrics
    
    Args:
        limit: Maximum number of articles to analyze
        
    Returns:
        Dictionary with results
    """
    logger.info("Starting analyze_articles task")
    
    try:
        db = get_db()
        
        # Get articles for processing
        articles_to_process = article.get_articles_for_processing(
            db=db, limit=limit
        )
        
        if not articles_to_process:
            logger.info("No articles to analyze")
            return {"status": "success", "message": "No articles to analyze", "processed": 0}
        
        # Initialize bias detector
        detector = BiasDetector()
        
        # Process each article
        processed_count = 0
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        for db_article in articles_to_process:
            if not db_article.content:
                # Skip articles without content
                continue
                
            try:
                # Analyze the article
                analysis = loop.run_until_complete(
                    detector.get_full_bias_analysis(db_article.content)
                )
                
                # Update the article with the analysis results
                article.update_bias_metrics(
                    db=db,
                    db_obj=db_article,
                    political_bias=analysis["political_bias"],
                    emotional_language=analysis["emotional_language"],
                    fact_opinion_ratio=analysis["fact_opinion_ratio"]
                )
                
                # Update status to processing
                article.update_status(
                    db=db,
                    db_obj=db_article,
                    status="processing"
                )
                
                processed_count += 1
                
            except Exception as e:
                logger.error(f"Error analyzing article {db_article.id}: {e}")
                
                # Mark as error status
                article.update_status(
                    db=db,
                    db_obj=db_article,
                    status="error"
                )
        
        # Clean up the loop
        loop.close()
        
        logger.info(f"Completed analyze_articles task: {processed_count} articles processed")
        
        return {
            "status": "success",
            "message": f"Analyzed {processed_count} articles",
            "processed": processed_count
        }
        
    except Exception as e:
        logger.error(f"Error in analyze_articles task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()

@celery_app.task
def publish_articles(limit: int = 20) -> Dict[str, Any]:
    """
    Mark processed articles as published
    
    Args:
        limit: Maximum number of articles to publish
        
    Returns:
        Dictionary with results
    """
    logger.info("Starting publish_articles task")
    
    try:
        db = get_db()
        
        # Get articles in "processing" status, ordered by discovered time
        processing_articles = (
            db.query(Article)
            .filter(Article.status == "processing")
            .order_by(Article.discovered_at.asc())
            .limit(limit)
            .all()
        )
        
        if not processing_articles:
            logger.info("No articles to publish")
            return {"status": "success", "message": "No articles to publish", "published": 0}
        
        # Update status to published
        published_count = 0
        
        for db_article in processing_articles:
            # Apply any additional publishing logic here
            # For example, filtering based on bias scores
            
            # Mark as published
            article.update_status(
                db=db,
                db_obj=db_article,
                status="published"
            )
            
            published_count += 1
        
        logger.info(f"Completed publish_articles task: {published_count} articles published")
        
        return {
            "status": "success",
            "message": f"Published {published_count} articles",
            "published": published_count
        }
        
    except Exception as e:
        logger.error(f"Error in publish_articles task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()

# One-time task to import sources from the default configuration
@celery_app.task
def import_default_sources() -> Dict[str, Any]:
    """
    Import default sources into the database
    
    Returns:
        Dictionary with results
    """
    logger.info("Starting import_default_sources task")
    
    try:
        db = get_db()
        
        # Get default sources
        default_sources = get_default_sources()
        
        # Import each source
        imported_count = 0
        skipped_count = 0
        
        for src in default_sources:
            # Check if source already exists
            db_source = source.get_by_name(db=db, name=src["name"])
            if db_source:
                skipped_count += 1
                continue
                
            # Create source object
            source_data = {
                "name": src["name"],
                "url": src["url"],
                "feed_url": src.get("feed_url"),
                "category": src.get("category", "General"),
                "reliability_score": src.get("reliability_score", 0.0),
                "bias_score": src.get("bias_score", 0.0),
            }
            
            # Create in database
            new_source = SourceCreate(**source_data)
            db_source = source.create(db=db, obj_in=new_source)
            
            # Add scraper config
            scraper_config = {
                "type": src.get("type", "auto"),
                "article_selector": src.get("article_selector"),
                "content_selector": src.get("content_selector"),
            }
            
            # Update source with scraper config
            db_source.scraper_config = scraper_config
            db.add(db_source)
            db.commit()
            
            imported_count += 1
        
        logger.info(f"Completed import_default_sources task: {imported_count} sources imported, {skipped_count} skipped")
        
        return {
            "status": "success",
            "message": f"Imported {imported_count} sources, skipped {skipped_count}",
            "imported": imported_count,
            "skipped": skipped_count
        }
        
    except Exception as e:
        logger.error(f"Error in import_default_sources task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()