"""
Redis caching utilities for the Heart of News backend
"""

import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar, Union, cast

import redis
from fastapi import Request, Response

from app.core.config import settings

# Type variable for generic function
F = TypeVar("F", bound=Callable[..., Any])

# Configure logging
logger = logging.getLogger(__name__)

# Create Redis connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=0,  # Use DB 0 for caching
    decode_responses=True,  # Auto-decode Redis responses to strings
)


def get_redis() -> redis.Redis:
    """
    Get Redis client with connection pooling
    
    Returns:
        Redis client instance
    """
    return redis.Redis(connection_pool=redis_pool)


def cache_key_builder(prefix: str, *args, **kwargs) -> str:
    """
    Build a cache key from prefix and arguments
    
    Args:
        prefix: Key prefix (usually function name)
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        Cache key string
    """
    # Convert args and kwargs to strings and join with delimiter
    args_str = ":".join(str(arg) for arg in args if arg is not None)
    kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()) if v is not None)
    
    # Build key with prefix and arguments
    parts = [prefix]
    if args_str:
        parts.append(args_str)
    if kwargs_str:
        parts.append(kwargs_str)
    
    return ":".join(parts)


def cache(
    expire: int = 60,
    key_prefix: Optional[str] = None,
    include_request: bool = False,
) -> Callable[[F], F]:
    """
    Cache decorator for functions
    
    Args:
        expire: Cache expiration time in seconds
        key_prefix: Custom key prefix (defaults to function name)
        include_request: Whether to include request object in cache key
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Get cache prefix
            prefix = key_prefix or func.__name__
            
            # Build cache key
            cache_args = list(args)
            cache_kwargs = dict(kwargs)
            
            # Skip self/cls argument for methods
            if cache_args and hasattr(cache_args[0], "__dict__"):
                cache_args = cache_args[1:]
                
            # Handle request object
            if not include_request:
                if cache_args and isinstance(cache_args[0], Request):
                    cache_args = cache_args[1:]
                if "request" in cache_kwargs:
                    del cache_kwargs["request"]
                    
            # Build cache key
            cache_key = cache_key_builder(prefix, *cache_args, **cache_kwargs)
            
            # Get Redis client
            redis_client = get_redis()
            
            # Check cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                try:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in cache: {cache_key}")
                    
            # Execute function
            result = await func(*args, **kwargs)
            
            # Cache result
            try:
                redis_client.setex(
                    cache_key,
                    expire,
                    json.dumps(result, default=str)  # Use str for non-serializable objects
                )
                logger.debug(f"Cache set: {cache_key} (expires in {expire}s)")
            except Exception as e:
                logger.warning(f"Failed to cache result: {str(e)}")
                
            return result
            
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            # Get cache prefix
            prefix = key_prefix or func.__name__
            
            # Build cache key
            cache_args = list(args)
            cache_kwargs = dict(kwargs)
            
            # Skip self/cls argument for methods
            if cache_args and hasattr(cache_args[0], "__dict__"):
                cache_args = cache_args[1:]
                
            # Handle request object
            if not include_request:
                if cache_args and isinstance(cache_args[0], Request):
                    cache_args = cache_args[1:]
                if "request" in cache_kwargs:
                    del cache_kwargs["request"]
                    
            # Build cache key
            cache_key = cache_key_builder(prefix, *cache_args, **cache_kwargs)
            
            # Get Redis client
            redis_client = get_redis()
            
            # Check cache
            cached_result = redis_client.get(cache_key)
            if cached_result:
                try:
                    logger.debug(f"Cache hit: {cache_key}")
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in cache: {cache_key}")
                    
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            try:
                redis_client.setex(
                    cache_key,
                    expire,
                    json.dumps(result, default=str)  # Use str for non-serializable objects
                )
                logger.debug(f"Cache set: {cache_key} (expires in {expire}s)")
            except Exception as e:
                logger.warning(f"Failed to cache result: {str(e)}")
                
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return cast(F, async_wrapper)
        return cast(F, sync_wrapper)
        
    return decorator


def cache_response(
    expire: int = 60,
    key_prefix: Optional[str] = None,
    key_from_query: Optional[List[str]] = None,
) -> Callable[[F], F]:
    """
    Cache decorator for API response
    
    Args:
        expire: Cache expiration time in seconds
        key_prefix: Custom key prefix (defaults to function name)
        key_from_query: List of query params to include in cache key
        
    Returns:
        Decorated function
    """
    def decorator(func: F) -> F:
        @wraps(func)
        async def async_wrapper(request: Request, *args, **kwargs) -> Response:
            # Get cache prefix
            prefix = key_prefix or func.__name__
            
            # Build cache key parts
            key_parts = [prefix, request.url.path]
            
            # Add query parameters if specified
            if key_from_query:
                query_params = []
                for param in key_from_query:
                    value = request.query_params.get(param)
                    if value:
                        query_params.append(f"{param}={value}")
                        
                if query_params:
                    key_parts.append("&".join(query_params))
            
            # Build final cache key
            cache_key = ":".join(key_parts)
            
            # Get Redis client
            redis_client = get_redis()
            
            # Check cache
            cached_response = redis_client.get(cache_key)
            if cached_response:
                try:
                    logger.debug(f"Response cache hit: {cache_key}")
                    response_data = json.loads(cached_response)
                    return Response(
                        content=response_data["content"],
                        status_code=response_data["status_code"],
                        headers=response_data["headers"],
                        media_type=response_data["media_type"],
                    )
                except Exception as e:
                    logger.warning(f"Failed to parse cached response: {str(e)}")
            
            # Execute function
            response = await func(request, *args, **kwargs)
            
            # Cache response
            try:
                response_data = {
                    "content": response.body.decode() if hasattr(response, "body") else "",
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "media_type": response.media_type,
                }
                
                redis_client.setex(
                    cache_key,
                    expire,
                    json.dumps(response_data)
                )
                logger.debug(f"Response cache set: {cache_key} (expires in {expire}s)")
            except Exception as e:
                logger.warning(f"Failed to cache response: {str(e)}")
                
            return response
            
        # Currently, only async functions are supported for response caching
        if not asyncio.iscoroutinefunction(func):
            raise ValueError("Response caching only supports async functions")
            
        return cast(F, async_wrapper)
        
    return decorator


def invalidate_cache(pattern: str) -> int:
    """
    Invalidate cache keys matching pattern
    
    Args:
        pattern: Redis key pattern to match (e.g., "articles:*")
        
    Returns:
        Number of keys invalidated
    """
    redis_client = get_redis()
    
    # Find keys matching pattern
    keys = redis_client.keys(pattern)
    
    # Delete keys
    if keys:
        return redis_client.delete(*keys)
    
    return 0


def cache_clear_all() -> int:
    """
    Clear all cache entries
    
    Returns:
        Number of keys cleared
    """
    redis_client = get_redis()
    
    # Find all keys
    keys = redis_client.keys("*")
    
    # Delete keys
    if keys:
        return redis_client.delete(*keys)
    
    return 0