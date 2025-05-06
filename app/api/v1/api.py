"""
Main API Router for the Heart of News API
"""

from fastapi import APIRouter

from app.api.v1.endpoints import articles, sources, health

api_router = APIRouter()

api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(health.router, prefix="/health", tags=["health"])