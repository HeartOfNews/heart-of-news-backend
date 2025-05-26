#!/usr/bin/env python3
"""
Russian Verified News Worker
Scrapes real news from Russian media sources, detects propaganda, rewrites content if needed, and publishes verified news
"""

import asyncio
import logging
import sys
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.services.scraper.rss_scraper import RSSScraper
from app.services.scraper.sources_ru import get_russian_sources, get_russian_sources_by_priority
from app.services.ai.propaganda_detector import propaganda_detector
from app.services.telegram_service_ru import telegram_russian_service
from app.models.article import Article
from app.models.source import Source
import httpx
import feedparser
from bs4 import BeautifulSoup
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/russian_verified_news.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class RussianNewsRewriter:
    """Rewrites news content to remove propaganda while maintaining factual accuracy"""
    
    def __init__(self):
        self.propaganda_replacements = {
            # Loaded language replacements
            "режим": "правительство",
            "оккупация": "присутствие",
            "аннексия": "присоединение",
            "марионетка": "представитель",
            "диктатор": "лидер",
            "тиран": "руководитель",
            "террористы": "вооруженные группы",
            "экстремисты": "радикальные группы",
            "фанатики": "сторонники",
            
            # Emotional manipulation
            "возмутительный": "спорный",
            "шокирующий": "неожиданный",
            "разрушительный": "значительный",
            "ужасающий": "серьезный",
            "угроза демократии": "политический вызов",
            "экзистенциальный кризис": "серьезная проблема",
            "катастрофический": "значительный",
            
            # False dichotomy fixes
            "с нами или против нас": "различные позиции",
            "единственный выбор": "один из вариантов",
            "нет альтернативы": "ограниченные варианты",
        }
        
        self.neutral_replacements = {
            # Make language more neutral
            "заявил": "сообщил",
            "обвинил": "указал на",
            "раскритиковал": "выразил несогласие с",
            "осудил": "выразил обеспокоенность",
            "потребовал": "призвал к",
        }
    
    def rewrite_content(self, title: str, content: str, propaganda_analysis: Dict[str, Any]) -> Dict[str, str]:
        """
        Rewrite content to remove propaganda while maintaining factual accuracy
        
        Args:
            title: Original title
            content: Original content
            propaganda_analysis: Results from propaganda detection
            
        Returns:
            Dictionary with rewritten title and content
        """
        rewritten_title = self._rewrite_text(title, propaganda_analysis)
        rewritten_content = self._rewrite_text(content, propaganda_analysis)
        
        # Ensure factual claims are preserved
        rewritten_content = self._preserve_facts(content, rewritten_content)
        
        return {
            "title": rewritten_title,
            "content": rewritten_content,
            "changes_made": self._detect_changes(title, content, rewritten_title, rewritten_content)
        }
    
    def _rewrite_text(self, text: str, analysis: Dict[str, Any]) -> str:
        """Rewrite text to remove propaganda techniques"""
        rewritten = text
        
        # Apply propaganda-specific replacements
        for original, replacement in self.propaganda_replacements.items():
            rewritten = re.sub(r'\b' + re.escape(original) + r'\b', replacement, rewritten, flags=re.IGNORECASE)
        
        # Apply neutral language replacements
        for original, replacement in self.neutral_replacements.items():
            rewritten = re.sub(r'\b' + re.escape(original) + r'\b', replacement, rewritten, flags=re.IGNORECASE)
        
        # Remove excessive emotional language
        rewritten = self._tone_down_emotional_language(rewritten)
        
        # Fix false dichotomies
        rewritten = self._fix_false_dichotomies(rewritten)
        
        # Remove unverified claims if not from reliable sources
        rewritten = self._qualify_unverified_claims(rewritten)
        
        return rewritten
    
    def _tone_down_emotional_language(self, text: str) -> str:
        """Reduce emotional intensity in language"""
        # Replace superlatives with more measured language
        emotional_patterns = {
            r'\bкрайне\s+(\w+)': r'весьма \1',
            r'\bчрезвычайно\s+(\w+)': r'очень \1',
            r'\bневероятно\s+(\w+)': r'заметно \1',
            r'\bшокирующе\s+(\w+)': r'неожиданно \1',
        }
        
        for pattern, replacement in emotional_patterns.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _fix_false_dichotomies(self, text: str) -> str:
        """Fix false either/or statements"""
        # Replace absolute statements with more nuanced language
        dichotomy_fixes = {
            r'\bлибо\s+(\w+),?\s+либо\s+(\w+)': r'среди вариантов \1 и \2',
            r'\bтолько\s+(\w+)\s+или\s+(\w+)': r'главным образом \1 или \2',
            r'\bнет\s+другого\s+выбора': 'варианты ограничены',
        }
        
        for pattern, replacement in dichotomy_fixes.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _qualify_unverified_claims(self, text: str) -> str:
        """Add qualifiers to unverified claims"""
        # Add "по сообщениям" or similar qualifiers to unverified statements
        unverified_patterns = [
            (r'\bсообщается,?\s+что\s+', 'по имеющимся сообщениям, '),
            (r'\bизвестно,?\s+что\s+', 'согласно источникам, '),
            (r'\bутверждается,?\s+что\s+', 'предполагается, что '),
        ]
        
        for pattern, replacement in unverified_patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _preserve_facts(self, original: str, rewritten: str) -> str:
        """Ensure factual information like dates, numbers, names are preserved"""
        # Extract and preserve dates
        date_pattern = r'\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b|\b\d{1,2}\s+\w+\s+\d{4}\b'
        original_dates = re.findall(date_pattern, original)
        rewritten_dates = re.findall(date_pattern, rewritten)
        
        # If dates were lost, try to preserve them
        if len(original_dates) > len(rewritten_dates):
            for date in original_dates:
                if date not in rewritten:
                    # Find a good place to insert the date
                    rewritten = self._insert_preserved_fact(rewritten, date, "date")
        
        # Preserve numbers and percentages
        number_pattern = r'\b\d+[.,]?\d*\s*%|\b\d+[.,]?\d*\s*(миллион|миллиард|тысяч|процент)'
        original_numbers = re.findall(number_pattern, original)
        rewritten_numbers = re.findall(number_pattern, rewritten)
        
        if len(original_numbers) > len(rewritten_numbers):
            for number in original_numbers:
                if number not in rewritten:
                    rewritten = self._insert_preserved_fact(rewritten, number, "number")
        
        return rewritten
    
    def _insert_preserved_fact(self, text: str, fact: str, fact_type: str) -> str:
        """Insert a preserved fact into the rewritten text"""
        # Simple insertion at the end of the first sentence
        sentences = text.split('.')
        if len(sentences) > 1:
            sentences[0] += f" ({fact})"
            return '.'.join(sentences)
        return text + f" ({fact})"
    
    def _detect_changes(self, orig_title: str, orig_content: str, new_title: str, new_content: str) -> List[str]:
        """Detect what changes were made during rewriting"""
        changes = []
        
        if orig_title != new_title:
            changes.append("title_rewritten")
        
        if orig_content != new_content:
            changes.append("content_rewritten")
        
        # Check for specific types of changes
        for original, replacement in self.propaganda_replacements.items():
            if original.lower() in orig_content.lower() and replacement.lower() in new_content.lower():
                changes.append(f"propaganda_language_removed: {original} -> {replacement}")
        
        return changes


class RussianVerifiedNewsWorker:
    """Main worker for processing Russian news with propaganda detection and verification"""
    
    def __init__(self):
        self.scraper = RSSScraper()
        self.rewriter = RussianNewsRewriter()
        self.sources = get_russian_sources_by_priority("high")
        self.published_articles = set()  # Track published articles to avoid duplicates
        
    async def run_continuous(self, interval_minutes: int = 30):
        """Run the worker continuously, checking for new news every interval"""
        logger.info(f"Starting Russian verified news worker with {interval_minutes} minute intervals")
        
        while True:
            try:
                await self.process_news_cycle()
                logger.info(f"Sleeping for {interval_minutes} minutes...")
                await asyncio.sleep(interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in news cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def process_news_cycle(self):
        """Process one complete news cycle: scrape, verify, rewrite if needed, publish"""
        logger.info("=== Starting Russian news cycle ===")
        
        # Step 1: Scrape news from Russian sources
        logger.info("Scraping news from Russian sources...")
        articles = await self._scrape_russian_news()
        logger.info(f"Found {len(articles)} new articles")
        
        if not articles:
            logger.info("No new articles found")
            return
        
        # Step 2: Process each article
        verified_articles = []
        for article in articles:
            processed_article = await self._process_article(article)
            if processed_article:
                verified_articles.append(processed_article)
        
        logger.info(f"Verified {len(verified_articles)} articles for publishing")
        
        # Step 3: Publish verified articles
        if verified_articles:
            await self._publish_articles(verified_articles)
        
        logger.info("=== Russian news cycle complete ===")
    
    async def _scrape_russian_news(self) -> List[Dict[str, Any]]:
        """Scrape news from Russian sources"""
        articles = []
        
        for source_config in self.sources:
            try:
                logger.info(f"Scraping from {source_config['name']}")
                
                # Use RSS scraper for RSS sources
                if source_config.get("type") == "rss" and source_config.get("feed_url"):
                    source_articles = await self._scrape_rss_source(source_config)
                    articles.extend(source_articles)
                    
                await asyncio.sleep(2)  # Rate limiting
                
            except Exception as e:
                logger.error(f"Error scraping {source_config['name']}: {e}")
                continue
        
        # Filter out duplicates and already published
        unique_articles = []
        seen_titles = set()
        
        for article in articles:
            title_key = article['title'].lower().strip()
            article_id = f"{article['source_name']}:{title_key}"
            
            if title_key not in seen_titles and article_id not in self.published_articles:
                seen_titles.add(title_key)
                unique_articles.append(article)
        
        return unique_articles
    
    async def _scrape_rss_source(self, source_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Scrape a single RSS source"""
        articles = []
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(source_config["feed_url"])
                response.raise_for_status()
                
                feed = feedparser.parse(response.text)
                
                for entry in feed.entries[:10]:  # Limit to 10 recent articles
                    # Skip if article is older than 24 hours
                    pub_date = entry.get('published_parsed')
                    if pub_date:
                        pub_datetime = datetime(*pub_date[:6])
                        if datetime.now() - pub_datetime > timedelta(days=1):
                            continue
                    
                    # Extract article content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    # Clean HTML
                    if content:
                        soup = BeautifulSoup(content, 'html.parser')
                        content = soup.get_text().strip()
                    
                    article = {
                        "title": entry.title,
                        "content": content,
                        "url": entry.link,
                        "source_name": source_config["name"],
                        "source_config": source_config,
                        "published_at": pub_datetime if pub_date else datetime.now(),
                        "language": "ru"
                    }
                    
                    articles.append(article)
                    
        except Exception as e:
            logger.error(f"Error scraping RSS {source_config['feed_url']}: {e}")
        
        return articles
    
    async def _process_article(self, article_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single article: analyze, verify, rewrite if needed"""
        title = article_data["title"]
        content = article_data["content"]
        source_config = article_data["source_config"]
        
        logger.info(f"Processing: {title[:100]}...")
        
        # Step 1: Analyze for propaganda and bias
        analysis = propaganda_detector.analyze_content(title, content, source_config)
        
        logger.info(f"Analysis results - Propaganda: {analysis['propaganda_score']:.2f}, "
                   f"Bias: {analysis['bias_score']:.2f}, Reliability: {analysis['reliability_score']:.2f}")
        
        # Step 2: Make decision based on analysis
        recommendation = analysis["recommendation"]
        
        if recommendation == "REJECT":
            logger.warning(f"REJECTED: {title[:50]}... - {analysis['concerns']}")
            return None
        
        processed_article = {
            "original_title": title,
            "original_content": content,
            "title": title,
            "content": content,
            "url": article_data["url"],
            "source_name": article_data["source_name"],
            "source_config": source_config,
            "published_at": article_data["published_at"],
            "language": "ru",
            "analysis": analysis,
            "rewrite_applied": False,
            "changes_made": []
        }
        
        # Step 3: Rewrite if needed (REVIEW cases or detected propaganda)
        if (recommendation == "REVIEW" or 
            analysis["propaganda_score"] > 0.3 or 
            len(analysis["propaganda_techniques"]) > 0):
            
            logger.info(f"Rewriting article due to propaganda detection: {analysis['propaganda_techniques']}")
            
            rewrite_result = self.rewriter.rewrite_content(title, content, analysis)
            
            processed_article.update({
                "title": rewrite_result["title"],
                "content": rewrite_result["content"],
                "rewrite_applied": True,
                "changes_made": rewrite_result["changes_made"]
            })
            
            logger.info(f"Article rewritten. Changes: {rewrite_result['changes_made']}")
        
        # Step 4: Final verification
        if analysis["verification_needed"]:
            logger.info("Article requires additional verification - marking for manual review")
            processed_article["requires_manual_review"] = True
        
        return processed_article
    
    async def _publish_articles(self, articles: List[Dict[str, Any]]):
        """Publish verified articles to Telegram"""
        logger.info(f"Publishing {len(articles)} verified articles to Russian Telegram channel")
        
        published_count = 0
        for article_data in articles:
            try:
                # Skip articles requiring manual review
                if article_data.get("requires_manual_review"):
                    logger.info(f"Skipping article requiring manual review: {article_data['title'][:50]}...")
                    continue
                
                # Create Article object for Telegram service
                article = self._create_article_object(article_data)
                
                # Publish to Telegram
                result = await telegram_russian_service.publish_article(article)
                
                if result["success"]:
                    published_count += 1
                    
                    # Mark as published to avoid duplicates
                    article_id = f"{article_data['source_name']}:{article_data['original_title'].lower().strip()}"
                    self.published_articles.add(article_id)
                    
                    # Log publication details
                    rewrite_status = "REWRITTEN" if article_data["rewrite_applied"] else "ORIGINAL"
                    logger.info(f"✅ PUBLISHED ({rewrite_status}): {article_data['title'][:50]}...")
                    
                    if article_data["rewrite_applied"]:
                        logger.info(f"   Changes made: {article_data['changes_made']}")
                    
                    # Add delay between publications
                    await asyncio.sleep(3)
                else:
                    logger.error(f"Failed to publish: {article_data['title'][:50]}... - {result.get('error')}")
                
            except Exception as e:
                logger.error(f"Error publishing article: {e}")
        
        logger.info(f"Successfully published {published_count} articles to Russian Telegram channel")
    
    def _create_article_object(self, article_data: Dict[str, Any]) -> Article:
        """Create Article object from article data"""
        # Create a mock Article object with required fields
        class MockArticle:
            def __init__(self, data):
                self.id = hash(data["title"])
                self.title = data["title"]
                self.content = data["content"]
                self.summary = data["content"][:300] + "..." if len(data["content"]) > 300 else data["content"]
                self.url = data["url"]
                self.image_url = None
                self.published_at = data["published_at"]
                self.categories = ["Новости", "Россия"]
                self.source = MockSource(data["source_name"])
                
        class MockSource:
            def __init__(self, name):
                self.name = name
        
        return MockArticle(article_data)


async def main():
    """Main entry point"""
    # Test connection first
    logger.info("Testing Russian Telegram connection...")
    connection_test = await telegram_russian_service.test_connection()
    
    if not connection_test["success"]:
        logger.error(f"Russian Telegram connection failed: {connection_test.get('error')}")
        logger.error("Please check your TELEGRAM_RU_BOT_TOKEN and TELEGRAM_RU_CHANNEL_ID configuration")
        return
    
    logger.info(f"✅ Russian Telegram connected: @{connection_test.get('bot_username')}")
    
    # Start the worker
    worker = RussianVerifiedNewsWorker()
    
    # Check if we should run once or continuously
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        logger.info("Running single news cycle...")
        await worker.process_news_cycle()
    else:
        # Run continuously with 30 minute intervals
        await worker.run_continuous(interval_minutes=30)


if __name__ == "__main__":
    asyncio.run(main())