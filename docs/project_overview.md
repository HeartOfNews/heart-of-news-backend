# Heart of News Backend

## Overview

Heart of News is a news aggregation platform with AI-powered bias detection capabilities. This backend service provides:

1. Automated scraping of news articles from various sources
2. AI analysis of article content for bias and propaganda
3. REST API for retrieving and managing articles and sources
4. Background processing for scheduled tasks

## Architecture

The application follows a modern, modular architecture with:

- **FastAPI**: High-performance web framework for building APIs
- **SQLAlchemy**: ORM for database operations
- **Pydantic**: Data validation and settings management
- **Celery**: Distributed task queue for background processing
- **Redis**: Message broker and caching
- **ElasticSearch**: Full-text search capabilities (optional)

## Core Components

### API Layer

REST API endpoints for:
- Article management
- Source management
- Health checks
- Task management

### Data Layer

- SQLAlchemy models for database representation
- Pydantic schemas for data validation
- CRUD operations for database interactions

### Service Layer

- **Scraper Service**: Fetches articles from news sources
  - RSS scrapers
  - Web scrapers with HTML parsing
  
- **AI Bias Detection**: Analyzes articles for:
  - Political bias (-1 to 1 scale)
  - Emotional language (0-1 scale)
  - Propaganda techniques
  - Fact-to-opinion ratio

### Background Processing

- Scheduled scraping of news sources
- Automated bias analysis of new articles
- Article publishing workflows

## Data Flow

1. **Scraping**: Scheduled tasks fetch new articles from configured sources
2. **Processing**: Articles are cleaned, normalized, and stored
3. **Analysis**: AI models analyze content for bias and propaganda
4. **Access**: REST API provides access to processed articles and metadata

## Deployment

The application is containerized with Docker and can be deployed using:
- Docker Compose for development
- Kubernetes for production (configuration not included)

## Getting Started

See [README.md](../README.md) for setup and deployment instructions.

## Additional Documentation

- [API Endpoints](api_endpoints.md)
- [Database Models](database_repositories.md)
- [Scraper Service](scraper_service.md)
- [Bias Detection](bias_detection.md)
- [Task Queue](task_queue.md)