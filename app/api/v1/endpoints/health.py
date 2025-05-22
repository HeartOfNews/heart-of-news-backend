"""
API endpoints for system health monitoring
"""

import os
import time
import asyncio
import socket
import platform
import psutil
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, BackgroundTasks, Query
from sqlalchemy.orm import Session
import redis
import elasticsearch
from loguru import logger

from app.db.session import get_db, engine
from app.core.config import settings
from app.services.ai.bias_detector import BiasDetector
from app.worker import celery_app
from app.crud import source, article

router = APIRouter()

# Cache for health check results to avoid overloading services
health_cache = {
    "last_check": None,
    "result": None,
    "detailed_status": None,
    "last_detailed_check": None
}

def get_system_info() -> Dict[str, Any]:
    """Get system information for the server."""
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return {
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "cpu_usage": psutil.cpu_percent(interval=0.1),
        "memory": {
            "total": memory.total,
            "available": memory.available,
            "percent_used": memory.percent,
        },
        "disk": {
            "total": disk.total,
            "free": disk.free,
            "percent_used": disk.percent,
        },
        "uptime": time.time() - psutil.boot_time(),
    }

async def check_redis() -> Dict[str, Any]:
    """Check Redis connectivity."""
    result = {"status": "ok"}
    
    try:
        r = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            socket_connect_timeout=2,
        )
        ping_result = r.ping()
        if not ping_result:
            result["status"] = "error"
            result["error"] = "Redis ping failed"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

async def check_elasticsearch() -> Dict[str, Any]:
    """Check Elasticsearch connectivity."""
    result = {"status": "ok"}
    
    if not (settings.ELASTICSEARCH_HOST and settings.ELASTICSEARCH_PORT):
        result["status"] = "disabled"
        return result
    
    try:
        es = elasticsearch.Elasticsearch(
            [f"{settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}"],
            request_timeout=2
        )
        health = es.cluster.health()
        result["cluster_status"] = health.get("status")
        
        if health.get("status") == "red":
            result["status"] = "warning"
            result["warning"] = "Cluster health is red"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

async def check_database_stats(db: Session) -> Dict[str, Any]:
    """Get database statistics."""
    result = {
        "status": "ok",
        "tables": {},
        "connection_pool": {}
    }
    
    try:
        # Check connection pool
        pool_status = engine.pool.status()
        result["connection_pool"] = {
            "size": pool_status.size,
            "checked_in": pool_status.checkedin,
            "checked_out": pool_status.checkedout,
        }
        
        # Get table sizes
        tables = ["articles", "sources"]
        for table in tables:
            count_query = f"SELECT COUNT(*) FROM {table}"
            count = db.execute(count_query).scalar()
            result["tables"][table] = count
            
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        
    return result

@router.get("/", response_model=Dict[str, Any])
async def health_check(
    db: Session = Depends(get_db),
    force_refresh: bool = Query(False, description="Force a refresh of the health check"),
) -> Any:
    """
    Check system health, including database connectivity and services.
    """
    # Check cache if not forced to refresh
    if not force_refresh and health_cache["last_check"]:
        cache_age = datetime.now() - health_cache["last_check"]
        if cache_age < timedelta(seconds=30):  # Cache for 30 seconds
            return health_cache["result"]
    
    health_status = {
        "status": "healthy",
        "api": "ok",
        "database": "ok",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "timestamp": datetime.now().isoformat(),
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
            
            # Get additional Celery stats
            stats = i.stats()
            registered_tasks = i.registered()
            scheduled = i.scheduled()
            
            health_status["services"]["task_queue_details"] = {
                "workers": len(stats) if stats else 0,
                "tasks_registered": sum(len(tasks) for worker, tasks in registered_tasks.items()) if registered_tasks else 0,
                "tasks_scheduled": sum(len(tasks) for worker, tasks in scheduled.items()) if scheduled else 0,
            }
        else:
            health_status["services"]["task_queue"] = "error"
            health_status["services"]["task_queue_error"] = "No response from Celery workers"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["services"]["task_queue"] = "error"
        health_status["services"]["task_queue_error"] = str(e)
        health_status["status"] = "degraded"
    
    # Check Redis
    redis_status = await check_redis()
    health_status["services"]["redis"] = redis_status["status"]
    if redis_status["status"] != "ok":
        health_status["services"]["redis_error"] = redis_status.get("error", "Unknown error")
        health_status["status"] = "degraded"
    
    # Check Elasticsearch if configured
    if settings.ELASTICSEARCH_HOST:
        es_status = await check_elasticsearch()
        health_status["services"]["elasticsearch"] = es_status["status"]
        if es_status["status"] not in ["ok", "disabled"]:
            health_status["services"]["elasticsearch_error"] = es_status.get("error", es_status.get("warning", "Unknown error"))
            health_status["status"] = health_status["status"] if es_status["status"] == "warning" else "degraded"
    
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
    
    # Update cache
    health_cache["last_check"] = datetime.now()
    health_cache["result"] = health_status
    
    return health_status

@router.get("/status", response_model=Dict[str, Any])
async def service_status(
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
    include_system_info: bool = Query(False, description="Include detailed system information"),
    force_refresh: bool = Query(False, description="Force a refresh of the status check"),
) -> Any:
    """
    Get detailed system status, including article and source statistics.
    """
    # Check cache if not forced to refresh
    if not force_refresh and health_cache["last_detailed_check"]:
        cache_age = datetime.now() - health_cache["last_detailed_check"]
        if cache_age < timedelta(seconds=60):  # Cache for 60 seconds
            result = health_cache["detailed_status"]
            
            # Add system info if requested
            if include_system_info and "system" not in result:
                result["system"] = get_system_info()
                
            return result
    
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
    
    # Get recent article stats
    day_ago = datetime.now() - timedelta(days=1)
    week_ago = datetime.now() - timedelta(days=7)
    
    articles_24h = db.query(article.model).filter(article.model.created_at >= day_ago).count()
    articles_7d = db.query(article.model).filter(article.model.created_at >= week_ago).count()
    
    # Database stats
    db_stats = await check_database_stats(db)
    
    # Calculate average processing time (stub for now)
    avg_processing_time = 60  # seconds
    
    result = {
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENVIRONMENT,
        "article_stats": article_stats,
        "total_articles": sum(article_stats.values()),
        "recent_activity": {
            "articles_24h": articles_24h,
            "articles_7d": articles_7d,
        },
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
        },
        "database": db_stats
    }
    
    # Add system info if requested
    if include_system_info:
        result["system"] = get_system_info()
    
    # Update cache
    health_cache["last_detailed_check"] = datetime.now()
    health_cache["detailed_status"] = result
    
    return result

@router.get("/metrics", response_model=Dict[str, Any])
async def application_metrics(
    db: Session = Depends(get_db),
) -> Any:
    """
    Get application metrics for monitoring dashboards.
    
    This endpoint provides metrics specifically formatted for visualization systems.
    """
    # Get basic stats
    article_count = db.query(article.model).count()
    source_count = db.query(source.model).count()
    
    # Get status distribution
    status_counts = {}
    for status in ["draft", "processing", "published", "rejected", "error"]:
        status_counts[status] = db.query(article.model).filter(article.model.status == status).count()
    
    # Get time-based metrics (last 30 days)
    days_back = 30
    daily_counts = []
    
    for day in range(days_back, -1, -1):
        day_date = datetime.now() - timedelta(days=day)
        next_day = day_date + timedelta(days=1)
        
        # Format date as YYYY-MM-DD
        day_str = day_date.strftime("%Y-%m-%d")
        
        # Count articles created on this day
        day_count = db.query(article.model).filter(
            article.model.created_at >= day_date,
            article.model.created_at < next_day
        ).count()
        
        daily_counts.append({
            "date": day_str,
            "count": day_count
        })
    
    # Get top sources by article count
    top_sources_query = """
        SELECT s.name, COUNT(a.id) as article_count
        FROM sources s
        JOIN articles a ON s.id = a.source_id
        GROUP BY s.name
        ORDER BY article_count DESC
        LIMIT 10
    """
    top_sources = []
    
    try:
        top_sources_results = db.execute(top_sources_query).fetchall()
        top_sources = [{"name": row[0], "article_count": row[1]} for row in top_sources_results]
    except Exception as e:
        logger.error(f"Error fetching top sources: {e}")
    
    return {
        "counts": {
            "articles": article_count,
            "sources": source_count,
        },
        "status_distribution": status_counts,
        "daily_article_counts": daily_counts,
        "top_sources": top_sources
    }

@router.post("/test-alert", response_model=Dict[str, Any])
async def test_alert() -> Any:
    """
    Test the alerting system by generating a test alert.
    
    This is used to verify that the monitoring and alerting system is working.
    """
    # Log a test error to trigger alert systems
    logger.error("TEST ALERT: This is a test of the alerting system. No action needed.")
    
    # If using Sentry, can trigger a test exception
    if settings.SENTRY_DSN:
        try:
            # Intentionally raise an exception that will be caught by Sentry
            raise ValueError("TEST ALERT: This is a test exception for the alerting system.")
        except ValueError as e:
            import sentry_sdk
            sentry_sdk.capture_exception(e)
    
    return {
        "status": "success",
        "message": "Test alert triggered successfully."
    }