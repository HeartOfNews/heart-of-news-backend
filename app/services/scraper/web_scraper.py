"""
General web scraper for news websites
"""

import logging
import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, List, Optional, Any
from dateutil import parser as date_parser

from app.services.scraper.base import BaseScraper, ArticleData

logger = logging.getLogger(__name__)


class WebScraper(BaseScraper):
    """General web scraper for news websites"""
    
    def __init__(self, source_config: Dict[str, Any]):
        super().__init__(source_config)
        self.selectors = source_config.get("selectors", {})
        self.required_selectors = ["article_links", "title", "content"]
        
        # Validate required selectors
        for selector in self.required_selectors:
            if selector not in self.selectors:
                raise ValueError(f"Web scraper requires '{selector}' selector in source config")
    
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """Fetch articles from the website's main page"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.source_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch {self.source_url}: {response.status}")
                        return []
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Find article links
                    article_links = soup.select(self.selectors["article_links"])
                    articles = []
                    
                    for link_element in article_links[:limit]:
                        article_url = self._extract_url(link_element)
                        if article_url and self._is_valid_article_url(article_url):
                            # Try to extract basic info from the listing page
                            article_data = await self._extract_article_preview(link_element, article_url)
                            if article_data:
                                articles.append(article_data)
                    
                    logger.info(f"Found {len(articles)} articles from {self.name}")
                    return articles
                    
        except Exception as e:
            logger.error(f"Error fetching articles from {self.name}: {str(e)}")
            return []
    
    async def fetch_article_content(self, article_url: str) -> Optional[ArticleData]:
        """Fetch full content for a specific article"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(article_url) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch article {article_url}: {response.status}")
                        return None
                    
                    content = await response.text()
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    return self._extract_article_data(soup, article_url)
                    
        except Exception as e:
            logger.error(f"Error fetching article content from {article_url}: {str(e)}")
            return None
    
    def _extract_url(self, link_element) -> Optional[str]:
        """Extract URL from a link element"""
        if link_element.name == 'a':
            href = link_element.get('href', '')
        else:
            link = link_element.find('a')
            href = link.get('href', '') if link else ''
        
        if not href:
            return None
        
        # Convert relative URLs to absolute
        if href.startswith('/'):
            from urllib.parse import urljoin
            href = urljoin(self.source_url, href)
        elif not href.startswith('http'):
            return None
        
        return href
    
    def _is_valid_article_url(self, url: str) -> bool:
        """Check if URL looks like a valid article URL"""
        # Basic validation - you might want to customize this per source
        invalid_patterns = ['/tag/', '/category/', '/author/', '/search/', '?', '#']
        return not any(pattern in url for pattern in invalid_patterns)
    
    async def _extract_article_preview(self, element, url: str) -> Optional[ArticleData]:
        """Extract basic article info from listing page element"""
        try:
            title_element = element.find(self.selectors.get("title_preview", "h1, h2, h3"))
            title = title_element.get_text(strip=True) if title_element else "No Title"
            
            summary_element = element.find(self.selectors.get("summary_preview", ".summary, .excerpt"))
            summary = summary_element.get_text(strip=True) if summary_element else None
            
            return ArticleData(
                url=url,
                title=title,
                content=None,  # Will be fetched separately
                summary=summary,
                published_at=None,  # Will be extracted when fetching full content
                author=None,
                image_url=None,
                tags=None,
                metadata={
                    "source": self.name,
                    "source_id": self.source_id,
                    "scraped_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error extracting article preview: {str(e)}")
            return None
    
    def _extract_article_data(self, soup: BeautifulSoup, url: str) -> Optional[ArticleData]:
        """Extract full article data from article page"""
        try:
            # Extract title
            title_element = soup.find(self.selectors["title"])
            title = title_element.get_text(strip=True) if title_element else "No Title"
            
            # Extract content
            content_elements = soup.select(self.selectors["content"])
            content_parts = []
            for element in content_elements:
                text = element.get_text(strip=True)
                if text:
                    content_parts.append(text)
            content = "\n\n".join(content_parts) if content_parts else None
            
            # Extract summary/description
            summary = None
            if "summary" in self.selectors:
                summary_element = soup.find(self.selectors["summary"])
                summary = summary_element.get_text(strip=True) if summary_element else None
            
            # Try to get summary from meta description if not found
            if not summary:
                meta_desc = soup.find("meta", {"name": "description"})
                summary = meta_desc.get("content") if meta_desc else None
            
            # Extract published date
            published_at = None
            if "published_date" in self.selectors:
                date_element = soup.find(self.selectors["published_date"])
                if date_element:
                    date_text = date_element.get_text(strip=True)
                    try:
                        published_at = date_parser.parse(date_text)
                    except Exception as e:
                        logger.warning(f"Failed to parse date '{date_text}': {e}")
            
            # Extract author
            author = None
            if "author" in self.selectors:
                author_element = soup.find(self.selectors["author"])
                author = author_element.get_text(strip=True) if author_element else None
            
            # Extract image
            image_url = None
            if "image" in self.selectors:
                img_element = soup.find(self.selectors["image"])
                if img_element:
                    image_url = img_element.get("src") or img_element.get("data-src")
            
            # Extract tags
            tags = []
            if "tags" in self.selectors:
                tag_elements = soup.select(self.selectors["tags"])
                tags = [tag.get_text(strip=True) for tag in tag_elements]
            
            return ArticleData(
                url=url,
                title=title,
                content=content,
                summary=summary,
                published_at=published_at,
                author=author,
                image_url=image_url,
                tags=tags,
                metadata={
                    "source": self.name,
                    "source_id": self.source_id,
                    "scraped_at": datetime.utcnow().isoformat()
                }
            )
            
        except Exception as e:
            logger.error(f"Error extracting article data: {str(e)}")
            return None