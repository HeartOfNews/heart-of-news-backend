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

- Automated news collection from diverse sources
- Bias detection and neutralization
- Multi-platform publishing
- Content categorization and tagging
- Analytics and performance tracking

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

## Testing

Run tests with:

```bash
pytest
```

## License

[MIT License](LICENSE)