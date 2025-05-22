"""
Heart of News Backend Application - Main entry point
"""

import os
import json
import logging
import asyncio
import time
from contextlib import asynccontextmanager
from typing import Callable

import uvicorn
from fastapi import FastAPI, Request, Response
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
from app.core.profiling import query_profiler, reset_query_stats
from app.core.cache import get_redis, cache_clear_all
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
    
    # Reset query statistics
    if settings.DB_ENABLE_QUERY_PROFILING:
        reset_query_stats()
        logger.info("Query profiling enabled")
    
    # Test Redis connection
    if settings.CACHE_ENABLED:
        try:
            redis_client = get_redis()
            redis_client.ping()
            logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            logger.warning("Caching will be disabled")
            settings.CACHE_ENABLED = False
    
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

# Database query profiling middleware
class QueryProfilingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.DB_ENABLE_QUERY_PROFILING:
            return await call_next(request)
            
        # Start profiling
        with query_profiler():
            return await call_next(request)

if settings.DB_ENABLE_QUERY_PROFILING:
    app.add_middleware(QueryProfilingMiddleware)

# Response caching middleware
class ResponseCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if not settings.CACHE_ENABLED:
            return await call_next(request)
            
        # Skip caching for non-GET requests
        if request.method != "GET":
            return await call_next(request)
            
        # Skip caching for certain paths
        no_cache_paths = [
            "/health",
            "/api/v1/health",
            "/api/v1/auth",
            "/metrics",
        ]
        if any(request.url.path.startswith(path) for path in no_cache_paths):
            return await call_next(request)
            
        # Build cache key
        cache_key = f"response:{request.method}:{request.url.path}"
        
        # Add query parameters to cache key if present
        if request.query_params:
            query_string = str(request.query_params)
            cache_key += f":{query_string}"
        
        # Check cache
        redis_client = get_redis()
        cached_response = redis_client.get(cache_key)
        
        if cached_response and settings.CACHE_ENABLED:
            try:
                # Parse cached response
                cached_data = json.loads(cached_response)
                
                # Create response from cached data
                return Response(
                    content=cached_data["content"],
                    status_code=cached_data["status_code"],
                    headers=cached_data["headers"],
                    media_type=cached_data["media_type"],
                )
            except Exception as e:
                logger.warning(f"Failed to use cached response: {e}")
        
        # Execute request
        response = await call_next(request)
        
        # Cache response if cacheable
        if (
            settings.CACHE_ENABLED and
            response.status_code == 200 and
            hasattr(response, "body")
        ):
            try:
                # Determine TTL based on path
                ttl = settings.CACHE_TTL_MEDIUM  # Default to medium TTL
                
                if "articles" in request.url.path:
                    if request.url.path.endswith("/"):
                        # List endpoints
                        ttl = settings.CACHE_TTL_SHORT
                    else:
                        # Detail endpoints
                        ttl = settings.CACHE_TTL_MEDIUM
                elif "sources" in request.url.path:
                    ttl = settings.CACHE_TTL_LONG
                
                # Prepare response data
                response_data = {
                    "content": response.body.decode(),
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                }
                
                # Cache response
                redis_client.setex(
                    cache_key,
                    ttl,
                    json.dumps(response_data)
                )
            except Exception as e:
                logger.warning(f"Failed to cache response: {e}")
        
        return response

if settings.CACHE_ENABLED:
    app.add_middleware(ResponseCacheMiddleware)

# Performance monitoring middleware
class PerformanceMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Start timer
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Add duration header
        response.headers["X-Process-Time"] = str(duration)
        
        # Log slow requests
        if duration > 1.0:  # Log requests that take more than 1 second
            logger.warning(f"Slow request: {request.method} {request.url.path} took {duration:.4f}s")
        
        return response

app.add_middleware(PerformanceMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint that can be used by load balancers.
    More detailed health information is available at /api/v1/health/
    """
    return {"status": "healthy"}

@app.get("/cache/clear", status_code=200)
async def clear_cache():
    """
    Clear all cache entries.
    This is for development and troubleshooting only.
    """
    if not settings.DEBUG:
        return {"error": "Cache clearing is only available in debug mode"}
        
    count = cache_clear_all()
    return {"status": "success", "cleared_entries": count}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=settings.DEBUG,
        log_level=settings.UVICORN_LOG_LEVEL.lower(),
    )