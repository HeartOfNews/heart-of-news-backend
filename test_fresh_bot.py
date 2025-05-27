#!/usr/bin/env python3
"""
Test the fresh Russian bot
"""

import os
import sys

# Set test environment
os.environ['TELEGRAM_RU_BOT_TOKEN'] = 'test_token'
os.environ['TELEGRAM_RU_CHANNEL_ID'] = '@test_channel'

sys.path.append('/tmp/heart-of-news-backend')
from fresh_russian_bot import FreshRussianBot

class TestFreshBot(FreshRussianBot):
    """Test version that doesn't send to Telegram"""
    
    def send_to_telegram(self, message: str) -> bool:
        """Override to show what would be sent"""
        print("📤 WOULD SEND TO TELEGRAM:")
        print("=" * 50)
        print(message)
        print("=" * 50)
        print()
        return True

def main():
    print("🧪 TESTING FRESH RUSSIAN BOT")
    print("=" * 40)
    
    bot = TestFreshBot()
    
    # Test content generation
    print("🎲 Generating sample content...\n")
    
    for i in range(5):
        print(f"📰 Sample {i+1}:")
        
        # Generate different types
        if i < 3:
            news = bot.generate_dynamic_news()
        else:
            news = bot.generate_seasonal_news()
        
        print(f"   Category: {news['category']}")
        print(f"   Icon: {news['icon']}")
        print(f"   Title: {news['title']}")
        print(f"   Content: {news['content'][:100]}...")
        print()
    
    print("\n🔄 Testing publishing cycle...")
    published = bot.run_publishing_cycle()
    print(f"\n✅ Test complete - published {published} items")

if __name__ == "__main__":
    main()