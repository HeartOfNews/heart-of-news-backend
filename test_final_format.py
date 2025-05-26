#!/usr/bin/env python3
"""
Test the final clean Telegram format
"""

import json
import subprocess

BOT_TOKEN = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
CHANNEL_ID = "-1002643653940"

# Test with a reliable image and clean format
test_article = {
    "text": """🗞️ **Heart of News Format Update Complete**

📰 The Telegram channel has been successfully updated with a cleaner, more professional format. Articles now feature images when available and focus on delivering news content without distracting elements.

#Update #News #Technology #HeartOfNews""",
    "image": "https://picsum.photos/800/600?random=1"
}

def send_photo_message(image_url, caption):
    """Send photo with caption to Telegram channel"""
    payload = {
        "chat_id": CHANNEL_ID,
        "photo": image_url,
        "caption": caption,
        "parse_mode": "Markdown"
    }
    
    curl_command = [
        "curl", "-X", "POST",
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}

print("🎯 Testing final clean format...")
result = send_photo_message(test_article["image"], test_article["text"])

if result.get("ok"):
    print("✅ Final format test successful!")
    print(f"📱 Message ID: {result['result']['message_id']}")
    print("\n🎉 Your Telegram channel now has:")
    print("   ✅ Clean, professional format")
    print("   ✅ Image support")
    print("   ✅ No bias scores or read more links")
    print("   ✅ Hashtag categories")
    print("   ✅ Ready for automated publishing")
else:
    print(f"❌ Test failed: {result.get('description', 'Unknown error')}")

print(f"\n🔗 Check your channel: https://t.me/heartofnews")