"""
Tests for scraper services
"""

import os
import asyncio
import unittest
from typing import Dict, List, Any
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.services.scraper.base import BaseScraper, ArticleData
from app.services.scraper.rss_scraper import RssScraper
from app.services.scraper.web_scraper import WebScraper
from app.services.scraper.factory import ScraperFactory
from app.services.scraper.manager import ScraperManager
from app.services.scraper.sources import get_default_sources

# Sample HTML response
SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Sample News Site</title>
    <meta name="description" content="This is a sample news site for testing scrapers">
    <meta property="og:image" content="https://example.com/image.jpg">
</head>
<body>
    <header>
        <h1>Sample News Site</h1>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <div class="featured">
            <h2><a href="/news/article1">Featured Article: Big News Today</a></h2>
            <p>This is a summary of the big news today.</p>
        </div>
        <div class="articles">
            <div class="article">
                <h3><a href="/news/article2">Another Important Story</a></h3>
                <p>Summary of another important story.</p>
                <span class="date">2025-05-07</span>
            </div>
            <div class="article">
                <h3><a href="/news/article3">Third News Item</a></h3>
                <p>Summary of the third news item.</p>
                <span class="date">2025-05-06</span>
            </div>
        </div>
    </main>
    <footer>
        <p>&copy; 2025 Sample News Site</p>
    </footer>
</body>
</html>
"""

# Sample article HTML
SAMPLE_ARTICLE_HTML = """<!DOCTYPE html>
<html>
<head>
    <title>Big News Today - Sample News Site</title>
    <meta name="description" content="Detailed article about the big news today">
    <meta property="og:image" content="https://example.com/article-image.jpg">
    <meta property="article:published_time" content="2025-05-07T12:00:00Z">
    <meta property="article:author" content="John Doe">
    <meta name="keywords" content="news,important,sample">
</head>
<body>
    <header>
        <h1>Sample News Site</h1>
        <nav>
            <ul>
                <li><a href="/">Home</a></li>
                <li><a href="/about">About</a></li>
                <li><a href="/contact">Contact</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <article class="article">
            <h1>Big News Today</h1>
            <div class="metadata">
                <span class="author">By John Doe</span>
                <time datetime="2025-05-07T12:00:00Z">May 7, 2025</time>
            </div>
            <div class="article-content">
                <p>This is the first paragraph of the article with detailed information about the big news today.</p>
                <p>This is the second paragraph with more details and context about what happened.</p>
                <p>Here's a third paragraph with some quotes and additional information from sources.</p>
                <p>The conclusion summarizes the key points and potential future developments.</p>
            </div>
            <div class="tags">
                <span>Tags:</span>
                <a href="/tags/news">News</a>
                <a href="/tags/important">Important</a>
                <a href="/tags/sample">Sample</a>
            </div>
        </article>
        <div class="related-articles">
            <h3>Related Articles</h3>
            <ul>
                <li><a href="/news/related1">Related Article 1</a></li>
                <li><a href="/news/related2">Related Article 2</a></li>
            </ul>
        </div>
    </main>
    <footer>
        <p>&copy; 2025 Sample News Site</p>
    </footer>
</body>
</html>
"""

# Sample RSS feed content
SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
    <title>Sample News Feed</title>
    <link>https://example.com</link>
    <description>Sample RSS feed for testing</description>
    <lastBuildDate>Wed, 07 May 2025 12:00:00 GMT</lastBuildDate>
    <item>
        <title>First News Item</title>
        <link>https://example.com/news/item1</link>
        <description>This is the description of the first news item.</description>
        <pubDate>Wed, 07 May 2025 10:00:00 GMT</pubDate>
        <author>Jane Smith</author>
        <category>News</category>
        <category>Important</category>
    </item>
    <item>
        <title>Second News Item</title>
        <link>https://example.com/news/item2</link>
        <description>This is the description of the second news item.</description>
        <pubDate>Wed, 07 May 2025 09:00:00 GMT</pubDate>
        <author>John Doe</author>
        <category>News</category>
        <category>Sample</category>
    </item>
    <item>
        <title>Third News Item</title>
        <link>https://example.com/news/item3</link>
        <description>This is the description of the third news item.</description>
        <pubDate>Wed, 07 May 2025 08:00:00 GMT</pubDate>
        <author>Alice Johnson</author>
        <category>News</category>
    </item>
</channel>
</rss>
"""


class MockResponse:
    def __init__(self, text, status=200):
        self.text = text
        self.status = status
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        pass
        
    async def text(self):
        return self.text


class MockSession:
    def __init__(self, mock_responses=None):
        self.mock_responses = mock_responses or {}
        self.urls_requested = []
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc, tb):
        pass
        
    async def get(self, url, headers=None):
        self.urls_requested.append(url)
        
        # Return the mock response for this URL if available
        if url in self.mock_responses:
            return MockResponse(self.mock_responses[url])
            
        # For article URLs, return the sample article
        if "/news/" in url or "/item" in url:
            return MockResponse(SAMPLE_ARTICLE_HTML)
            
        # Default responses based on URL patterns
        if url.endswith(".xml") or "rss" in url:
            return MockResponse(SAMPLE_RSS)
        else:
            return MockResponse(SAMPLE_HTML)


class TestWebScraper(unittest.TestCase):
    """Test the WebScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.source_config = {
            "id": "test-source",
            "name": "Test Source",
            "url": "https://example.com",
            "type": "web",
            "article_selector": ".article h3 a, .featured h2 a",
            "content_selector": ".article-content, article",
            "title_selector": "h1",
            "date_selector": "time, .date",
            "author_selector": ".author, meta[property='article:author']",
            "tag_selector": ".tags a"
        }
        
        # Create the scraper
        self.scraper = WebScraper(self.source_config)
        
        # Mock aiohttp.ClientSession
        self.session_patcher = patch("aiohttp.ClientSession", MockSession)
        self.MockClientSession = self.session_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session_patcher.stop()
    
    def test_initialization(self):
        """Test that scraper initializes correctly"""
        assert self.scraper is not None
        assert self.scraper.name == "Test Source"
        assert self.scraper.source_url == "https://example.com"
        assert self.scraper.source_id == "test-source"
        
    async def test_fetch_articles(self):
        """Test fetching articles from the web page"""
        articles = await self.scraper.fetch_articles(limit=5)
        
        # Should find both articles on the page
        assert len(articles) >= 2
        
        # Check the first article
        first_article = articles[0]
        assert "Big News Today" in first_article.title
        assert first_article.url.startswith("https://example.com/news/article")
        
    async def test_fetch_article_content(self):
        """Test fetching article content"""
        article = await self.scraper.fetch_article_content("https://example.com/news/article1")
        
        assert article is not None
        assert article.title == "Big News Today"
        assert article.author == "John Doe"
        assert len(article.content) > 200
        assert article.published_at is not None
        assert article.summary is not None
        assert len(article.tags) >= 2
        
    def test_should_ignore_url(self):
        """Test URL filtering logic"""
        # These should be ignored
        assert self.scraper._should_ignore_url("https://example.com/about") is True
        assert self.scraper._should_ignore_url("https://example.com/contact") is True
        assert self.scraper._should_ignore_url("https://example.com/image.jpg") is True
        assert self.scraper._should_ignore_url("https://otherdomain.com/news") is True
        
        # These should not be ignored
        assert self.scraper._should_ignore_url("https://example.com/news/article1") is False
        assert self.scraper._should_ignore_url("https://example.com/news/important-story") is False


class TestRssScraper(unittest.TestCase):
    """Test the RssScraper class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.source_config = {
            "id": "test-rss-source",
            "name": "Test RSS Source",
            "url": "https://example.com",
            "type": "rss",
            "feed_url": "https://example.com/feed.xml",
            "article_selector": ".article-content, article"
        }
        
        # Create the scraper
        self.scraper = RssScraper(self.source_config)
        
        # Mock aiohttp.ClientSession
        self.session_patcher = patch("aiohttp.ClientSession", MockSession)
        self.MockClientSession = self.session_patcher.start()
        
        # Mock feedparser
        self.feedparser_patcher = patch("feedparser.parse")
        self.mock_feedparser = self.feedparser_patcher.start()
        
        # Create a mock feed object
        mock_feed = MagicMock()
        mock_feed.entries = [
            MagicMock(
                title="First News Item",
                link="https://example.com/news/item1",
                summary="This is the description of the first news item.",
                published="Wed, 07 May 2025 10:00:00 GMT",
                author="Jane Smith",
                tags=[MagicMock(term="News"), MagicMock(term="Important")]
            ),
            MagicMock(
                title="Second News Item",
                link="https://example.com/news/item2",
                summary="This is the description of the second news item.",
                published="Wed, 07 May 2025 09:00:00 GMT",
                author="John Doe",
                tags=[MagicMock(term="News"), MagicMock(term="Sample")]
            )
        ]
        self.mock_feedparser.return_value = mock_feed
    
    def tearDown(self):
        """Clean up after tests"""
        self.session_patcher.stop()
        self.feedparser_patcher.stop()
    
    def test_initialization(self):
        """Test that scraper initializes correctly"""
        assert self.scraper is not None
        assert self.scraper.name == "Test RSS Source"
        assert self.scraper.feed_url == "https://example.com/feed.xml"
        
    async def test_fetch_articles(self):
        """Test fetching articles from the RSS feed"""
        articles = await self.scraper.fetch_articles(limit=5)
        
        # Should find both articles in the feed
        assert len(articles) == 2
        
        # Check the first article
        first_article = articles[0]
        assert first_article.title == "First News Item"
        assert first_article.url == "https://example.com/news/item1"
        assert first_article.summary == "This is the description of the first news item."
        assert first_article.author == "Jane Smith"
        assert len(first_article.tags) == 2
        assert "News" in first_article.tags
        assert "Important" in first_article.tags
        
    async def test_fetch_article_content(self):
        """Test fetching article content"""
        article = await self.scraper.fetch_article_content("https://example.com/news/item1")
        
        assert article is not None
        assert "Big News Today" in article.title
        assert len(article.content) > 200


class TestScraperFactory(unittest.TestCase):
    """Test the ScraperFactory class"""
    
    def test_create_rss_scraper(self):
        """Test creating an RSS scraper"""
        source_config = {
            "id": "test-rss",
            "name": "Test RSS",
            "url": "https://example.com",
            "type": "rss",
            "feed_url": "https://example.com/feed.xml"
        }
        
        scraper = ScraperFactory.create_scraper(source_config)
        
        assert scraper is not None
        assert isinstance(scraper, RssScraper)
        assert scraper.name == "Test RSS"
        assert scraper.feed_url == "https://example.com/feed.xml"
    
    def test_create_web_scraper(self):
        """Test creating a web scraper"""
        source_config = {
            "id": "test-web",
            "name": "Test Web",
            "url": "https://example.com",
            "type": "web"
        }
        
        scraper = ScraperFactory.create_scraper(source_config)
        
        assert scraper is not None
        assert isinstance(scraper, WebScraper)
        assert scraper.name == "Test Web"
        assert scraper.source_url == "https://example.com"
    
    def test_auto_detect_type(self):
        """Test auto-detecting scraper type"""
        # Should detect as RSS scraper
        source_config_rss = {
            "id": "test-auto-rss",
            "name": "Test Auto RSS",
            "url": "https://example.com",
            "type": "auto",
            "feed_url": "https://example.com/feed.xml"
        }
        
        scraper_rss = ScraperFactory.create_scraper(source_config_rss)
        assert isinstance(scraper_rss, RssScraper)
        
        # Should default to web scraper
        source_config_web = {
            "id": "test-auto-web",
            "name": "Test Auto Web",
            "url": "https://example.com",
            "type": "auto"
        }
        
        scraper_web = ScraperFactory.create_scraper(source_config_web)
        assert isinstance(scraper_web, WebScraper)
    
    def test_create_multiple_scrapers(self):
        """Test creating scrapers for multiple sources"""
        sources = [
            {
                "id": "source1",
                "name": "Source 1",
                "url": "https://example1.com",
                "type": "rss",
                "feed_url": "https://example1.com/feed.xml"
            },
            {
                "id": "source2",
                "name": "Source 2",
                "url": "https://example2.com",
                "type": "web"
            }
        ]
        
        scrapers = ScraperFactory.create_scrapers_for_sources(sources)
        
        assert len(scrapers) == 2
        assert "source1" in scrapers
        assert "source2" in scrapers
        assert isinstance(scrapers["source1"], RssScraper)
        assert isinstance(scrapers["source2"], WebScraper)


class TestScraperManager(unittest.TestCase):
    """Test the ScraperManager class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Mock the database session
        self.mock_db = MagicMock()
        
        # Create test manager
        self.manager = ScraperManager(db=self.mock_db)
        
        # Create mock scrapers
        self.mock_scraper1 = MagicMock(spec=BaseScraper)
        self.mock_scraper1.name = "Test Source 1"
        self.mock_scraper1.source_url = "https://example1.com"
        self.mock_scraper1.fetch_articles = AsyncMock(return_value=[
            ArticleData(url="https://example1.com/article1", title="Article 1"),
            ArticleData(url="https://example1.com/article2", title="Article 2")
        ])
        
        self.mock_scraper2 = MagicMock(spec=BaseScraper)
        self.mock_scraper2.name = "Test Source 2"
        self.mock_scraper2.source_url = "https://example2.com"
        self.mock_scraper2.fetch_articles = AsyncMock(return_value=[
            ArticleData(url="https://example2.com/article1", title="Article 1")
        ])
        
        # Set up the scrapers in the manager
        self.manager.scrapers = {
            "source1": self.mock_scraper1,
            "source2": self.mock_scraper2
        }
    
    async def test_scrape_all_sources(self):
        """Test scraping from all sources"""
        results = await self.manager.scrape_all_sources(limit_per_source=5)
        
        # Both scrapers should be called
        self.mock_scraper1.fetch_articles.assert_called_once_with(limit=5)
        self.mock_scraper2.fetch_articles.assert_called_once_with(limit=5)
        
        # Check results
        assert "source1" in results
        assert "source2" in results
        assert len(results["source1"]) == 2
        assert len(results["source2"]) == 1
        
        # Check that last_run is updated
        assert "source1" in self.manager.last_run
        assert "source2" in self.manager.last_run
    
    async def test_get_source_stats(self):
        """Test getting source statistics"""
        # First run a scrape to populate last_run
        await self.manager.scrape_all_sources()
        
        # Now get stats
        stats = await self.manager.get_source_stats()
        
        assert "source1" in stats
        assert "source2" in stats
        assert stats["source1"]["name"] == "Test Source 1"
        assert stats["source1"]["url"] == "https://example1.com"
        assert stats["source1"]["last_run"] is not None
        assert stats["source2"]["last_run"] is not None


if __name__ == "__main__":
    unittest.main()