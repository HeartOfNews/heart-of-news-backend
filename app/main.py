"""
Heart of News Backend Application - Main entry point
"""

import asyncio
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.api import api_router
from app.services.tasks.task_queue import task_queue


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await task_queue.start_workers()
    yield
    # Shutdown
    await task_queue.stop_workers()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Heart of News - AI-powered propaganda-free news aggregation",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)