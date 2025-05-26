"""
Breaking news publishing task - can be integrated into worker.py
"""

@celery_app.task
def publish_breaking_news(max_age_minutes: int = 30) -> Dict[str, Any]:
    """
    Immediately publish breaking news articles (very recent articles)
    
    Args:
        max_age_minutes: Maximum age of articles to consider as breaking news
        
    Returns:
        Dictionary with results
    """
    logger.info("Starting publish_breaking_news task")
    
    try:
        db = get_db()
        
        # Get very recent articles that haven't been published yet
        cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
        
        breaking_articles = (
            db.query(Article)
            .filter(Article.status == "analyzed")  # Ready for publishing
            .filter(Article.discovered_at >= cutoff_time)  # Very recent
            .order_by(Article.discovered_at.desc())
            .limit(5)  # Max 5 breaking articles at once
            .all()
        )
        
        if not breaking_articles:
            logger.info("No breaking news articles to publish")
            return {"status": "success", "message": "No breaking news", "published": 0}
        
        # Publish breaking news immediately
        published_count = 0
        telegram_results = []
        
        for db_article in breaking_articles:
            try:
                # Prioritize articles with images and political content
                has_image = db_article.image_url is not None
                
                # Check if it's truly breaking news (political keywords)
                breaking_keywords = [
                    "breaking", "urgent", "developing", "just in", "live", 
                    "election", "vote", "summit", "crisis", "announcement",
                    "biden", "trump", "eu", "nato", "congress", "parliament"
                ]
                
                article_text = (db_article.title + " " + (db_article.summary or "")).lower()
                is_breaking = any(keyword in article_text for keyword in breaking_keywords)
                
                if is_breaking or has_image:
                    # Publish to Telegram immediately
                    if telegram_service.enabled:
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            telegram_result = loop.run_until_complete(
                                telegram_service.publish_article(db_article)
                            )
                            telegram_results.append({
                                "article_id": db_article.id,
                                "telegram": telegram_result,
                                "breaking": True
                            })
                            loop.close()
                        except Exception as e:
                            logger.error(f"Failed to publish breaking article {db_article.id}: {e}")
                            continue
                    
                    # Mark as published
                    article.update_status(
                        db=db,
                        db_obj=db_article,
                        status="published"
                    )
                    
                    published_count += 1
                    logger.info(f"Published breaking news: {db_article.title[:50]}...")
                    
            except Exception as e:
                logger.error(f"Error processing breaking article {db_article.id}: {e}")
                continue
        
        logger.info(f"Completed publish_breaking_news task: {published_count} articles published")
        
        telegram_success = len([r for r in telegram_results if r.get("telegram", {}).get("success")])
        
        return {
            "status": "success",
            "message": f"Published {published_count} breaking news articles",
            "published": published_count,
            "telegram": {
                "enabled": telegram_service.enabled,
                "published": telegram_success,
                "total": len(telegram_results),
                "results": telegram_results
            }
        }
        
    except Exception as e:
        logger.error(f"Error in publish_breaking_news task: {e}")
        return {
            "status": "error",
            "message": str(e)
        }
    finally:
        db.close()