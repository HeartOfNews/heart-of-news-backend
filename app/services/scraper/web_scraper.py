"""
Web scraper for news sources without RSS feeds
"""

import logging
import re
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
from urllib.parse import urlparse, urljoin

import aiohttp
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from app.services.scraper.base import BaseScraper, ArticleData

logger = logging.getLogger(__name__)

class WebScraper(BaseScraper):
    """
    Scraper for websites without RSS feeds
    """
    
    def __init__(self, source_config: Dict[str, Any]):
        """
        Initialize the web scraper
        
        Args:
            source_config: Dictionary containing:
                - name: Name of the source
                - url: Base URL of the source
                - id: Unique identifier for the source
                - article_selector: CSS selector for article links
                - content_selector: CSS selector for article content
                - title_selector: CSS selector for article title (optional)
                - date_selector: CSS selector for publication date (optional)
                - author_selector: CSS selector for author (optional)
                - tag_selector: CSS selector for tags/categories (optional)
                - ignore_urls: List of URL patterns to ignore (optional)
                - headers: Custom headers for requests (optional)
        """
        super().__init__(source_config)
        if not self.source_url:
            raise ValueError("url is required for web scraper")
            
        self.article_selector = source_config.get("article_selector", "a.article, .headline a, .story a, h2 a, h3 a")
        self.content_selector = source_config.get("content_selector", "article, .article, .post, .content, #content, main")
        self.title_selector = source_config.get("title_selector", "h1")
        self.date_selector = source_config.get("date_selector", "time, .date, .published, meta[property='article:published_time']")
        self.author_selector = source_config.get("author_selector", ".author, .byline, [rel=author], meta[property='article:author']")
        self.tag_selector = source_config.get("tag_selector", ".tags a, .categories a, .topics a")
        
        self.ignore_urls = source_config.get("ignore_urls", [
            "/search", "/login", "/signup", "/subscribe", "/account", "/privacy", "/terms", 
            "/about", "/contact", "/advertise", "/tag/", "/category/", "/author/"
        ])
        
        self.headers = source_config.get("headers", {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
        
        # For keeping track of already processed URLs
        self._processed_urls = set()
        
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """
        Fetch articles from the website
        
        Args:
            limit: Maximum number of articles to fetch
            
        Returns:
            List of ArticleData objects
        """
        try:
            # Fetch the main page
            async with aiohttp.ClientSession() as session:
                async with session.get(self.source_url, headers=self.headers) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch main page from {self.source_url}: {response.status}")
                        return []
                    
                    html_content = await response.text()
            
            # Parse the HTML
            soup = BeautifulSoup(html_content, "html.parser")
            
            # Extract article links
            article_links = []
            selectors = self.article_selector.split(",")
            
            for selector in selectors:
                for link in soup.select(selector.strip()):
                    if not link.has_attr("href"):
                        continue
                    
                    url = link["href"]
                    
                    # Handle relative URLs
                    if not url.startswith(("http://", "https://")):
                        url = urljoin(self.source_url, url)
                    
                    # Skip unwanted URLs
                    if self._should_ignore_url(url):
                        continue
                    
                    # Add URL to the list if not already there
                    if url not in article_links and url not in self._processed_urls:
                        article_links.append(url)
                        
                        # Stop if we have enough links
                        if len(article_links) >= limit:
                            break
                
                # Stop if we have enough links
                if len(article_links) >= limit:
                    break
            
            # If insufficient links found with primary selectors, try more generic ones
            if len(article_links) < limit:
                # Look for any link that seems like an article
                for link in soup.find_all("a", href=True):
                    url = link["href"]
                    
                    # Handle relative URLs
                    if not url.startswith(("http://", "https://")):
                        url = urljoin(self.source_url, url)
                    
                    # Skip unwanted URLs
                    if self._should_ignore_url(url):
                        continue
                    
                    # Articles often have "news", "article", "story", or date patterns in URL
                    article_patterns = [
                        r'/\d{4}/\d{2}/\d{2}/',  # Date pattern
                        r'/news/',
                        r'/article[s]?/',
                        r'/story/'
                    ]
                    
                    if any(re.search(pattern, url) for pattern in article_patterns):
                        # Add URL to the list if not already there
                        if url not in article_links and url not in self._processed_urls:
                            article_links.append(url)
                            
                            # Stop if we have enough links
                            if len(article_links) >= limit:
                                break
            
            # Fetch content for each article in parallel
            articles = []
            tasks = []
            
            for url in article_links:
                tasks.append(self.fetch_article_content(url))
            
            # Wait for all tasks to complete
            article_results = await asyncio.gather(*tasks)
            
            # Filter out None results
            articles = [article for article in article_results if article is not None]
            
            # Update processed URLs
            self._processed_urls.update(article_links)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching articles from {self.source_url}: {e}")
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
            title = ""
            # Try with configured selector
            title_element = soup.select_one(self.title_selector)
            if title_element:
                title = title_element.get_text().strip()
            
            # Fallback to title tag
            if not title:
                title_tag = soup.find("title")
                title = title_tag.text.strip() if title_tag else ""
            
            # Extract article content
            content_element = None
            
            # Try with the configured selector
            selectors = self.content_selector.split(",")
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
            
            # Try using the configured selector
            date_elements = soup.select(self.date_selector)
            if date_elements:
                date_element = date_elements[0]
                date_str = None
                
                # Check for datetime attribute
                if date_element.has_attr("datetime"):
                    date_str = date_element["datetime"]
                elif date_element.has_attr("content"):
                    date_str = date_element["content"]
                else:
                    date_str = date_element.get_text().strip()
                
                if date_str:
                    published_at = self._extract_published_date({"date_str": date_str})
            
            # Try meta tags as fallback
            if not published_at:
                meta_date = soup.find("meta", property=["article:published_time", "og:published_time", "publication_date"])
                if meta_date and meta_date.get("content"):
                    published_at = self._extract_published_date({"date_str": meta_date["content"]})
            
            # Extract author
            author = None
            
            # Try using the configured selector
            author_elements = soup.select(self.author_selector)
            if author_elements:
                author_element = author_elements[0]
                
                if author_element.name == "meta" and author_element.has_attr("content"):
                    author = author_element["content"]
                else:
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
                    img_src = img_tag["src"]
                    # Handle relative URLs
                    if not img_src.startswith(("http://", "https://")):
                        image_url = urljoin(article_url, img_src)
                    else:
                        image_url = img_src
            
            # Extract tags/categories
            tags = []
            
            # Try using the configured selector
            tag_elements = soup.select(self.tag_selector)
            if tag_elements:
                tags = [element.get_text().strip() for element in tag_elements]
            
            # Try meta keywords as fallback
            if not tags:
                meta_keywords = soup.find("meta", {"name": "keywords"})
                if meta_keywords and meta_keywords.get("content"):
                    tags = [tag.strip() for tag in meta_keywords["content"].split(",")]
            
            # Extract summary
            summary = None
            meta_description = soup.find("meta", {"name": "description"})
            if meta_description and meta_description.get("content"):
                summary = meta_description["content"]
            
            if not summary:
                og_description = soup.find("meta", property=["og:description", "twitter:description"])
                if og_description and og_description.get("content"):
                    summary = og_description["content"]
            
            # If still no summary, use first paragraph of content
            if not summary and content:
                paragraphs = content.split('\n')
                if paragraphs:
                    first_para = paragraphs[0].strip()
                    if len(first_para) > 50:
                        summary = first_para[:200] + ('...' if len(first_para) > 200 else '')
            
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
    
    def _should_ignore_url(self, url: str) -> bool:
        """
        Check if a URL should be ignored
        
        Args:
            url: URL to check
            
        Returns:
            True if the URL should be ignored, False otherwise
        """
        # Parse URL
        parsed_url = urlparse(url)
        
        # Check if URL is on the same domain
        source_domain = urlparse(self.source_url).netloc
        url_domain = parsed_url.netloc
        
        if not url_domain.endswith(source_domain) and not source_domain.endswith(url_domain):
            return True
        
        # Check against ignore patterns
        path = parsed_url.path.lower()
        
        for pattern in self.ignore_urls:
            if pattern.lower() in path:
                return True
        
        # Check for common non-article URL patterns
        if path.endswith((".jpg", ".jpeg", ".png", ".gif", ".pdf", ".zip", ".doc", ".docx")):
            return True
        
        if path in ["/", "/index.html", "/index.php", ""]:
            return True
        
        # Check for pagination and list pages
        if re.search(r'/(page|p)/\d+/?$', path):
            return True
        
        return False
    
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
            # Clean up date string
            date_str = re.sub(r"(Published|Updated|Posted)[\s:]+", "", date_str)
            
            # Try to parse with dateutil parser
            return date_parser.parse(date_str)
        except (ValueError, TypeError):
            logger.warning(f"Failed to parse date: {date_str}")
            return None