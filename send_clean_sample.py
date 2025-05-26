#!/usr/bin/env python3
"""
Send clean format sample articles with images to Telegram
"""

import json
import subprocess
import time

BOT_TOKEN = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
CHANNEL_ID = "-1002643653940"

# Sample articles with images and clean format
SAMPLE_ARTICLES = [
    {
        "text": """🗞️ **Global Climate Summit Reaches Historic Agreement**

📰 World leaders unite on comprehensive climate action plan, focusing on renewable energy transition and carbon reduction targets for the next decade.

#Environment #Politics #Global #ClimateChange""",
        "image": "https://images.unsplash.com/photo-1569163139394-de4e5f43e4e3?w=800&h=600&fit=crop"
    },
    {
        "text": """🗞️ **Tech Industry Announces Major AI Safety Initiative**

📰 Leading technology companies collaborate on new artificial intelligence safety protocols, addressing concerns about AI development and deployment.

#Technology #AI #Business #Innovation""",
        "image": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&h=600&fit=crop"
    },
    {
        "text": """🗞️ **Medical Breakthrough in Cancer Research Announced**

📰 Scientists unveil promising new treatment approach for cancer therapy, showing significant improvement in patient outcomes during clinical trials.

#Health #Medical #Science #Research""",
        "image": "https://images.unsplash.com/photo-1559757148-5c350d0d3c56?w=800&h=600&fit=crop"
    }
]

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

def send_text_message(text):
    """Send text message to Telegram channel"""
    payload = {
        "chat_id": CHANNEL_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    curl_command = [
        "curl", "-X", "POST",
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    
    try:
        result = subprocess.run(curl_command, capture_output=True, text=True)
        response = json.loads(result.stdout)
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    print("🎨 Sending clean format news articles with images...")
    print("=" * 60)
    
    for i, article in enumerate(SAMPLE_ARTICLES, 1):
        print(f"\n📤 Sending article {i}/{len(SAMPLE_ARTICLES)}...")
        
        if article.get("image"):
            # Send with image
            result = send_photo_message(article["image"], article["text"])
            post_type = "📸 Photo post"
        else:
            # Send text only
            result = send_text_message(article["text"])
            post_type = "📝 Text post"
        
        if result.get("ok"):
            print(f"✅ {post_type} sent successfully!")
            print(f"   Message ID: {result['result']['message_id']}")
        else:
            print(f"❌ Failed: {result.get('description', 'Unknown error')}")
        
        # Delay between posts
        if i < len(SAMPLE_ARTICLES):
            print("   ⏳ Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n🎉 All articles sent!")
    print(f"🔗 Check your channel: https://t.me/heartofnews")
    print("\n📋 New format features:")
    print("   ✅ Clean message format (no bias scores or read more links)")
    print("   ✅ Images included when available")
    print("   ✅ Professional news appearance")
    print("   ✅ Hashtag categories")

if __name__ == "__main__":
    main()