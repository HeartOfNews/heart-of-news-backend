#!/usr/bin/env python3
"""
Test Telegram Connection for Russian Bot
"""

import asyncio
import json
import os
from typing import Dict, Any

try:
    import httpx
except ImportError:
    print("Installing httpx...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "httpx", "feedparser", "beautifulsoup4"])
    import httpx

class TelegramTester:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
        self.channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    async def test_bot_connection(self) -> Dict[str, Any]:
        """Test bot connection"""
        print("🔍 Testing bot connection...")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getMe", timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    bot_info = result["result"]
                    print(f"✅ Bot connected: @{bot_info.get('username')} - {bot_info.get('first_name')}")
                    return {"success": True, "bot_info": bot_info}
                else:
                    print(f"❌ Bot connection failed: {result}")
                    return {"success": False, "error": result}
                    
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return {"success": False, "error": str(e)}
    
    async def test_channel_access(self) -> Dict[str, Any]:
        """Test channel access"""
        print(f"🔍 Testing access to channel: {self.channel_id}")
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/getChat", 
                                          params={"chat_id": self.channel_id}, 
                                          timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    chat_info = result["result"]
                    print(f"✅ Channel access confirmed: {chat_info.get('title', 'Unknown')}")
                    print(f"   Type: {chat_info.get('type')}")
                    print(f"   Members: {chat_info.get('members_count', 'Unknown')}")
                    return {"success": True, "chat_info": chat_info}
                else:
                    print(f"❌ Channel access failed: {result}")
                    return {"success": False, "error": result}
                    
        except Exception as e:
            print(f"❌ Channel access error: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_test_message(self) -> Dict[str, Any]:
        """Send a test message"""
        print("📤 Sending test message...")
        
        test_message = """🔴 **ПРОВЕРЕННЫЕ НОВОСТИ**

**Тестовое сообщение от бота Heart of News RUS**

Система автоматической публикации российских новостей запущена и готова к работе!

✅ Пропаганда детектируется и удаляется
✅ Контент верифицируется  
✅ Источники проверяются

🇷🇺 #Новости #Россия #ТестБота"""
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(f"{self.base_url}/sendMessage",
                                           json={
                                               "chat_id": self.channel_id,
                                               "text": test_message,
                                               "parse_mode": "Markdown"
                                           },
                                           timeout=10.0)
                response.raise_for_status()
                
                result = response.json()
                if result.get("ok"):
                    message_id = result["result"]["message_id"]
                    print(f"✅ Test message sent successfully! Message ID: {message_id}")
                    return {"success": True, "message_id": message_id}
                else:
                    print(f"❌ Message send failed: {result}")
                    return {"success": False, "error": result}
                    
        except Exception as e:
            print(f"❌ Message send error: {e}")
            return {"success": False, "error": str(e)}

async def main():
    print("🇷🇺 HEART OF NEWS RUSSIAN BOT - CONNECTION TEST")
    print("=" * 60)
    
    # Check environment
    bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN')
    channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID')
    
    if not bot_token or not channel_id:
        print("❌ Missing environment variables!")
        print(f"Bot Token: {'✅ Set' if bot_token else '❌ Missing'}")
        print(f"Channel ID: {'✅ Set' if channel_id else '❌ Missing'}")
        return
    
    print(f"🤖 Bot Token: {bot_token[:10]}...{bot_token[-5:]}")
    print(f"📢 Channel: {channel_id}")
    print()
    
    # Run tests
    tester = TelegramTester()
    
    # Test 1: Bot connection
    bot_result = await tester.test_bot_connection()
    if not bot_result["success"]:
        print("❌ Bot connection failed. Please check your bot token.")
        return
    
    print()
    
    # Test 2: Channel access
    channel_result = await tester.test_channel_access()
    if not channel_result["success"]:
        print("❌ Channel access failed. Make sure:")
        print("   - The channel exists")
        print("   - The bot is added as an administrator")
        print("   - The channel ID is correct")
        return
    
    print()
    
    # Test 3: Send test message
    message_result = await tester.send_test_message()
    if not message_result["success"]:
        print("❌ Test message failed. Check bot permissions.")
        return
    
    print()
    print("🎉 ALL TESTS PASSED!")
    print("Your Russian Heart of News bot is ready to publish verified news!")
    print()
    print("To start the news worker:")
    print("python3 russian_verified_news_worker.py --once")

if __name__ == "__main__":
    asyncio.run(main())