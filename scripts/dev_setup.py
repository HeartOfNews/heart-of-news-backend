#!/usr/bin/env python3
"""
Development setup script for Heart of News Backend
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from app.db.session import Base
from app.models.article import Article
from app.models.source import Source
from app.core.config import settings
from app.crud import source as crud_source
from app.db.session import SessionLocal


def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def create_sample_sources():
    """Create sample news sources for testing"""
    print("Creating sample news sources...")
    
    db = SessionLocal()
    try:
        sample_sources = [
            {
                "name": "BBC News",
                "url": "https://www.bbc.com/news",
                "feed_url": "http://feeds.bbci.co.uk/news/rss.xml",
                "category": "General",
                "scraper_config": {
                    "type": "rss"
                },
                "crawl_frequency": 6.0  # 6 hours
            },
            {
                "name": "Reuters",
                "url": "https://www.reuters.com",
                "feed_url": "https://www.reuters.com/arc/outboundfeeds/rss/category/world/",
                "category": "General",
                "scraper_config": {
                    "type": "rss"
                },
                "crawl_frequency": 4.0  # 4 hours
            },
            {
                "name": "TechCrunch",
                "url": "https://techcrunch.com",
                "feed_url": "https://techcrunch.com/feed/",
                "category": "Technology",
                "scraper_config": {
                    "type": "rss"
                },
                "crawl_frequency": 2.0  # 2 hours
            },
            {
                "name": "Example Web Source",
                "url": "https://example-news.com",
                "category": "General",
                "scraper_config": {
                    "type": "web",
                    "selectors": {
                        "article_links": "article h2 a, .post-title a",
                        "title": "h1.entry-title, h1.post-title",
                        "content": ".entry-content p, .post-content p",
                        "published_date": ".published, .post-date",
                        "author": ".author, .byline"
                    }
                },
                "crawl_frequency": 12.0  # 12 hours
            }
        ]
        
        created_count = 0
        for source_data in sample_sources:
            # Check if source already exists
            existing = crud_source.get_source_by_url(db, source_data["url"])
            if existing:
                print(f"⚠️  Source already exists: {source_data['name']}")
                continue
            
            # Create source
            from app.schemas.source import SourceCreate
            source_create = SourceCreate(**source_data)
            crud_source.create_source(db, source_create)
            created_count += 1
            print(f"✅ Created source: {source_data['name']}")
        
        print(f"✅ Created {created_count} sample sources")
        
    except Exception as e:
        print(f"❌ Error creating sample sources: {str(e)}")
        db.rollback()
    finally:
        db.close()


async def test_scraping():
    """Test scraping functionality"""
    print("Testing scraping functionality...")
    
    try:
        from app.services.tasks.news_tasks import schedule_periodic_scraping
        from app.services.tasks.task_queue import task_queue
        
        # Start task queue
        await task_queue.start_workers()
        
        # Schedule scraping
        schedule_periodic_scraping()
        
        # Wait a bit for tasks to complete
        await task_queue.wait_for_completion(timeout=30)
        
        # Stop task queue
        await task_queue.stop_workers()
        
        print("✅ Scraping test completed")
        
    except Exception as e:
        print(f"❌ Error testing scraping: {str(e)}")


def main():
    """Main setup function"""
    print("🚀 Setting up Heart of News Backend for development...")
    
    try:
        # Create database tables
        create_tables()
        
        # Create sample sources
        create_sample_sources()
        
        # Test scraping (optional)
        # print("Would you like to test scraping? (y/n): ", end="")
        # if input().lower().startswith('y'):
        #     asyncio.run(test_scraping())
        
        print("\n🎉 Development setup completed!")
        print("\nNext steps:")
        print("1. Download NLP models: python scripts/download_models.py")
        print("2. Start the development server: uvicorn app.main:app --reload")
        print("3. Visit http://localhost:8000/docs for API documentation")
        print("4. Test bias detection: /api/v1/bias/test-sample")
        print("5. Use the /api/v1/tasks/scrape/all endpoint to test scraping")
        
    except Exception as e:
        print(f"❌ Setup failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()