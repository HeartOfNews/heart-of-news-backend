#!/usr/bin/env python3
"""
Seed data script for Heart of News local development
This script adds initial data to get started with the application
"""

import asyncio
import sys
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.db.session import get_db
from app.models.user import User
from app.models.source import Source
from app.models.article import Article
from sqlalchemy.orm import Session

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def seed_users(db: Session):
    """Create initial users"""
    users = [
        {
            "email": "admin@heartofnews.local",
            "username": "admin",
            "hashed_password": hash_password("admin123"),
            "role": "admin",
            "is_active": True
        },
        {
            "email": "user@heartofnews.local", 
            "username": "testuser",
            "hashed_password": hash_password("user123"),
            "role": "user",
            "is_active": True
        },
        {
            "email": "editor@heartofnews.local",
            "username": "editor",
            "hashed_password": hash_password("editor123"),
            "role": "admin",
            "is_active": True
        }
    ]
    
    for user_data in users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing_user:
            user = User(**user_data)
            db.add(user)
            print(f"Created user: {user_data['email']}")
        else:
            print(f"User already exists: {user_data['email']}")

def seed_sources(db: Session):
    """Create initial news sources"""
    sources = [
        {
            "name": "BBC News",
            "url": "https://www.bbc.com/news",
            "rss_feed": "http://feeds.bbci.co.uk/news/rss.xml",
            "is_active": True,
            "reliability_score": 0.9,
            "bias_score": 0.1
        },
        {
            "name": "Reuters",
            "url": "https://www.reuters.com",
            "rss_feed": "https://www.reuters.com/tools/rss",
            "is_active": True,
            "reliability_score": 0.95,
            "bias_score": 0.05
        },
        {
            "name": "AP News",
            "url": "https://apnews.com",
            "rss_feed": "https://apnews.com/index.rss",
            "is_active": True,
            "reliability_score": 0.93,
            "bias_score": 0.08
        },
        {
            "name": "CNN",
            "url": "https://www.cnn.com",
            "rss_feed": "http://rss.cnn.com/rss/edition.rss",
            "is_active": True,
            "reliability_score": 0.8,
            "bias_score": 0.3
        },
        {
            "name": "Fox News",
            "url": "https://www.foxnews.com",
            "rss_feed": "https://feeds.foxnews.com/foxnews/latest",
            "is_active": True,
            "reliability_score": 0.75,
            "bias_score": -0.35
        },
        {
            "name": "NPR",
            "url": "https://www.npr.org",
            "rss_feed": "https://feeds.npr.org/1001/rss.xml",
            "is_active": True,
            "reliability_score": 0.88,
            "bias_score": 0.15
        }
    ]
    
    for source_data in sources:
        # Check if source already exists
        existing_source = db.query(Source).filter(Source.name == source_data["name"]).first()
        if not existing_source:
            source = Source(**source_data)
            db.add(source)
            print(f"Created source: {source_data['name']}")
        else:
            print(f"Source already exists: {source_data['name']}")

def seed_articles(db: Session):
    """Create sample articles"""
    # Get sources from database
    sources = db.query(Source).all()
    if not sources:
        print("No sources found. Please seed sources first.")
        return
    
    sample_articles = [
        {
            "title": "Global Climate Summit Reaches Historic Agreement",
            "content": "<p>World leaders gathered at the annual climate summit have reached a groundbreaking agreement on carbon emissions reduction. The accord, signed by 195 countries, sets ambitious targets for the next decade.</p><p>The agreement includes provisions for renewable energy investment, carbon pricing mechanisms, and support for developing nations in their transition to clean energy.</p><p>Environmental groups have praised the deal as a significant step forward, while some critics argue that the targets may not be ambitious enough to prevent catastrophic climate change.</p>",
            "summary": "195 countries sign historic climate agreement with ambitious carbon reduction targets and renewable energy investments.",
            "url": "https://example.com/climate-summit-agreement",
            "categories": ["Environment", "Politics", "International"],
            "image_url": "https://images.unsplash.com/photo-1569163139394-de44cb2e0dee?w=800&h=400&fit=crop",
            "bias_score": {
                "political_bias": 0.1,
                "emotional_tone": 0.2,
                "overall_score": 0.15,
                "propaganda_techniques": []
            }
        },
        {
            "title": "Tech Giants Face New Regulatory Challenges in Europe",
            "content": "<p>The European Union has announced sweeping new regulations targeting major technology companies, focusing on data privacy, market competition, and content moderation.</p><p>The Digital Services Act and Digital Markets Act will impose strict requirements on platforms with more than 45 million users, including mandatory risk assessments and external audits.</p><p>Technology companies have expressed concerns about compliance costs and implementation timelines, while consumer advocacy groups welcome the increased oversight.</p>",
            "summary": "EU introduces comprehensive tech regulations focusing on privacy, competition, and content moderation for major platforms.",
            "url": "https://example.com/eu-tech-regulations",
            "categories": ["Technology", "Politics", "Business"],
            "image_url": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800&h=400&fit=crop",
            "bias_score": {
                "political_bias": -0.05,
                "emotional_tone": 0.3,
                "overall_score": 0.18,
                "propaganda_techniques": []
            }
        },
        {
            "title": "Medical Breakthrough: New Treatment Shows Promise for Alzheimer's",
            "content": "<p>Researchers at leading medical institutions have announced promising results from clinical trials of a new Alzheimer's treatment. The therapy targets amyloid plaques in the brain and has shown significant cognitive improvement in early-stage patients.</p><p>The treatment, developed over 15 years of research, represents a potential breakthrough in addressing one of the most challenging neurological diseases.</p><p>While results are encouraging, researchers emphasize that larger studies are needed before the treatment can be widely available to patients.</p>",
            "summary": "New Alzheimer's treatment shows promising results in clinical trials, targeting brain plaques and improving cognitive function.",
            "url": "https://example.com/alzheimers-breakthrough",
            "categories": ["Health", "Science"],
            "image_url": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=400&fit=crop",
            "bias_score": {
                "political_bias": 0.0,
                "emotional_tone": 0.1,
                "overall_score": 0.05,
                "propaganda_techniques": []
            }
        },
        {
            "title": "Space Mission Successfully Lands on Mars",
            "content": "<p>The international space mission to Mars has achieved a successful landing, marking a significant milestone in space exploration. The robotic lander touched down in the Martian polar region and has begun transmitting data back to Earth.</p><p>The mission aims to search for signs of past microbial life and analyze the planet's geology and atmosphere. Advanced instruments aboard the lander will conduct soil samples and atmospheric measurements over the next two years.</p><p>Space agencies from multiple countries collaborated on this mission, demonstrating the power of international cooperation in advancing scientific knowledge.</p>",
            "summary": "International Mars mission achieves successful landing, beginning two-year exploration of planet's geology and potential signs of life.",
            "url": "https://example.com/mars-mission-success",
            "categories": ["Science", "Space", "International"],
            "image_url": "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800&h=400&fit=crop",
            "bias_score": {
                "political_bias": 0.0,
                "emotional_tone": 0.15,
                "overall_score": 0.08,
                "propaganda_techniques": []
            }
        }
    ]
    
    for i, article_data in enumerate(sample_articles):
        # Assign to different sources
        source = sources[i % len(sources)]
        
        # Check if article already exists
        existing_article = db.query(Article).filter(Article.title == article_data["title"]).first()
        if not existing_article:
            article = Article(
                title=article_data["title"],
                content=article_data["content"],
                summary=article_data["summary"],
                url=article_data["url"],
                source_id=source.id,
                categories=article_data["categories"],
                image_url=article_data["image_url"],
                published_at=datetime.utcnow() - timedelta(days=i),
                bias_score=article_data["bias_score"]
            )
            db.add(article)
            print(f"Created article: {article_data['title']}")
        else:
            print(f"Article already exists: {article_data['title']}")

def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Get database session
    db = next(get_db())
    
    try:
        # Seed data in order
        print("\n1. Seeding users...")
        seed_users(db)
        
        print("\n2. Seeding sources...")
        seed_sources(db)
        
        print("\n3. Seeding articles...")
        seed_articles(db)
        
        # Commit all changes
        db.commit()
        print("\n✅ Database seeding completed successfully!")
        
        print("\n📋 Default credentials:")
        print("Admin: admin@heartofnews.local / admin123")
        print("User: user@heartofnews.local / user123")
        print("Editor: editor@heartofnews.local / editor123")
        
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    main()