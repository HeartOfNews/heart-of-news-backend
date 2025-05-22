"""
Integration tests for the articles API endpoints
"""

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.models.article import Article
from app.models.source import Source
from tests.utils import create_test_source, create_test_article, create_batch_test_articles


def test_read_articles(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test getting a list of articles"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create some test articles
    articles = create_batch_test_articles(
        db=db,
        base_article_data=sample_article_data,
        source_id=source.id,
        count=5
    )
    
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/articles/")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert we got a list with the correct number of articles
    assert isinstance(data, list)
    assert len(data) == 5
    
    # Assert the article data is correct
    assert data[0]["title"] == "Test Article 1"
    assert data[0]["source"]["name"] == "Test Source"


def test_read_article(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test getting a specific article"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create a test article
    article = create_test_article(db, sample_article_data, source.id)
    
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/articles/{article.id}")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the article data is correct
    assert data["title"] == sample_article_data["title"]
    assert data["url"] == sample_article_data["url"]
    assert data["author"] == sample_article_data["author"]
    assert data["source"]["name"] == sample_source_data["name"]


def test_read_article_not_found(client: TestClient):
    """Test getting a non-existent article"""
    response = client.get(f"{settings.API_V1_STR}/articles/nonexistent-id")
    
    # Assert response is 404
    assert response.status_code == 404


def test_create_article(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test creating a new article"""
    # Create a source first
    source = create_test_source(db, sample_source_data)
    
    # Prepare article data
    article_data = sample_article_data.copy()
    article_data["source"]["id"] = source.id
    
    # Call the API
    response = client.post(
        f"{settings.API_V1_STR}/articles/",
        json=article_data,
    )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the article was created correctly
    assert data["title"] == article_data["title"]
    assert data["url"] == article_data["url"]
    assert data["author"] == article_data["author"]
    assert data["source"]["id"] == source.id
    
    # Verify it's in the database
    article_in_db = db.query(Article).filter(Article.id == data["id"]).first()
    assert article_in_db is not None
    assert article_in_db.title == article_data["title"]


def test_create_article_duplicate_url(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test creating an article with an existing URL"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create a test article
    article = create_test_article(db, sample_article_data, source.id)
    
    # Prepare a new article with the same URL
    new_article_data = sample_article_data.copy()
    new_article_data["title"] = "Different Title, Same URL"
    new_article_data["source"]["id"] = source.id
    
    # Call the API
    response = client.post(
        f"{settings.API_V1_STR}/articles/",
        json=new_article_data,
    )
    
    # Assert response indicates conflict
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_article(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test updating an article"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create a test article
    article = create_test_article(db, sample_article_data, source.id)
    
    # Prepare update data
    update_data = {
        "title": "Updated Article Title",
        "summary": "Updated summary text"
    }
    
    # Call the API
    response = client.put(
        f"{settings.API_V1_STR}/articles/{article.id}",
        json=update_data,
    )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the article was updated correctly
    assert data["title"] == update_data["title"]
    assert data["summary"] == update_data["summary"]
    assert data["url"] == sample_article_data["url"]  # Unchanged field
    
    # Verify it's updated in the database
    updated_article = db.query(Article).filter(Article.id == article.id).first()
    assert updated_article.title == update_data["title"]
    assert updated_article.summary == update_data["summary"]


def test_delete_article(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test deleting an article"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create a test article
    article = create_test_article(db, sample_article_data, source.id)
    
    # Call the API
    response = client.delete(f"{settings.API_V1_STR}/articles/{article.id}")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Verify it's deleted from the database
    deleted_article = db.query(Article).filter(Article.id == article.id).first()
    assert deleted_article is None


def test_analyze_article(client: TestClient, db: Session, sample_article_data, sample_source_data):
    """Test analyzing an article for bias"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Create a test article with substantial content
    article_data = sample_article_data.copy()
    article_data["content"] = """
        This is a longer article with more content for bias analysis.
        It contains some factual statements and some opinions.
        The government's new policy is a terrible idea that will destroy the economy.
        Studies show that the policy could lead to a 2% decrease in GDP over five years.
        We must stop this radical agenda before it's too late.
        According to experts, alternative approaches should be considered.
    """
    article = create_test_article(db, article_data, source.id)
    
    # Call the API
    response = client.post(f"{settings.API_V1_STR}/articles/{article.id}/analyze")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the article analysis fields are populated
    assert "political_bias" in data
    assert "emotional_language" in data
    assert "fact_opinion_ratio" in data
    
    # Verify values are in expected ranges
    assert -1.0 <= data["political_bias"] <= 1.0
    assert 0.0 <= data["emotional_language"] <= 1.0
    assert 0.0 <= data["fact_opinion_ratio"] <= 1.0
    
    # Verify status is updated
    assert data["status"] == "processing"