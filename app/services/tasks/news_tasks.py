"""
Background tasks for news processing
"""

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.crud import article as crud_article, source as crud_source
from app.services.scraper.scraper_factory import ScraperFactory
from app.services.ai.bias_detector import BiasDetector
from app.services.tasks.task_queue import task_queue

logger = logging.getLogger(__name__)


async def scrape_source_articles(source_id: str, limit: int = 10):
    """Background task to scrape articles from a specific source"""
    db = SessionLocal()
    try:
        # Get source configuration
        source = crud_source.get_source(db, source_id)
        if not source:
            raise ValueError(f"Source {source_id} not found")
        
        # Create scraper
        source_config = {
            "id": str(source.id),
            "name": source.name,
            "url": source.url,
            "feed_url": source.feed_url,
            "scraper_type": source.scraper_config.get("type", "rss") if source.scraper_config else "rss",
        }
        if source.scraper_config:
            source_config.update(source.scraper_config)
        
        scraper = ScraperFactory.create_scraper(source_config)
        if not scraper:
            raise ValueError(f"Failed to create scraper for source {source_id}")
        
        # Fetch articles
        articles = await scraper.fetch_articles(limit=limit)
        logger.info(f"Scraped {len(articles)} articles from {source.name}")
        
        # Save articles to database
        saved_count = 0
        bias_detector = BiasDetector()
        
        for article_data in articles:
            try:
                # Check if article already exists
                existing = db.query(crud_article.Article).filter(
                    crud_article.Article.original_url == str(article_data.url)
                ).first()
                
                if existing:
                    logger.debug(f"Article already exists: {article_data.url}")
                    continue
                
                # Create article
                article = crud_article.Article(
                    title=article_data.title,
                    summary=article_data.summary,
                    content=article_data.content,
                    original_url=str(article_data.url),
                    published_at=article_data.published_at,
                    source_id=source.id,
                    entities=article_data.metadata,
                    status="processing"
                )
                
                db.add(article)
                db.commit()
                db.refresh(article)
                
                # Schedule bias analysis
                if article_data.content:
                    task_id = f"bias_analysis_{article.id}_{int(datetime.utcnow().timestamp())}"
                    task_queue.add_task(
                        task_id,
                        f"Analyze bias for article {article.id}",
                        analyze_article_bias,
                        str(article.id)
                    )
                
                saved_count += 1
                logger.debug(f"Saved article: {article_data.title}")
                
            except Exception as e:
                logger.error(f"Error saving article {article_data.url}: {str(e)}")
                db.rollback()
        
        # Update source last crawled time
        crud_source.update_last_crawled(db, source_id)
        
        logger.info(f"Saved {saved_count} new articles from {source.name}")
        return {"scraped": len(articles), "saved": saved_count}
        
    except Exception as e:
        logger.error(f"Error scraping source {source_id}: {str(e)}")
        raise
    finally:
        db.close()


async def analyze_article_bias(article_id: str):
    """Background task to analyze bias in an article"""
    db = SessionLocal()
    try:
        article = crud_article.get_article(db, article_id)
        if not article:
            raise ValueError(f"Article {article_id} not found")
        
        if not article.content:
            logger.warning(f"Article {article_id} has no content for bias analysis")
            return
        
        # Perform bias analysis
        bias_detector = BiasDetector()
        analysis = await bias_detector.get_full_bias_analysis(article.content)
        
        # Update article with bias scores
        crud_article.update_article_bias_analysis(
            db=db,
            article_id=article_id,
            political_bias=analysis["political_bias"],
            emotional_language=analysis["emotional_language"],
            fact_opinion_ratio=analysis["fact_opinion_ratio"]
        )
        
        # Update article status
        article.status = "published"
        db.commit()
        
        logger.info(f"Completed bias analysis for article {article_id}")
        return analysis
        
    except Exception as e:
        logger.error(f"Error analyzing bias for article {article_id}: {str(e)}")
        raise
    finally:
        db.close()


async def scrape_all_sources(limit: int = 10):
    """Background task to scrape articles from all active sources"""
    db = SessionLocal()
    try:
        sources = crud_source.get_sources(db, limit=100)  # Get all sources
        total_scraped = 0
        total_saved = 0
        
        for source in sources:
            try:
                task_id = f"scrape_source_{source.id}_{int(datetime.utcnow().timestamp())}"
                task = task_queue.add_task(
                    task_id,
                    f"Scrape articles from {source.name}",
                    scrape_source_articles,
                    str(source.id),
                    limit
                )
                
                # For this task, we'll wait for completion
                # In a real scenario, you might want to run these concurrently
                while task.status.value in ["pending", "running"]:
                    await asyncio.sleep(0.1)
                
                if task.status.value == "completed" and task.result:
                    total_scraped += task.result.get("scraped", 0)
                    total_saved += task.result.get("saved", 0)
                
            except Exception as e:
                logger.error(f"Error scheduling scrape for source {source.id}: {str(e)}")
        
        logger.info(f"Scraping completed: {total_scraped} articles scraped, {total_saved} saved")
        return {"total_scraped": total_scraped, "total_saved": total_saved}
        
    except Exception as e:
        logger.error(f"Error in scrape_all_sources: {str(e)}")
        raise
    finally:
        db.close()


def schedule_periodic_scraping():
    """Schedule periodic scraping of all sources"""
    task_id = f"periodic_scrape_{int(datetime.utcnow().timestamp())}"
    task_queue.add_task(
        task_id,
        "Periodic scraping of all sources",
        scrape_all_sources,
        limit=20
    )
    logger.info("Scheduled periodic scraping task")


def schedule_source_scraping(source_id: str, limit: int = 10):
    """Schedule scraping for a specific source"""
    task_id = f"scrape_{source_id}_{int(datetime.utcnow().timestamp())}"
    task_queue.add_task(
        task_id,
        f"Scrape source {source_id}",
        scrape_source_articles,
        source_id,
        limit
    )
    logger.info(f"Scheduled scraping task for source {source_id}")
    return task_id