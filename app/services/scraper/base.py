"""
Base scraper service for retrieving news articles
"""

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, HttpUrl

logger = logging.getLogger(__name__)

class ArticleData(BaseModel):
    """Data structure for scraped articles"""
    url: HttpUrl
    title: str
    content: Optional[str] = None
    summary: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, source_config: Dict[str, Any]):
        self.source_config = source_config
        self.name = source_config.get("name", "Unknown Source")
        self.source_url = source_config.get("url")
        self.source_id = source_config.get("id")
    
    @abstractmethod
    async def fetch_articles(self, limit: int = 10) -> List[ArticleData]:
        """Fetch articles from the source"""
        pass
    
    @abstractmethod
    async def fetch_article_content(self, article_url: str) -> Optional[ArticleData]:
        """Fetch full content for a specific article"""
        pass
    
    def _clean_html(self, html_content: str) -> str:
        """Clean HTML content by removing ads, navigation, etc."""
        # This would contain HTML cleaning logic
        # For now it's a placeholder
        return html_content
    
    def _extract_published_date(self, data: Dict[str, Any]) -> Optional[datetime]:
        """Extract and parse published date from various formats"""
        # This would contain date parsing logic
        # For now it's a placeholder
        return datetime.now()
    
    def _extract_article_image(self, html_content: str, article_url: str) -> Optional[str]:
        """Extract the main article image from HTML content"""
        if not html_content:
            return None
        
        # Priority order for image extraction
        image_selectors = [
            # OpenGraph image (most reliable)
            r'<meta\s+property=["\']og:image["\'][^>]*content=["\']([^"\']+)["\']',
            # Twitter card image
            r'<meta\s+name=["\']twitter:image["\'][^>]*content=["\']([^"\']+)["\']',
            # Article main image
            r'<img[^>]+class=["\'][^"\']*(?:main|hero|featured|article)[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
            # First img in article content
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*(?:alt=["\'][^"\']*(?:photo|image|picture)[^"\']*["\'])?',
            # Any img with news-related alt text
            r'<img[^>]+alt=["\'][^"\']*(?:news|article|story|photo)[^"\']*["\'][^>]*src=["\']([^"\']+)["\']'
        ]
        
        for selector in image_selectors:
            matches = re.findall(selector, html_content, re.IGNORECASE | re.DOTALL)
            if matches:
                image_url = matches[0]
                # Convert relative URLs to absolute
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                elif image_url.startswith('/'):
                    image_url = urljoin(article_url, image_url)
                elif not image_url.startswith('http'):
                    image_url = urljoin(article_url, image_url)
                
                # Validate image URL
                if self._is_valid_image_url(image_url):
                    return image_url
        
        return None
    
    def _is_valid_image_url(self, url: str) -> bool:
        """Validate if URL is a real image"""
        if not url:
            return False
        
        # Check for common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg']
        url_lower = url.lower()
        
        # Direct extension check
        if any(url_lower.endswith(ext) for ext in image_extensions):
            return True
        
        # Check for image in URL path
        if any(ext in url_lower for ext in image_extensions):
            return True
        
        # Exclude obvious non-images
        exclude_patterns = [
            'logo', 'icon', 'avatar', 'placeholder', 
            'blank', 'spacer', 'pixel', 'transparent',
            'ad.', 'ads.', 'banner', 'promo'
        ]
        
        if any(pattern in url_lower for pattern in exclude_patterns):
            return False
        
        # Check domain reputation (basic)
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Trusted image domains
        trusted_domains = [
            'reuters.com', 'ap.org', 'bbc.com', 'cnn.com',
            'politico.com', 'euronews.com', 'ft.com',
            'washingtonpost.com', 'nytimes.com', 'wsj.com',
            'bloomberg.com', 'theguardian.com'
        ]
        
        # If from trusted news domain, more likely to be real
        if any(trusted in domain for trusted in trusted_domains):
            return True
        
        # Basic size/quality indicators in URL
        quality_indicators = ['large', 'high', 'full', 'original', 'master']
        if any(indicator in url_lower for indicator in quality_indicators):
            return True
        
        return True  # Default to true for now, can be more restrictive
    
    def _extract_image_metadata(self, html_content: str) -> Dict[str, str]:
        """Extract image metadata like alt text, caption"""
        metadata = {}
        
        # Extract alt text
        alt_match = re.search(r'alt=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
        if alt_match:
            metadata['alt'] = alt_match.group(1)
        
        # Extract caption (common patterns)
        caption_selectors = [
            r'<figcaption[^>]*>([^<]+)</figcaption>',
            r'<div[^>]*class=["\'][^"\']*caption[^"\']*["\'][^>]*>([^<]+)</div>',
            r'<p[^>]*class=["\'][^"\']*caption[^"\']*["\'][^>]*>([^<]+)</p>'
        ]
        
        for selector in caption_selectors:
            caption_match = re.search(selector, html_content, re.IGNORECASE | re.DOTALL)
            if caption_match:
                metadata['caption'] = caption_match.group(1).strip()
                break
        
        return metadata