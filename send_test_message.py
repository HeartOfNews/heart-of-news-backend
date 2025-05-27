#!/usr/bin/env python3
"""
Send a simple test message to verify bot works
"""

import urllib.request
import urllib.parse
import json

def send_test_message():
    bot_token = "7851345007:AAF4ubtbbR5NSiMxBYRRqtY31hMpEq9AZxM"
    channel_id = "@HeartofNews_Rus"
    
    message = """🇷🇺 **ТЕСТ БОТА**

**Fresh Russian Bot запущен!**

Бот готов к публикации новостей России. Система работает корректно.

✅ #ТестБота #НовостиРоссии"""
    
    try:
        data = {
            'chat_id': channel_id,
            'text': message,
            'parse_mode': 'Markdown'
        }
        
        encoded_data = urllib.parse.urlencode(data).encode('utf-8')
        request = urllib.request.Request(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            data=encoded_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if result.get("ok"):
            print("✅ Test message sent successfully!")
            print(f"   Message ID: {result['result']['message_id']}")
            return True
        else:
            print(f"❌ Failed to send: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("📤 Sending test message...")
    send_test_message()