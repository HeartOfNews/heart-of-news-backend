"""
CRUD operations for Article model
"""

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session, joinedload

from app.models.article import Article
from app.models.source import Source
from app.schemas.article import ArticleCreate, ArticleUpdate
from app.crud.base import CRUDBase


class CRUDArticle(CRUDBase[Article, ArticleCreate, ArticleUpdate]):
    """
    CRUD operations for Article model
    """
    
    def get_with_source(self, db: Session, id: Any) -> Optional[Article]:
        """
        Get article by ID with source data loaded
        
        Args:
            db: Database session
            id: Article ID
            
        Returns:
            Article with source or None if not found
        """
        return (
            db.query(Article)
            .options(joinedload(Article.source))
            .filter(Article.id == id)
            .first()
        )
    
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        source_id: Optional[str] = None,
        status: Optional[str] = None,
        search_term: Optional[str] = None,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        order_by: str = "published_at",
        order_desc: bool = True
    ) -> List[Article]:
        """
        Get multiple articles with filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            source_id: Filter by source ID
            status: Filter by article status
            search_term: Search in title and content
            from_date: Filter by published_at >= from_date
            to_date: Filter by published_at <= to_date
            order_by: Field to order by
            order_desc: Order descending if True, ascending if False
            
        Returns:
            List of articles matching the filters
        """
        query = db.query(Article).options(joinedload(Article.source))
        
        # Apply filters
        if source_id:
            query = query.filter(Article.source_id == uuid.UUID(source_id))
            
        if status:
            query = query.filter(Article.status == status)
            
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Article.title.ilike(search_pattern),
                    Article.content.ilike(search_pattern),
                    Article.summary.ilike(search_pattern)
                )
            )
            
        if from_date:
            query = query.filter(Article.published_at >= from_date)
            
        if to_date:
            query = query.filter(Article.published_at <= to_date)
        
        # Apply ordering
        if hasattr(Article, order_by):
            order_column = getattr(Article, order_by)
            if order_desc:
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(order_column)
        else:
            # Default ordering
            query = query.order_by(desc(Article.published_at))
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def create_with_source_id(
        self, db: Session, *, obj_in: ArticleCreate, source_id: str
    ) -> Article:
        """
        Create a new article with a given source ID
        
        Args:
            db: Database session
            obj_in: Article data
            source_id: Source ID
            
        Returns:
            The created article
        """
        obj_in_data = jsonable_encoder(obj_in, exclude={"source"})
        db_obj = Article(**obj_in_data, source_id=uuid.UUID(source_id))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_url(self, db: Session, url: str) -> Optional[Article]:
        """
        Get article by URL
        
        Args:
            db: Database session
            url: Article URL
            
        Returns:
            Article or None if not found
        """
        return db.query(Article).filter(Article.original_url == url).first()
    
    def update_bias_metrics(
        self,
        db: Session,
        *,
        db_obj: Article,
        political_bias: float,
        emotional_language: float,
        fact_opinion_ratio: float
    ) -> Article:
        """
        Update bias metrics for an article
        
        Args:
            db: Database session
            db_obj: Article to update
            political_bias: Political bias score
            emotional_language: Emotional language score
            fact_opinion_ratio: Fact vs opinion ratio
            
        Returns:
            The updated article
        """
        db_obj.political_bias = political_bias
        db_obj.emotional_language = emotional_language
        db_obj.fact_opinion_ratio = fact_opinion_ratio
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_status(
        self,
        db: Session,
        *,
        db_obj: Article,
        status: str
    ) -> Article:
        """
        Update article status
        
        Args:
            db: Database session
            db_obj: Article to update
            status: New status
            
        Returns:
            The updated article
        """
        db_obj.status = status
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_articles_for_processing(
        self,
        db: Session,
        *,
        limit: int = 10
    ) -> List[Article]:
        """
        Get articles in 'draft' status for processing
        
        Args:
            db: Database session
            limit: Maximum number of articles to return
            
        Returns:
            List of articles to process
        """
        return (
            db.query(Article)
            .filter(Article.status == "draft")
            .order_by(Article.discovered_at.asc())
            .limit(limit)
            .all()
        )


article = CRUDArticle(Article)