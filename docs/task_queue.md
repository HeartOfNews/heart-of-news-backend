# Background Task Queue

This document describes the background task queue system for the Heart of News backend.

## Overview

The Heart of News backend uses Celery with Redis as a broker for background task processing. The task queue handles operations that might take a significant amount of time or need to be scheduled, such as:

1. Scraping news sources for new articles
2. Analyzing articles for bias
3. Publishing processed articles
4. Importing default sources

## Architecture

The task queue system consists of several components:

1. **Celery Application**: The main entry point for task definition and execution
2. **Redis Broker**: Message broker for task queue communication
3. **Task Workers**: Processes that execute the actual tasks
4. **Task Scheduler (Celery Beat)**: Schedules recurring tasks
5. **API Endpoints**: For manually triggering tasks

## Task Definitions

### Scrape Sources

```python
@celery_app.task
def scrape_sources(
    limit_per_source: int = 10,
    source_ids: Optional[List[str]] = None
) -> Dict[str, Any]
```

This task scrapes articles from news sources and saves them to the database.

**Parameters:**
- `limit_per_source`: Maximum number of articles to fetch per source
- `source_ids`: Optional list of source IDs to scrape (if None, scrapes sources based on crawl frequency)

**Returns:** Dictionary with results including the number of articles scraped and saved

**Process:**
1. Get sources to scrape (either specified sources or sources due for crawling)
2. Create scraper configurations for each source
3. Initialize the scraper manager
4. Run the scrape operation
5. Save results to the database
6. Update last_crawled_at timestamp for each source

### Analyze Articles

```python
@celery_app.task
def analyze_articles(limit: int = 20) -> Dict[str, Any]
```

This task analyzes draft articles for bias and updates their metrics.

**Parameters:**
- `limit`: Maximum number of articles to analyze

**Returns:** Dictionary with results including the number of articles processed

**Process:**
1. Get articles in 'draft' status
2. Initialize the bias detector
3. For each article:
   - Analyze the article content
   - Update the article with analysis results
   - Update status to 'processing'
4. Return processing results

### Publish Articles

```python
@celery_app.task
def publish_articles(limit: int = 20) -> Dict[str, Any]
```

This task marks processed articles as published.

**Parameters:**
- `limit`: Maximum number of articles to publish

**Returns:** Dictionary with results including the number of articles published

**Process:**
1. Get articles in 'processing' status
2. For each article:
   - Apply any additional publishing logic (e.g., filtering based on bias scores)
   - Update status to 'published'
3. Return publishing results

### Import Default Sources

```python
@celery_app.task
def import_default_sources() -> Dict[str, Any]
```

This one-time task imports default sources into the database.

**Returns:** Dictionary with results including the number of sources imported and skipped

**Process:**
1. Get default source configurations
2. For each source:
   - Check if source already exists
   - Create source in database if new
   - Add scraper configuration
3. Return import results

## Scheduled Tasks

The system uses Celery Beat to schedule recurring tasks:

```python
celery_app.conf.beat_schedule = {
    "scrape-sources": {
        "task": "app.worker.scrape_sources",
        "schedule": 60 * 60,  # every hour
    },
    "analyze-articles": {
        "task": "app.worker.analyze_articles",
        "schedule": 15 * 60,  # every 15 minutes
    },
    "publish-articles": {
        "task": "app.worker.publish_articles",
        "schedule": 30 * 60,  # every 30 minutes
    },
}
```

This configuration schedules:
- Scraping sources every hour
- Analyzing articles every 15 minutes
- Publishing articles every 30 minutes

## Task Queue Configuration

The Celery application is configured with Redis as both the broker and backend:

```python
celery_app = Celery(
    "heart_of_news_worker",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
)
```

Task routing is configured to use separate queues for different task types:

```python
celery_app.conf.task_routes = {
    "app.worker.scrape_sources": {"queue": "scraper"},
    "app.worker.analyze_articles": {"queue": "analyzer"},
    "app.worker.publish_articles": {"queue": "publisher"},
}
```

## API Integration

The task system is integrated with the API through dedicated endpoints:

```
POST /api/v1/tasks/scrape-sources
POST /api/v1/tasks/analyze-articles
POST /api/v1/tasks/publish-articles
POST /api/v1/tasks/import-sources
GET /api/v1/tasks/task/{task_id}
```

These endpoints allow for manual triggering of tasks and checking task status.

## Deployment

In a production environment, the Celery workers and beat scheduler are deployed as separate processes:

1. **Worker for scraper queue:**
   ```
   celery -A app.worker worker -l info -Q scraper
   ```

2. **Worker for analyzer queue:**
   ```
   celery -A app.worker worker -l info -Q analyzer
   ```

3. **Worker for publisher queue:**
   ```
   celery -A app.worker worker -l info -Q publisher
   ```

4. **Beat scheduler:**
   ```
   celery -A app.worker beat -l info
   ```

## Error Handling

The task system includes error handling:

1. **Task-level try/except:** Each task has a top-level try/except to catch and log errors
2. **Per-item processing:** For tasks that process multiple items, errors in one item won't stop others
3. **Status tracking:** Articles with processing errors are marked with 'error' status
4. **Result reporting:** Error details are included in task results

## Monitoring

Task execution can be monitored through:

1. **Health API endpoint:** Shows task queue status
2. **Task status endpoint:** Shows status of individual tasks
3. **Logs:** All tasks include detailed logging
4. **Celery Flower:** A web-based monitoring tool can be deployed in production

## Best Practices

When working with the task queue system:

1. **Keep tasks idempotent:** Tasks should be safe to run multiple times
2. **Use appropriate task granularity:** Avoid very long-running tasks
3. **Set appropriate timeouts:** Prevent tasks from hanging indefinitely
4. **Handle transient failures:** Use retries for operations that might fail temporarily
5. **Monitor queue sizes:** Prevent queue buildup by adjusting worker count or task scheduling