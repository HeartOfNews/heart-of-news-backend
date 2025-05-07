"""
API endpoints for background task management
"""

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Body

from app.worker import celery_app, scrape_sources, analyze_articles, publish_articles, import_default_sources

router = APIRouter()

@router.post("/scrape-sources", response_model=Dict[str, Any])
def trigger_scrape_sources(
    limit_per_source: int = Query(10, description="Maximum number of articles per source"),
    source_ids: Optional[List[str]] = Body(None, description="Optional list of source IDs")
) -> Any:
    """
    Trigger a background task to scrape sources
    
    - **limit_per_source**: Maximum number of articles to fetch per source
    - **source_ids**: Optional list of source IDs to scrape (if None, scrapes sources based on crawl frequency)
    """
    task = scrape_sources.delay(limit_per_source=limit_per_source, source_ids=source_ids)
    
    return {
        "task_id": task.id,
        "status": "started",
        "message": "Source scraping task initiated"
    }

@router.post("/analyze-articles", response_model=Dict[str, Any])
def trigger_analyze_articles(
    limit: int = Query(20, description="Maximum number of articles to analyze")
) -> Any:
    """
    Trigger a background task to analyze articles
    
    - **limit**: Maximum number of articles to analyze
    """
    task = analyze_articles.delay(limit=limit)
    
    return {
        "task_id": task.id,
        "status": "started",
        "message": "Article analysis task initiated"
    }

@router.post("/publish-articles", response_model=Dict[str, Any])
def trigger_publish_articles(
    limit: int = Query(20, description="Maximum number of articles to publish")
) -> Any:
    """
    Trigger a background task to publish articles
    
    - **limit**: Maximum number of articles to publish
    """
    task = publish_articles.delay(limit=limit)
    
    return {
        "task_id": task.id,
        "status": "started",
        "message": "Article publishing task initiated"
    }

@router.post("/import-sources", response_model=Dict[str, Any])
def trigger_import_default_sources() -> Any:
    """
    Trigger a background task to import default sources
    """
    task = import_default_sources.delay()
    
    return {
        "task_id": task.id,
        "status": "started",
        "message": "Default sources import task initiated"
    }

@router.get("/task/{task_id}", response_model=Dict[str, Any])
def get_task_status(task_id: str) -> Any:
    """
    Get the status of a background task
    
    - **task_id**: ID of the task to check
    """
    task = celery_app.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task.status
    }
    
    if task.ready():
        if task.successful():
            response["result"] = task.result
        else:
            response["error"] = str(task.result)
    
    return response