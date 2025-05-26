#!/usr/bin/env python3
"""
Start Russian Heart of News Bot - Working Version
Publishes real verified Russian news with propaganda detection
"""

import urllib.request
import urllib.parse
import json
import os
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any
import xml.etree.ElementTree as ET

class RussianNewsBot:
    """Complete Russian news bot with propaganda detection"""
    
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Russian sources with RSS feeds - more sources for frequent updates
        self.sources = [
            {
                "name": "BBC Russian",
                "feed_url": "https://feeds.bbci.co.uk/russian/rss.xml",
                "reliability": 0.95,
                "bias": 0.0
            },
            {
                "name": "Deutsche Welle Russian",
                "feed_url": "https://rss.dw.com/rdf/rss-ru-all",
                "reliability": 0.9,
                "bias": 0.0
            },
            {
                "name": "Meduza",
                "feed_url": "https://meduza.io/rss/all",
                "reliability": 0.85,
                "bias": -0.1
            },
            {
                "name": "Radio Svoboda",
                "feed_url": "https://www.svoboda.org/api/epiqq",
                "reliability": 0.85,
                "bias": -0.2
            },
            {
                "name": "Current Time",
                "feed_url": "https://www.currenttime.tv/api/epiqq",
                "reliability": 0.85,
                "bias": -0.1
            },
            {
                "name": "RBC",
                "feed_url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
                "reliability": 0.8,
                "bias": 0.1
            }
        ]
        
        # Propaganda detection patterns
        self.propaganda_patterns = {
            "loaded_language": [
                r"\b(марионетк|кукловод|режим|экстремист|радикал|террорист|провокаци)\w*",
                r"\b(оккупант|агрессор|захватчик|фашист|нацист)\w*"
            ],
            "emotional_manipulation": [
                r"\b(возмутительн|шокирующ|ужасающ|катастрофическ|экзистенциальн)\w*",
                r"\b(позорн|постыдн|чудовищн|варварск)\w*"
            ],
            "unverified_claims": [
                r"\b(согласно источникам|по сообщениям инсайдеров|как стало известно)",
                r"\b(по слухам|ходят слухи|как говорят)\b"
            ]
        }
        
        # Content rewriting rules
        self.replacements = {
            "марионетки": "представители",
            "кукловоды": "партнеры", 
            "режим": "правительство",
            "экстремисты": "вооруженные группы",
            "радикалы": "активисты",
            "террористы": "вооруженные формирования",
            "провокации": "действия",
            "возмутительные": "спорные",
            "шокирующие": "неожиданные",
            "ужасающие": "серьезные",
            "катастрофические": "значительные",
            "согласно источникам": "по имеющимся данным"
        }
        
        self.published_articles = set()
        
    def fetch_rss_feed(self, url: str) -> List[Dict]:
        """Fetch and parse RSS feed"""
        try:
            print(f"📡 Fetching RSS from: {url}")
            with urllib.request.urlopen(url, timeout=15) as response:
                content = response.read().decode('utf-8')
            
            # Parse XML
            root = ET.fromstring(content)
            articles = []
            
            # Find items (handle different RSS formats)
            items = root.findall('.//item') or root.findall('.//{http://purl.org/rss/1.0/}item')
            
            for item in items[:10]:  # Get more articles for frequent updates
                title_elem = item.find('title') or item.find('{http://purl.org/rss/1.0/}title')
                desc_elem = item.find('description') or item.find('{http://purl.org/rss/1.0/}description')
                link_elem = item.find('link') or item.find('{http://purl.org/rss/1.0/}link')
                
                if title_elem is not None and title_elem.text:
                    # Check publication date for freshness
                    pub_date_elem = item.find('pubDate') or item.find('{http://purl.org/rss/1.0/}date')
                    pub_timestamp = datetime.now()  # Default to now if no date
                    
                    # Parse publication date if available
                    if pub_date_elem is not None and pub_date_elem.text:
                        try:
                            import email.utils
                            parsed_time = email.utils.parsedate_to_datetime(pub_date_elem.text)
                            pub_timestamp = parsed_time.replace(tzinfo=None)
                        except:
                            pub_timestamp = datetime.now()
                    
                    # Only include articles published in the last 6 hours for freshness
                    if datetime.now() - pub_timestamp < timedelta(hours=6):
                        article = {
                            "title": title_elem.text.strip(),
                            "content": desc_elem.text.strip() if desc_elem is not None and desc_elem.text else "",
                            "url": link_elem.text.strip() if link_elem is not None and link_elem.text else "",
                            "timestamp": pub_timestamp
                        }
                        
                        # Clean HTML tags from content
                        article["content"] = re.sub(r'<[^>]+>', '', article["content"])
                        
                        articles.append(article)
            
            print(f"✅ Found {len(articles)} articles")
            return articles
            
        except Exception as e:
            print(f"❌ Error fetching RSS {url}: {e}")
            return []
    
    def analyze_propaganda(self, title: str, content: str, source_reliability: float) -> Dict[str, Any]:
        """Analyze content for propaganda"""
        full_text = f"{title} {content}".lower()
        
        analysis = {
            "propaganda_score": 0.0,
            "techniques": [],
            "detected_phrases": [],
            "reliability": source_reliability,
            "recommendation": "APPROVE"
        }
        
        # Check for propaganda patterns
        for technique, patterns in self.propaganda_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    if technique not in analysis["techniques"]:
                        analysis["techniques"].append(technique)
                    analysis["detected_phrases"].append(match.group())
                    analysis["propaganda_score"] += 0.2
        
        # Limit score
        analysis["propaganda_score"] = min(1.0, analysis["propaganda_score"])
        
        # Make recommendation
        if analysis["propaganda_score"] > 0.6:
            analysis["recommendation"] = "REJECT"
        elif analysis["propaganda_score"] > 0.3:
            analysis["recommendation"] = "REVIEW"
        
        return analysis
    
    def rewrite_content(self, title: str, content: str) -> Dict[str, str]:
        """Rewrite content to remove propaganda"""
        rewritten_title = title
        rewritten_content = content
        changes = []
        
        for original, replacement in self.replacements.items():
            if original in rewritten_title.lower():
                rewritten_title = re.sub(re.escape(original), replacement, rewritten_title, flags=re.IGNORECASE)
                changes.append(f"title: {original} → {replacement}")
            
            if original in rewritten_content.lower():
                rewritten_content = re.sub(re.escape(original), replacement, rewritten_content, flags=re.IGNORECASE)
                changes.append(f"content: {original} → {replacement}")
        
        return {
            "title": rewritten_title,
            "content": rewritten_content,
            "changes": changes
        }
    
    def format_telegram_message(self, article: Dict, source_name: str, rewritten: bool = False) -> str:
        """Format article for Telegram"""
        # Determine flag
        title_lower = article["title"].lower()
        if any(word in title_lower for word in ["россия", "российский", "рф"]):
            flag = "🇷🇺"
        elif any(word in title_lower for word in ["украина", "украинский"]):
            flag = "🇺🇦"
        elif any(word in title_lower for word in ["ес", "европ", "брюссель"]):
            flag = "🇪🇺"
        else:
            flag = "🌍"
        
        # Create summary
        summary = article["content"][:250] + "..." if len(article["content"]) > 250 else article["content"]
        
        message = f"""🔴 **НОВОСТИ**

**{article['title']}**

{summary}

{flag} #Новости #Россия"""
        
        return message
    
    def send_telegram_message(self, text: str) -> bool:
        """Send message to Telegram channel"""
        try:
            data = {
                'chat_id': self.channel_id,
                'text': text,
                'parse_mode': 'Markdown'
            }
            
            post_data = urllib.parse.urlencode(data).encode('utf-8')
            req = urllib.request.Request(
                f"{self.base_url}/sendMessage",
                data=post_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode())
            
            if result.get("ok"):
                print(f"✅ Message sent to Telegram (ID: {result['result']['message_id']})")
                return True
            else:
                print(f"❌ Telegram error: {result}")
                return False
                
        except Exception as e:
            print(f"❌ Send error: {e}")
            return False
    
    def process_news_cycle(self):
        """Process one complete news cycle"""
        print("🇷🇺 HEART OF NEWS RUSSIAN - NEWS CYCLE STARTING")
        print("=" * 60)
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        total_processed = 0
        total_published = 0
        total_rewritten = 0
        total_rejected = 0
        
        for source in self.sources:
            print(f"📰 Processing source: {source['name']}")
            
            # Fetch articles
            articles = self.fetch_rss_feed(source['feed_url'])
            
            for article in articles:
                total_processed += 1
                
                # Skip if already published
                article_id = f"{source['name']}:{article['title']}"
                if article_id in self.published_articles:
                    continue
                
                print(f"🔍 Analyzing: {article['title'][:50]}...")
                
                # Analyze for propaganda
                analysis = self.analyze_propaganda(
                    article['title'], 
                    article['content'],
                    source['reliability']
                )
                
                print(f"   Propaganda score: {analysis['propaganda_score']:.2f}")
                print(f"   Recommendation: {analysis['recommendation']}")
                
                if analysis['recommendation'] == 'REJECT':
                    print(f"❌ REJECTED - too much propaganda")
                    total_rejected += 1
                    continue
                
                # Process article
                final_article = article.copy()
                rewritten = False
                
                if analysis['recommendation'] == 'REVIEW':
                    print(f"✏️ Rewriting article...")
                    rewrite_result = self.rewrite_content(article['title'], article['content'])
                    final_article.update({
                        'title': rewrite_result['title'],
                        'content': rewrite_result['content']
                    })
                    rewritten = True
                    total_rewritten += 1
                    
                    if rewrite_result['changes']:
                        print(f"   Changes: {', '.join(rewrite_result['changes'][:2])}")
                
                # Format and send to Telegram
                message = self.format_telegram_message(final_article, source['name'], rewritten)
                
                if self.send_telegram_message(message):
                    total_published += 1
                    self.published_articles.add(article_id)
                    print(f"✅ PUBLISHED to Telegram")
                    
                    # Rate limiting - faster publishing
                    time.sleep(1)
                else:
                    print(f"❌ Failed to publish")
                
                print()
        
        # Summary
        print("=" * 60)
        print("📊 CYCLE SUMMARY")
        print(f"Processed: {total_processed} articles")
        print(f"Published: {total_published} articles")
        print(f"Rewritten: {total_rewritten} articles (propaganda removed)")
        print(f"Rejected: {total_rejected} articles (too much propaganda)")
        print(f"Published articles in channel: https://t.me/{self.channel_id[1:]}")
        print("=" * 60)
    
    def run_continuous(self, interval_minutes: int = 1):
        """Run continuously with high frequency updates"""
        print(f"🚀 Starting high-frequency Russian news publishing")
        print(f"📢 Channel: {self.channel_id}")
        print(f"⚡ Check interval: {interval_minutes} minute (ultra real-time mode)")
        print(f"📰 Monitoring {len(self.sources)} Russian news sources")
        print()
        
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n🔄 CYCLE #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                self.process_news_cycle()
                
                print(f"\n⏱️ Waiting {interval_minutes} minute for fresh news...")
                print(f"Next check at: {(datetime.now() + timedelta(minutes=interval_minutes)).strftime('%H:%M:%S')}")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Retrying in 30 seconds...")
            time.sleep(30)

def main():
    """Main entry point"""
    print("🇷🇺 HEART OF NEWS RUSSIAN BOT")
    print("Verified news with propaganda detection")
    print("=" * 50)
    
    # Check environment
    bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
    
    if not bot_token or not channel_id:
        print("❌ Missing environment variables!")
        print("Please set TELEGRAM_RU_BOT_TOKEN and TELEGRAM_RU_CHANNEL_ID")
        return
    
    print(f"✅ Bot configured for channel: {channel_id}")
    print()
    
    # Initialize and start bot
    bot = RussianNewsBot()
    
    # Run once or continuously
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("🧪 Running once (test mode)")
        bot.process_news_cycle()
    else:
        print("🔄 Running in ultra real-time mode")
        bot.run_continuous(interval_minutes=1)

if __name__ == "__main__":
    main()