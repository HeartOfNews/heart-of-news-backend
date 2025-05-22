"""
Integration tests for the task API endpoints
"""

import json
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.api.v1.api import api_router
from tests.utils import create_test_source, create_test_article


def test_list_tasks(client: TestClient):
    """Test getting a list of tasks"""
    # Mock the Celery inspection API
    with patch("app.worker.celery_app.control") as mock_celery_control:
        # Setup mock data for active and scheduled tasks
        active_tasks = {
            "worker1": [
                {
                    "id": "task1",
                    "name": "app.worker.scrape_source",
                    "args": ["source-id-1"],
                    "kwargs": {},
                    "type": "scrape_source",
                    "hostname": "worker1",
                    "time_start": 1652112345.123,
                    "acknowledged": True,
                    "delivery_info": {"exchange": "", "routing_key": "celery"},
                    "worker_pid": 1234
                }
            ]
        }
        
        scheduled_tasks = {
            "worker1": [
                {
                    "eta": "2025-05-15T12:00:00",
                    "priority": 5,
                    "request": {
                        "id": "task2",
                        "name": "app.worker.analyze_article",
                        "args": ["article-id-1"],
                        "kwargs": {},
                        "type": "analyze_article"
                    }
                }
            ]
        }
        
        # Set up the mock responses
        mock_inspect = MagicMock()
        mock_inspect.active.return_value = active_tasks
        mock_inspect.scheduled.return_value = scheduled_tasks
        mock_celery_control.inspect.return_value = mock_inspect
        
        # Call the API
        response = client.get(f"{settings.API_V1_STR}/tasks/")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response structure
    assert "active_tasks" in data
    assert "scheduled_tasks" in data
    assert len(data["active_tasks"]) == 1
    assert len(data["scheduled_tasks"]) == 1
    
    # Check task details
    assert data["active_tasks"][0]["id"] == "task1"
    assert data["active_tasks"][0]["name"] == "app.worker.scrape_source"
    assert data["scheduled_tasks"][0]["id"] == "task2"
    assert data["scheduled_tasks"][0]["name"] == "app.worker.analyze_article"


def test_get_task_status(client: TestClient):
    """Test getting a specific task status"""
    # Mock the Celery task result
    task_id = "test-task-id"
    task_result = {
        "id": task_id,
        "status": "SUCCESS",
        "result": {"processed": 10, "status": "completed"},
        "date_done": "2025-05-14T12:34:56"
    }
    
    with patch("app.worker.celery_app.AsyncResult") as mock_async_result:
        # Setup mock task result
        mock_result = MagicMock()
        mock_result.id = task_id
        mock_result.status = "SUCCESS"
        mock_result.result = {"processed": 10, "status": "completed"}
        mock_result.date_done = "2025-05-14T12:34:56"
        mock_async_result.return_value = mock_result
        
        # Call the API
        response = client.get(f"{settings.API_V1_STR}/tasks/{task_id}")
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the task data
    assert data["id"] == task_id
    assert data["status"] == "SUCCESS"
    assert data["result"] is not None
    assert data["result"]["processed"] == 10


def test_get_nonexistent_task(client: TestClient):
    """Test getting a non-existent task"""
    # Mock the Celery task result for a non-existent task
    task_id = "nonexistent-task"
    
    with patch("app.worker.celery_app.AsyncResult") as mock_async_result:
        # Setup mock for non-existent task
        mock_result = MagicMock()
        mock_result.id = task_id
        mock_result.state = "PENDING"
        mock_result.result = None
        mock_async_result.return_value = mock_result
        
        # Call the API
        response = client.get(f"{settings.API_V1_STR}/tasks/{task_id}")
    
    # The API should return successfully even for pending/unknown tasks
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the task data
    assert data["id"] == task_id
    assert data["status"] == "PENDING"
    assert data["result"] is None


def test_schedule_source_scrape_task(client: TestClient, db: Session, sample_source_data):
    """Test scheduling a source scrape task"""
    # Create a test source
    source = create_test_source(db, sample_source_data)
    
    # Mock the Celery task
    with patch("app.worker.scrape_source.delay") as mock_task:
        # Setup mock task result
        task_id = "test-scrape-task-id"
        mock_task.return_value = MagicMock(id=task_id)
        
        # Call the API
        response = client.post(
            f"{settings.API_V1_STR}/tasks/scrape-source/{source.id}",
            json={"limit": 10}
        )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response data
    assert data["task_id"] == task_id
    assert data["source_id"] == source.id
    assert data["status"] == "scheduled"


def test_schedule_article_analysis_task(client: TestClient, db: Session, sample_source_data, sample_article_data):
    """Test scheduling an article analysis task"""
    # Create a source and article
    source = create_test_source(db, sample_source_data)
    article = create_test_article(db, sample_article_data, source.id)
    
    # Mock the Celery task
    with patch("app.worker.analyze_article.delay") as mock_task:
        # Setup mock task result
        task_id = "test-analysis-task-id"
        mock_task.return_value = MagicMock(id=task_id)
        
        # Call the API
        response = client.post(
            f"{settings.API_V1_STR}/tasks/analyze-article/{article.id}"
        )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response data
    assert data["task_id"] == task_id
    assert data["article_id"] == article.id
    assert data["status"] == "scheduled"


def test_cancel_task(client: TestClient):
    """Test cancelling a task"""
    # Task to cancel
    task_id = "task-to-cancel"
    
    # Mock the Celery task revocation
    with patch("app.worker.celery_app.control.revoke") as mock_revoke:
        # Call the API
        response = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/cancel",
            json={"terminate": True}
        )
    
    # Assert response is successful
    assert response.status_code == 200
    
    # Parse the response
    data = response.json()
    
    # Check the response data
    assert data["task_id"] == task_id
    assert data["status"] == "cancelled"
    
    # Verify the task was revoked
    mock_revoke.assert_called_once_with(task_id, terminate=True)