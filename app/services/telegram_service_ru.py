"""
Russian Telegram Channel Publishing Service
Handles posting news articles to Russian-language Telegram channels
"""

import asyncio
import logging
from typing import List, Optional, Dict, Any

import httpx
from app.core.config import settings
from app.models.article import Article

logger = logging.getLogger(__name__)


class TelegramRussianService:
    """Service for publishing news articles to Russian Telegram channels"""
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_RU_BOT_TOKEN
        self.channel_id = settings.TELEGRAM_RU_CHANNEL_ID
        self.enabled = settings.TELEGRAM_RU_ENABLED and self.bot_token and self.channel_id
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}" if self.bot_token else None
        
    async def send_message(self, text: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a text message to the configured Russian Telegram channel"""
        if not self.enabled:
            logger.warning("Russian Telegram service is not enabled or configured")
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
                    logger.info(f"Russian message sent successfully to Telegram channel {self.channel_id}")
                    return {"success": True, "message_id": result["result"]["message_id"]}
                else:
                    logger.error(f"Russian Telegram API error: {result}")
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Russian Telegram message: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending Russian Telegram message: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_photo(self, photo_url: str, caption: str, parse_mode: str = "Markdown") -> Dict[str, Any]:
        """Send a photo with caption to the configured Russian Telegram channel"""
        if not self.enabled:
            logger.warning("Russian Telegram service is not enabled or configured")
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
                    logger.info(f"Russian photo sent successfully to Telegram channel {self.channel_id}")
                    return {"success": True, "message_id": result["result"]["message_id"]}
                else:
                    logger.error(f"Russian Telegram API error: {result}")
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending Russian Telegram photo: {e}")
            return {"success": False, "error": str(e)}
        except Exception as e:
            logger.error(f"Unexpected error sending Russian Telegram photo: {e}")
            return {"success": False, "error": str(e)}
    
    def format_article_message(self, article: Article, translate_to_russian: bool = True) -> str:
        """Format an article into a Russian Telegram message"""
        # Translate/format categories for Russian audience
        categories = self._format_russian_categories(article.categories or [])
        
        # Determine region flag based on Russian geopolitical perspective
        region_flag = self._get_russian_region_flag(article)
        
        # Use Russian title and summary if available, otherwise use translation
        title = article.title
        summary = article.summary or article.content[:300] + "..."
        
        if translate_to_russian:
            title = self._translate_to_russian_context(title)
            summary = self._translate_to_russian_context(summary)
        
        # Format the message using Russian template
        message = settings.TELEGRAM_RU_MESSAGE_TEMPLATE.format(
            title=self._escape_markdown(title),
            summary=self._escape_markdown(summary),
            region_flag=region_flag,
            categories=categories
        )
        
        return message
    
    def _format_russian_categories(self, categories: List[str]) -> str:
        """Format categories for Russian audience with proper hashtags"""
        # Translation mapping for common categories
        category_translations = {
            "Politics": "Политика",
            "USA": "США", 
            "European Union": "ЕС",
            "Europe": "Европа",
            "Economics": "Экономика",
            "Breaking": "Срочно",
            "International": "Международное",
            "Defense": "Оборона",
            "Security": "Безопасность",
            "Elections": "Выборы",
            "Congress": "Конгресс",
            "Parliament": "Парламент",
            "NATO": "НАТО",
            "Technology": "Технологии",
            "AI": "ИИ"
        }
        
        russian_categories = []
        for cat in categories:
            # Use translation if available, otherwise use original
            russian_cat = category_translations.get(cat, cat)
            # Create hashtag
            hashtag = f"#{russian_cat.replace(' ', '').replace('-', '')}"
            russian_categories.append(hashtag)
        
        if not russian_categories:
            russian_categories = ["#Новости"]
        
        return " ".join(russian_categories)
    
    def _get_russian_region_flag(self, article: Article) -> str:
        """Get appropriate flag emoji based on Russian geopolitical perspective"""
        categories = [cat.lower() for cat in (article.categories or [])]
        source_name = article.source.name.lower() if article.source else ""
        title_content = (article.title + " " + (article.summary or "")).lower()
        
        # Russia-related indicators
        russia_keywords = ["россия", "российский", "путин", "кремль", "москва", "russia", "russian"]
        if any(keyword in title_content for keyword in russia_keywords):
            return "🇷🇺"
        
        # USA indicators
        usa_keywords = ["сша", "америка", "washington", "congress", "white house", "biden", "trump", "united states"]
        if any(keyword in title_content for keyword in usa_keywords) or "usa" in categories:
            return "🇺🇸"
        
        # EU/Europe indicators  
        eu_keywords = ["европейский союз", "ес", "брюссель", "europe", "european union", "eu"]
        if any(keyword in title_content for keyword in eu_keywords) or "european union" in categories:
            return "🇪🇺"
        
        # Ukraine indicators
        ukraine_keywords = ["украина", "украинский", "киев", "зеленский", "ukraine"]
        if any(keyword in title_content for keyword in ukraine_keywords):
            return "🇺🇦"
        
        # China indicators
        china_keywords = ["китай", "китайский", "пекин", "china", "chinese"]
        if any(keyword in title_content for keyword in china_keywords):
            return "🇨🇳"
        
        # Default to global
        return "🌍"
    
    def _translate_to_russian_context(self, text: str) -> str:
        """Adapt text for Russian-speaking audience context"""
        # Simple context adaptations for key terms
        adaptations = {
            "European Union": "Европейский союз",
            "United States": "Соединенные Штаты",
            "Congress": "Конгресс США",
            "Parliament": "Парламент",
            "NATO": "НАТО",
            "White House": "Белый дом",
            "Brussels": "Брюссель",
            "Washington": "Вашингтон"
        }
        
        adapted_text = text
        for en_term, ru_term in adaptations.items():
            adapted_text = adapted_text.replace(en_term, ru_term)
        
        return adapted_text
    
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
        """Publish a single article to the Russian Telegram channel"""
        if not self.enabled:
            return {"success": False, "error": "Russian Telegram service not enabled"}
        
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
                logger.info(f"Successfully published article {article.id} to Russian Telegram")
            else:
                logger.error(f"Failed to publish article {article.id} to Russian Telegram: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error publishing article {article.id} to Russian Telegram: {e}")
            return {"success": False, "error": str(e)}
    
    async def publish_articles(self, articles: List[Article]) -> Dict[str, Any]:
        """Publish multiple articles to the Russian Telegram channel"""
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
        
        logger.info(f"Russian Telegram publishing complete: {published} published, {failed} failed")
        
        return {
            "success": failed == 0,
            "published": published,
            "failed": failed,
            "errors": errors
        }
    
    async def test_connection(self) -> Dict[str, Any]:
        """Test the Russian Telegram bot connection"""
        if not self.enabled:
            return {"success": False, "error": "Russian Telegram service not configured"}
        
        url = f"{self.base_url}/getMe"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    bot_info = result["result"]
                    logger.info(f"Russian Telegram bot connection successful: @{bot_info.get('username')}")
                    return {
                        "success": True,
                        "bot_username": bot_info.get("username"),
                        "bot_name": bot_info.get("first_name")
                    }
                else:
                    return {"success": False, "error": result.get("description", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Error testing Russian Telegram connection: {e}")
            return {"success": False, "error": str(e)}


# Global instance
telegram_russian_service = TelegramRussianService()