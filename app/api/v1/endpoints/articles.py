"""
API endpoints for article management
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.article import Article, ArticleCreate, ArticleUpdate
from app.crud import article as crud_article

router = APIRouter()

@router.get("/", response_model=List[Article])
def read_articles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    source_id: str = None,
) -> Any:
    """
    Retrieve articles with optional filtering.
    """
    articles = crud_article.get_articles(
        db=db, 
        skip=skip, 
        limit=limit, 
        category=category, 
        source_id=source_id
    )
    return articles

@router.get("/{article_id}", response_model=Article)
def read_article(
    article_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific article by ID.
    """
    article = crud_article.get_article(db=db, article_id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.post("/", response_model=Article)
def create_article(
    article_in: ArticleCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new article (admin only).
    """
    article = crud_article.create_article(db=db, article=article_in)
    return article

@router.put("/{article_id}", response_model=Article)
def update_article(
    article_id: str,
    article_in: ArticleUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Update an article (admin only).
    """
    article = crud_article.update_article(db=db, article_id=article_id, article_update=article_in)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.delete("/{article_id}")
def delete_article(
    article_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete an article (admin only).
    """
    success = crud_article.delete_article(db=db, article_id=article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}