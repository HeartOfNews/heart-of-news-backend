"""
Integration tests for the sources API endpoints
"""

import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.api.v1.api import api_router
from app.core.config import settings
from app.models.source import Source
from app.models.article import Article
from tests.utils import create_test_source, create_test_article


def test_read_sources(client: TestClient, db: Session, sample_source_data):
    """Test getting a list of sources"""
    # Create some test sources
    source1 = create_test_source(db, sample_source_data)
    
    source2_data = sample_source_data.copy()
    source2_data["id"] = "test-source-2"
    source2_data["name"] = "Test Source 2"
    source2_data["url"] = "https://example2.com"
    source2 = create_test_source(db, source2_data)
    
    source3_data = sample_source_data.copy()
    source3_data["id"] = "test-source-3"
    source3_data["name"] = "Test Source 3"
    source3_data["url"] = "https://example3.com"
    source3 = create_test_source(db, source3_data)
    
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/sources/")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert we got a list with the correct number of sources
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Assert the source data is correct
    source_names = [s["name"] for s in data]
    assert "Test Source" in source_names
    assert "Test Source 2" in source_names
    assert "Test Source 3" in source_names


def test_read_source(client: TestClient, db: Session, sample_source_data):
    """Test getting a specific source"""
    # Create a test source
    source = create_test_source(db, sample_source_data)
    
    # Call the API
    response = client.get(f"{settings.API_V1_STR}/sources/{source.id}")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the source data is correct
    assert data["id"] == sample_source_data["id"]
    assert data["name"] == sample_source_data["name"]
    assert data["url"] == sample_source_data["url"]
    assert data["description"] == sample_source_data["description"]
    assert data["bias_score"] == sample_source_data["bias_score"]


def test_read_source_not_found(client: TestClient):
    """Test getting a non-existent source"""
    response = client.get(f"{settings.API_V1_STR}/sources/nonexistent-id")
    
    # Assert response is 404
    assert response.status_code == 404


def test_create_source(client: TestClient, db: Session, sample_source_data):
    """Test creating a new source"""
    # Prepare unique source data
    source_data = sample_source_data.copy()
    source_data["id"] = "new-test-source"
    source_data["name"] = "New Test Source"
    source_data["url"] = "https://newexample.com"
    
    # Call the API
    response = client.post(
        f"{settings.API_V1_STR}/sources/",
        json=source_data,
    )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the source was created correctly
    assert data["id"] == source_data["id"]
    assert data["name"] == source_data["name"]
    assert data["url"] == source_data["url"]
    
    # Verify it's in the database
    source_in_db = db.query(Source).filter(Source.id == data["id"]).first()
    assert source_in_db is not None
    assert source_in_db.name == source_data["name"]


def test_create_source_duplicate_name(client: TestClient, db: Session, sample_source_data):
    """Test creating a source with an existing name"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Prepare a new source with the same name
    new_source_data = sample_source_data.copy()
    new_source_data["id"] = "different-id"
    new_source_data["url"] = "https://different-url.com"
    
    # Call the API
    response = client.post(
        f"{settings.API_V1_STR}/sources/",
        json=new_source_data,
    )
    
    # Assert response indicates conflict
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_update_source(client: TestClient, db: Session, sample_source_data):
    """Test updating a source"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Prepare update data
    update_data = {
        "name": "Updated Source Name",
        "description": "Updated source description",
        "is_active": False
    }
    
    # Call the API
    response = client.put(
        f"{settings.API_V1_STR}/sources/{source.id}",
        json=update_data,
    )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the source was updated correctly
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["is_active"] == update_data["is_active"]
    assert data["url"] == sample_source_data["url"]  # Unchanged field
    
    # Verify it's updated in the database
    updated_source = db.query(Source).filter(Source.id == source.id).first()
    assert updated_source.name == update_data["name"]
    assert updated_source.description == update_data["description"]
    assert updated_source.is_active == update_data["is_active"]


def test_delete_source(client: TestClient, db: Session, sample_source_data):
    """Test deleting a source"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Call the API
    response = client.delete(f"{settings.API_V1_STR}/sources/{source.id}")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Verify it's deleted from the database
    deleted_source = db.query(Source).filter(Source.id == source.id).first()
    assert deleted_source is None


def test_evaluate_source(client: TestClient, db: Session, sample_source_data):
    """Test evaluating a source"""
    # Create a source
    source = create_test_source(db, sample_source_data)
    
    # Evaluation data
    eval_data = {
        "reliability_score": 0.75,
        "bias_score": 0.25,
        "sensationalism_score": 0.5
    }
    
    # Call the API
    response = client.post(
        f"{settings.API_V1_STR}/sources/{source.id}/evaluate",
        json=eval_data,
    )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Assert the source was updated with evaluation scores
    assert data["reliability_score"] == eval_data["reliability_score"]
    assert data["bias_score"] == eval_data["bias_score"]
    assert data["sensationalism_score"] == eval_data["sensationalism_score"]
    
    # Verify it's updated in the database
    updated_source = db.query(Source).filter(Source.id == source.id).first()
    assert updated_source.reliability_score == eval_data["reliability_score"]
    assert updated_source.bias_score == eval_data["bias_score"]
    assert updated_source.sensationalism_score == eval_data["sensationalism_score"]