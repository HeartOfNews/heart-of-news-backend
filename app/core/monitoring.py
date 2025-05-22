"""
Monitoring, metrics, and logging configuration for the Heart of News backend.
"""

import time
import logging
from functools import wraps
from typing import Callable, Dict, Optional, Any, List, Union

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from loguru import logger
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, multiprocess
from prometheus_client.metrics import MetricWrapperBase
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

# Configure Prometheus registry
def get_prometheus_registry():
    """Get or create Prometheus registry."""
    registry = CollectorRegistry()
    multiprocess.MultiProcessCollector(registry)
    return registry

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total count of HTTP requests",
    ["method", "endpoint", "status_code"]
)

REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", 
    "HTTP request latency in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0, float("inf"))
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Number of active HTTP requests",
    ["method", "endpoint"]
)

DB_QUERY_LATENCY = Histogram(
    "db_query_duration_seconds",
    "Database query latency in seconds",
    ["operation", "table"],
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, float("inf"))
)

SCRAPER_LATENCY = Histogram(
    "scraper_duration_seconds",
    "Scraper operation latency in seconds",
    ["source_id", "operation"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, float("inf"))
)

ARTICLES_SCRAPED = Counter(
    "articles_scraped_total",
    "Total count of articles scraped",
    ["source_id", "status"]
)

BIAS_ANALYSIS_LATENCY = Histogram(
    "bias_analysis_duration_seconds",
    "Bias analysis operation latency in seconds",
    ["analysis_type"],
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, float("inf"))
)

TASK_LATENCY = Histogram(
    "task_duration_seconds",
    "Background task latency in seconds",
    ["task_name"],
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 300.0, 600.0, float("inf"))
)

TASK_COUNT = Counter(
    "tasks_total",
    "Total count of background tasks",
    ["task_name", "status"]
)

ACTIVE_TASKS = Gauge(
    "tasks_active",
    "Number of active background tasks",
    ["task_name"]
)

# Configure Sentry
def init_sentry():
    """Initialize Sentry error tracking."""
    if settings.SENTRY_DSN:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            traces_sample_rate=0.2,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )
        logger.info("Sentry initialized")


# Configure logging
def configure_logging():
    """Configure application logging."""
    # Remove default handlers
    logging.getLogger().handlers = []
    
    # Configure loguru
    logger.configure(
        handlers=[
            {
                "sink": "logs/app.log" if not settings.TESTING else "logs/test.log",
                "rotation": "500 MB",
                "retention": "10 days",
                "compression": "zip",
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{line} - {message}",
                "level": "DEBUG" if settings.DEBUG else "INFO",
            },
            {
                "sink": logging.sys.stderr,
                "format": "{time:YYYY-MM-DD HH:mm:ss.SSS} | <level>{level}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - {message}",
                "level": "DEBUG" if settings.DEBUG else "INFO",
                "colorize": True,
            },
        ]
    )
    
    # Set specific levels for noisy libraries
    logger.level("httpx", settings.HTTPX_LOG_LEVEL)
    logger.level("uvicorn", settings.UVICORN_LOG_LEVEL)
    logger.level("sqlalchemy.engine", settings.SQLALCHEMY_LOG_LEVEL)
    
    # Add logging for third-party libraries
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            logger_opt = logger.opt(depth=6, exception=record.exc_info)
            logger_opt.log(record.levelname, record.getMessage())
    
    # Set Uvicorn logging
    logging.getLogger("uvicorn").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    
    # Set SQLAlchemy logging
    logging.getLogger("sqlalchemy").handlers = [InterceptHandler()]
    
    # Return the configured logger
    return logger


# Prometheus HTTP middleware
class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware to track HTTP request metrics with Prometheus."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        method = request.method
        path = request.url.path
        
        # Track active requests
        ACTIVE_REQUESTS.labels(method=method, endpoint=path).inc()
        
        # Track request latency
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Record metrics
            status_code = response.status_code
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            return response
        
        except Exception as e:
            # Record exception metrics
            status_code = 500
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=method,
                endpoint=path,
                status_code=status_code
            ).inc()
            
            REQUEST_LATENCY.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Re-raise the exception
            raise e
        
        finally:
            # Decrement active requests gauge
            ACTIVE_REQUESTS.labels(method=method, endpoint=path).dec()


# Decorators for metrics tracking
def track_time(metric: Histogram, labels: Dict[str, str] = None):
    """Decorator to track execution time of a function with Prometheus."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if labels:
                metric.labels(**labels).observe(duration)
            else:
                metric.observe(duration)
                
            return result
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            if labels:
                metric.labels(**labels).observe(duration)
            else:
                metric.observe(duration)
                
            return result
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator


def track_db_query(operation: str, table: str):
    """Decorator to track database query execution time."""
    return track_time(
        DB_QUERY_LATENCY,
        labels={"operation": operation, "table": table}
    )


def track_scraper(source_id: str, operation: str):
    """Decorator to track scraper operation execution time."""
    return track_time(
        SCRAPER_LATENCY,
        labels={"source_id": source_id, "operation": operation}
    )


def track_bias_analysis(analysis_type: str):
    """Decorator to track bias analysis execution time."""
    return track_time(
        BIAS_ANALYSIS_LATENCY,
        labels={"analysis_type": analysis_type}
    )


def track_task(task_name: str):
    """Decorator to track background task execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Increment active tasks
            ACTIVE_TASKS.labels(task_name=task_name).inc()
            
            # Increment task count
            TASK_COUNT.labels(task_name=task_name, status="started").inc()
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                
                # Record successful completion
                TASK_COUNT.labels(task_name=task_name, status="success").inc()
                
                return result
                
            except Exception as e:
                # Record failure
                TASK_COUNT.labels(task_name=task_name, status="failure").inc()
                
                # Re-raise the exception
                raise e
                
            finally:
                # Record duration
                duration = time.time() - start_time
                TASK_LATENCY.labels(task_name=task_name).observe(duration)
                
                # Decrement active tasks
                ACTIVE_TASKS.labels(task_name=task_name).dec()
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Increment active tasks
            ACTIVE_TASKS.labels(task_name=task_name).inc()
            
            # Increment task count
            TASK_COUNT.labels(task_name=task_name, status="started").inc()
            
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Record successful completion
                TASK_COUNT.labels(task_name=task_name, status="success").inc()
                
                return result
                
            except Exception as e:
                # Record failure
                TASK_COUNT.labels(task_name=task_name, status="failure").inc()
                
                # Re-raise the exception
                raise e
                
            finally:
                # Record duration
                duration = time.time() - start_time
                TASK_LATENCY.labels(task_name=task_name).observe(duration)
                
                # Decrement active tasks
                ACTIVE_TASKS.labels(task_name=task_name).dec()
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return wrapper
    
    return decorator