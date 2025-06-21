"""
CRUD operations for articles
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.article import Article
from app.schemas.article import ArticleCreate, ArticleUpdate


def get_article(db: Session, article_id: str) -> Optional[Article]:
    """Get a single article by ID"""
    return db.query(Article).filter(Article.id == article_id).first()


def get_articles(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    source_id: Optional[str] = None,
    status: str = "published"
) -> List[Article]:
    """Get articles with optional filtering"""
    query = db.query(Article).filter(Article.status == status)
    
    if source_id:
        query = query.filter(Article.source_id == source_id)
    
    # TODO: Add category filtering when categories are implemented
    
    return query.order_by(desc(Article.published_at)).offset(skip).limit(limit).all()


def create_article(db: Session, article: ArticleCreate) -> Article:
    """Create a new article"""
    db_article = Article(
        title=article.title,
        summary=article.summary,
        content=article.content,
        original_url=str(article.url),
        published_at=article.published_at,
        source_id=article.source.get("id") if article.source else None,
    )
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


def update_article(db: Session, article_id: str, article_update: ArticleUpdate) -> Optional[Article]:
    """Update an existing article"""
    db_article = get_article(db, article_id)
    if not db_article:
        return None
    
    update_data = article_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field == "url":
            setattr(db_article, "original_url", str(value))
        else:
            setattr(db_article, field, value)
    
    db.commit()
    db.refresh(db_article)
    return db_article


def delete_article(db: Session, article_id: str) -> bool:
    """Delete an article"""
    db_article = get_article(db, article_id)
    if not db_article:
        return False
    
    db.delete(db_article)
    db.commit()
    return True


def update_article_bias_analysis(
    db: Session, 
    article_id: str, 
    political_bias: float,
    emotional_language: float,
    fact_opinion_ratio: float
) -> Optional[Article]:
    """Update bias analysis fields for an article"""
    db_article = get_article(db, article_id)
    if not db_article:
        return None
    
    db_article.political_bias = political_bias
    db_article.emotional_language = emotional_language
    db_article.fact_opinion_ratio = fact_opinion_ratio
    
    db.commit()
    db.refresh(db_article)
    return db_article