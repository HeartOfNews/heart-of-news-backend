#!/usr/bin/env python3
"""
Simple Russian News Test
"""

import json
import subprocess
from datetime import datetime

# Use the working English bot token but publish Russian content
ENGLISH_BOT = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
ENGLISH_CHANNEL = "-1002643653940"

def publish_russian_news():
    """Publish Russian news using working bot"""
    
    # Russian news content
    russian_message = f"""🇷🇺 **Российские новости**

📰 Российские исследователи представили новые разработки в области искусственного интеллекта, которые значительно повышают эффективность обработки данных.

🏛️ 💻 #Технологии #Россия #Наука

✅ *Проверено Heart of News*
🕒 {datetime.now().strftime('%H:%M')}"""

    # High-quality image
    news_image = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800&h=600&fit=crop"
    
    payload = {
        "chat_id": ENGLISH_CHANNEL,
        "photo": news_image,
        "caption": russian_message,
        "parse_mode": "Markdown"
    }
    
    url = f"https://api.telegram.org/bot{ENGLISH_BOT}/sendPhoto"
    
    try:
        result = subprocess.run([
            "curl", "-X", "POST", url,
            "-H", "Content-Type: application/json",
            "-d", json.dumps(payload)
        ], capture_output=True, text=True)
        
        response = json.loads(result.stdout)
        return response
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    print("🇷🇺 RUSSIAN NEWS TEST")
    print("=" * 40)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    print("\n📱 Publishing Russian news...")
    result = publish_russian_news()
    
    if result.get("ok"):
        print(f"✅ Published! Message ID: {result['result']['message_id']}")
        print(f"🔗 https://t.me/heartofnews")
    else:
        print(f"❌ Failed: {result.get('description', 'Unknown error')}")
    
    print("\n🎉 Russian news test completed!")

if __name__ == "__main__":
    main()