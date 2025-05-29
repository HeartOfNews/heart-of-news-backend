#!/usr/bin/env python3
"""
Verified Russian News Bot - Heart of News
Only publishes REAL news from verified sources
Bot Token: 7851345007:AAF4ubtbbR5NSiMxBYRRqtY31hMpEq9AZxM
Channel: @HeartofNews_Rus
"""

import urllib.request
import urllib.parse
import json
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import hashlib

class VerifiedRussianNewsBot:
    """Russian news bot that only publishes verified real news"""
    
    def __init__(self):
        # Telegram configuration
        self.bot_token = "7851345007:AAF4ubtbbR5NSiMxBYRRqtY31hMpEq9AZxM"
        self.channel_id = "@HeartofNews_Rus"
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Track published articles to avoid duplicates
        self.published_hashes = set()
        
        # Verified Russian news sources (real news only)
        self.verified_sources = [
            {
                "name": "BBC Русская служба",
                "feed_url": "https://feeds.bbci.co.uk/russian/rss.xml",
                "reliability": 0.95,
                "description": "BBC Russian Service"
            },
            {
                "name": "Deutsche Welle на русском", 
                "feed_url": "https://rss.dw.com/rdf/rss-ru-all",
                "reliability": 0.90,
                "description": "DW Russian"
            },
            {
                "name": "РБК",
                "feed_url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss", 
                "reliability": 0.80,
                "description": "RBC News"
            }
        ]
    
    def test_connection(self) -> bool:
        """Test bot connection"""
        try:
            request = urllib.request.Request(f"{self.base_url}/getMe")
            with urllib.request.urlopen(request, timeout=10) as response:
                result = json.loads(response.read().decode())
            
            if result.get("ok"):
                bot_info = result["result"]
                print(f"✅ Bot connected: @{bot_info.get('username')}")
                return True
            else:
                print(f"❌ Bot connection failed: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def parse_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Parse RSS feed using built-in XML parser"""
        try:
            # Fetch RSS content
            request = urllib.request.Request(feed_url)
            request.add_header('User-Agent', 'Mozilla/5.0 (compatible; NewsBot)')
            
            with urllib.request.urlopen(request, timeout=15) as response:
                content = response.read().decode('utf-8')
            
            # Parse XML
            root = ET.fromstring(content)
            
            # Find all item elements (RSS entries)
            items = []
            
            # Try different RSS formats
            for item in root.findall('.//item'):
                title_elem = item.find('title')
                link_elem = item.find('link')
                description_elem = item.find('description')
                pubdate_elem = item.find('pubDate')
                
                if title_elem is not None and link_elem is not None:
                    items.append({
                        'title': title_elem.text or '',
                        'link': link_elem.text or '',
                        'description': description_elem.text or '' if description_elem is not None else '',
                        'pubDate': pubdate_elem.text or '' if pubdate_elem is not None else ''
                    })
            
            return items[:10]  # Limit to 10 items
            
        except Exception as e:
            print(f"❌ Error parsing RSS feed: {e}")
            return []
    
    def fetch_real_news(self, source: Dict[str, Any], max_articles: int = 5) -> List[Dict[str, Any]]:
        """Fetch real news articles from verified RSS feed"""
        try:
            print(f"📡 Fetching from {source['name']}...")
            
            # Parse RSS feed
            entries = self.parse_rss_feed(source["feed_url"])
            
            if not entries:
                print(f"⚠️ No articles found in {source['name']}")
                return []
            
            articles = []
            for entry in entries[:max_articles]:
                # Create article hash to avoid duplicates
                article_hash = hashlib.md5(
                    (entry['title'] + entry['link']).encode()
                ).hexdigest()[:12]
                
                if article_hash in self.published_hashes:
                    continue
                
                # Use current time as publication date
                pub_date = datetime.now()
                
                # Clean and validate content
                title = self.clean_text(entry['title'])
                summary = self.clean_text(entry['description'][:300])
                
                if not title or len(title) < 10:
                    continue
                
                article = {
                    "id": article_hash,
                    "title": title,
                    "summary": summary,
                    "link": entry['link'],
                    "published": pub_date,
                    "source": source["name"],
                    "reliability": source["reliability"]
                }
                
                articles.append(article)
            
            print(f"✅ Found {len(articles)} new articles from {source['name']}")
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching from {source['name']}: {e}")
            return []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        # Remove extra quotes and special characters
        text = text.strip('"\'""''')
        
        return text.strip()
    
    def verify_article_content(self, article: Dict[str, Any]) -> bool:
        """Basic verification of article content"""
        # Check for minimum content quality
        if len(article["title"]) < 10:
            return False
        
        # Check for spam/promotional content
        spam_keywords = [
            "купить", "продать", "скидка", "акция", "реклама",
            "click here", "buy now", "limited time"
        ]
        
        text_lower = (article["title"] + " " + article["summary"]).lower()
        if any(keyword in text_lower for keyword in spam_keywords):
            return False
        
        # Require high reliability source
        if article["reliability"] < 0.75:
            return False
        
        return True
    
    def create_telegram_message(self, article: Dict[str, Any]) -> str:
        """Create formatted message for news"""
        
        # Determine emoji based on content
        if any(word in article["title"].lower() for word in ["россия", "российский"]):
            flag = "🇷🇺"
        elif any(word in article["title"].lower() for word in ["украина", "украинский"]):
            flag = "🇺🇦"
        elif any(word in article["title"].lower() for word in ["европа", "ес", "европейский"]):
            flag = "🇪🇺"
        elif any(word in article["title"].lower() for word in ["сша", "америка"]):
            flag = "🇺🇸"
        else:
            flag = "🌍"
        
        # Format time
        time_str = article["published"].strftime("%H:%M")
        
        # Create message without source attribution
        message = f"""📰 {article['title']}

{article['summary']}

{flag} #{time_str.replace(':', '')} #Новости

📺 @HeartofNews_Rus"""
        
        return message
    
    def send_message(self, message: str) -> bool:
        """Send message to Telegram channel"""
        try:
            data = {
                'chat_id': self.channel_id,
                'text': message,
                'disable_web_page_preview': False
            }
            
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            request = urllib.request.Request(
                f"{self.base_url}/sendMessage",
                data=encoded_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(request, timeout=15) as response:
                result = json.loads(response.read().decode())
            
            if result.get("ok"):
                print(f"✅ Message sent successfully")
                return True
            else:
                print(f"❌ Telegram API error: {result.get('description', 'Unknown')}")
                return False
                
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def get_available_articles(self) -> List[Dict[str, Any]]:
        """Get all available articles from all sources"""
        all_articles = []
        
        for source in self.verified_sources:
            articles = self.fetch_real_news(source, max_articles=10)
            
            for article in articles:
                # Verify article content
                if self.verify_article_content(article):
                    all_articles.append(article)
        
        return all_articles
    
    def publish_single_article(self, articles: List[Dict[str, Any]]) -> bool:
        """Publish a single article from available articles"""
        if not articles:
            return False
        
        # Find an unpublished article
        for article in articles:
            if article["id"] not in self.published_hashes:
                # Create and send message
                message = self.create_telegram_message(article)
                
                print(f"📤 Publishing: {article['title'][:60]}...")
                
                if self.send_message(message):
                    self.published_hashes.add(article["id"])
                    print(f"✅ Published news article")
                    return True
                else:
                    print(f"❌ Failed to publish: {article['title'][:50]}...")
        
        return False
    
    def run_once(self):
        """Run news publishing once"""
        print("🇷🇺 RUSSIAN NEWS BOT - SINGLE RUN")
        print(f"📺 Channel: {self.channel_id}")
        print("=" * 40)
        
        if not self.test_connection():
            return
        
        # Get available articles
        articles = self.get_available_articles()
        
        if self.publish_single_article(articles):
            print("✅ Published news article")
        else:
            print("ℹ️ No new news to publish")
    
    def run_continuous(self):
        """Run bot continuously - posts every 1-5 minutes"""
        print("🇷🇺 RUSSIAN NEWS BOT - CONTINUOUS MODE")
        print(f"📺 Channel: {self.channel_id}")
        print("⏰ Posts every 1-5 minutes when news is available")
        print("=" * 50)
        
        if not self.test_connection():
            return
        
        total_published = 0
        articles_cache = []
        last_refresh = datetime.now() - timedelta(hours=1)  # Force initial refresh
        
        try:
            while True:
                current_time = datetime.now()
                
                # Refresh articles every 30 minutes
                if (current_time - last_refresh).total_seconds() > 1800:
                    print(f"\n🔄 Refreshing news sources... {current_time.strftime('%H:%M:%S')}")
                    articles_cache = self.get_available_articles()
                    last_refresh = current_time
                    print(f"📰 Found {len(articles_cache)} articles available")
                
                # Try to publish an article
                if self.publish_single_article(articles_cache):
                    total_published += 1
                    print(f"📊 Total published: {total_published}")
                
                # Random interval between 1-5 minutes (60-300 seconds)
                import random
                next_interval = random.randint(60, 300)
                next_post = current_time + timedelta(seconds=next_interval)
                
                print(f"⏳ Next post at: {next_post.strftime('%H:%M:%S')} ({next_interval//60}min {next_interval%60}s)")
                
                time.sleep(next_interval)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Bot stopped")
            print(f"📊 Final stats: {total_published} articles published")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 Restarting in 30 seconds...")
            time.sleep(30)
            self.run_continuous()

def main():
    """Main function"""
    import sys
    
    print("🇷🇺 HEART OF NEWS - RUSSIAN NEWS BOT")
    print("=" * 40)
    
    bot = VerifiedRussianNewsBot()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("🧪 Testing connection...")
        bot.test_connection()
    elif len(sys.argv) > 1 and sys.argv[1] == "--once":
        bot.run_once()
    else:
        bot.run_continuous()  # Posts every 1-5 minutes

if __name__ == "__main__":
    main()