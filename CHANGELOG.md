# Changelog

## [Unreleased]

### Added
- Enhanced AI bias detector implementation with the following features:
  - Political bias analysis using keyword detection and statistical analysis
  - Emotional language detection with sentiment analysis
  - Propaganda techniques detection using pattern matching
  - Fact vs opinion ratio calculation for content analysis
  - Overall bias score calculation with weighted metrics
- Comprehensive scraper service implementation:
  - Base scraper abstract class
  - RSS feed scraper for sources with feeds
  - Web scraper for sources without feeds
  - Scraper factory for creating appropriate scrapers
  - Scraper manager for coordinating scraping operations
  - Source configuration system
- Database repository implementation:
  - Base CRUD class with generic operations
  - Article repository with filtering and advanced queries
  - Source repository with evaluation and crawling features
- API endpoints integration:
  - Article endpoints with filtering, analysis, and management
  - Source endpoints with scraping and evaluation
  - Background task management endpoints
  - Enhanced health/status monitoring endpoints
- Background task queue with Celery:
  - Scheduled article scraping tasks
  - Automatic bias analysis pipeline
  - Article publishing workflow
  - Source import and management tasks
- Unit tests for both the bias detector and scraper services
- Command-line test scripts for demonstrating functionality

### Changed
- Updated development timeline with new completion estimates
- Adjusted project completion date to June 24, 2025 (three weeks earlier)
- Completed backend development phase (100%)

### Fixed
- None

## [0.1.0] - 2025-05-01

### Added
- Initial project structure and skeleton
- Basic FastAPI application setup
- Database models for articles and sources
- API endpoint stubs
- Docker configuration

### Changed
- None

### Fixed
- None