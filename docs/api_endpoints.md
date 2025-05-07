# API Endpoints

This document describes the API endpoints available in the Heart of News backend.

## Base URL

All endpoints are prefixed with `/api/v1`

## Authentication

Authentication is not yet implemented. Future versions will require authentication for admin operations.

## Articles

### List Articles

```
GET /articles/
```

Retrieve articles with optional filtering.

**Query Parameters:**
- `skip`: Number of articles to skip (for pagination)
- `limit`: Maximum number of articles to return
- `source_id`: Filter by source ID
- `status`: Filter by article status (draft, processing, published, rejected)
- `search`: Search term in title and content
- `from_date`: Filter by published date >= from_date
- `to_date`: Filter by published date <= to_date
- `order_by`: Field to order by (published_at, discovered_at, title)
- `desc`: Sort order, True for descending, False for ascending

**Response:**
```json
[
  {
    "id": "article-id",
    "title": "Article Title",
    "summary": "Article summary text",
    "url": "https://example.com/article",
    "published_at": "2025-05-01T12:30:00Z",
    "discovered_at": "2025-05-01T12:35:00Z",
    "source": {
      "name": "Source Name",
      "url": "https://example.com"
    },
    "status": "published"
  },
  ...
]
```

### Get Article

```
GET /articles/{article_id}
```

Get a specific article by ID.

**Parameters:**
- `article_id`: The ID of the article to retrieve (path parameter)

**Response:**
```json
{
  "id": "article-id",
  "title": "Article Title",
  "summary": "Article summary text",
  "content": "Full article content",
  "url": "https://example.com/article",
  "published_at": "2025-05-01T12:30:00Z",
  "discovered_at": "2025-05-01T12:35:00Z",
  "source": {
    "name": "Source Name",
    "url": "https://example.com"
  },
  "status": "published"
}
```

### Create Article

```
POST /articles/
```

Create a new article (admin only).

**Request Body:**
```json
{
  "title": "New Article Title",
  "summary": "Article summary text",
  "content": "Full article content",
  "url": "https://example.com/new-article",
  "published_at": "2025-05-01T12:30:00Z",
  "source": {
    "id": "source-id"
  }
}
```

**Response:** The created article

### Update Article

```
PUT /articles/{article_id}
```

Update an article (admin only).

**Parameters:**
- `article_id`: The ID of the article to update (path parameter)

**Request Body:**
```json
{
  "title": "Updated Title",
  "summary": "Updated summary",
  "content": "Updated content",
  "status": "published"
}
```

**Response:** The updated article

### Analyze Article

```
POST /articles/{article_id}/analyze
```

Analyze an article for bias and update its metrics.

**Parameters:**
- `article_id`: The ID of the article to analyze (path parameter)

**Response:** The analyzed article with updated metrics

### Delete Article

```
DELETE /articles/{article_id}
```

Delete an article (admin only).

**Parameters:**
- `article_id`: The ID of the article to delete (path parameter)

**Response:** The deleted article

## Sources

### List Sources

```
GET /sources/
```

Retrieve news sources with optional filtering.

**Query Parameters:**
- `skip`: Number of sources to skip (for pagination)
- `limit`: Maximum number of sources to return
- `category`: Filter by source category
- `search`: Search by source name
- `min_reliability`: Filter by minimum reliability score (0.0-1.0)
- `max_bias`: Filter by maximum absolute bias score (0.0-1.0)

**Response:**
```json
[
  {
    "id": "source-id",
    "name": "Source Name",
    "url": "https://example.com",
    "category": "General",
    "feed_url": "https://example.com/rss",
    "reliability_score": 0.85,
    "bias_score": 0.1,
    "logo_url": "https://example.com/logo.png",
    "last_crawled_at": "2025-05-01T10:30:00Z"
  },
  ...
]
```

### Get Source

```
GET /sources/{source_id}
```

Get a specific news source by ID.

**Parameters:**
- `source_id`: The ID of the source to retrieve (path parameter)

**Response:**
```json
{
  "id": "source-id",
  "name": "Source Name",
  "url": "https://example.com",
  "category": "General",
  "feed_url": "https://example.com/rss",
  "reliability_score": 0.85,
  "bias_score": 0.1,
  "logo_url": "https://example.com/logo.png",
  "last_crawled_at": "2025-05-01T10:30:00Z"
}
```

### Create Source

```
POST /sources/
```

Create a new news source (admin only).

**Request Body:**
```json
{
  "name": "New Source",
  "url": "https://newsource.com",
  "category": "Technology",
  "feed_url": "https://newsource.com/rss"
}
```

**Response:** The created source

### Update Source

```
PUT /sources/{source_id}
```

Update a news source (admin only).

**Parameters:**
- `source_id`: The ID of the source to update (path parameter)

**Request Body:**
```json
{
  "name": "Updated Name",
  "reliability_score": 0.9,
  "bias_score": -0.2
}
```

**Response:** The updated source

### Scrape Source

```
POST /sources/{source_id}/scrape
```

Manually trigger a scrape operation for a specific source.

**Parameters:**
- `source_id`: The ID of the source to scrape (path parameter)
- `limit`: Maximum number of articles to scrape (query parameter, default=10)

**Response:**
```json
{
  "source": {
    "id": "source-id",
    "name": "Source Name"
  },
  "articles_scraped": 5,
  "new_articles": 3,
  "article_details": [
    {
      "id": "article-id-1",
      "title": "Article Title 1",
      "url": "https://example.com/article1"
    },
    {
      "id": "article-id-2",
      "title": "Article Title 2",
      "url": "https://example.com/article2"
    },
    {
      "id": "article-id-3",
      "title": "Article Title 3",
      "url": "https://example.com/article3"
    }
  ]
}
```

### Evaluate Source

```
POST /sources/{source_id}/evaluate
```

Update evaluation scores for a source (admin only).

**Parameters:**
- `source_id`: The ID of the source to evaluate (path parameter)

**Request Body:**
```json
{
  "reliability_score": 0.95,
  "bias_score": 0.05,
  "sensationalism_score": 0.1
}
```

**Response:** The updated source

### Delete Source

```
DELETE /sources/{source_id}
```

Delete a news source (admin only).

**Parameters:**
- `source_id`: The ID of the source to delete (path parameter)

**Response:** The deleted source

## Tasks

### Scrape Sources

```
POST /tasks/scrape-sources
```

Trigger a background task to scrape sources.

**Query Parameters:**
- `limit_per_source`: Maximum number of articles to fetch per source

**Request Body:**
```json
{
  "source_ids": ["source-id-1", "source-id-2"]
}
```

**Response:**
```json
{
  "task_id": "task-id",
  "status": "started",
  "message": "Source scraping task initiated"
}
```

### Analyze Articles

```
POST /tasks/analyze-articles
```

Trigger a background task to analyze articles.

**Query Parameters:**
- `limit`: Maximum number of articles to analyze

**Response:**
```json
{
  "task_id": "task-id",
  "status": "started",
  "message": "Article analysis task initiated"
}
```

### Publish Articles

```
POST /tasks/publish-articles
```

Trigger a background task to publish articles.

**Query Parameters:**
- `limit`: Maximum number of articles to publish

**Response:**
```json
{
  "task_id": "task-id",
  "status": "started",
  "message": "Article publishing task initiated"
}
```

### Import Sources

```
POST /tasks/import-sources
```

Trigger a background task to import default sources.

**Response:**
```json
{
  "task_id": "task-id",
  "status": "started",
  "message": "Default sources import task initiated"
}
```

### Get Task Status

```
GET /tasks/task/{task_id}
```

Get the status of a background task.

**Parameters:**
- `task_id`: ID of the task to check (path parameter)

**Response:**
```json
{
  "task_id": "task-id",
  "status": "SUCCESS",
  "result": {
    "status": "success",
    "message": "Task completed successfully",
    "details": {}
  }
}
```

## Health

### Health Check

```
GET /health/
```

Check system health, including database connectivity and services.

**Response:**
```json
{
  "status": "healthy",
  "api": "ok",
  "database": "ok",
  "version": "0.1.0",
  "services": {
    "bias_detector": "ok",
    "task_queue": "ok"
  },
  "data": {
    "sources": 10,
    "articles": 150
  }
}
```

### Service Status

```
GET /health/status
```

Get detailed system status, including article and source statistics.

**Response:**
```json
{
  "article_stats": {
    "draft": 25,
    "processing": 10,
    "published": 100,
    "rejected": 10,
    "error": 5
  },
  "total_articles": 150,
  "source_stats": {
    "total": 10,
    "reliable": 8,
    "bias_distribution": {
      "left": 3,
      "neutral": 5,
      "right": 2
    }
  },
  "performance": {
    "avg_processing_time": 60,
    "article_processing_rate": 60
  }
}
```