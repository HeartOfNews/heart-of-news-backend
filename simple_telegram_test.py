#!/usr/bin/env python3
"""
Simple Telegram Test using only built-in Python modules
"""

import urllib.request
import urllib.parse
import json
import os
import sys

def test_telegram_bot():
    print("🇷🇺 HEART OF NEWS RUSSIAN BOT - CONNECTION TEST")
    print("=" * 60)
    
    # Get credentials from environment
    bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
    
    if not bot_token or not channel_id:
        print("❌ Missing environment variables!")
        print(f"Bot Token: {'✅ Set' if bot_token else '❌ Missing'}")
        print(f"Channel ID: {'✅ Set' if channel_id else '❌ Missing'}")
        print("\nPlease set:")
        print("export TELEGRAM_RU_BOT_TOKEN='your_bot_token'")
        print("export TELEGRAM_RU_CHANNEL_ID='@your_channel_id'")
        return False
    
    print(f"🤖 Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"📢 Channel: {channel_id}")
    print()
    
    base_url = f"https://api.telegram.org/bot{bot_token}"
    
    # Test 1: Bot connection
    print("🔍 Testing bot connection...")
    try:
        with urllib.request.urlopen(f"{base_url}/getMe", timeout=10) as response:
            result = json.loads(response.read().decode())
            
        if result.get("ok"):
            bot_info = result["result"]
            print(f"✅ Bot connected: @{bot_info.get('username')} - {bot_info.get('first_name')}")
        else:
            print(f"❌ Bot connection failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False
    
    print()
    
    # Test 2: Send test message
    print("📤 Sending test message...")
    
    test_message = """🔴 **ПРОВЕРЕННЫЕ НОВОСТИ**

**Тестовое сообщение от бота Heart of News RUS**

Система автоматической публикации российских новостей запущена и готова к работе!

✅ Пропаганда детектируется и удаляется
✅ Контент верифицируется  
✅ Источники проверяются

🇷🇺 #Новости #Россия #ТестБота"""
    
    try:
        # Prepare data for POST request
        data = {
            'chat_id': channel_id,
            'text': test_message,
            'parse_mode': 'Markdown'
        }
        
        # Encode data
        post_data = urllib.parse.urlencode(data).encode('utf-8')
        
        # Create request
        req = urllib.request.Request(
            f"{base_url}/sendMessage",
            data=post_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        # Send request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if result.get("ok"):
            message_id = result["result"]["message_id"]
            print(f"✅ Test message sent successfully! Message ID: {message_id}")
            print(f"🔗 Check your channel: https://t.me/{channel_id[1:]}")
        else:
            print(f"❌ Message send failed: {result}")
            error_desc = result.get('description', 'Unknown error')
            
            if "chat not found" in error_desc.lower():
                print("💡 Make sure:")
                print("   - The channel exists")
                print("   - The channel ID is correct (including @)")
                print("   - The channel is public")
            elif "bot is not a member" in error_desc.lower():
                print("💡 Add the bot to your channel:")
                print("   - Go to your channel settings")
                print("   - Add administrators")
                print(f"   - Search for @{bot_info.get('username')}")
                print("   - Give it permission to post messages")
            
            return False
            
    except Exception as e:
        print(f"❌ Message send error: {e}")
        return False
    
    print()
    print("🎉 ALL TESTS PASSED!")
    print("Your Russian Heart of News bot is ready!")
    print()
    print("Next steps:")
    print("1. Install dependencies: pip install httpx feedparser beautifulsoup4")
    print("2. Run the news worker: python3 russian_verified_news_worker.py --once")
    
    return True

if __name__ == "__main__":
    success = test_telegram_bot()
    sys.exit(0 if success else 1)