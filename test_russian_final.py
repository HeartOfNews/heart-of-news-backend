#!/usr/bin/env python3
"""
Final test for Russian Heart of News channel
"""

import json
import subprocess
import time

RUSSIAN_BOT_TOKEN = "7294645697:AAGJxaixBkgtBqAIpFU-kR8uzo06amOQOLs"
RUSSIAN_CHANNEL_ID = "@HeartofNews_Rus"

def send_russian_breaking_news(title, summary, image_url, region_flag, categories):
    """Send Russian breaking news"""
    
    message = f"""🗞️ **{title}**

📰 {summary}

🏛️ {region_flag} #{categories}"""
    
    payload = {
        "chat_id": RUSSIAN_CHANNEL_ID,
        "photo": image_url,
        "caption": message,
        "parse_mode": "Markdown"
    }
    
    curl_command = [
        "curl", "-X", "POST",
        f"https://api.telegram.org/bot{RUSSIAN_BOT_TOKEN}/sendPhoto",
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
    print("🇷🇺 HEART OF NEWS RUSSIA - ФИНАЛЬНЫЙ ТЕСТ")
    print("=" * 50)
    
    # Test Russian political news
    russian_news = [
        {
            "title": "ЕС принимает новые санкции против России",
            "summary": "Европейский парламент одобрил очередной пакет экономических санкций в ответ на последние геополитические события. Меры затронут энергетический и финансовый секторы.",
            "region_flag": "🇪🇺",
            "categories": "Срочно Политика ЕС Санкции",
            "image": "https://picsum.photos/800/600?random=20"
        },
        {
            "title": "Конгресс США утверждает военную помощь Украине",
            "summary": "Американские законодатели одобрили новый пакет военной поддержки на сумму 60 миллиардов долларов для укрепления обороноспособности украинских вооруженных сил.",
            "region_flag": "🇺🇸",
            "categories": "Политика США Украина Оборона",
            "image": "https://picsum.photos/800/600?random=21"
        },
        {
            "title": "Россия и Китай подписывают энергетические соглашения",
            "summary": "Президенты России и Китая договорились о расширении сотрудничества в энергетической сфере, включая поставки газа и нефти по льготным ценам.",
            "region_flag": "🇷🇺",
            "categories": "Политика Россия Китай Энергетика",
            "image": "https://picsum.photos/800/600?random=22"
        }
    ]
    
    print("🧪 Тестирование публикации русских новостей...")
    
    for i, news in enumerate(russian_news, 1):
        print(f"\n📤 Публикация {i}/{len(russian_news)}: {news['title'][:40]}...")
        
        result = send_russian_breaking_news(
            news['title'],
            news['summary'],
            news['image'],
            news['region_flag'],
            news['categories']
        )
        
        if result.get("ok"):
            print(f"   ✅ ОПУБЛИКОВАНО! Message ID: {result['result']['message_id']}")
            print(f"   📱 Канал: https://t.me/HeartofNews_Rus")
        else:
            print(f"   ❌ Ошибка: {result.get('description', 'Unknown error')}")
        
        if i < len(russian_news):
            time.sleep(3)
    
    print(f"\n🎉 РУССКИЙ КАНАЛ ГОТОВ К РАБОТЕ!")
    print("=" * 50)
    print("🚀 СИСТЕМА ДВУЯЗЫЧНЫХ НОВОСТЕЙ:")
    print("   🇬🇧 English: https://t.me/heartofnews")
    print("   🇷🇺 Русский: https://t.me/HeartofNews_Rus")
    print()
    print("🤖 БОТЫ:")
    print("   🇬🇧 @HeartOfNews_bot")
    print("   🇷🇺 @HeartofNewsRus_bot")
    print()
    print("⚡ ГОТОВО К АВТОМАТИЧЕСКОЙ ПУБЛИКАЦИИ!")

if __name__ == "__main__":
    main()