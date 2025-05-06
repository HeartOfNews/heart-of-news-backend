"""
API endpoints for system health monitoring
"""

from typing import Any, Dict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
def health_check(
    db: Session = Depends(get_db),
) -> Any:
    """
    Check system health, including database connectivity.
    """
    health_status = {
        "status": "healthy",
        "api": "ok",
        "database": "ok",
        "version": "0.1.0",
    }
    
    try:
        # Check database connectivity
        db.execute("SELECT 1")
    except Exception as e:
        health_status["database"] = "error"
        health_status["database_error"] = str(e)
        health_status["status"] = "unhealthy"
    
    return health_status