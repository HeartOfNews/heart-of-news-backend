"""
API endpoints for system health monitoring
"""

import asyncio
from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.services.ai.bias_detector import BiasDetector
from app.worker import celery_app
from app.crud import source, article

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def health_check(
    db: Session = Depends(get_db),
) -> Any:
    """
    Check system health, including database connectivity and services.
    """
    health_status = {
        "status": "healthy",
        "api": "ok",
        "database": "ok",
        "version": settings.VERSION,
        "services": {}
    }
    
    # Check database connectivity
    try:
        db.execute("SELECT 1")
    except Exception as e:
        health_status["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "unhealthy"
    
    # Check bias detector service
    try:
        detector = BiasDetector()
        sample_text = "This is a test of the bias detector service."
        analysis = await detector.analyze_political_bias(sample_text)
        health_status["services"]["bias_detector"] = "ok"
    except Exception as e:
        health_status["services"]["bias_detector"] = "error"
        health_status["services"]["bias_detector_error"] = str(e)
        health_status["status"] = "degraded"
    
    # Check Celery
    try:
        i = celery_app.control.inspect()
        ping = i.ping()
        if ping:
            health_status["services"]["task_queue"] = "ok"
        else:
            health_status["services"]["task_queue"] = "error"
            health_status["services"]["task_queue_error"] = "No response from Celery workers"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["task_queue"] = "error"
        health_status["services"]["task_queue_error"] = str(e)
        health_status["status"] = "degraded"
    
    # Check data status
    try:
        source_count = db.query(source.model).count()
        article_count = db.query(article.model).count()
        
        health_status["data"] = {
            "sources": source_count,
            "articles": article_count
        }
    except Exception as e:
        health_status["data"] = "error"
        health_status["data_error"] = str(e)
        
    return health_status

@router.get("/status", response_model=Dict[str, Any])
def service_status(
    db: Session = Depends(get_db),
) -> Any:
    """
    Get detailed system status, including article and source statistics.
    """
    # Get counts by article status
    article_stats = {}
    for status in ["draft", "processing", "published", "rejected", "error"]:
        count = db.query(article.model).filter(article.model.status == status).count()
        article_stats[status] = count
    
    # Get source statistics
    reliable_sources = db.query(source.model).filter(source.model.reliability_score >= 0.7).count()
    
    # Get bias distribution
    left_sources = db.query(source.model).filter(source.model.bias_score < -0.2).count()
    neutral_sources = db.query(source.model).filter(source.model.bias_score.between(-0.2, 0.2)).count()
    right_sources = db.query(source.model).filter(source.model.bias_score > 0.2).count()
    
    # Calculate average processing time (stub for now)
    avg_processing_time = 60  # seconds
    
    return {
        "article_stats": article_stats,
        "total_articles": sum(article_stats.values()),
        "source_stats": {
            "total": db.query(source.model).count(),
            "reliable": reliable_sources,
            "bias_distribution": {
                "left": left_sources,
                "neutral": neutral_sources,
                "right": right_sources
            }
        },
        "performance": {
            "avg_processing_time": avg_processing_time,
            "article_processing_rate": 3600 / max(avg_processing_time, 1)  # articles per hour
        }
    }