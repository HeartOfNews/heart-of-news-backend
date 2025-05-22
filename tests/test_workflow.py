"""
End-to-end tests for full application workflows
"""

import asyncio
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.source import Source
from app.models.article import Article
from app.services.scraper.base import ArticleData
from tests.utils import create_test_source, create_test_article, create_batch_test_articles


@pytest.mark.asyncio
async def test_full_article_workflow(client: TestClient, db: Session, sample_source_data, sample_article_data):
    """
    Test the full article workflow:
    1. Create a source
    2. Scrape articles from the source
    3. Process and analyze articles
    4. Verify article status updates
    """
    # 1. Create a source
    source = create_test_source(db, sample_source_data)
    
    # 2. Mock the scraper to return article data
    with patch("app.services.scraper.factory.ScraperFactory.create_scraper") as mock_factory:
        # Create mock scraper
        mock_scraper = AsyncMock()
        mock_scraper.fetch_articles = AsyncMock()
        
        # Setup article data
        article_data_list = [
            ArticleData(
                url=sample_article_data["url"],
                title=sample_article_data["title"],
                summary=sample_article_data["summary"],
                content=sample_article_data["content"],
                published_at=sample_article_data["published_at"],
                author=sample_article_data["author"],
                tags=sample_article_data["tags"],
                image_url=sample_article_data["image_url"]
            )
        ]
        mock_scraper.fetch_articles.return_value = article_data_list
        mock_factory.return_value = mock_scraper
        
        # Trigger scraping
        response = client.post(f"{settings.API_V1_STR}/sources/{source.id}/scrape?limit=5")
        
        # Verify scraping was successful
        assert response.status_code == 200
        scrape_result = response.json()
        assert scrape_result["source"]["id"] == source.id
        assert scrape_result["articles_scraped"] == 1
        
        # Get the created article ID
        article_id = scrape_result["article_details"][0]["id"]
        
    # 3. Analyze the article
    response = client.post(f"{settings.API_V1_STR}/articles/{article_id}/analyze")
    assert response.status_code == 200
    
    # Verify analysis results are present
    analysis_result = response.json()
    assert "political_bias" in analysis_result
    assert "emotional_language" in analysis_result
    assert "fact_opinion_ratio" in analysis_result
    
    # 4. Verify article is now in processing status
    response = client.get(f"{settings.API_V1_STR}/articles/{article_id}")
    assert response.status_code == 200
    article_data = response.json()
    assert article_data["status"] == "processing"
    
    # 5. Check health status to verify counts
    response = client.get(f"{settings.API_V1_STR}/health/status")
    assert response.status_code == 200
    health_data = response.json()
    assert health_data["article_stats"]["processing"] >= 1


@pytest.mark.asyncio
async def test_source_evaluation_workflow(client: TestClient, db: Session, sample_source_data):
    """
    Test the source evaluation workflow:
    1. Create a source
    2. Update source evaluation metrics
    3. Verify source appears in correct categories in health status
    """
    # 1. Create a source
    source_data = sample_source_data.copy()
    source_data["bias_score"] = 0  # Neutral to start
    source_data["reliability_score"] = 0.5  # Medium reliability
    source = create_test_source(db, source_data)
    
    # 2. Evaluate source as left-leaning and highly reliable
    evaluation_data = {
        "bias_score": -0.8,  # Left-leaning
        "reliability_score": 0.9,  # Highly reliable
        "sensationalism_score": 0.2  # Low sensationalism
    }
    
    response = client.post(
        f"{settings.API_V1_STR}/sources/{source.id}/evaluate",
        json=evaluation_data,
    )
    assert response.status_code == 200
    
    # 3. Check source now appears in correct categories in health status
    response = client.get(f"{settings.API_V1_STR}/health/status")
    assert response.status_code == 200
    health_data = response.json()
    
    # Should be counted as a reliable source
    assert health_data["source_stats"]["reliable"] >= 1
    
    # Should be counted as left-leaning
    assert health_data["source_stats"]["bias_distribution"]["left"] >= 1


@pytest.mark.asyncio
async def test_task_scheduling_workflow(client: TestClient, db: Session, sample_source_data, sample_article_data):
    """
    Test the background task workflow:
    1. Create source and article
    2. Schedule tasks for scraping and analysis
    3. Verify task statuses
    """
    # 1. Create source and article
    source = create_test_source(db, sample_source_data)
    article = create_test_article(db, sample_article_data, source.id)
    
    # 2. Schedule a scrape task
    with patch("app.worker.scrape_source.delay") as mock_scrape_task:
        mock_scrape_task.return_value = MagicMock(id="scrape-task-id")
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/scrape-source/{source.id}",
            json={"limit": 10}
        )
        assert response.status_code == 200
        scrape_result = response.json()
        assert scrape_result["task_id"] == "scrape-task-id"
        assert scrape_result["source_id"] == source.id
    
    # 3. Schedule an analysis task
    with patch("app.worker.analyze_article.delay") as mock_analyze_task:
        mock_analyze_task.return_value = MagicMock(id="analyze-task-id")
        
        response = client.post(
            f"{settings.API_V1_STR}/tasks/analyze-article/{article.id}"
        )
        assert response.status_code == 200
        analyze_result = response.json()
        assert analyze_result["task_id"] == "analyze-task-id"
        assert analyze_result["article_id"] == article.id
    
    # 4. Check task status
    with patch("app.worker.celery_app.AsyncResult") as mock_async_result:
        # Mock completed task
        mock_result = MagicMock()
        mock_result.id = "analyze-task-id"
        mock_result.status = "SUCCESS"
        mock_result.result = {"article_id": article.id, "status": "completed"}
        mock_async_result.return_value = mock_result
        
        response = client.get(f"{settings.API_V1_STR}/tasks/analyze-task-id")
        assert response.status_code == 200
        task_result = response.json()
        assert task_result["status"] == "SUCCESS"
        assert task_result["result"]["article_id"] == article.id