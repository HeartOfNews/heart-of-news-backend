"""
Query profiling utilities for the Heart of News backend
"""

import functools
import logging
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict, List, Optional, Generator, TypeVar, cast

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.monitoring import DB_QUERY_LATENCY

# Type variable for generic function
F = TypeVar("F", bound=Callable[..., Any])

# Configure logging
logger = logging.getLogger(__name__)

# Global query statistics
query_stats = {
    "total_queries": 0,
    "slow_queries": 0,
    "total_time": 0.0,
    "slow_threshold": 0.1,  # seconds
    "queries_by_table": {},
    "slow_queries_log": [],
}


@contextmanager
def query_profiler() -> Generator[None, None, None]:
    """
    Context manager for profiling database queries
    
    Example:
        with query_profiler():
            # Run database queries
            db.query(User).filter(User.id == user_id).first()
    
    Yields:
        None
    """
    # Set up query profiling
    if not hasattr(query_profiler, "initialized"):
        # Add event listeners for query profiling
        @event.listens_for(Engine, "before_cursor_execute")
        def before_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            conn.info.setdefault("query_start_time", []).append(time.time())
            
        @event.listens_for(Engine, "after_cursor_execute")
        def after_cursor_execute(
            conn, cursor, statement, parameters, context, executemany
        ):
            start_time = conn.info["query_start_time"].pop()
            execution_time = time.time() - start_time
            
            # Update query statistics
            query_stats["total_queries"] += 1
            query_stats["total_time"] += execution_time
            
            # Check for slow queries
            if execution_time > query_stats["slow_threshold"]:
                query_stats["slow_queries"] += 1
                
                # Log slow queries
                query_log = {
                    "execution_time": execution_time,
                    "statement": statement,
                    "parameters": parameters,
                }
                query_stats["slow_queries_log"].append(query_log)
                
                # Log to logger
                logger.warning(
                    f"Slow query detected ({execution_time:.4f}s): {statement}"
                )
                
            # Update table statistics
            # Extract table name from query (simple approach)
            statement_lower = statement.lower()
            
            # Identify operation type
            operation = "unknown"
            if statement_lower.startswith("select"):
                operation = "select"
            elif statement_lower.startswith("insert"):
                operation = "insert"
            elif statement_lower.startswith("update"):
                operation = "update"
            elif statement_lower.startswith("delete"):
                operation = "delete"
                
            # Extract table name (simple approach)
            table_name = "unknown"
            if " from " in statement_lower:
                # For SELECT queries
                from_part = statement_lower.split(" from ")[1].strip()
                table_name = from_part.split()[0].strip('"')
            elif "insert into" in statement_lower:
                # For INSERT queries
                into_part = statement_lower.split("insert into")[1].strip()
                table_name = into_part.split()[0].strip('"')
            elif "update " in statement_lower:
                # For UPDATE queries
                update_part = statement_lower.split("update ")[1].strip()
                table_name = update_part.split()[0].strip('"')
            elif "delete from" in statement_lower:
                # For DELETE queries
                from_part = statement_lower.split("delete from")[1].strip()
                table_name = from_part.split()[0].strip('"')
                
            # Update table statistics
            table_key = f"{table_name}"
            if table_key not in query_stats["queries_by_table"]:
                query_stats["queries_by_table"][table_key] = {
                    "count": 0,
                    "total_time": 0.0,
                    "operations": {
                        "select": 0,
                        "insert": 0,
                        "update": 0,
                        "delete": 0,
                        "other": 0,
                    },
                }
                
            table_stats = query_stats["queries_by_table"][table_key]
            table_stats["count"] += 1
            table_stats["total_time"] += execution_time
            
            # Update operation count
            if operation in table_stats["operations"]:
                table_stats["operations"][operation] += 1
            else:
                table_stats["operations"]["other"] += 1
                
            # Record metric in Prometheus
            if settings.ENABLE_METRICS:
                DB_QUERY_LATENCY.labels(
                    operation=operation, table=table_name
                ).observe(execution_time)
                
        # Mark as initialized
        query_profiler.initialized = True
        
    try:
        yield
    finally:
        pass
        

def profile_query(func: F) -> F:
    """
    Decorator for profiling database queries
    
    Args:
        func: Function to profile
        
    Returns:
        Decorated function
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with query_profiler():
            return func(*args, **kwargs)
            
    return cast(F, wrapper)
    

def get_query_stats() -> Dict[str, Any]:
    """
    Get query statistics
    
    Returns:
        Dict with query statistics
    """
    stats = {
        "total_queries": query_stats["total_queries"],
        "slow_queries": query_stats["slow_queries"],
        "total_time": query_stats["total_time"],
        "avg_query_time": (
            query_stats["total_time"] / query_stats["total_queries"]
            if query_stats["total_queries"] > 0
            else 0
        ),
        "tables": [],
    }
    
    # Add table statistics
    for table_name, table_stats in query_stats["queries_by_table"].items():
        stats["tables"].append({
            "name": table_name,
            "query_count": table_stats["count"],
            "total_time": table_stats["total_time"],
            "avg_time": (
                table_stats["total_time"] / table_stats["count"]
                if table_stats["count"] > 0
                else 0
            ),
            "operations": table_stats["operations"],
        })
        
    # Sort tables by query count (descending)
    stats["tables"].sort(key=lambda x: x["query_count"], reverse=True)
    
    return stats
    

def reset_query_stats() -> None:
    """
    Reset query statistics
    """
    query_stats["total_queries"] = 0
    query_stats["slow_queries"] = 0
    query_stats["total_time"] = 0.0
    query_stats["queries_by_table"] = {}
    query_stats["slow_queries_log"] = []
    

def get_slow_queries(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get slow queries log
    
    Args:
        limit: Maximum number of slow queries to return
        
    Returns:
        List of slow queries
    """
    # Sort by execution time (descending)
    sorted_queries = sorted(
        query_stats["slow_queries_log"],
        key=lambda x: x["execution_time"],
        reverse=True
    )
    
    return sorted_queries[:limit]