#!/usr/bin/env python3
"""
Fresh Russian News Bot - Heart of News
Brand new architecture with dynamic content generation
"""

import urllib.request
import urllib.parse
import json
import os
import time
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict, Any

class FreshRussianBot:
    """Brand new Russian news bot with dynamic content"""
    
    def __init__(self):
        # Telegram configuration
        self.bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Track published content
        self.published_today = set()
        self.last_reset = datetime.now().date()
        
        # Content categories with dynamic templates
        self.content_categories = {
            "technology": {
                "icon": "💻",
                "topics": [
                    "искусственный интеллект",
                    "кибербезопасность", 
                    "цифровые технологии",
                    "блокчейн",
                    "интернет вещей",
                    "квантовые вычисления"
                ],
                "actions": [
                    "представила новое решение",
                    "запустила инновационный проект", 
                    "объявила о прорыве",
                    "внедрила передовую технологию",
                    "разработала платформу"
                ],
                "results": [
                    "повышающее эффективность на 40%",
                    "улучшающее пользовательский опыт",
                    "обеспечивающее высокий уровень защиты",
                    "соответствующее мировым стандартам",
                    "превосходящее аналоги"
                ]
            },
            "economy": {
                "icon": "📈",
                "topics": [
                    "российская экономика",
                    "промышленность",
                    "энергетический сектор",
                    "экспорт",
                    "инвестиции",
                    "малый бизнес"
                ],
                "actions": [
                    "показывает устойчивый рост",
                    "демонстрирует положительную динамику",
                    "достигла новых рекордов",
                    "укрепляет позиции",
                    "расширяет присутствие"
                ],
                "results": [
                    "превышая прогнозы экспертов",
                    "опережая европейские показатели",
                    "привлекая международных партнеров",
                    "создавая новые рабочие места",
                    "обеспечивая энергетическую безопасность"
                ]
            },
            "science": {
                "icon": "🔬",
                "topics": [
                    "космические исследования",
                    "медицинские разработки",
                    "экологические проекты",
                    "арктические исследования",
                    "новые материалы",
                    "ядерные технологии"
                ],
                "actions": [
                    "совершили важное открытие",
                    "завершили успешный эксперимент",
                    "представили результаты исследований",
                    "разработали инновационный метод",
                    "создали уникальную технологию"
                ],
                "results": [
                    "получившее международное признание",
                    "открывающее новые возможности",
                    "способное изменить отрасль",
                    "превосходящее мировые аналоги",
                    "обеспечивающее технологический суверенитет"
                ]
            },
            "culture": {
                "icon": "🎭",
                "topics": [
                    "российская культура",
                    "театральное искусство",
                    "кинематограф",
                    "литература",
                    "музыкальное искусство",
                    "народные традиции"
                ],
                "actions": [
                    "представила новый проект",
                    "получила престижную награду",
                    "открыла фестиваль",
                    "запустила культурную программу",
                    "организовала выставку"
                ],
                "results": [
                    "привлекающую международное внимание",
                    "объединяющую поколения",
                    "сохраняющую традиции",
                    "развивающую современное искусство",
                    "укрепляющую культурные связи"
                ]
            }
        }
        
        # Current events and seasonal topics
        self.current_topics = [
            "Новый год",
            "День защитника Отечества", 
            "Международный женский день",
            "День космонавтики",
            "День Победы",
            "День России",
            "День народного единства"
        ]
        
        # Positive achievements and developments
        self.achievements = [
            "международное сотрудничество",
            "технологический прорыв",
            "экономический рост",
            "научное достижение",
            "культурное развитие",
            "социальные программы",
            "экологические инициативы"
        ]
    
    def reset_daily_cache(self):
        """Reset published cache daily"""
        today = datetime.now().date()
        if today != self.last_reset:
            self.published_today.clear()
            self.last_reset = today
            print(f"🔄 Daily cache reset for {today}")
    
    def generate_dynamic_news(self) -> Dict[str, Any]:
        """Generate dynamic news content"""
        category_name = random.choice(list(self.content_categories.keys()))
        category = self.content_categories[category_name]
        
        # Build dynamic content
        topic = random.choice(category["topics"])
        action = random.choice(category["actions"])
        result = random.choice(category["results"])
        
        # Create variations
        subjects = [
            "Российские специалисты",
            "Эксперты",
            "Исследователи",
            "Разработчики",
            "Команда проекта"
        ]
        
        locations = [
            "в Москве",
            "в Санкт-Петербурге", 
            "в Новосибирске",
            "в Екатеринбурге",
            "в российских регионах"
        ]
        
        # Generate title with proper grammar
        subject = random.choice(subjects)
        location = random.choice(locations)
        
        # Fix grammar based on action type
        if "представила" in action or "запустила" in action:
            title = f"{subject} {location} {action.replace('представила', 'представили').replace('запустила', 'запустили')} в области {topic}"
        else:
            title = f"{subject} {location} {action} в области {topic}"
        
        # Generate content with proper grammar
        fixed_action = action.replace('представила', 'представили').replace('запустила', 'запустили').replace('показывает', 'показали')
        
        content_parts = [
            f"{subject} {fixed_action} в области {topic}, {result}.",
            f"Проект реализуется {location} при поддержке федеральных программ.",
            f"Эксперты отмечают важность данной инициативы для развития отрасли.",
            f"Планируется расширение проекта на другие регионы страны."
        ]
        
        content = " ".join(content_parts)
        
        return {
            "title": title.capitalize(),
            "content": content,
            "category": category_name,
            "icon": category["icon"],
            "timestamp": datetime.now()
        }
    
    def generate_seasonal_news(self) -> Dict[str, Any]:
        """Generate seasonal/holiday content"""
        current_month = datetime.now().month
        
        seasonal_content = {
            1: {"event": "Новый год", "theme": "планы и достижения"},
            2: {"event": "День защитника Отечества", "theme": "оборона и безопасность"},
            3: {"event": "Международный женский день", "theme": "достижения женщин"},
            4: {"event": "День космонавтики", "theme": "космические проекты"},
            5: {"event": "День Победы", "theme": "память и традиции"},
            6: {"event": "День России", "theme": "национальные проекты"},
            12: {"event": "День Конституции", "theme": "правовые инициативы"}
        }
        
        if current_month in seasonal_content:
            event_data = seasonal_content[current_month]
            
            title = f"Подготовка к {event_data['event']}: новые инициативы в области {event_data['theme']}"
            content = f"В преддверии {event_data['event']} российские организации представили комплекс мероприятий, направленных на развитие {event_data['theme']}. Программа включает образовательные, культурные и социальные проекты."
            
            return {
                "title": title,
                "content": content,
                "category": "special",
                "icon": "🇷🇺",
                "timestamp": datetime.now()
            }
        
        return self.generate_dynamic_news()
    
    def create_telegram_message(self, news_item: Dict[str, Any]) -> str:
        """Create formatted Telegram message"""
        
        # Time and category tags
        time_tag = datetime.now().strftime("%H:%M")
        category_tag = f"#{news_item['category'].title()}"
        
        # Regional flags for variety
        flags = ["🇷🇺", "🌍", "⭐", "🔥", "✨"]
        flag = random.choice(flags)
        
        message = f"""{news_item['icon']} **НОВОСТИ РОССИИ**

**{news_item['title']}**

{news_item['content']}

{flag} #НовостиРоссии {category_tag} #{time_tag.replace(':', '')}"""
        
        return message
    
    def send_to_telegram(self, message: str) -> bool:
        """Send message to Telegram channel"""
        if not self.bot_token or not self.channel_id:
            print("❌ Telegram not configured")
            return False
        
        try:
            data = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': True
            }
            
            encoded_data = urllib.parse.urlencode(data).encode('utf-8')
            request = urllib.request.Request(
                f"{self.base_url}/sendMessage",
                data=encoded_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            with urllib.request.urlopen(request, timeout=10) as response:
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
    
    def get_content_hash(self, title: str) -> str:
        """Generate hash for content tracking"""
        return hashlib.md5(title.lower().encode()).hexdigest()[:8]
    
    def publish_news_item(self) -> bool:
        """Generate and publish a single news item"""
        # Reset cache if new day
        self.reset_daily_cache()
        
        # Generate content (70% dynamic, 30% seasonal)
        if random.random() < 0.7:
            news_item = self.generate_dynamic_news()
        else:
            news_item = self.generate_seasonal_news()
        
        # Check for duplicates
        content_hash = self.get_content_hash(news_item["title"])
        if content_hash in self.published_today:
            return False
        
        # Create and send message
        message = self.create_telegram_message(news_item)
        
        print(f"🆕 Publishing: {news_item['title'][:60]}...")
        
        if self.send_to_telegram(message):
            self.published_today.add(content_hash)
            print(f"✅ Published to channel")
            return True
        else:
            print(f"❌ Failed to publish")
            return False
    
    def run_publishing_cycle(self) -> int:
        """Run one publishing cycle"""
        print(f"🔄 Publishing cycle - {datetime.now().strftime('%H:%M:%S')}")
        
        # Publish 1-3 items per cycle
        items_to_publish = random.randint(1, 3)
        published_count = 0
        
        for i in range(items_to_publish):
            if self.publish_news_item():
                published_count += 1
                # Delay between publications
                if i < items_to_publish - 1:
                    time.sleep(5)
        
        print(f"📊 Published {published_count}/{items_to_publish} items")
        print(f"📈 Total published today: {len(self.published_today)}")
        
        return published_count
    
    def run_continuous(self, interval_minutes: int = 20):
        """Run bot continuously"""
        print(f"🚀 FRESH RUSSIAN NEWS BOT - HEART OF NEWS")
        print(f"📺 Channel: {self.channel_id}")
        print(f"⏰ Publishing every {interval_minutes} minutes")
        print(f"🎯 Dynamic content with 4 categories")
        print("=" * 50)
        
        total_published = 0
        cycle_count = 0
        
        try:
            while True:
                cycle_count += 1
                print(f"\n📅 CYCLE #{cycle_count}")
                
                published_this_cycle = self.run_publishing_cycle()
                total_published += published_this_cycle
                
                next_run = datetime.now() + timedelta(minutes=interval_minutes)
                print(f"⏳ Next cycle at: {next_run.strftime('%H:%M:%S')}")
                print(f"🏆 Session total: {total_published} articles")
                
                time.sleep(interval_minutes * 60)
                
        except KeyboardInterrupt:
            print(f"\n🛑 Bot stopped")
            print(f"📊 Final stats: {total_published} articles published")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("🔄 Restarting in 30 seconds...")
            time.sleep(30)
            self.run_continuous(interval_minutes)

def main():
    """Main entry point"""
    print("🇷🇺 FRESH RUSSIAN NEWS BOT")
    print("Dynamic Content Generation")
    print("=" * 40)
    
    # Check environment
    if not os.getenv('TELEGRAM_RU_BOT_TOKEN') or not os.getenv('TELEGRAM_RU_CHANNEL_ID'):
        print("❌ Missing environment variables!")
        print("Set TELEGRAM_RU_BOT_TOKEN and TELEGRAM_RU_CHANNEL_ID")
        return
    
    print(f"✅ Configured for: {os.getenv('TELEGRAM_RU_CHANNEL_ID')}")
    
    bot = FreshRussianBot()
    
    # Run mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        print("\n🧪 Single run mode")
        bot.run_publishing_cycle()
    else:
        print("\n🔄 Continuous mode")
        bot.run_continuous(20)

if __name__ == "__main__":
    main()