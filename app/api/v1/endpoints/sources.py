"""
API endpoints for news source management
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path, Body
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import source, article
from app.schemas.source import Source, SourceCreate, SourceUpdate
from app.schemas.article import ArticleCreate
from app.services.scraper.factory import ScraperFactory
from app.services.scraper.manager import ScraperManager

router = APIRouter()

@router.get("/", response_model=List[Source])
def read_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_reliability: Optional[float] = None,
    max_bias: Optional[float] = None,
) -> Any:
    """
    Retrieve news sources with optional filtering.
    
    - **skip**: Number of sources to skip (for pagination)
    - **limit**: Maximum number of sources to return
    - **category**: Filter by source category
    - **search**: Search by source name
    - **min_reliability**: Filter by minimum reliability score (0.0-1.0)
    - **max_bias**: Filter by maximum absolute bias score (0.0-1.0)
    """
    sources = source.get_multi_with_filters(
        db=db,
        skip=skip,
        limit=limit,
        category=category,
        search_term=search,
        min_reliability=min_reliability,
        max_bias=max_bias
    )
    return sources

@router.get("/{source_id}", response_model=Source)
def read_source(
    source_id: str = Path(..., description="The ID of the source to retrieve"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific news source by ID.
    """
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )
    return db_source

@router.post("/", response_model=Source)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new news source (admin only).
    """
    # Check if source with this name already exists
    db_source = source.get_by_name(db=db, name=source_in.name)
    if db_source:
        raise HTTPException(
            status_code=400,
            detail="Source with this name already exists"
        )
    
    # Check if source with this URL already exists
    db_source = source.get_by_url(db=db, url=str(source_in.url))
    if db_source:
        raise HTTPException(
            status_code=400,
            detail="Source with this URL already exists"
        )
    
    return source.create(db=db, obj_in=source_in)

@router.put("/{source_id}", response_model=Source)
def update_source(
    source_in: SourceUpdate,
    source_id: str = Path(..., description="The ID of the source to update"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update a news source (admin only).
    """
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )
    
    # If name is being updated, check if new name is already taken
    if source_in.name and source_in.name != db_source.name:
        db_source_with_name = source.get_by_name(db=db, name=source_in.name)
        if db_source_with_name:
            raise HTTPException(
                status_code=400,
                detail="Source with this name already exists"
            )
    
    # If URL is being updated, check if new URL is already taken
    if source_in.url and str(source_in.url) != db_source.url:
        db_source_with_url = source.get_by_url(db=db, url=str(source_in.url))
        if db_source_with_url:
            raise HTTPException(
                status_code=400,
                detail="Source with this URL already exists"
            )
    
    return source.update(db=db, db_obj=db_source, obj_in=source_in)

@router.delete("/{source_id}", response_model=Source)
def delete_source(
    source_id: str = Path(..., description="The ID of the source to delete"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete a news source (admin only).
    """
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )
    
    return source.remove(db=db, id=source_id)

@router.post("/{source_id}/scrape", response_model=Dict[str, Any])
async def scrape_source(
    source_id: str = Path(..., description="The ID of the source to scrape"),
    limit: int = Query(10, description="Maximum number of articles to scrape"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Manually trigger a scrape operation for a specific source.
    
    This will scrape articles from the source and store them in the database.
    """
    # Get the source
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )
    
    # Create source configuration for the scraper
    source_config = {
        "id": str(db_source.id),
        "name": db_source.name,
        "url": db_source.url,
        "feed_url": db_source.feed_url
    }
    
    # Add scraper config if available
    if db_source.scraper_config:
        source_config.update(db_source.scraper_config)
    
    # Create a scraper for this source
    scraper = ScraperFactory.create_scraper(source_config)
    if not scraper:
        raise HTTPException(
            status_code=500,
            detail="Failed to create scraper for this source"
        )
    
    # Scrape articles
    try:
        articles_data = await scraper.fetch_articles(limit=limit)
        
        # Process articles
        new_articles = []
        for article_data in articles_data:
            # Check if article already exists
            existing = article.get_by_url(db=db, url=str(article_data.url))
            if existing:
                continue
            
            # Create new article object
            new_article = {
                "url": article_data.url,
                "title": article_data.title,
                "summary": article_data.summary,
                "content": article_data.content,
                "published_at": article_data.published_at,
                "source": {"id": str(db_source.id)}
            }
            
            # Create the article in DB
            db_article = article.create_with_source_id(
                db=db,
                obj_in=ArticleCreate(**new_article),
                source_id=str(db_source.id)
            )
            
            new_articles.append({
                "id": str(db_article.id),
                "title": db_article.title,
                "url": db_article.original_url
            })
        
        # Update source last_crawled_at timestamp
        source.update_crawl_timestamp(db=db, db_obj=db_source)
        
        return {
            "source": {
                "id": str(db_source.id),
                "name": db_source.name
            },
            "articles_scraped": len(articles_data),
            "new_articles": len(new_articles),
            "article_details": new_articles
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping source: {str(e)}"
        )

@router.post("/{source_id}/evaluate", response_model=Source)
async def evaluate_source(
    source_id: str = Path(..., description="The ID of the source to evaluate"),
    reliability_score: Optional[float] = Body(None, ge=0.0, le=1.0),
    bias_score: Optional[float] = Body(None, ge=-1.0, le=1.0),
    sensationalism_score: Optional[float] = Body(None, ge=0.0, le=1.0),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update evaluation scores for a source (admin only).
    
    - **reliability_score**: Source reliability score (0.0-1.0)
    - **bias_score**: Source political bias score (-1.0 to 1.0)
    - **sensationalism_score**: Source sensationalism score (0.0-1.0)
    """
    # Get the source
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found"
        )
    
    # Update evaluation scores
    db_source = source.update_evaluation_scores(
        db=db,
        db_obj=db_source,
        reliability_score=reliability_score,
        bias_score=bias_score,
        sensationalism_score=sensationalism_score
    )
    
    return db_source