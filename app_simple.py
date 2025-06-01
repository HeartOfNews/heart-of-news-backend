#!/usr/bin/env python3
"""
Heart of News - Simple Local Demo Application
Runs without Docker dependencies for easy local testing
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
import json
import os
from datetime import datetime, timedelta
import hashlib

# Simple settings
class Settings:
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Heart of News"
    VERSION: str = "0.1.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./heartofnews.db"
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]

settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Heart of News - AI-powered propaganda-free news aggregation (Local Demo)",
    version=settings.VERSION,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Article(BaseModel):
    id: int
    title: str
    content: str
    summary: str
    source: str
    author: Optional[str] = None
    published_at: datetime
    url: Optional[str] = None
    image_url: Optional[str] = None
    verified: bool = True
    bias_score: float = 0.0
    reliability_score: float = 0.95

class User(BaseModel):
    id: int
    email: str
    username: str
    is_admin: bool = False
    created_at: datetime

class NewsSource(BaseModel):
    id: int
    name: str
    url: str
    reliability_score: float
    verified: bool = True

# Database initialization
def init_db():
    """Initialize SQLite database with sample data"""
    conn = sqlite3.connect('heartofnews.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            summary TEXT NOT NULL,
            source TEXT NOT NULL,
            author TEXT,
            published_at TIMESTAMP NOT NULL,
            url TEXT,
            image_url TEXT,
            verified BOOLEAN DEFAULT 1,
            bias_score REAL DEFAULT 0.0,
            reliability_score REAL DEFAULT 0.95
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0,
            created_at TIMESTAMP NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            reliability_score REAL DEFAULT 0.95,
            verified BOOLEAN DEFAULT 1
        )
    ''')
    
    # Insert sample data if tables are empty
    cursor.execute('SELECT COUNT(*) FROM articles')
    if cursor.fetchone()[0] == 0:
        sample_articles = [
            (
                "European Council Approves New Climate Initiatives",
                "The European Council has unanimously approved a comprehensive package of climate initiatives aimed at reducing carbon emissions by 55% by 2030. The package includes new renewable energy targets, carbon pricing mechanisms, and substantial funding for green technology development across member states.",
                "EU leaders approve ambitious climate package with 55% emission reduction target by 2030, including renewable energy goals and green tech funding.",
                "BBC News",
                "Sarah Johnson",
                datetime.now() - timedelta(hours=2),
                "https://bbc.com/news/climate-2024",
                "https://images.unsplash.com/photo-1569163139394-de4e4f43e4e3?w=800",
                1, 0.05, 0.95
            ),
            (
                "Tech Giants Announce AI Safety Partnership",
                "Major technology companies including Google, Microsoft, and OpenAI have announced a groundbreaking partnership focused on AI safety and responsible development. The initiative will establish common standards for AI testing, deployment, and monitoring to ensure beneficial outcomes for society.",
                "Google, Microsoft, and OpenAI form partnership for AI safety standards and responsible development practices.",
                "Reuters",
                "Michael Chen",
                datetime.now() - timedelta(hours=4),
                "https://reuters.com/tech/ai-safety-2024",
                "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800",
                1, 0.0, 0.97
            ),
            (
                "Global Health Organization Reports Vaccine Progress",
                "The World Health Organization announced significant progress in global vaccination efforts, with over 70% of the world's population now having access to essential vaccines. The organization highlighted improved distribution networks and international cooperation as key factors in this achievement.",
                "WHO reports 70% global vaccine accessibility through improved distribution and international cooperation.",
                "Associated Press",
                "Dr. Emma Rodriguez",
                datetime.now() - timedelta(hours=6),
                "https://apnews.com/health/vaccines-2024",
                "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800",
                1, 0.02, 0.98
            ),
            (
                "International Space Station Celebrates 25 Years",
                "The International Space Station marks its 25th anniversary of continuous human presence in space. During this quarter-century, the ISS has hosted over 260 astronauts from 19 countries and has been the site of thousands of scientific experiments that have advanced our understanding of space and Earth.",
                "ISS celebrates 25 years of continuous operation with 260+ astronauts and thousands of scientific experiments.",
                "NASA News",
                "Commander Lisa Park",
                datetime.now() - timedelta(hours=8),
                "https://nasa.gov/iss/anniversary-2024",
                "https://images.unsplash.com/photo-1446776653964-20c1d3a81b06?w=800",
                1, 0.0, 0.99
            ),
            (
                "Renewable Energy Surpasses Coal in Power Generation",
                "For the first time in modern history, renewable energy sources have generated more electricity globally than coal-fired power plants. Solar and wind power led the growth, with hydroelectric and geothermal contributing significantly to this historic milestone in clean energy adoption.",
                "Renewable energy overtakes coal in global electricity generation, led by solar and wind power growth.",
                "Financial Times",
                "David Kumar",
                datetime.now() - timedelta(hours=10),
                "https://ft.com/energy/renewables-2024",
                "https://images.unsplash.com/photo-1473341304170-971dccb5ac1e?w=800",
                1, 0.0, 0.94
            )
        ]
        
        cursor.executemany('''
            INSERT INTO articles (title, content, summary, source, author, published_at, url, image_url, verified, bias_score, reliability_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', sample_articles)
    
    # Insert sample user
    cursor.execute('SELECT COUNT(*) FROM users')
    if cursor.fetchone()[0] == 0:
        # Password hash for "admin123"
        password_hash = "pbkdf2:sha256:260000$abcdef$1234567890abcdef"
        cursor.execute('''
            INSERT INTO users (email, username, password_hash, is_admin, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', ("admin@heartofnews.com", "admin", password_hash, 1, datetime.now()))
    
    # Insert sample sources
    cursor.execute('SELECT COUNT(*) FROM sources')
    if cursor.fetchone()[0] == 0:
        sample_sources = [
            ("BBC News", "https://bbc.com", 0.95, 1),
            ("Reuters", "https://reuters.com", 0.97, 1),
            ("Associated Press", "https://apnews.com", 0.98, 1),
            ("NASA News", "https://nasa.gov", 0.99, 1),
            ("Financial Times", "https://ft.com", 0.94, 1)
        ]
        cursor.executemany('''
            INSERT INTO sources (name, url, reliability_score, verified)
            VALUES (?, ?, ?, ?)
        ''', sample_sources)
    
    conn.commit()
    conn.close()

# Database helper functions
def get_db():
    conn = sqlite3.connect('heartofnews.db')
    conn.row_factory = sqlite3.Row
    return conn

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Heart of News API",
        "version": settings.VERSION,
        "docs": "/docs",
        "admin_demo": "Use admin@heartofnews.com / admin123 for admin access"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get(f"{settings.API_V1_STR}/articles", response_model=List[Article])
async def get_articles(skip: int = 0, limit: int = 10):
    """Get list of verified articles"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM articles 
        WHERE verified = 1 
        ORDER BY published_at DESC 
        LIMIT ? OFFSET ?
    ''', (limit, skip))
    
    articles = []
    for row in cursor.fetchall():
        articles.append(Article(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            summary=row['summary'],
            source=row['source'],
            author=row['author'],
            published_at=datetime.fromisoformat(row['published_at'].replace('Z', '+00:00').replace(' ', 'T')),
            url=row['url'],
            image_url=row['image_url'],
            verified=bool(row['verified']),
            bias_score=row['bias_score'],
            reliability_score=row['reliability_score']
        ))
    
    conn.close()
    return articles

@app.get(f"{settings.API_V1_STR}/articles/{{article_id}}", response_model=Article)
async def get_article(article_id: int):
    """Get specific article by ID"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM articles WHERE id = ? AND verified = 1', (article_id,))
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Article not found")
    
    article = Article(
        id=row['id'],
        title=row['title'],
        content=row['content'],
        summary=row['summary'],
        source=row['source'],
        author=row['author'],
        published_at=datetime.fromisoformat(row['published_at'].replace('Z', '+00:00').replace(' ', 'T')),
        url=row['url'],
        image_url=row['image_url'],
        verified=bool(row['verified']),
        bias_score=row['bias_score'],
        reliability_score=row['reliability_score']
    )
    
    conn.close()
    return article

@app.get(f"{settings.API_V1_STR}/sources", response_model=List[NewsSource])
async def get_sources():
    """Get list of verified news sources"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sources WHERE verified = 1 ORDER BY reliability_score DESC')
    
    sources = []
    for row in cursor.fetchall():
        sources.append(NewsSource(
            id=row['id'],
            name=row['name'],
            url=row['url'],
            reliability_score=row['reliability_score'],
            verified=bool(row['verified'])
        ))
    
    conn.close()
    return sources

@app.get(f"{settings.API_V1_STR}/stats")
async def get_stats():
    """Get system statistics"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) as total FROM articles WHERE verified = 1')
    total_articles = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM sources WHERE verified = 1')
    total_sources = cursor.fetchone()['total']
    
    cursor.execute('SELECT AVG(reliability_score) as avg_reliability FROM articles WHERE verified = 1')
    avg_reliability = cursor.fetchone()['avg_reliability']
    
    cursor.execute('SELECT AVG(bias_score) as avg_bias FROM articles WHERE verified = 1')
    avg_bias = cursor.fetchone()['avg_bias']
    
    conn.close()
    
    return {
        "total_articles": total_articles,
        "total_sources": total_sources,
        "average_reliability": round(avg_reliability, 3),
        "average_bias_score": round(avg_bias, 3),
        "system_status": "operational",
        "last_updated": datetime.now()
    }

# Admin endpoints
@app.get(f"{settings.API_V1_STR}/admin/dashboard")
async def admin_dashboard():
    """Admin dashboard data"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Get article stats by source
    cursor.execute('''
        SELECT source, COUNT(*) as count, AVG(reliability_score) as avg_reliability
        FROM articles 
        WHERE verified = 1 
        GROUP BY source 
        ORDER BY count DESC
    ''')
    source_stats = cursor.fetchall()
    
    # Get recent articles
    cursor.execute('''
        SELECT title, source, published_at, bias_score, reliability_score
        FROM articles 
        WHERE verified = 1 
        ORDER BY published_at DESC 
        LIMIT 5
    ''')
    recent_articles = cursor.fetchall()
    
    conn.close()
    
    return {
        "source_stats": [dict(row) for row in source_stats],
        "recent_articles": [dict(row) for row in recent_articles],
        "timestamp": datetime.now()
    }

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    init_db()
    print(f"🚀 {settings.PROJECT_NAME} started successfully!")
    print(f"📊 API Documentation: http://localhost:8000/docs")
    print(f"🔧 Admin Demo: admin@heartofnews.com / admin123")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )