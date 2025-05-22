"""
Integration tests for health check endpoints
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.source import Source
from app.models.article import Article
from tests.utils import create_test_source, create_test_article, create_batch_test_articles


def test_health_check_endpoint(client: TestClient, db: Session):
    """Test the health check endpoint"""
    # Call the API
    with patch("app.worker.celery_app.control") as mock_celery_control:
        # Setup mock Celery response
        mock_inspect = MagicMock()
        mock_inspect.ping.return_value = {"worker1": {"ok": "pong"}}
        mock_celery_control.inspect.return_value = mock_inspect
        
        response = client.get(f"{settings.API_V1_STR}/health/")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the health status is correct
    assert data["status"] == "healthy"
    assert data["api"] == "ok"
    assert data["database"] == "ok"
    assert data["version"] == settings.VERSION
    assert "services" in data
    assert "bias_detector" in data["services"]
    assert "task_queue" in data["services"]
    assert "data" in data
    assert "sources" in data["data"]
    assert "articles" in data["data"]


def test_health_check_with_database_data(client: TestClient, db: Session, sample_source_data, sample_article_data):
    """Test health check with data in the database"""
    # Create some test data
    source = create_test_source(db, sample_source_data)
    articles = create_batch_test_articles(
        db=db,
        base_article_data=sample_article_data,
        source_id=source.id,
        count=5
    )
    
    # Call the API
    with patch("app.worker.celery_app.control") as mock_celery_control:
        # Setup mock Celery response
        mock_inspect = MagicMock()
        mock_inspect.ping.return_value = {"worker1": {"ok": "pong"}}
        mock_celery_control.inspect.return_value = mock_inspect
        
        response = client.get(f"{settings.API_V1_STR}/health/")
    
    # Parse the response
    data = response.json()
    
    # Check that the counts are correct
    assert data["data"]["sources"] == 1
    assert data["data"]["articles"] == 5


def test_service_status_endpoint(client: TestClient, db: Session):
    """Test the service status endpoint"""
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/health/status")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check that the status data structure is correct
    assert "article_stats" in data
    assert "total_articles" in data
    assert "source_stats" in data
    assert "total" in data["source_stats"]
    assert "bias_distribution" in data["source_stats"]
    assert "performance" in data


def test_service_status_with_diverse_data(client: TestClient, db: Session, sample_source_data, sample_article_data):
    """Test service status with diverse data"""
    # Create sources with different bias scores
    left_source_data = sample_source_data.copy()
    left_source_data["id"] = "left-source"
    left_source_data["name"] = "Left Source"
    left_source_data["url"] = "https://left.com"
    left_source_data["bias_score"] = -0.8
    left_source = create_test_source(db, left_source_data)
    
    center_source_data = sample_source_data.copy()
    center_source_data["id"] = "center-source"
    center_source_data["name"] = "Center Source"
    center_source_data["url"] = "https://center.com"
    center_source_data["bias_score"] = 0.0
    center_source = create_test_source(db, center_source_data)
    
    right_source_data = sample_source_data.copy()
    right_source_data["id"] = "right-source"
    right_source_data["name"] = "Right Source"
    right_source_data["url"] = "https://right.com"
    right_source_data["bias_score"] = 0.8
    right_source = create_test_source(db, right_source_data)
    
    # Create articles with different statuses
    article_data = sample_article_data.copy()
    
    # Create a few articles for each source with different statuses
    statuses = ["draft", "processing", "published", "rejected", "error"]
    for i, status in enumerate(statuses):
        # Create an article with this status for each source
        for src in [left_source, center_source, right_source]:
            article_copy = article_data.copy()
            article_copy["title"] = f"{article_data['title']} {src.name} {status}"
            article_copy["url"] = f"{article_data['url']}-{src.id}-{status}"
            article = create_test_article(db, article_copy, src.id)
            
            # Update status
            article.status = status
            db.commit()
    
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/health/status")
    
    # Parse the response
    data = response.json()
    
    # Check source distribution
    assert data["source_stats"]["total"] == 3
    assert data["source_stats"]["bias_distribution"]["left"] == 1
    assert data["source_stats"]["bias_distribution"]["neutral"] == 1
    assert data["source_stats"]["bias_distribution"]["right"] == 1
    
    # Check article statuses
    assert data["article_stats"]["draft"] == 3
    assert data["article_stats"]["processing"] == 3
    assert data["article_stats"]["published"] == 3
    assert data["article_stats"]["rejected"] == 3
    assert data["article_stats"]["error"] == 3
    assert data["total_articles"] == 15