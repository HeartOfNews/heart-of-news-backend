"""
Heart of News Backend Application - Main entry point
"""

import os
import logging
import asyncio
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from prometheus_client.exposition import start_http_server
import sentry_sdk
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.monitoring import (
    configure_logging, 
    init_sentry, 
    PrometheusMiddleware,
    get_prometheus_registry
)
from app.api.v1.api import api_router

# Configure logging
logger = configure_logging()

# Set up metrics directory for multiprocess metrics
if settings.ENABLE_METRICS:
    os.makedirs(settings.PROMETHEUS_MULTIPROC_DIR, exist_ok=True)
    os.environ["PROMETHEUS_MULTIPROC_DIR"] = settings.PROMETHEUS_MULTIPROC_DIR

# Initialize Sentry if configured
if settings.SENTRY_DSN:
    init_sentry()

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} in {settings.ENVIRONMENT} environment")
    
    # Start metrics server if enabled
    prometheus_server = None
    if settings.ENABLE_METRICS and not settings.TESTING:
        try:
            # Start Prometheus metrics server on a separate port
            registry = get_prometheus_registry()
            prometheus_server = start_http_server(9090, registry=registry)
            logger.info("Started Prometheus metrics server on port 9090")
        except Exception as e:
            logger.error(f"Failed to start Prometheus metrics server: {e}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")
    
    # Shutdown metrics server if it was started
    if prometheus_server:
        prometheus_server.shutdown()
        logger.info("Stopped Prometheus metrics server")

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API for Heart of News - AI-powered propaganda-free news aggregation",
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# Configure middleware
if settings.ENABLE_METRICS:
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware)
    
    # Create metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handling middleware
class ErrorLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            # Log the error
            logger.exception(f"Uncaught exception: {str(e)}")
            
            # Capture with Sentry if available
            if settings.SENTRY_DSN:
                sentry_sdk.capture_exception(e)
                
            # Return JSON error response
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"}
            )

app.add_middleware(ErrorLoggingMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint that can be used by load balancers.
    More detailed health information is available at /api/v1/health/
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG,
        log_level=settings.UVICORN_LOG_LEVEL.lower(),
    )