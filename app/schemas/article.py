"""
Pydantic schemas for article data validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, HttpUrl

from app.schemas.source import SourceBase

# Shared properties
class ArticleBase(BaseModel):
    title: str
    summary: Optional[str] = None
    content: Optional[str] = None
    url: HttpUrl
    published_at: Optional[datetime] = None

# Properties to receive on article creation
class ArticleCreate(ArticleBase):
    source: Dict[str, Any]

# Properties to receive on article update
class ArticleUpdate(ArticleBase):
    title: Optional[str] = None
    url: Optional[HttpUrl] = None

# Properties shared by models stored in DB
class ArticleInDBBase(ArticleBase):
    id: str
    source: Dict[str, Any]
    discovered_at: datetime
    status: str

    class Config:
        orm_mode = True

# Properties to return to client
class Article(ArticleInDBBase):
    pass

# Properties stored in DB
class ArticleInDB(ArticleInDBBase):
    political_bias: Optional[float] = None
    emotional_language: Optional[float] = None
    fact_opinion_ratio: Optional[float] = None
    entities: Optional[List[Dict[str, Any]]] = None
    topics: Optional[List[Dict[str, Any]]] = None
    sentiment_score: Optional[float] = None