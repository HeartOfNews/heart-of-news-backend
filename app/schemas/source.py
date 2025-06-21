"""
Pydantic schemas for source data validation
"""

from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, HttpUrl

# Shared properties
class SourceBase(BaseModel):
    name: str
    url: HttpUrl
    feed_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    category: Optional[str] = None
    subcategories: Optional[List[str]] = None

# Properties to receive on source creation
class SourceCreate(SourceBase):
    scraper_config: Optional[Dict[str, Any]] = None
    crawl_frequency: Optional[float] = None  # in hours

# Properties to receive on source update
class SourceUpdate(BaseModel):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    feed_url: Optional[HttpUrl] = None
    logo_url: Optional[HttpUrl] = None
    category: Optional[str] = None
    subcategories: Optional[List[str]] = None
    scraper_config: Optional[Dict[str, Any]] = None
    crawl_frequency: Optional[float] = None
    reliability_score: Optional[float] = None
    bias_score: Optional[float] = None
    sensationalism_score: Optional[float] = None

# Properties shared by models stored in DB
class SourceInDBBase(SourceBase):
    id: str
    reliability_score: float
    bias_score: float
    sensationalism_score: float
    last_crawled_at: Optional[datetime] = None
    crawl_frequency: float
    
    class Config:
        orm_mode = True

# Properties to return to client
class Source(SourceInDBBase):
    pass

# Properties stored in DB
class SourceInDB(SourceInDBBase):
    scraper_config: Optional[Dict[str, Any]] = None