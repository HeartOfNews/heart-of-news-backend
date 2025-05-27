#!/usr/bin/env python3
"""
Test bot connection and permissions
"""

import urllib.request
import json
import os

def test_bot_connection():
    """Test if bot token is valid"""
    bot_token = "7851345007:AAF4ubtbbR5NSiMxBYRRqtY31hMpEq9AZxM"
    url = f"https://api.telegram.org/bot{bot_token}/getMe"
    
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if result.get("ok"):
            bot_info = result["result"]
            print(f"✅ Bot connection successful!")
            print(f"   Bot username: @{bot_info.get('username')}")
            print(f"   Bot name: {bot_info.get('first_name')}")
            return True
        else:
            print(f"❌ Bot connection failed: {result}")
            return False
    except Exception as e:
        print(f"❌ Error testing bot: {e}")
        return False

def test_channel_access():
    """Test if bot can access the channel"""
    bot_token = "7851345007:AAF4ubtbbR5NSiMxBYRRqtY31hMpEq9AZxM"
    channel_id = "@HeartofNews_Rus"
    url = f"https://api.telegram.org/bot{bot_token}/getChat"
    
    try:
        data = urllib.parse.urlencode({'chat_id': channel_id}).encode('utf-8')
        request = urllib.request.Request(url, data=data)
        
        with urllib.request.urlopen(request, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if result.get("ok"):
            chat_info = result["result"]
            print(f"✅ Channel access successful!")
            print(f"   Channel: {chat_info.get('title')}")
            print(f"   Type: {chat_info.get('type')}")
            return True
        else:
            print(f"❌ Channel access failed: {result.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error accessing channel: {e}")
        return False

def main():
    print("🔍 TESTING BOT CONNECTION")
    print("=" * 40)
    
    print("1️⃣ Testing bot token...")
    bot_ok = test_bot_connection()
    print()
    
    if bot_ok:
        print("2️⃣ Testing channel access...")
        import urllib.parse
        channel_ok = test_channel_access()
        print()
        
        if not channel_ok:
            print("💡 SOLUTION:")
            print("1. Make sure the bot is added to @HeartofNews_Rus channel")
            print("2. Give the bot admin permissions to post messages")
            print("3. Try sending a test message manually first")
    
    print("=" * 40)

if __name__ == "__main__":
    main()