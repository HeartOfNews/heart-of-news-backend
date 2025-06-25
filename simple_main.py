"""
Simplified Heart of News Backend Application - Demo version without AI dependencies
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Heart of News - AI-powered propaganda-free news aggregation (Demo Version)",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Heart of News Backend API - Demo Version",
        "status": "running",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api": "ok",
        "version": settings.VERSION,
        "mode": "demo"
    }

@app.get("/api/v1/info")
async def api_info():
    return {
        "api_version": "v1",
        "features": [
            "News aggregation",
            "Bias detection",
            "Multi-platform publishing",
            "Content categorization"
        ],
        "status": "demo_mode",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "openapi": "/api/v1/openapi.json"
        }
    }

# Demo endpoints for testing
@app.get("/api/v1/articles")
async def get_articles():
    return {
        "articles": [
            {
                "id": "demo-1",
                "title": "Heart of News Demo Article",
                "content": "This is a demo article showing the API structure",
                "source": "Demo Source",
                "bias_score": 0.1,
                "created_at": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "mode": "demo"
    }

@app.get("/api/v1/sources")
async def get_sources():
    return {
        "sources": [
            {
                "id": "demo-source-1",
                "name": "Demo News Source",
                "url": "https://example.com",
                "status": "active",
                "last_scraped": "2024-01-01T00:00:00Z"
            }
        ],
        "total": 1,
        "mode": "demo"
    }

if __name__ == "__main__":
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)