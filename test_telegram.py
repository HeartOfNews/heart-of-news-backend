#!/usr/bin/env python3
"""
Quick test script for Telegram bot connection
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Set environment variables from .env.local
os.environ["TELEGRAM_BOT_TOKEN"] = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
os.environ["TELEGRAM_CHANNEL_ID"] = "@heartofnews"
os.environ["TELEGRAM_ENABLED"] = "true"
os.environ["FRONTEND_URL"] = "http://localhost:3000"

from app.services.telegram_service import telegram_service


async def test_telegram():
    """Test Telegram bot connection and send a test message"""
    print("🤖 Testing Telegram Bot Connection...")
    print(f"Bot Token: {telegram_service.bot_token[:20]}...")
    print(f"Channel ID: {telegram_service.channel_id}")
    print(f"Enabled: {telegram_service.enabled}")
    print()
    
    # Test connection
    print("1. Testing bot connection...")
    connection_result = await telegram_service.test_connection()
    
    if connection_result["success"]:
        print(f"✅ Bot connection successful!")
        print(f"   Bot Username: @{connection_result.get('bot_username')}")
        print(f"   Bot Name: {connection_result.get('bot_name')}")
    else:
        print(f"❌ Bot connection failed: {connection_result.get('error')}")
        return False
    
    print()
    
    # Send test message
    print("2. Sending test message to channel...")
    test_message = """
🧪 **Heart of News - Test Message**

✅ Your Telegram bot integration is working perfectly!

🤖 This message was sent automatically by the Heart of News system.

📅 Ready to start publishing news articles to @heartofnews
    """.strip()
    
    send_result = await telegram_service.send_message(test_message)
    
    if send_result["success"]:
        print(f"✅ Test message sent successfully!")
        print(f"   Message ID: {send_result.get('message_id')}")
        print(f"   Check your channel: https://t.me/heartofnews")
    else:
        print(f"❌ Failed to send test message: {send_result.get('error')}")
        return False
    
    print()
    print("🎉 Telegram integration is fully working!")
    print("Your channel is ready to receive automated news posts.")
    
    return True


if __name__ == "__main__":
    asyncio.run(test_telegram())