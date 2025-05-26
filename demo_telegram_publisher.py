#!/usr/bin/env python3
"""
Demo script to simulate automated Telegram news publishing
"""

import json
import random
import time
from datetime import datetime
from urllib.parse import quote
import subprocess

# Bot configuration
BOT_TOKEN = "7568175094:AAHh3nHCoRqssSUo9A1FLnM5yi5K1bu54vs"
CHANNEL_ID = "-1002643653940"

# Sample news articles
SAMPLE_ARTICLES = [
    {
        "title": "Global Climate Summit Reaches Historic Agreement",
        "summary": "World leaders unite on comprehensive climate action plan, focusing on renewable energy transition and carbon reduction targets for the next decade.",
        "url": "http://localhost:3000/articles/climate-summit-2024",
        "categories": ["Environment", "Politics", "Global"],
        "bias_score": 9,
        "source_reliability": 8
    },
    {
        "title": "Tech Industry Announces Major AI Safety Initiative",
        "summary": "Leading technology companies collaborate on new artificial intelligence safety protocols, addressing concerns about AI development and deployment.",
        "url": "http://localhost:3000/articles/ai-safety-initiative",
        "categories": ["Technology", "AI", "Business"],
        "bias_score": 8,
        "source_reliability": 9
    },
    {
        "title": "Economic Markets Show Steady Growth in Q4",
        "summary": "Financial analysts report positive trends across major markets, with sustainable growth patterns observed in both domestic and international sectors.",
        "url": "http://localhost:3000/articles/economic-growth-q4",
        "categories": ["Economy", "Finance", "Markets"],
        "bias_score": 9,
        "source_reliability": 7
    },
    {
        "title": "Medical Breakthrough in Cancer Research Announced",
        "summary": "Scientists unveil promising new treatment approach for cancer therapy, showing significant improvement in patient outcomes during clinical trials.",
        "url": "http://localhost:3000/articles/cancer-research-breakthrough",
        "categories": ["Health", "Medical", "Science"],
        "bias_score": 10,
        "source_reliability": 9
    }
]

def format_telegram_message(article):
    """Format article for Telegram posting"""
    categories = " ".join([f"#{cat.replace(' ', '')}" for cat in article["categories"]])
    
    message = f"""🗞️ **{article['title']}**

📰 {article['summary']}

🔗 [Read more]({article['url']})

📊 Bias Score: {article['bias_score']}/10
📈 Source Reliability: {article['source_reliability']}/10

{categories}"""
    
    return message

def send_telegram_message(message):
    """Send message to Telegram channel using curl"""
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
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
    """Main demo function"""
    print("🤖 Heart of News - Telegram Publishing Demo")
    print("=" * 50)
    print(f"📱 Channel: @heartofnews")
    print(f"🕐 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    while True:
        print("📋 Available demo options:")
        print("1. Send random news article")
        print("2. Send all sample articles")
        print("3. Send custom test message")
        print("4. Exit")
        print()
        
        choice = input("Choose option (1-4): ").strip()
        
        if choice == "1":
            # Send random article
            article = random.choice(SAMPLE_ARTICLES)
            message = format_telegram_message(article)
            
            print(f"\n📤 Publishing: {article['title'][:50]}...")
            result = send_telegram_message(message)
            
            if result.get("ok"):
                print(f"✅ Published successfully! Message ID: {result['result']['message_id']}")
                print(f"🔗 Check: https://t.me/heartofnews")
            else:
                print(f"❌ Failed: {result.get('description', 'Unknown error')}")
        
        elif choice == "2":
            # Send all articles with delay
            print(f"\n📤 Publishing {len(SAMPLE_ARTICLES)} articles...")
            
            for i, article in enumerate(SAMPLE_ARTICLES, 1):
                message = format_telegram_message(article)
                print(f"  {i}/{len(SAMPLE_ARTICLES)}: {article['title'][:40]}...")
                
                result = send_telegram_message(message)
                
                if result.get("ok"):
                    print(f"    ✅ Published (ID: {result['result']['message_id']})")
                else:
                    print(f"    ❌ Failed: {result.get('description', 'Unknown error')}")
                
                # Delay between messages
                if i < len(SAMPLE_ARTICLES):
                    print("    ⏳ Waiting 3 seconds...")
                    time.sleep(3)
            
            print(f"\n🎉 Batch publishing complete!")
        
        elif choice == "3":
            # Custom message
            custom_text = input("\nEnter custom message: ").strip()
            if custom_text:
                result = send_telegram_message(custom_text)
                
                if result.get("ok"):
                    print(f"✅ Sent! Message ID: {result['result']['message_id']}")
                else:
                    print(f"❌ Failed: {result.get('description', 'Unknown error')}")
        
        elif choice == "4":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice. Please try again.")
        
        print("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main()