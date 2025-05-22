"""
Cache invalidation strategies for the Heart of News backend
"""

import logging
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from sqlalchemy.orm import Session

from app.core.cache import invalidate_cache, get_redis
from app.models.article import Article
from app.models.source import Source
from app.models.user import User

# Configure logging
logger = logging.getLogger(__name__)

# Define cache key patterns for entities
CACHE_KEYS = {
    "article": {
        "detail": "article:*:{id}",
        "list": "get_multi_with_filters:*",
        "by_source": "articles:source:{source_id}:*",
        "by_status": "articles:status:{status}:*",
        "metrics": "article_metrics:*",
    },
    "source": {
        "detail": "source:*:{id}",
        "list": "sources:*",
        "with_articles": "source:{id}:articles:*",
        "metrics": "source_metrics:*",
    },
    "user": {
        "detail": "user:*:{id}",
        "list": "users:*",
        "by_email": "user:email:{email}",
        "by_username": "user:username:{username}",
        "sessions": "user:{id}:sessions:*",
    },
    "health": {
        "status": "health_status:*",
        "metrics": "metrics:*",
    },
    "global": {
        "all": "*"
    }
}


def invalidate_article_cache(db: Session, article_id: str) -> int:
    """
    Invalidate cache for a specific article
    
    Args:
        db: Database session
        article_id: Article ID
    
    Returns:
        Number of cache keys invalidated
    """
    count = 0
    
    # Get article data
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        return 0
        
    # Invalidate article detail cache
    count += invalidate_cache(CACHE_KEYS["article"]["detail"].format(id=article_id))
    
    # Invalidate article list cache
    count += invalidate_cache(CACHE_KEYS["article"]["list"])
    
    # Invalidate source-specific article cache
    if article.source_id:
        count += invalidate_cache(
            CACHE_KEYS["article"]["by_source"].format(source_id=article.source_id)
        )
    
    # Invalidate status-specific article cache
    if article.status:
        count += invalidate_cache(
            CACHE_KEYS["article"]["by_status"].format(status=article.status)
        )
    
    # Invalidate article metrics cache
    count += invalidate_cache(CACHE_KEYS["article"]["metrics"])
    
    logger.info(f"Invalidated {count} cache entries for article {article_id}")
    return count


def invalidate_source_cache(db: Session, source_id: str) -> int:
    """
    Invalidate cache for a specific source
    
    Args:
        db: Database session
        source_id: Source ID
    
    Returns:
        Number of cache keys invalidated
    """
    count = 0
    
    # Get source data
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return 0
        
    # Invalidate source detail cache
    count += invalidate_cache(CACHE_KEYS["source"]["detail"].format(id=source_id))
    
    # Invalidate source list cache
    count += invalidate_cache(CACHE_KEYS["source"]["list"])
    
    # Invalidate source with articles cache
    count += invalidate_cache(
        CACHE_KEYS["source"]["with_articles"].format(id=source_id)
    )
    
    # Invalidate source metrics cache
    count += invalidate_cache(CACHE_KEYS["source"]["metrics"])
    
    # Invalidate related article caches
    count += invalidate_cache(
        CACHE_KEYS["article"]["by_source"].format(source_id=source_id)
    )
    
    logger.info(f"Invalidated {count} cache entries for source {source_id}")
    return count


def invalidate_user_cache(db: Session, user_id: str) -> int:
    """
    Invalidate cache for a specific user
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Number of cache keys invalidated
    """
    count = 0
    
    # Get user data
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return 0
        
    # Invalidate user detail cache
    count += invalidate_cache(CACHE_KEYS["user"]["detail"].format(id=user_id))
    
    # Invalidate user list cache
    count += invalidate_cache(CACHE_KEYS["user"]["list"])
    
    # Invalidate user by email cache
    if user.email:
        count += invalidate_cache(
            CACHE_KEYS["user"]["by_email"].format(email=user.email)
        )
    
    # Invalidate user by username cache
    if user.username:
        count += invalidate_cache(
            CACHE_KEYS["user"]["by_username"].format(username=user.username)
        )
    
    # Invalidate user sessions cache
    count += invalidate_cache(
        CACHE_KEYS["user"]["sessions"].format(id=user_id)
    )
    
    logger.info(f"Invalidated {count} cache entries for user {user_id}")
    return count


def invalidate_health_cache() -> int:
    """
    Invalidate health check cache
    
    Returns:
        Number of cache keys invalidated
    """
    count = 0
    
    # Invalidate health status cache
    count += invalidate_cache(CACHE_KEYS["health"]["status"])
    
    # Invalidate metrics cache
    count += invalidate_cache(CACHE_KEYS["health"]["metrics"])
    
    logger.info(f"Invalidated {count} health and metrics cache entries")
    return count


def setup_cache_invalidation_triggers(engine) -> None:
    """
    Set up database triggers for automatic cache invalidation
    
    In a production environment, this would use PostgreSQL triggers to
    automatically invalidate cache when data changes. For now, we'll rely
    on explicit invalidation in the CRUD operations.
    
    Args:
        engine: SQLAlchemy engine
    """
    # This is a placeholder for potential future implementation
    pass