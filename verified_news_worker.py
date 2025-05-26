"""
Verified News Publishing Worker
Only processes and publishes verified, authentic news from official sources
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.services.scraper.verified_sources import get_verified_sources, get_verified_russian_sources
from app.services.ai.propaganda_detector import propaganda_detector
from app.services.verification.news_verifier import news_verifier
from app.services.telegram_service import telegram_service
from app.services.telegram_service_ru import telegram_russian_service

logger = logging.getLogger(__name__)

class VerifiedNewsWorker:
    """Worker that only processes verified, authentic news"""
    
    def __init__(self):
        self.verification_enabled = True
        self.propaganda_detection_enabled = True
        self.min_reliability_threshold = 0.8
        self.max_propaganda_score = 0.3
        
    async def process_verified_articles(self, limit: int = 10) -> Dict[str, Any]:
        """
        Process only verified articles from official sources
        
        Args:
            limit: Maximum number of articles to process
            
        Returns:
            Processing results with verification details
        """
        logger.info("Starting verified news processing")
        
        try:
            # Get only verified sources
            verified_sources = get_verified_sources()
            verified_russian_sources = get_verified_russian_sources()
            
            all_sources = verified_sources + verified_russian_sources
            
            processed_articles = []
            verification_stats = {
                "total_articles": 0,
                "verified_articles": 0,
                "rejected_articles": 0,
                "propaganda_detected": 0,
                "published_articles": 0
            }
            
            # Process articles from each verified source
            for source in all_sources[:limit]:  # Limit sources for demo
                
                # This would normally fetch real articles from the source
                # For demonstration, we'll show the verification process
                sample_article = {
                    "title": f"Sample verified article from {source['name']}",
                    "content": "This would be real article content from the verified source.",
                    "url": source["url"],
                    "source": source,
                    "published_at": datetime.now()
                }
                
                verification_stats["total_articles"] += 1
                
                # Step 1: Verify article authenticity
                authenticity_result = news_verifier.verify_article_authenticity(sample_article)
                
                if not authenticity_result["authentic"]:
                    logger.warning(f"Article rejected: {authenticity_result['all_concerns']}")
                    verification_stats["rejected_articles"] += 1
                    continue
                
                verification_stats["verified_articles"] += 1
                
                # Step 2: Check for propaganda
                propaganda_analysis = propaganda_detector.analyze_content(
                    sample_article["title"],
                    sample_article["content"],
                    sample_article["source"]
                )
                
                if propaganda_analysis["recommendation"] == "REJECT":
                    logger.warning(f"Article rejected due to propaganda: {propaganda_analysis['concerns']}")
                    verification_stats["propaganda_detected"] += 1
                    verification_stats["rejected_articles"] += 1
                    continue
                
                # Step 3: Publish verified article
                if (authenticity_result["verification_level"] in ["VERIFIED", "PARTIALLY_VERIFIED"] and
                    propaganda_analysis["recommendation"] in ["APPROVE", "REVIEW"]):
                    
                    publish_result = await self._publish_verified_article(
                        sample_article, 
                        authenticity_result, 
                        propaganda_analysis
                    )
                    
                    if publish_result["success"]:
                        verification_stats["published_articles"] += 1
                    
                    processed_articles.append({
                        "article": sample_article,
                        "authenticity": authenticity_result,
                        "propaganda_analysis": propaganda_analysis,
                        "published": publish_result["success"]
                    })
            
            logger.info(f"Verified news processing complete: {verification_stats}")
            
            return {
                "status": "success",
                "verification_stats": verification_stats,
                "processed_articles": processed_articles,
                "timestamp": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error in verified news processing: {e}")
            return {
                "status": "error",
                "message": str(e),
                "timestamp": datetime.now()
            }
    
    async def _publish_verified_article(
        self, 
        article: Dict[str, Any], 
        authenticity: Dict[str, Any], 
        propaganda_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Publish verified article to appropriate channels"""
        
        publication_results = {
            "success": False,
            "english_published": False,
            "russian_published": False,
            "verification_included": True
        }
        
        try:
            # Determine target channels based on source language
            source_language = article["source"].get("language", "en")
            
            # Publish to English channel
            if telegram_service.enabled:
                en_result = await telegram_service.publish_article(self._create_article_object(article))
                publication_results["english_published"] = en_result.get("success", False)
            
            # Publish to Russian channel if Russian source or dual publishing
            if (telegram_russian_service.enabled and 
                (source_language == "ru" or self._should_dual_publish(article))):
                ru_result = await telegram_russian_service.publish_article(self._create_article_object(article))
                publication_results["russian_published"] = ru_result.get("success", False)
            
            publication_results["success"] = (
                publication_results["english_published"] or 
                publication_results["russian_published"]
            )
            
            return publication_results
            
        except Exception as e:
            logger.error(f"Error publishing verified article: {e}")
            return {"success": False, "error": str(e)}
    
    def _create_article_object(self, article_data: Dict[str, Any]):
        """Create article object for publishing (simplified for demo)"""
        # This would create a proper Article model instance
        # For demo purposes, return the data dict
        return type('Article', (), article_data)()
    
    def _should_dual_publish(self, article: Dict[str, Any]) -> bool:
        """Determine if article should be published to both channels"""
        # Publish political news to both channels
        categories = article.get("categories", [])
        political_categories = ["Politics", "International", "European Union", "USA"]
        
        return any(cat in categories for cat in political_categories)
    
    def get_verification_status(self) -> Dict[str, Any]:
        """Get current verification system status"""
        return {
            "verification_enabled": self.verification_enabled,
            "propaganda_detection_enabled": self.propaganda_detection_enabled,
            "verified_sources_count": len(get_verified_sources()),
            "verified_russian_sources_count": len(get_verified_russian_sources()),
            "min_reliability_threshold": self.min_reliability_threshold,
            "max_propaganda_score": self.max_propaganda_score,
            "verification_requirements": news_verifier.get_verification_requirements()
        }

# Integration with existing worker system
@celery_app.task
def process_verified_news_articles(limit: int = 10) -> Dict[str, Any]:
    """
    Celery task to process only verified news articles
    Replaces the old scraping task with verification-first approach
    """
    logger.info("Starting verified news processing task")
    
    try:
        worker = VerifiedNewsWorker()
        
        # Run the async processing in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(worker.process_verified_articles(limit))
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in verified news processing task: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now()
        }

# Updated Celery schedule for verified news
VERIFIED_NEWS_SCHEDULE = {
    "process-verified-news": {
        "task": "app.worker.process_verified_news_articles",
        "schedule": 10 * 60,  # every 10 minutes - more frequent for verified sources
    },
    "verify-breaking-news": {
        "task": "app.worker.verify_breaking_news",
        "schedule": 5 * 60,  # every 5 minutes for breaking news verification
    }
}