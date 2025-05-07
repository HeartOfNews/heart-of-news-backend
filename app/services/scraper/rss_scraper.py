"""
RSS Feed scraper for news sources
"""

import logging
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse

import aiohttp
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from app.services.scraper.base import BaseScraper, ArticleData

logger = logging.getLogger(__name__)

class RssScraper(BaseScraper):
    """
    Scraper for RSS feed news sources
    """
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize the RSS scraper
        
        Args:
            source_config: Dictionary containing:
                - name: Name of the source
                - url: Base URL of the source
                - id: Unique identifier for the source
                - feed_url: URL of the RSS feed
                - article_selector: CSS selector for the main article content
                - date_format: Format of dates in the feed (optional)
                - headers: Custom headers for requests (optional)
        """
        super().__init__(source_config)
        self.feed_url = source_config.get("feed_url")
        if not self.feed_url:
            raise ValueError("feed_url is required for RSS scraper")
            
        self.article_selector = source_config.get("article_selector", "article, .article, .post, .content, #content, main")
        self.date_format = source_config.get("date_format")
        self.headers = source_config.get("headers", {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """
        Fetch articles from the RSS feed
        
        Args:
            limit: Maximum number of articles to fetch
            
        Returns:
            List of ArticleData objects
        """
        try:
            # Fetch the RSS feed
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch RSS feed from {self.feed_url}: {response.status}")
                        return []
                    
                    feed_content = await response.text()
            
            # Parse the feed
            feed = feedparser.parse(feed_content)
            
            if not feed.entries:
                logger.warning(f"No entries found in feed: {self.feed_url}")
                return []
            
            # Process feed entries
            articles = []
            for entry in feed.entries[:limit]:
                try:
                    # Extract basic article data
                    article_url = entry.link
                    title = entry.title
                    
                    # Try to get summary/content from feed
                    content = None
                    summary = None
                    
                    if hasattr(entry, "content") and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, "summary"):
                        summary = entry.summary
                        
                    # Parse publication date
                    published_at = None
                    if hasattr(entry, "published"):
                        published_at = self._extract_published_date({"date_str": entry.published})
                    elif hasattr(entry, "updated"):
                        published_at = self._extract_published_date({"date_str": entry.updated})
                    
                    # Extract author
                    author = None
                    if hasattr(entry, "author"):
                        author = entry.author
                    
                    # Extract tags
                    tags = []
                    if hasattr(entry, "tags"):
                        tags = [tag.term for tag in entry.tags] if hasattr(entry, "tags") else []
                    elif hasattr(entry, "categories"):
                        tags = list(entry.categories)
                    
                    # Extract image URL
                    image_url = None
                    if hasattr(entry, "media_content") and entry.media_content:
                        for media in entry.media_content:
                            if "url" in media and media.get("medium", "") in ["image", ""]:
                                image_url = media["url"]
                                break
                    
                    if not image_url and hasattr(entry, "links"):
                        for link in entry.links:
                            if link.get("type", "").startswith("image/"):
                                image_url = link.href
                                break
                                
                    if not image_url and summary:
                        # Try to extract image from summary HTML
                        soup = BeautifulSoup(summary, "html.parser")
                        img_tag = soup.find("img")
                        if img_tag and img_tag.get("src"):
                            image_url = img_tag["src"]
                    
                    # Create article data object
                    article = ArticleData(
                        url=article_url,
                        title=title,
                        content=content,
                        summary=summary,
                        published_at=published_at,
                        author=author,
                        image_url=image_url,
                        tags=tags
                    )
                    
                    articles.append(article)
                    
                except Exception as e:
                    logger.error(f"Error processing RSS entry: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed from {self.feed_url}: {e}")
            return []
    
    async def fetch_article_content(self, article_url: str) -> Optional[ArticleData]:
        """
        Fetch full content for a specific article
        
        Args:
            article_url: URL of the article to fetch
            
        Returns:
            ArticleData object with full content or None if failed
        """
        try:
            # Fetch the article page
            async with aiohttp.ClientSession() as session:
                async with session.get(article_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch article from {article_url}: {response.status}")
                        return None
                    
                    html_content = await response.text()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract article title
            title_tag = soup.find("title")
            title = title_tag.text.strip() if title_tag else ""
            
            # Try to find a more specific title in the article
            article_title_tags = soup.select("h1")
            if article_title_tags:
                title = article_title_tags[0].text.strip()
            
            # Extract article content
            content_element = None
            
            # Try with the configured selector
            selectors = self.article_selector.split(",")
            for selector in selectors:
                content_element = soup.select_one(selector.strip())
                if content_element:
                    break
            
            # If still no content element, try common fallbacks
            if not content_element:
                for selector in ["article", ".article-body", ".entry-content", "#article-body"]:
                    content_element = soup.select_one(selector)
                    if content_element:
                        break
            
            # Extract content as text
            content = ""
            if content_element:
                # Remove unwanted elements
                for unwanted in content_element.select(".ad, .advertisement, .social-share, nav, .nav, .comments, .sidebar, .related-articles"):
                    unwanted.decompose()
                
                content = content_element.get_text("\n").strip()
            else:
                # Fallback: just extract the main text from the body
                body = soup.find("body")
                if body:
                    for unwanted in body.select("header, footer, nav, .nav, .menu, script, style, [role=banner], [role=navigation]"):
                        unwanted.decompose()
                    content = "\n".join(p.get_text().strip() for p in body.find_all("p") if len(p.get_text().strip()) > 50)
            
            # Clean the content
            content = self._clean_html(content)
            
            # Extract publication date
            published_at = None
            # Try meta tags first
            meta_date = soup.find("meta", property=["article:published_time", "og:published_time", "publication_date"])
            if meta_date and meta_date.get("content"):
                published_at = self._extract_published_date({"date_str": meta_date["content"]})
            
            # Try common time tags if meta tag not found
            if not published_at:
                time_tags = soup.find_all("time")
                if time_tags and time_tags[0].get("datetime"):
                    published_at = self._extract_published_date({"date_str": time_tags[0]["datetime"]})
            
            # Extract author
            author = None
            # Try various common patterns
            author_meta = soup.find("meta", property=["article:author", "og:author", "author"])
            if author_meta and author_meta.get("content"):
                author = author_meta["content"]
            
            if not author:
                author_element = soup.select_one(".author, .byline, [rel=author]")
                if author_element:
                    author = author_element.get_text().strip()
                    # Clean up common prefixes
                    author = re.sub(r"^(By|Author)[:\s]+", "", author, flags=re.IGNORECASE).strip()
            
            # Extract image URL
            image_url = None
            og_image = soup.find("meta", property=["og:image", "twitter:image"])
            if og_image and og_image.get("content"):
                image_url = og_image["content"]
            
            if not image_url and content_element:
                img_tag = content_element.find("img")
                if img_tag and img_tag.get("src"):
                    image_url = img_tag["src"]
            
            # Extract tags/categories
            tags = []
            meta_keywords = soup.find("meta", {"name": "keywords"})
            if meta_keywords and meta_keywords.get("content"):
                tags = [tag.strip() for tag in meta_keywords["content"].split(",")]
            
            if not tags:
                # Try to find tag links
                tag_links = soup.select(".tags a, .categories a, .topics a")
                if tag_links:
                    tags = [link.get_text().strip() for link in tag_links]
            
            # Extract summary
            summary = None
            meta_description = soup.find("meta", {"name": "description"})
            if meta_description and meta_description.get("content"):
                summary = meta_description["content"]
            
            if not summary:
                og_description = soup.find("meta", property=["og:description", "twitter:description"])
                if og_description and og_description.get("content"):
                    summary = og_description["content"]
            
            # Create article data object
            article = ArticleData(
                url=article_url,
                title=title,
                content=content,
                summary=summary,
                published_at=published_at,
                author=author,
                image_url=image_url,
                tags=tags
            )
            
            return article
            
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {e}")
            return None
    
    def _clean_html(self, html_content: str) -> str:
        """
        Clean HTML content
        
        Args:
            html_content: HTML content to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', html_content).strip()
        
        # Remove common advertisement phrases
        ad_patterns = [
            r'ADVERTISEMENT',
            r'Sponsored Content',
            r'Click here to.*',
            r'Subscribe to.*',
            r'Follow us on.*',
            r'Share this article',
            r'Download our app',
        ]
        
        for pattern in ad_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Deduplicate paragraphs (sometimes the same text appears multiple times)
        paragraphs = text.split('\n')
        unique_paragraphs = []
        seen = set()
        
        for p in paragraphs:
            p_cleaned = p.strip()
            if p_cleaned and p_cleaned not in seen and len(p_cleaned) > 20:
                seen.add(p_cleaned)
                unique_paragraphs.append(p)
        
        return '\n'.join(unique_paragraphs)
    
    def _extract_published_date(self, data: Dict[str, Any]) -> Optional[datetime]:
        """
        Extract and parse published date
        
        Args:
            data: Dictionary containing date information
            
        Returns:
            Parsed datetime object or None if parsing failed
        """
        date_str = data.get("date_str")
        if not date_str:
            return None
        
        try:
            # Try to parse with dateutil parser
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse date: {date_str}")
            return None