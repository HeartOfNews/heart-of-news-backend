"""
CRUD operations for Source model
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, or_, desc
from sqlalchemy.orm import Session

from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate
from app.crud.base import CRUDBase


class CRUDSource(CRUDBase[Source, SourceCreate, SourceUpdate]):
    """
    CRUD operations for Source model
    """
    
    def get_by_name(self, db: Session, name: str) -> Optional[Source]:
        """
        Get source by name
        
        Args:
            db: Database session
            name: Source name
            
        Returns:
            Source or None if not found
        """
        return db.query(Source).filter(Source.name == name).first()
    
    def get_by_url(self, db: Session, url: str) -> Optional[Source]:
        """
        Get source by URL
        
        Args:
            db: Database session
            url: Source URL
            
        Returns:
            Source or None if not found
        """
        return db.query(Source).filter(Source.url == url).first()
    
    def get_multi_with_filters(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        category: Optional[str] = None,
        search_term: Optional[str] = None,
        min_reliability: Optional[float] = None,
        max_bias: Optional[float] = None
    ) -> List[Source]:
        """
        Get multiple sources with filters
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            category: Filter by category
            search_term: Search in name
            min_reliability: Filter by minimum reliability score
            max_bias: Filter by maximum absolute bias score
            
        Returns:
            List of sources matching the filters
        """
        query = db.query(Source)
        
        # Apply filters
        if category:
            query = query.filter(Source.category == category)
            
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(Source.name.ilike(search_pattern))
            
        if min_reliability is not None:
            query = query.filter(Source.reliability_score >= min_reliability)
            
        if max_bias is not None:
            # Filter by absolute value of bias_score
            query = query.filter(
                and_(
                    Source.bias_score >= -max_bias,
                    Source.bias_score <= max_bias
                )
            )
        
        # Apply ordering (most reliable first)
        query = query.order_by(desc(Source.reliability_score))
        
        # Apply pagination
        return query.offset(skip).limit(limit).all()
    
    def update_crawl_timestamp(
        self,
        db: Session,
        *,
        db_obj: Source,
        timestamp: Optional[datetime] = None
    ) -> Source:
        """
        Update the last_crawled_at timestamp
        
        Args:
            db: Database session
            db_obj: Source to update
            timestamp: Timestamp to set (defaults to current time)
            
        Returns:
            The updated source
        """
        db_obj.last_crawled_at = timestamp or datetime.utcnow()
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_sources_for_crawling(
        self,
        db: Session,
        *,
        limit: int = 5
    ) -> List[Source]:
        """
        Get sources that need to be crawled
        
        Args:
            db: Database session
            limit: Maximum number of sources to return
            
        Returns:
            List of sources to crawl
        """
        now = datetime.utcnow()
        
        # Get sources that have never been crawled first
        never_crawled = (
            db.query(Source)
            .filter(Source.last_crawled_at.is_(None))
            .limit(limit)
            .all()
        )
        
        if len(never_crawled) >= limit:
            return never_crawled
        
        # If we still have room, get sources that need to be crawled based on frequency
        remaining = limit - len(never_crawled)
        
        # This query gets sources where current time > last_crawled_at + crawl_frequency (in hours)
        needs_crawling = (
            db.query(Source)
            .filter(Source.last_crawled_at.isnot(None))
            .filter(
                Source.last_crawled_at + Source.crawl_frequency * 3600 < now
            )
            .order_by(Source.last_crawled_at.asc())  # Oldest first
            .limit(remaining)
            .all()
        )
        
        return never_crawled + needs_crawling
    
    def update_evaluation_scores(
        self,
        db: Session,
        *,
        db_obj: Source,
        reliability_score: Optional[float] = None,
        bias_score: Optional[float] = None,
        sensationalism_score: Optional[float] = None
    ) -> Source:
        """
        Update the evaluation scores for a source
        
        Args:
            db: Database session
            db_obj: Source to update
            reliability_score: New reliability score
            bias_score: New bias score
            sensationalism_score: New sensationalism score
            
        Returns:
            The updated source
        """
        if reliability_score is not None:
            db_obj.reliability_score = reliability_score
            
        if bias_score is not None:
            db_obj.bias_score = bias_score
            
        if sensationalism_score is not None:
            db_obj.sensationalism_score = sensationalism_score
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


source = CRUDSource(Source)