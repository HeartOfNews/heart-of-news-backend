"""
Telegram Channel Publishing Service
Handles posting news articles to Telegram channels
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from urllib.parse import quote

import httpx
from app.core.config import settings
from app.models.article import Article

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for publishing news articles to Telegram channels"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_CHANNEL_ID
        self.enabled = settings.TELEGRAM_ENABLED and self.bot_token and self.channel_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a text message to the configured Telegram channel"""
        if not self.enabled:
            logger.warning("Telegram service is not enabled or configured")
            return {"success": False, "error": "Service not configured"}
        
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": self.channel_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": False
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Message sent successfully to Telegram channel {self.channel_id}")
                    return {"success": True, "message_id": result["result"]["message_id"]}
                else:
                    logger.error(f"Telegram API error: {result}")
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Telegram message: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_photo(self, photo_url: str, caption: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a photo with caption to the configured Telegram channel"""
        if not self.enabled:
            logger.warning("Telegram service is not enabled or configured")
            return {"success": False, "error": "Service not configured"}
        
        url = f"{self.base_url}/sendPhoto"
        data = {
            "chat_id": self.channel_id,
            "photo": photo_url,
            "caption": caption,
            "parse_mode": parse_mode
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=30.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    logger.info(f"Photo sent successfully to Telegram channel {self.channel_id}")
                    return {"success": True, "message_id": result["result"]["message_id"]}
                else:
                    logger.error(f"Telegram API error: {result}")
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Telegram photo: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram photo: {e}")
            return {"success": False, "error": str(e)}
    
    def format_article_message(self, article: Article) -> str:
        """Format an article into a Telegram message"""
        # Format categories as hashtags
        categories = " ".join([f"#{cat.replace(' ', '').replace('-', '')}" 
                              for cat in (article.categories or [])])
        if not categories:
            categories = "#News"
        
        # Determine region flag based on categories and source
        region_flag = self._get_region_flag(article)
        
        # Format the message using the template
        message = settings.TELEGRAM_MESSAGE_TEMPLATE.format(
            title=self._escape_markdown(article.title),
            summary=self._escape_markdown(article.summary or article.content[:300] + "..."),
            region_flag=region_flag,
            categories=categories
        )
        
        return message
    
    def _get_region_flag(self, article: Article) -> str:
        """Get appropriate flag emoji based on article content and categories"""
        categories = [cat.lower() for cat in (article.categories or [])]
        source_name = article.source.name.lower() if article.source else ""
        title_content = (article.title + " " + (article.summary or "")).lower()
        
        # EU/Europe indicators
        eu_keywords = ["european union", "europe", "eu", "brussels", "eurozone", "european"]
        eu_sources = ["euronews", "politico europe", "euractiv", "eu observer"]
        
        if (any(keyword in title_content for keyword in eu_keywords) or
            any(source in source_name for source in eu_sources) or
            "european union" in categories or "europe" in categories):
            return "🇪🇺"
        
        # USA indicators
        usa_keywords = ["united states", "america", "washington", "congress", "white house", "biden", "trump"]
        usa_sources = ["associated press", "politico", "the hill", "cnn politics"]
        
        if (any(keyword in title_content for keyword in usa_keywords) or
            any(source in source_name for source in usa_sources) or
            "usa" in categories):
            return "🇺🇸"
        
        # Default to global politics
        return "🌍"
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Telegram Markdown"""
        if not text:
            return ""
        
        # Characters that need escaping in Telegram Markdown
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    async def publish_article(self, article: Article) -> Dict[str, Any]:
        """Publish a single article to the Telegram channel"""
        if not self.enabled:
            return {"success": False, "error": "Telegram service not enabled"}
        
        try:
            message = self.format_article_message(article)
            
            # Check if article has an image
            if article.image_url and article.image_url.strip():
                # Send as photo with caption
                result = await self.send_photo(article.image_url, message)
            else:
                # Send as text message
                result = await self.send_message(message)
            
            if result["success"]:
                logger.info(f"Successfully published article {article.id} to Telegram")
            else:
                logger.error(f"Failed to publish article {article.id} to Telegram: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error publishing article {article.id} to Telegram: {e}")
            return {"success": False, "error": str(e)}
    
    async def publish_articles(self, articles: List[Article]) -> Dict[str, Any]:
        """Publish multiple articles to the Telegram channel"""
        if not articles:
            return {"success": True, "published": 0, "failed": 0}
        
        published = 0
        failed = 0
        errors = []
        
        for article in articles:
            result = await self.publish_article(article)
            
            if result["success"]:
                published += 1
                # Add a small delay between messages to avoid rate limiting
                await asyncio.sleep(1)
            else:
                failed += 1
                errors.append(f"Article {article.id}: {result.get('error', 'Unknown error')}")
        
        logger.info(f"Telegram publishing complete: {published} published, {failed} failed")
        
        return {
            "success": failed == 0,
            "published": published,
            "failed": failed,
            "errors": errors
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the Telegram bot connection"""
        if not self.enabled:
            return {"success": False, "error": "Telegram service not configured"}
        
        url = f"{self.base_url}/getMe"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    bot_info = result["result"]
                    logger.info(f"Telegram bot connection successful: @{bot_info.get('username')}")
                    return {
                        "success": True,
                        "bot_username": bot_info.get("username"),
                        "bot_name": bot_info.get("first_name")
                    }
                else:
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Error testing Telegram connection: {e}")
            return {"success": False, "error": str(e)}


# Global instance
telegram_service = TelegramService()