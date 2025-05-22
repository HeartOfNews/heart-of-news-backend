# Heart of News Monitoring System

This document describes the monitoring and metrics system for the Heart of News backend.

## Overview

The monitoring system provides:

1. **Real-time Metrics** - Prometheus metrics for system performance and application behavior
2. **Error Tracking** - Sentry integration for error reporting and debugging
3. **Detailed Logging** - Structured logging with loguru
4. **Health Checks** - Comprehensive service health monitoring
5. **Performance Monitoring** - Integration with APM tools

## Setup

To initialize the monitoring environment:

```bash
./scripts/init_monitoring.sh
```

This script:
- Creates required directories
- Sets appropriate permissions
- Adds placeholder config to your .env file

## Configuration

Configure monitoring through environment variables (in `.env`):

```
# Monitoring settings
LOG_LEVEL=INFO                           # Log level (DEBUG, INFO, WARNING, ERROR)
ENABLE_METRICS=true                      # Enable Prometheus metrics
PROMETHEUS_MULTIPROC_DIR=/tmp/prometheus_multiproc  # Directory for Prometheus metrics
SENTRY_DSN=                              # Sentry DSN for error tracking
ENABLE_PERFORMANCE_TRACKING=true         # Enable detailed performance tracking
METRICS_EXPORT_INTERVAL=15               # Metrics export interval in seconds

# APM Settings
ELASTIC_APM_SERVER_URL=                  # Elastic APM server URL
DATADOG_API_KEY=                         # Datadog API key
DATADOG_APP_KEY=                         # Datadog APP key
```

## Available Metrics

The system collects the following metrics:

### HTTP Metrics

- `http_requests_total` - Total count of HTTP requests (by method, endpoint, status code)
- `http_request_duration_seconds` - HTTP request latency (by method, endpoint)
- `http_requests_active` - Number of active HTTP requests (by method, endpoint)

### Database Metrics

- `db_query_duration_seconds` - Database query latency (by operation, table)

### Scraper Metrics

- `scraper_duration_seconds` - Scraper operation latency (by source_id, operation)
- `articles_scraped_total` - Total count of articles scraped (by source_id, status)

### Bias Analysis Metrics

- `bias_analysis_duration_seconds` - Bias analysis operation latency (by analysis_type)

### Task Metrics

- `task_duration_seconds` - Background task latency (by task_name)
- `tasks_total` - Total count of background tasks (by task_name, status)
- `tasks_active` - Number of active background tasks (by task_name)

## Health Check Endpoints

The application provides several health check endpoints:

### Basic Health Check

```
GET /health
```

Returns a simple health status. Useful for load balancers and basic monitoring.

### Detailed Health Check

```
GET /api/v1/health/
```

Provides comprehensive health status of all system components including:
- Database connectivity
- Redis status
- Elasticsearch status
- Bias detector service
- Celery task queue
- Data statistics

### System Status

```
GET /api/v1/health/status
```

Provides detailed statistics about the application state:
- Article statistics by status
- Source distribution by bias
- Performance metrics
- Database connection pool statistics
- Recent activity

Optional query parameters:
- `include_system_info=true` - Include server system information
- `force_refresh=true` - Force refresh of cached data

### Metrics Dashboard Data

```
GET /api/v1/health/metrics
```

Provides metrics specifically formatted for visualization dashboards:
- Article and source counts
- Status distribution
- Daily article counts (last 30 days)
- Top sources by article count

### Testing Alerts

```
POST /api/v1/health/test-alert
```

Generates a test alert to verify monitoring systems are working correctly.

## Prometheus Metrics Endpoint

Prometheus metrics are exposed at:

```
GET /metrics
```

This endpoint provides all collected Prometheus metrics in the standard format for scraping.

## Integration with Monitoring Tools

### Grafana Dashboard

A sample Grafana dashboard is provided in `monitoring/grafana/dashboards/heart-of-news.json`.

### Prometheus Configuration

Sample Prometheus configuration:

```yaml
scrape_configs:
  - job_name: 'heart-of-news'
    scrape_interval: 15s
    static_configs:
      - targets: ['heart-of-news-backend:9090']
```

### Sentry Configuration

1. Create a Sentry project at https://sentry.io/
2. Add your DSN to the `.env` file
3. Errors will be automatically reported

## Alerting

Alerts can be configured through Prometheus AlertManager, Sentry, or other monitoring tools.

Sample alert rules for Prometheus AlertManager:

```yaml
groups:
  - name: heart-of-news
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status_code=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on Heart of News"
          description: "Error rate is {{ $value }} per second for the past 5 minutes"
```

## Logging

Logs are stored in:
- `logs/app.log` - Main application log
- `logs/test.log` - Test log (when running tests)

Log format:
```
{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{line} - {message}
```

## Performance Monitoring

For advanced performance monitoring, the system supports:

1. **Elastic APM** - Set `ELASTIC_APM_SERVER_URL` to enable
2. **Datadog APM** - Set `DATADOG_API_KEY` and `DATADOG_APP_KEY` to enable

## Decorators for Tracking Performance

The monitoring system provides several decorators you can use in your code:

```python
from app.core.monitoring import track_time, track_db_query, track_scraper, track_bias_analysis, track_task

# Track function execution time
@track_time(CUSTOM_HISTOGRAM, labels={"operation": "my_operation"})
def my_function():
    # ...

# Track database operations
@track_db_query(operation="select", table="articles")
def get_articles():
    # ...

# Track scraper operations
@track_scraper(source_id="source_1", operation="fetch")
async def fetch_articles():
    # ...

# Track bias analysis
@track_bias_analysis(analysis_type="political")
async def analyze_political_bias():
    # ...

# Track background tasks
@track_task(task_name="process_article")
def process_article_task():
    # ...
```