#!/usr/bin/env python3
"""
Demo for Russian-language Heart of News Telegram channel
"""

import json
import subprocess
import time

# Russian bot credentials
RUSSIAN_BOT_TOKEN = "7294645697:AAGJxaixBkgtBqAIpFU-kR8uzo06amOQOLs"
RUSSIAN_CHANNEL_ID = "@HeartofNews_Rus"

def send_russian_news(title, summary, image_url, region_flag, categories):
    """Send Russian news with proper formatting"""
    
    # Russian message format
    message = f"""🗞️ **{title}**

📰 {summary}

🏛️ {region_flag} #{categories}"""
    
    # Send with image if available
    if image_url:
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
    else:
        payload = {
            "chat_id": RUSSIAN_CHANNEL_ID,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        curl_command = [
            "curl", "-X", "POST",
            f"https://api.telegram.org/bot{RUSSIAN_BOT_TOKEN}/sendMessage",
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
    print("🇷🇺 СЕРДЦЕ НОВОСТЕЙ - РУССКОЯЗЫЧНЫЙ КАНАЛ")
    print("=" * 60)
    
    if RUSSIAN_BOT_TOKEN == "your_russian_bot_token_here":
        print("⚠️  ВНИМАНИЕ: Настройте Russian bot credentials!")
        print()
        print("📋 ИНСТРУКЦИЯ ПО НАСТРОЙКЕ:")
        print("1. Создайте Russian Telegram bot через @BotFather")
        print("2. Создайте Russian Telegram channel")  
        print("3. Добавьте бота как администратора канала")
        print("4. Обновите credentials в скрипте")
        print()
        print("🤖 Telegram Bot API для тестирования:")
        
        # Show sample Russian news for demonstration
        sample_news = [
            {
                "title": "ЕС принимает новые санкции против России",
                "summary": "Европейский парламент одобрил очередной пакет экономических санкций в ответ на последние геополитические события в регионе.",
                "region_flag": "🇪🇺",
                "categories": "Политика ЕС Санкции",
                "image": "https://picsum.photos/800/600?random=10"
            },
            {
                "title": "Конгресс США обсуждает новый оборонный бюджет",
                "summary": "Американские законодатели рассматривают увеличение военных расходов и поддержку союзников в Восточной Европе.",
                "region_flag": "🇺🇸", 
                "categories": "Политика США Оборона",
                "image": "https://picsum.photos/800/600?random=11"
            },
            {
                "title": "Россия и Китай укрепляют экономическое сотрудничество",
                "summary": "Президенты двух стран подписали соглашения о расширении торговых отношений и инвестиционных проектов.",
                "region_flag": "🇷🇺",
                "categories": "Политика Россия Китай Экономика",
                "image": "https://picsum.photos/800/600?random=12"
            }
        ]
        
        print("\n📰 ОБРАЗЦЫ РУССКИХ НОВОСТЕЙ:")
        for i, news in enumerate(sample_news, 1):
            print(f"\n{i}. {news['title']}")
            print(f"   📰 {news['summary'][:80]}...")
            print(f"   🏛️ {news['region_flag']} #{news['categories']}")
            print(f"   🖼️ Изображение: {news['image']}")
        
        return
    
    # If credentials are configured, test the Russian channel
    print("🧪 Тестирование русскоязычного канала...")
    
    # Test Russian political news
    russian_news = [
        {
            "title": "ЕС обсуждает новые энергетические инициативы",
            "summary": "Европейская комиссия представила план по снижению зависимости от российского газа и развитию возобновляемых источников энергии.",
            "region_flag": "🇪🇺",
            "categories": "Политика ЕС Энергетика",
            "image": "https://picsum.photos/800/600?random=7"
        },
        {
            "title": "Байден подписал новый закон о поддержке Украины", 
            "summary": "Президент США утвердил пакет военной и гуманитарной помощи на сумму 60 миллиардов долларов для поддержки украинского правительства.",
            "region_flag": "🇺🇸",
            "categories": "Политика США Украина",
            "image": "https://picsum.photos/800/600?random=8"
        }
    ]
    
    for i, news in enumerate(russian_news, 1):
        print(f"\n📤 Отправка новости {i}/{len(russian_news)}...")
        print(f"   📰 {news['title'][:50]}...")
        
        result = send_russian_news(
            news['title'],
            news['summary'],
            news['image'],
            news['region_flag'],
            news['categories']
        )
        
        if result.get("ok"):
            print(f"   ✅ Опубликовано! Message ID: {result['result']['message_id']}")
        else:
            print(f"   ❌ Ошибка: {result.get('description', 'Unknown error')}")
        
        if i < len(russian_news):
            print("   ⏳ Следующая новость через 3 секунды...")
            time.sleep(3)
    
    print(f"\n🎉 Тестирование русскоязычного канала завершено!")
    print("\n📋 ВОЗМОЖНОСТИ РУССКОГО КАНАЛА:")
    print("   ✅ Русскоязычные новости")
    print("   ✅ Политическая аналитика")
    print("   ✅ Международные отношения")
    print("   ✅ ЕС-Россия-США фокус")
    print("   ✅ Региональные флаги")
    print("   ✅ Изображения из источников")
    print("   ✅ Мгновенная публикация")

if __name__ == "__main__":
    main()