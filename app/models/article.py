"""
SQLAlchemy models for articles
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import Column, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base

class Article(Base):
    """
    Article model representing a news article
    """
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    original_url = Column(String, index=True, nullable=False)
    title = Column(String, nullable=False)
    summary = Column(Text)
    content = Column(Text)
    
    # Source information
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"))
    source = relationship("Source", back_populates="articles")
    
    # Timestamps
    discovered_at = Column(DateTime, default=datetime.utcnow)
    published_at = Column(DateTime)
    
    # Content analysis fields
    entities = Column(JSON)
    topics = Column(JSON)
    sentiment_score = Column(Float)
    
    # Bias analysis
    political_bias = Column(Float)
    emotional_language = Column(Float)
    fact_opinion_ratio = Column(Float)
    
    # Publication status
    status = Column(String, default="draft")  # draft, processing, published, rejected
    
    def __repr__(self):
        return f"<Article {self.title}>"