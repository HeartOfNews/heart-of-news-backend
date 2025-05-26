"""
Dual-language publishing worker extension
Handles publishing to both English and Russian channels
"""

from app.services.telegram_service import telegram_service
from app.services.telegram_service_ru import telegram_russian_service

async def publish_dual_language_article(article):
    """Publish article to both English and Russian channels"""
    results = {
        "english": {"enabled": False, "success": False},
        "russian": {"enabled": False, "success": False}
    }
    
    # Publish to English channel
    if telegram_service.enabled:
        try:
            results["english"]["enabled"] = True
            en_result = await telegram_service.publish_article(article)
            results["english"]["success"] = en_result.get("success", False)
            results["english"]["message_id"] = en_result.get("message_id")
        except Exception as e:
            results["english"]["error"] = str(e)
    
    # Publish to Russian channel  
    if telegram_russian_service.enabled:
        try:
            results["russian"]["enabled"] = True
            ru_result = await telegram_russian_service.publish_article(article)
            results["russian"]["success"] = ru_result.get("success", False)
            results["russian"]["message_id"] = ru_result.get("message_id")
        except Exception as e:
            results["russian"]["error"] = str(e)
    
    return results

# This function would be integrated into the main worker.py file
@celery_app.task
def publish_dual_language_articles(limit: int = 20) -> Dict[str, Any]:
    """
    Publish processed articles to both English and Russian channels
    """
    logger.info("Starting dual-language publish task")
    
    try:
        db = get_db()
        
        # Get articles ready for publishing
        processing_articles = (
            db.query(Article)
            .filter(Article.status == "processing")
            .order_by(Article.discovered_at.asc())
            .limit(limit)
            .all()
        )
        
        if not processing_articles:
            return {"status": "success", "message": "No articles to publish", "published": 0}
        
        published_count = 0
        dual_results = []
        
        for db_article in processing_articles:
            try:
                # Publish to both channels
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                dual_result = loop.run_until_complete(
                    publish_dual_language_article(db_article)
                )
                dual_results.append({
                    "article_id": db_article.id,
                    "dual_publish": dual_result
                })
                loop.close()
                
                # Mark as published if at least one channel succeeded
                if (dual_result["english"]["success"] or dual_result["russian"]["success"]):
                    article.update_status(
                        db=db,
                        db_obj=db_article,
                        status="published"
                    )
                    published_count += 1
                
            except Exception as e:
                logger.error(f"Error in dual publishing for article {db_article.id}: {e}")
                continue
        
        # Calculate success rates
        en_success = len([r for r in dual_results if r["dual_publish"]["english"]["success"]])
        ru_success = len([r for r in dual_results if r["dual_publish"]["russian"]["success"]])
        
        return {
            "status": "success",
            "message": f"Published {published_count} articles to dual channels",
            "published": published_count,
            "english": {
                "enabled": telegram_service.enabled,
                "published": en_success,
                "total": len(dual_results)
            },
            "russian": {
                "enabled": telegram_russian_service.enabled,
                "published": ru_success,
                "total": len(dual_results)
            },
            "results": dual_results
        }
        
    except Exception as e:
        logger.error(f"Error in dual-language publish task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()