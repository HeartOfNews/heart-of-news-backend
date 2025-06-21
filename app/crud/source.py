"""
CRUD operations for news sources
"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.source import Source
from app.schemas.source import SourceCreate, SourceUpdate


def get_source(db: Session, source_id: str) -> Optional[Source]:
    """Get a single source by ID"""
    return db.query(Source).filter(Source.id == source_id).first()


def get_source_by_url(db: Session, url: str) -> Optional[Source]:
    """Get a source by URL"""
    return db.query(Source).filter(Source.url == url).first()


def get_sources(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None
) -> List[Source]:
    """Get sources with optional filtering"""
    query = db.query(Source)
    
    if category:
        query = query.filter(Source.category == category)
    
    return query.offset(skip).limit(limit).all()


def create_source(db: Session, source: SourceCreate) -> Source:
    """Create a new source"""
    db_source = Source(
        name=source.name,
        url=str(source.url),
        feed_url=str(source.feed_url) if source.feed_url else None,
        logo_url=str(source.logo_url) if source.logo_url else None,
        category=source.category,
        subcategories=source.subcategories,
        scraper_config=source.scraper_config,
        crawl_frequency=source.crawl_frequency or 24.0,  # Default 24 hours
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


def update_source(db: Session, source_id: str, source_update: SourceUpdate) -> Optional[Source]:
    """Update an existing source"""
    db_source = get_source(db, source_id)
    if not db_source:
        return None
    
    update_data = source_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["url", "feed_url", "logo_url"] and value:
            setattr(db_source, field, str(value))
        else:
            setattr(db_source, field, value)
    
    db.commit()
    db.refresh(db_source)
    return db_source


def delete_source(db: Session, source_id: str) -> bool:
    """Delete a source"""
    db_source = get_source(db, source_id)
    if not db_source:
        return False
    
    db.delete(db_source)
    db.commit()
    return True


def update_source_scores(
    db: Session,
    source_id: str,
    reliability_score: Optional[float] = None,
    bias_score: Optional[float] = None,
    sensationalism_score: Optional[float] = None
) -> Optional[Source]:
    """Update evaluation scores for a source"""
    db_source = get_source(db, source_id)
    if not db_source:
        return None
    
    if reliability_score is not None:
        db_source.reliability_score = reliability_score
    if bias_score is not None:
        db_source.bias_score = bias_score
    if sensationalism_score is not None:
        db_source.sensationalism_score = sensationalism_score
    
    db.commit()
    db.refresh(db_source)
    return db_source


def update_last_crawled(db: Session, source_id: str) -> Optional[Source]:
    """Update the last crawled timestamp for a source"""
    db_source = get_source(db, source_id)
    if not db_source:
        return None
    
    db_source.last_crawled_at = datetime.utcnow()
    db.commit()
    db.refresh(db_source)
    return db_source