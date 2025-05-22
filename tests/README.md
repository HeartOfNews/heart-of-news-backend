# Heart of News Testing Suite

This directory contains the testing suite for the Heart of News backend application.

## Test Organization

The tests are organized into the following categories:

- **Unit Tests**: Tests for individual functions and classes
- **Integration Tests**: Tests for API endpoints and service interactions
- **End-to-End Tests**: Tests for complete application workflows

## Directory Structure

- `/tests`: Root test directory
  - `/api`: API endpoint tests
  - `/services`: Service-level tests
    - `/ai`: AI service tests
    - `/scraper`: Scraper service tests
  - `conftest.py`: Test fixtures and configuration
  - `utils.py`: Test utilities and helper functions
  - `test_workflow.py`: End-to-end workflow tests

## Running Tests

To run all tests:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=app tests/
```

To run specific test categories:

```bash
# Run API tests
pytest tests/api/

# Run specific test file
pytest tests/api/test_articles.py

# Run tests with specific markers
pytest -m "api"
pytest -m "e2e"
```

## Test Fixtures

Common test fixtures are defined in `conftest.py` and include:

- `db`: Test database session
- `client`: FastAPI test client
- `sample_article_data`: Sample article data for tests
- `sample_source_data`: Sample source data for tests

## Mocking

External services and dependencies are mocked to ensure tests are isolated and reproducible. The following services are commonly mocked:

- Celery tasks
- External HTTP requests
- Scraper services
- AI bias detection

## Continuous Integration

Tests are automatically run on CI through GitHub Actions. The workflow is defined in `.github/workflows/main.yml`.