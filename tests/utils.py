"""
Test utilities and helper functions
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app import crud, models
from app.schemas.article import ArticleCreate
from app.schemas.source import SourceCreate


def create_test_source(db: Session, source_data: Dict[str, Any]) -> models.source.Source:
    """
    Create a source in the test database
    """
    source_in = SourceCreate(**source_data)
    return crud.source.create(db=db, obj_in=source_in)


def create_test_article(
    db: Session, 
    article_data: Dict[str, Any], 
    source_id: Optional[str] = None
) -> models.article.Article:
    """
    Create an article in the test database
    
    If source_id is provided, it will be used instead of the ID in the article_data
    """
    # Use provided source_id if available, otherwise use the one in article_data
    if source_id:
        # Create a copy to avoid modifying the original
        article_data = article_data.copy()
        article_data["source"]["id"] = source_id
    
    source_id = article_data["source"]["id"]
    article_in = ArticleCreate(**article_data)
    
    return crud.article.create_with_source_id(db=db, obj_in=article_in, source_id=source_id)


def create_batch_test_articles(
    db: Session,
    base_article_data: Dict[str, Any],
    source_id: str,
    count: int = 5
) -> List[models.article.Article]:
    """
    Create multiple test articles with variations
    """
    articles = []
    for i in range(count):
        # Create a copy of the base article data
        article_data = base_article_data.copy()
        # Modify the copy with unique values
        article_data["title"] = f"{article_data['title']} {i+1}"
        article_data["url"] = f"{article_data['url']}-{i+1}"
        article_data["content"] = f"{article_data['content']} This is article number {i+1}."
        article_data["summary"] = f"{article_data['summary']} #{i+1}"
        article_data["source"]["id"] = source_id
        
        # Create the article
        article = create_test_article(db=db, article_data=article_data, source_id=source_id)
        articles.append(article)
    
    return articles