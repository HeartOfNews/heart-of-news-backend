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

## Technical Stack

- **Language**: Python 3.10+
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Search**: Elasticsearch
- **Task Queue**: Celery with Redis
- **NLP**: Hugging Face Transformers, PyTorch
- **Scraping**: Scrapy, Beautiful Soup
- **Containerization**: Docker, Kubernetes

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

# Test bias detector with sample articles
python -m scripts.test_bias_detector

# Test scraper with real sources
python -m scripts.test_scraper --source "Example News" --limit 3
```

## License

[MIT License](LICENSE)