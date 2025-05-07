"""
API endpoints for article management
"""

from datetime import datetime
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.crud import article, source
from app.schemas.article import Article, ArticleCreate, ArticleUpdate
from app.services.ai.bias_detector import BiasDetector

router = APIRouter()

@router.get("/", response_model=List[Article])
def read_articles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    order_by: str = "published_at",
    desc: bool = True,
) -> Any:
    """
    Retrieve articles with optional filtering.
    
    - **skip**: Number of articles to skip (for pagination)
    - **limit**: Maximum number of articles to return
    - **source_id**: Filter by source ID
    - **status**: Filter by article status (draft, processing, published, rejected)
    - **search**: Search term in title and content
    - **from_date**: Filter by published date >= from_date
    - **to_date**: Filter by published date <= to_date
    - **order_by**: Field to order by (published_at, discovered_at, title)
    - **desc**: Sort order, True for descending, False for ascending
    """
    articles = article.get_multi_with_filters(
        db=db,
        skip=skip,
        limit=limit,
        source_id=source_id,
        status=status,
        search_term=search,
        from_date=from_date,
        to_date=to_date,
        order_by=order_by,
        order_desc=desc
    )
    return articles

@router.get("/{article_id}", response_model=Article)
def read_article(
    article_id: str = Path(..., description="The ID of the article to retrieve"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific article by ID.
    """
    db_article = article.get_with_source(db=db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    return db_article

@router.post("/", response_model=Article)
def create_article(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new article (admin only).
    
    This endpoint allows manual creation of articles.
    For automatic article creation from scrapers, use the scraper service directly.
    """
    # Validate source exists
    source_dict = article_in.source
    source_id = source_dict.get("id")
    if not source_id:
        raise HTTPException(
            status_code=400,
            detail="Source ID is required",
        )
    
    db_source = source.get(db=db, id=source_id)
    if not db_source:
        raise HTTPException(
            status_code=404,
            detail="Source not found",
        )
    
    # Check if article with this URL already exists
    existing_article = article.get_by_url(db=db, url=str(article_in.url))
    if existing_article:
        raise HTTPException(
            status_code=400,
            detail="Article with this URL already exists",
        )
    
    # Create the article
    db_article = article.create_with_source_id(
        db=db, 
        obj_in=article_in, 
        source_id=source_id
    )
    
    return db_article

@router.put("/{article_id}", response_model=Article)
def update_article(
    article_in: ArticleUpdate,
    article_id: str = Path(..., description="The ID of the article to update"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Update an article (admin only).
    """
    db_article = article.get(db=db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    
    db_article = article.update(db=db, db_obj=db_article, obj_in=article_in)
    return db_article

@router.post("/{article_id}/analyze", response_model=Article)
async def analyze_article(
    article_id: str = Path(..., description="The ID of the article to analyze"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Analyze an article for bias and update its metrics.
    """
    db_article = article.get(db=db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    
    if not db_article.content:
        raise HTTPException(
            status_code=400,
            detail="Article has no content to analyze",
        )
    
    # Initialize bias detector
    detector = BiasDetector()
    
    # Analyze the article
    analysis = await detector.get_full_bias_analysis(db_article.content)
    
    # Update the article with the analysis results
    db_article = article.update_bias_metrics(
        db=db,
        db_obj=db_article,
        political_bias=analysis["political_bias"],
        emotional_language=analysis["emotional_language"],
        fact_opinion_ratio=analysis["fact_opinion_ratio"]
    )
    
    # Update status to processing
    db_article = article.update_status(
        db=db,
        db_obj=db_article,
        status="processing"
    )
    
    return db_article

@router.delete("/{article_id}", response_model=Article)
def delete_article(
    article_id: str = Path(..., description="The ID of the article to delete"),
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete an article (admin only).
    """
    db_article = article.get(db=db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=404,
            detail="Article not found",
        )
    
    db_article = article.remove(db=db, id=article_id)
    return db_article