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
    category: Optional[str] = None
    feed_url: Optional[HttpUrl] = None

# Properties to receive on source creation
class SourceCreate(SourceBase):
    pass

# Properties to receive on source update
class SourceUpdate(SourceBase):
    name: Optional[str] = None
    url: Optional[HttpUrl] = None
    reliability_score: Optional[float] = None
    bias_score: Optional[float] = None

# Properties shared by models stored in DB
class SourceInDBBase(SourceBase):
    id: str
    reliability_score: float
    bias_score: float
    
    class Config:
        orm_mode = True

# Properties to return to client
class Source(SourceInDBBase):
    logo_url: Optional[str] = None
    last_crawled_at: Optional[datetime] = None

# Properties stored in DB
class SourceInDB(SourceInDBBase):
    scraper_config: Optional[Dict[str, Any]] = None
    crawl_frequency: Optional[float] = None
    sensationalism_score: Optional[float] = None
    subcategories: Optional[List[str]] = None