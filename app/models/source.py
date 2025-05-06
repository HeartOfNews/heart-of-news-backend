"""
SQLAlchemy models for news sources
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Source(Base):
    """
    Source model representing a news source
    """
    __tablename__ = "sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, index=True)
    feed_url = Column(String)
    logo_url = Column(String)
    
    # Categorization
    category = Column(String)
    subcategories = Column(JSON)
    
    # Source evaluation
    reliability_score = Column(Float, default=0.0)
    bias_score = Column(Float, default=0.0)
    sensationalism_score = Column(Float, default=0.0)
    
    # Scraping metadata
    scraper_config = Column(JSON)
    last_crawled_at = Column(DateTime)
    crawl_frequency = Column(Float)  # in hours
    
    # Relationships
    articles = relationship("Article", back_populates="source")
    
    def __repr__(self):
        return f"<Source {self.name}>"