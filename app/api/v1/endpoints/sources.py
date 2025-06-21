"""
API endpoints for news source management
"""

from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.source import Source, SourceCreate, SourceUpdate
from app.crud import source as crud_source

router = APIRouter()

@router.get("/", response_model=List[Source])
def read_sources(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    category: str = None,
) -> Any:
    """
    Retrieve news sources with optional filtering.
    """
    sources = crud_source.get_sources(
        db=db, 
        skip=skip, 
        limit=limit, 
        category=category
    )
    return sources

@router.get("/{source_id}", response_model=Source)
def read_source(
    source_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific news source by ID.
    """
    source = crud_source.get_source(db=db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.post("/", response_model=Source)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Create a new news source (admin only).
    """
    # Check if source already exists
    existing_source = crud_source.get_source_by_url(db=db, url=str(source_in.url))
    if existing_source:
        raise HTTPException(status_code=400, detail="Source with this URL already exists")
    
    source = crud_source.create_source(db=db, source=source_in)
    return source

@router.put("/{source_id}", response_model=Source)
def update_source(
    source_id: str,
    source_in: SourceUpdate,
    db: Session = Depends(get_db),
) -> Any:
    """
    Update a news source (admin only).
    """
    source = crud_source.update_source(db=db, source_id=source_id, source_update=source_in)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.delete("/{source_id}")
def delete_source(
    source_id: str,
    db: Session = Depends(get_db),
) -> Any:
    """
    Delete a news source (admin only).
    """
    success = crud_source.delete_source(db=db, source_id=source_id)
    if not success:
        raise HTTPException(status_code=404, detail="Source not found")
    return {"message": "Source deleted successfully"}