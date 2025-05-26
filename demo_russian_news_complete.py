#!/usr/bin/env python3
"""
Complete Russian News Demo
Shows the full pipeline: scraping, propaganda detection, rewriting, and formatting for Telegram
"""

import json
import urllib.request
import urllib.parse
import os
import re
from datetime import datetime
from typing import Dict, List, Any

# Sample real Russian news data (simulated from RSS feeds)
SAMPLE_RUSSIAN_NEWS = [
    {
        "title": "Украинские радикалы при поддержке западных марионеток готовят новые провокации",
        "content": "Согласно источникам в разведке, украинские экстремисты планируют очередные возмутительные атаки на мирное население. Эти террористические действия представляют экзистенциальную угрозу для всего региона. Режим в Киеве получает прямую поддержку от своих западных кукловодов.",
        "source": "EurAsia Daily",
        "url": "https://eadaily.com/ru/news/2024/05/26/ukraine-provocations",
        "published": "2024-05-26 15:30:00",
        "reliability_score": 0.7,
        "bias_score": 0.4
    },
    {
        "title": "ЕС призывает к мирному урегулированию украинского конфликта",
        "content": "Представители Европейского союза заявили о необходимости поиска дипломатических решений для урегулирования конфликта на Украине. По словам официальных лиц ЕС, все стороны должны вернуться к переговорному процессу. Брюссель готов выступить посредником в мирных переговорах.",
        "source": "BBC Russian",
        "url": "https://bbc.com/russian/news-68123456",
        "published": "2024-05-26 14:15:00",
        "reliability_score": 0.95,
        "bias_score": 0.0
    },
    {
        "title": "Шокирующие данные о коррупции в российских министерствах",
        "content": "Расследование показало ужасающие масштабы коррупции в государственных структурах. По сообщениям инсайдеров, чиновники украли более 50 миллиардов рублей за последний год. Эксперты называют эти факты катастрофическими для экономики страны.",
        "source": "Meduza",
        "url": "https://meduza.io/feature/2024/05/26/corruption-investigation",
        "published": "2024-05-26 13:45:00",
        "reliability_score": 0.85,
        "bias_score": 0.0
    },
    {
        "title": "Россия укрепляет сотрудничество с партнерами по БРИКС",
        "content": "В рамках саммита БРИКС обсуждаются вопросы экономического партнерства и торговых отношений. Российская делегация представила новые инициативы по развитию многостороннего сотрудничества. Участники встречи отметили важность укрепления связей между странами-участницами.",
        "source": "RBC",
        "url": "https://rbc.ru/politics/2024/05/26/brics-summit",
        "published": "2024-05-26 12:30:00",
        "reliability_score": 0.8,
        "bias_score": 0.1
    }
]

class RussianPropagandaDetector:
    """Advanced propaganda detection for Russian content"""
    
    def __init__(self):
        self.propaganda_patterns = {
            "loaded_language": [
                r"\b(марионетки|кукловоды|режим|экстремисты|радикалы|террористы|провокации)\b",
                r"\b(оккупанты|агрессоры|захватчики|фашисты|нацисты)\b"
            ],
            "emotional_manipulation": [
                r"\b(возмутительн|шокирующ|ужасающ|катастрофическ|экзистенциальн)\w*",
                r"\b(позорн|постыдн|чудовищн|варварск)\w*"
            ],
            "unverified_claims": [
                r"\b(согласно источникам|по сообщениям инсайдеров|как стало известно)",
                r"\b(по слухам|ходят слухи|как говорят)\b"
            ],
            "false_dichotomy": [
                r"\b(либо|или)\b.*\b(никто не может|нет выбора|единственный путь)\b",
                r"\b(с нами или против нас|выбирайте сторону)\b"
            ]
        }
    
    def analyze_content(self, title: str, content: str, source_info: Dict) -> Dict[str, Any]:
        """Analyze content for propaganda and bias"""
        full_text = f"{title} {content}".lower()
        
        analysis = {
            "propaganda_score": 0.0,
            "bias_score": source_info.get("bias_score", 0.0),
            "reliability_score": source_info.get("reliability_score", 0.8),
            "propaganda_techniques": [],
            "detected_phrases": [],
            "recommendation": "APPROVE",
            "confidence": 0.9
        }
        
        # Detect propaganda techniques
        for technique, patterns in self.propaganda_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, full_text, re.IGNORECASE)
                for match in matches:
                    if technique not in analysis["propaganda_techniques"]:
                        analysis["propaganda_techniques"].append(technique)
                    analysis["detected_phrases"].append({
                        "technique": technique,
                        "phrase": match.group(),
                        "context": full_text[max(0, match.start()-20):match.end()+20]
                    })
                    analysis["propaganda_score"] += 0.2
        
        # Limit propaganda score
        analysis["propaganda_score"] = min(1.0, analysis["propaganda_score"])
        
        # Make recommendation
        if analysis["propaganda_score"] > 0.6:
            analysis["recommendation"] = "REJECT"
        elif analysis["propaganda_score"] > 0.3 or len(analysis["propaganda_techniques"]) > 1:
            analysis["recommendation"] = "REVIEW"
        
        return analysis

class RussianContentRewriter:
    """Rewrite Russian content to remove propaganda while preserving facts"""
    
    def __init__(self):
        self.replacements = {
            # Loaded language
            "марионетки": "представители",
            "кукловоды": "партнеры",
            "режим": "правительство",
            "экстремисты": "вооруженные группы",
            "радикалы": "активисты",
            "террористы": "вооруженные формирования",
            "провокации": "действия",
            
            # Emotional language
            "возмутительные": "спорные",
            "шокирующие": "неожиданные",
            "ужасающие": "серьезные",
            "катастрофические": "значительные",
            "экзистенциальную угрозу": "серьезную проблему",
            
            # Qualifiers for unverified claims
            "согласно источникам": "по имеющимся данным",
            "по сообщениям инсайдеров": "согласно некоторым источникам",
            "как стало известно": "по информации",
        }
    
    def rewrite_content(self, title: str, content: str, analysis: Dict) -> Dict[str, str]:
        """Rewrite content to remove propaganda"""
        rewritten_title = title
        rewritten_content = content
        changes_made = []
        
        for original, replacement in self.replacements.items():
            # Replace in title
            if original in rewritten_title.lower():
                old_title = rewritten_title
                rewritten_title = re.sub(re.escape(original), replacement, rewritten_title, flags=re.IGNORECASE)
                if old_title != rewritten_title:
                    changes_made.append(f"title: {original} → {replacement}")
            
            # Replace in content
            if original in rewritten_content.lower():
                old_content = rewritten_content
                rewritten_content = re.sub(re.escape(original), replacement, rewritten_content, flags=re.IGNORECASE)
                if old_content != rewritten_content:
                    changes_made.append(f"content: {original} → {replacement}")
        
        return {
            "title": rewritten_title,
            "content": rewritten_content,
            "changes_made": changes_made
        }

class TelegramPublisher:
    """Format and publish to Telegram"""
    
    def __init__(self, bot_token: str, channel_id: str):
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    def format_message(self, article: Dict) -> str:
        """Format article for Telegram"""
        # Determine region flag
        title_lower = article["title"].lower()
        if any(word in title_lower for word in ["россия", "российский", "рф"]):
            flag = "🇷🇺"
        elif any(word in title_lower for word in ["украина", "украинский"]):
            flag = "🇺🇦"
        elif any(word in title_lower for word in ["ес", "европ", "брюссель"]):
            flag = "🇪🇺"
        else:
            flag = "🌍"
        
        # Create summary
        summary = article["content"][:200] + "..." if len(article["content"]) > 200 else article["content"]
        
        # Status indicator
        status = "🔄 ПЕРЕПИСАНО" if article.get("rewrite_applied") else "✅ ОДОБРЕНО"
        
        message = f"""🔴 **ПРОВЕРЕННЫЕ НОВОСТИ**

**{article['title']}**

{summary}

{flag} **Источник:** {article['source']}
{status} | Надежность: {article.get('reliability_score', 0.8):.1f}/1.0

#Новости #Россия #ПроверенныеНовости"""
        
        return message
    
    def publish_message(self, message: str) -> Dict[str, Any]:
        """Publish message to Telegram (demo mode)"""
        print(f"📤 ПУБЛИКАЦИЯ В TELEGRAM:")
        print(f"📢 Канал: {self.channel_id}")
        print("─" * 60)
        print(message)
        print("─" * 60)
        
        # In real mode, this would actually send to Telegram
        # For demo, we just return success
        return {"success": True, "message_id": 12345}

def main():
    """Main demo function"""
    print("🇷🇺 HEART OF NEWS RUSSIAN - ПОЛНАЯ ДЕМОНСТРАЦИЯ")
    print("=" * 70)
    print("Обработка реальных российских новостей с детекцией пропаганды")
    print("=" * 70)
    print()
    
    # Initialize components
    detector = RussianPropagandaDetector()
    rewriter = RussianContentRewriter()
    
    # Get Telegram credentials (for demo, use placeholder if not set)
    bot_token = os.getenv('TELEGRAM_RU_BOT_TOKEN', 'demo_token')
    channel_id = os.getenv('TELEGRAM_RU_CHANNEL_ID', '@HeartofNews_Rus')
    publisher = TelegramPublisher(bot_token, channel_id)
    
    processed_articles = []
    
    print(f"📊 ОБРАБОТКА {len(SAMPLE_RUSSIAN_NEWS)} НОВОСТНЫХ СТАТЕЙ")
    print()
    
    for i, article in enumerate(SAMPLE_RUSSIAN_NEWS, 1):
        print(f"📰 СТАТЬЯ {i}/{len(SAMPLE_RUSSIAN_NEWS)}")
        print(f"Заголовок: {article['title']}")
        print(f"Источник: {article['source']} (надежность: {article['reliability_score']:.1f})")
        print("─" * 50)
        
        # Analyze for propaganda
        analysis = detector.analyze_content(
            article["title"], 
            article["content"], 
            {"reliability_score": article["reliability_score"], "bias_score": article["bias_score"]}
        )
        
        print(f"🔍 АНАЛИЗ ПРОПАГАНДЫ:")
        print(f"   • Оценка пропаганды: {analysis['propaganda_score']:.2f}/1.0")
        print(f"   • Предвзятость источника: {analysis['bias_score']:+.1f}")
        print(f"   • Надежность: {analysis['reliability_score']:.1f}/1.0")
        
        if analysis['propaganda_techniques']:
            print(f"   • Техники пропаганды: {', '.join(analysis['propaganda_techniques'])}")
            for phrase in analysis['detected_phrases'][:3]:  # Show first 3
                print(f"     - {phrase['technique']}: '{phrase['phrase']}'")
        else:
            print(f"   • Техники пропаганды: не обнаружено")
        
        print(f"   • Рекомендация: {analysis['recommendation']}")
        
        # Process based on recommendation
        final_article = article.copy()
        final_article['analysis'] = analysis
        
        if analysis['recommendation'] == 'REJECT':
            print("❌ СТАТЬЯ ОТКЛОНЕНА - слишком много пропаганды")
            print()
            continue
        
        elif analysis['recommendation'] == 'REVIEW':
            print("✏️ ПЕРЕПИСЫВАНИЕ СТАТЬИ для удаления пропаганды...")
            
            rewrite_result = rewriter.rewrite_content(
                article['title'], 
                article['content'], 
                analysis
            )
            
            final_article.update({
                'title': rewrite_result['title'],
                'content': rewrite_result['content'],
                'rewrite_applied': True,
                'changes_made': rewrite_result['changes_made']
            })
            
            if rewrite_result['changes_made']:
                print("📝 Внесенные изменения:")
                for change in rewrite_result['changes_made']:
                    print(f"     • {change}")
            else:
                print("📝 Автоматические изменения не потребовались")
        
        else:
            print("✅ СТАТЬЯ ОДОБРЕНА без изменений")
            final_article['rewrite_applied'] = False
        
        # Format for Telegram
        telegram_message = publisher.format_message(final_article)
        
        # Publish (demo mode)
        result = publisher.publish_message(telegram_message)
        
        if result['success']:
            print(f"✅ Опубликовано успешно")
        else:
            print(f"❌ Ошибка публикации: {result.get('error')}")
        
        processed_articles.append(final_article)
        print()
    
    # Summary
    print("=" * 70)
    print("📊 ИТОГОВАЯ СТАТИСТИКА")
    print("=" * 70)
    
    total_articles = len(SAMPLE_RUSSIAN_NEWS)
    published_articles = len(processed_articles)
    rewritten_articles = sum(1 for a in processed_articles if a.get('rewrite_applied'))
    rejected_articles = total_articles - published_articles
    
    print(f"📰 Всего статей обработано: {total_articles}")
    print(f"✅ Опубликовано: {published_articles}")
    print(f"✏️ Переписано (удалена пропаганда): {rewritten_articles}")
    print(f"➡️ Одобрено без изменений: {published_articles - rewritten_articles}")
    print(f"❌ Отклонено (слишком много пропаганды): {rejected_articles}")
    
    print()
    print("🎯 РЕЗУЛЬТАТЫ:")
    if published_articles > 0:
        propaganda_rate = (rewritten_articles / published_articles) * 100
        print(f"• {propaganda_rate:.1f}% статей содержали пропаганду и были исправлены")
        print(f"• {100 - propaganda_rate:.1f}% статей были чистыми")
    
    print()
    print("🔗 ИСТОЧНИКИ ПО НАДЕЖНОСТИ:")
    sources_by_reliability = {}
    for article in SAMPLE_RUSSIAN_NEWS:
        source = article['source']
        reliability = article['reliability_score']
        sources_by_reliability[source] = reliability
    
    for source, reliability in sorted(sources_by_reliability.items(), key=lambda x: x[1], reverse=True):
        status = "🟢" if reliability >= 0.9 else "🟡" if reliability >= 0.8 else "🟠"
        print(f"{status} {source}: {reliability:.1f}/1.0")
    
    print()
    print("✨ СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("Для запуска с реальными новостями:")
    print("1. Добавьте бота @HeartofNewsRus_bot как администратора канала")
    print("2. Запустите: python3 russian_verified_news_worker.py --once")

if __name__ == "__main__":
    main()