#!/usr/bin/env python3
"""
Test the new political news format with regional flags
"""

import json
import subprocess
import time

BOT_TOKEN = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
CHANNEL_ID = "-1002643653940"

# Sample political news with regional focus
POLITICAL_NEWS = [
    {
        "text": """🗞️ **European Parliament Approves New AI Regulation Framework**

📰 The European Union has passed comprehensive artificial intelligence legislation, setting global standards for AI safety and transparency. The new regulations will affect major tech companies operating in EU markets.

🏛️ 🇪🇺 #Politics #EuropeanUnion #AI #Technology #Regulation""",
        "image": "https://picsum.photos/800/600?random=2"
    },
    {
        "text": """🗞️ **US Congress Debates Federal Election Security Measures**

📰 American lawmakers are considering new legislation to strengthen election infrastructure and cybersecurity protocols ahead of upcoming electoral cycles. Bipartisan support emerges for key provisions.

🏛️ 🇺🇸 #Politics #USA #Elections #Cybersecurity #Congress""",
        "image": "https://picsum.photos/800/600?random=3"
    },
    {
        "text": """🗞️ **NATO Summit Addresses Eastern European Security**

📰 Alliance leaders meet in Brussels to discuss enhanced defense commitments and strategic positioning in response to evolving geopolitical challenges in the region.

🏛️ 🌍 #Politics #NATO #EasternEurope #Defense #Security""",
        "image": "https://picsum.photos/800/600?random=4"
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

def main():
    print("🏛️ Testing Political News Format with Regional Flags...")
    print("=" * 60)
    
    for i, news in enumerate(POLITICAL_NEWS, 1):
        print(f"\n📤 Sending political news {i}/{len(POLITICAL_NEWS)}...")
        
        result = send_photo_message(news["image"], news["text"])
        
        if result.get("ok"):
            print(f"✅ Political news sent successfully!")
            print(f"   Message ID: {result['result']['message_id']}")
        else:
            print(f"❌ Failed: {result.get('description', 'Unknown error')}")
        
        # Delay between posts
        if i < len(POLITICAL_NEWS):
            print("   ⏳ Waiting 3 seconds...")
            time.sleep(3)
    
    print(f"\n🎉 Political news test complete!")
    print(f"🔗 Check your channel: https://t.me/heartofnews")
    print("\n📋 New political features:")
    print("   ✅ Regional flags (🇪🇺 EU, 🇺🇸 USA, 🌍 Global)")
    print("   ✅ Political hashtags prioritized")
    print("   ✅ Current news focus (15-minute scraping)")
    print("   ✅ EU and USA sources emphasized")
    print("   ✅ 20-minute publishing cycle")

if __name__ == "__main__":
    main()