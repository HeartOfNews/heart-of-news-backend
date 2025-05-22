"""
Configuration for pytest and test fixtures
"""

import os
import asyncio
import pytest
from typing import Generator, Dict, Any
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from sqlalchemy.ext.declarative import declarative_base

from app.db.session import Base
from app.main import app
from app.core.config import settings
from app.db.session import get_db


# Create test database engine
TEST_SQLALCHEMY_DATABASE_URI = "sqlite:///./test.db"
engine = create_engine(
    TEST_SQLALCHEMY_DATABASE_URI, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator:
    """
    Test database fixture
    Creates all tables, yields a testing database session,
    and drops all tables when test is complete
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        
    # Drop tables
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db) -> Generator:
    """
    FastAPI test client with overridden dependencies
    """
    def _get_test_db():
        try:
            yield db
        finally:
            pass
    
    # Override the get_db dependency
    app.dependency_overrides[get_db] = _get_test_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Clear dependency overrides
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def sample_article_data() -> Dict[str, Any]:
    """Sample article data for tests"""
    return {
        "title": "Test Article",
        "url": "https://example.com/test-article",
        "content": """This is a test article with some content. 
        The content should be long enough to analyze for bias.
        This article contains factual information about events.
        There are multiple paragraphs to ensure there's enough text to process.""",
        "summary": "Summary of test article",
        "published_at": "2025-05-10T12:00:00",
        "source": {
            "id": "test-source",
            "name": "Test Source"
        },
        "author": "Test Author",
        "tags": ["test", "sample"],
        "image_url": "https://example.com/image.jpg"
    }


@pytest.fixture(scope="function")
def sample_source_data() -> Dict[str, Any]:
    """Sample source data for tests"""
    return {
        "id": "test-source",
        "name": "Test Source",
        "url": "https://example.com",
        "feed_url": "https://example.com/feed.xml",
        "type": "rss",
        "description": "A test news source",
        "logo_url": "https://example.com/logo.png",
        "country": "US",
        "language": "en",
        "categories": ["news", "test"],
        "bias_score": 0.0,
        "reliability_score": 0.85,
        "is_active": True
    }


@pytest.fixture(scope="module")
def event_loop():
    """Create an event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()