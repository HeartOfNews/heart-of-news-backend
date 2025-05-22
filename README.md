# Heart of News Backend

Backend service for the Heart of News project - an AI-powered, propaganda-free news aggregation and distribution system.

## Overview

Heart of News is designed to deliver information to people without propaganda from any side. The service constantly scans the internet for fresh, relevant news and posts them on multiple platforms:

- Website
- Telegram channel
- VK community
- Twitter/X
- Facebook

The system is fully administered by AI, with automated content collection, bias detection, and neutral presentation.

## Features

- **Automated News Collection**: Multi-source scraping with support for RSS feeds and web pages
- **Bias Detection**: Advanced AI-powered analysis for political bias, emotional language, and propaganda techniques
- **Content Processing Pipeline**: Background task queue for scraping, analysis, and publishing
- **Flexible API**: Comprehensive endpoints with filtering, pagination, and advanced querying
- **Multi-platform Publishing**: Automated distribution across various platforms
- **Source Evaluation**: Reliability and bias scoring for news sources
- **Performance Monitoring**: Health checks and detailed system status metrics
- **User Authentication**: Role-based access control with JWT authentication
- **Database Optimization**: Efficient queries with indexing and caching support
- **Monitoring Stack**: Comprehensive monitoring with Prometheus, Grafana, and ELK
- **Production-Ready Deployment**: Kubernetes manifests for high-availability deployment

## Technical Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Search**: Elasticsearch
- **Task Queue**: Celery with Redis
- **Caching**: Redis
- **NLP**: Hugging Face Transformers, PyTorch
- **Scraping**: Scrapy, Beautiful Soup
- **Containerization**: Docker, Kubernetes
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **Authentication**: JWT with role-based access control
- **CI/CD**: GitHub Actions

## Development Setup

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Docker (optional)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/HeartOfNews/heart-of-news-backend.git
cd heart-of-news-backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a .env file:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run database migrations:
```bash
alembic upgrade head
```

6. Start the development server:
```bash
uvicorn app.main:app --reload
```

### Docker Development

Alternatively, you can use Docker:

```bash
docker-compose up -d
```

## Deployment

Heart of News supports multiple deployment environments:

- **Development**: Local development with Docker Compose
- **Staging**: Testing environment with full monitoring stack
- **Production**: High-availability Kubernetes deployment

For detailed deployment instructions, see:
- [Deployment Guide](docs/deployment.md)
- [Staging Setup](docs/staging_setup.md)
- [Production Setup](docs/production_setup.md)

### Staging Deployment

Deploy to staging environment:

```bash
# Automatic deployment via GitHub Actions
git push origin develop

# Manual deployment on the staging server
./scripts/deploy_staging.sh
```

### Production Deployment

Deploy to production environment:

```bash
# Automatic deployment via GitHub Actions
git push origin main
# or create a release tag
git tag v1.0.0
git push origin v1.0.0

# Manual deployment
./scripts/deploy_production.sh
```

## API Documentation

Once the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

For detailed API documentation, see the [API Endpoints](docs/api_endpoints.md) guide.

## Technical Documentation

- [API Endpoints](docs/api_endpoints.md): Detailed documentation of all API endpoints
- [Database Repositories](docs/database_repositories.md): Database operations and repository pattern
- [Bias Detection](docs/bias_detection.md): AI-powered bias detection service
- [Scraper Service](docs/scraper_service.md): News collection and extraction
- [Task Queue](docs/task_queue.md): Background processing with Celery
- [Deployment Guide](docs/deployment.md): Deployment process and environments
- [Staging Setup](docs/staging_setup.md): Staging environment configuration
- [Production Setup](docs/production_setup.md): Production environment configuration

## Development Status

See the [Development Process](DEVELOPMENT_PROCESS.md) document for current project status.

## Testing

Run tests with:

```bash
# Run all tests
pytest

# Run specific test modules
pytest tests/services/ai/test_bias_detector.py
pytest tests/services/scraper/test_scrapers.py

# Run with coverage report
pytest --cov=app tests/

# Test bias detector with sample articles
python -m scripts.test_bias_detector

# Test scraper with real sources
python -m scripts.test_scraper --source "Example News" --limit 3
```

## Load Testing

Run load tests to ensure performance under high traffic:

```bash
# Local load testing
./load_tests/run_load_test.sh

# Kubernetes-based load testing
./scripts/run_k8s_load_test.sh
```

## Monitoring

The Heart of News backend includes comprehensive monitoring:

```bash
# Start the monitoring stack (development)
./scripts/start_monitoring.sh

# For staging environment
./scripts/monitoring_staging.sh
```

Access Grafana dashboards at:
- Development: http://localhost:3000
- Staging: https://grafana-staging.heartofnews.com
- Production: https://grafana.heartofnews.com

## License

[MIT License](LICENSE)