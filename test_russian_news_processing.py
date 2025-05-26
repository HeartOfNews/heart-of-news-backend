#!/usr/bin/env python3
"""
Test Russian News Processing - Demonstration Script
Shows how the propaganda detection and rewriting works for Russian news
"""

import json
import sys
import os
from datetime import datetime

# Add app to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Sample Russian news articles with propaganda content
SAMPLE_ARTICLES = [
    {
        "title": "Западные марионетки угрожают России новыми санкциями",
        "content": "Режим в Киеве при поддержке своих западных кукловодов продолжает эскалацию конфликта. Согласно источникам, украинские экстремисты планируют новые провокации против мирного населения. Это возмутительное поведение представляет экзистенциальную угрозу для региональной стабильности.",
        "source": "EurAsia Daily"
    },
    {
        "title": "ЕС обвиняет Россию в нарушении международного права",
        "content": "Представители Европейского союза заявили о серьезных нарушениях международного права со стороны России. По данным аналитиков, ситуация требует дальнейшего изучения. Брюссель призывает к мирному урегулированию конфликта через дипломатические каналы.",
        "source": "BBC Russian"
    },
    {
        "title": "Шокирующие факты о коррупции в правительстве",
        "content": "Расследование показало, что коррумпированные чиновники украли миллиарды рублей из государственного бюджета. По сообщениям инсайдеров, схема работала годами. Эти ужасающие факты требуют немедленного расследования правоохранительными органами.",
        "source": "Meduza"
    }
]


class MockPropagandaDetector:
    """Mock propaganda detector for testing"""
    
    def analyze_content(self, title: str, content: str, source_info: dict) -> dict:
        """Analyze content for propaganda and bias"""
        full_text = f"{title} {content}".lower()
        
        # Detect propaganda indicators
        propaganda_score = 0.0
        propaganda_techniques = []
        
        # Check for loaded language
        loaded_words = ["марионетки", "режим", "экстремисты", "кукловоды", "провокации"]
        for word in loaded_words:
            if word in full_text:
                propaganda_score += 0.3
                propaganda_techniques.append("loaded_language")
                break
        
        # Check for emotional manipulation
        emotional_words = ["возмутительное", "шокирующие", "ужасающие", "экзистенциальную угрозу"]
        for word in emotional_words:
            if word in full_text:
                propaganda_score += 0.2
                propaganda_techniques.append("emotional_manipulation")
                break
        
        # Check for unverified claims
        unverified_phrases = ["согласно источникам", "по сообщениям инсайдеров"]
        for phrase in unverified_phrases:
            if phrase in full_text:
                propaganda_score += 0.1
                propaganda_techniques.append("unverified_claims")
                break
        
        # Determine bias based on source reliability
        reliability_score = source_info.get("reliability_score", 0.8)
        bias_score = 0.0
        
        if "EurAsia Daily" in source_info.get("name", ""):
            bias_score = 0.4  # Pro-government bias
        elif "BBC" in source_info.get("name", ""):
            bias_score = 0.0  # Neutral
        
        # Make recommendation
        if propaganda_score > 0.6:
            recommendation = "REJECT"
        elif propaganda_score > 0.3 or len(propaganda_techniques) > 1:
            recommendation = "REVIEW"
        else:
            recommendation = "APPROVE"
        
        return {
            "propaganda_score": min(1.0, propaganda_score),
            "bias_score": bias_score,
            "reliability_score": reliability_score,
            "propaganda_techniques": list(set(propaganda_techniques)),
            "recommendation": recommendation,
            "confidence": 0.9
        }


class MockNewsRewriter:
    """Mock news rewriter for testing"""
    
    def __init__(self):
        self.propaganda_replacements = {
            "марионетки": "представители",
            "режим": "правительство", 
            "экстремисты": "вооруженные группы",
            "кукловоды": "партнеры",
            "провокации": "действия",
            "возмутительное": "спорное",
            "шокирующие": "неожиданные",
            "ужасающие": "серьезные",
            "экзистенциальную угрозу": "серьезную проблему"
        }
    
    def rewrite_content(self, title: str, content: str, analysis: dict) -> dict:
        """Rewrite content to remove propaganda"""
        rewritten_title = title
        rewritten_content = content
        changes_made = []
        
        # Apply replacements
        for original, replacement in self.propaganda_replacements.items():
            if original in rewritten_title:
                rewritten_title = rewritten_title.replace(original, replacement)
                changes_made.append(f"title: {original} -> {replacement}")
            
            if original in rewritten_content:
                rewritten_content = rewritten_content.replace(original, replacement)
                changes_made.append(f"content: {original} -> {replacement}")
        
        # Add qualifiers to unverified claims
        if "Согласно источникам" in rewritten_content:
            rewritten_content = rewritten_content.replace("Согласно источникам", "По имеющимся данным")
            changes_made.append("qualified unverified claims")
        
        if "по сообщениям инсайдеров" in rewritten_content:
            rewritten_content = rewritten_content.replace("по сообщениям инсайдеров", "согласно некоторым источникам")
            changes_made.append("qualified insider reports")
        
        return {
            "title": rewritten_title,
            "content": rewritten_content,
            "changes_made": changes_made
        }


def format_telegram_message(title: str, content: str, source: str) -> str:
    """Format article for Telegram publishing"""
    # Limit content length for Telegram
    summary = content[:250] + "..." if len(content) > 250 else content
    
    message = f"""🔴 **ПРОВЕРЕННЫЕ НОВОСТИ**

**{title}**

{summary}

📰 Источник: {source}
✅ Проверено и обработано

#Новости #Россия #ПроверенныеНовости"""
    
    return message


def main():
    """Test the Russian news processing pipeline"""
    print("=== ТЕСТИРОВАНИЕ ОБРАБОТКИ РОССИЙСКИХ НОВОСТЕЙ ===\n")
    
    detector = MockPropagandaDetector()
    rewriter = MockNewsRewriter()
    
    processed_articles = []
    
    for i, article in enumerate(SAMPLE_ARTICLES, 1):
        print(f"📰 СТАТЬЯ {i}: {article['title']}")
        print(f"Источник: {article['source']}")
        print("-" * 80)
        
        # Create source info
        source_info = {
            "name": article["source"],
            "reliability_score": 0.9 if "BBC" in article["source"] else (0.8 if "Meduza" in article["source"] else 0.7)
        }
        
        # Analyze for propaganda
        analysis = detector.analyze_content(article["title"], article["content"], source_info)
        
        print(f"🔍 АНАЛИЗ:")
        print(f"  • Уровень пропаганды: {analysis['propaganda_score']:.2f}")
        print(f"  • Уровень предвзятости: {analysis['bias_score']:.2f}")
        print(f"  • Надежность источника: {analysis['reliability_score']:.2f}")
        print(f"  • Техники пропаганды: {', '.join(analysis['propaganda_techniques']) if analysis['propaganda_techniques'] else 'Не обнаружено'}")
        print(f"  • Рекомендация: {analysis['recommendation']}")
        
        # Process based on recommendation
        if analysis["recommendation"] == "REJECT":
            print("❌ СТАТЬЯ ОТКЛОНЕНА из-за высокого уровня пропаганды")
            print()
            continue
        
        elif analysis["recommendation"] == "REVIEW" or analysis["propaganda_score"] > 0.3:
            print("✏️ ПЕРЕПИСЫВАНИЕ СТАТЬИ для удаления пропаганды...")
            
            rewrite_result = rewriter.rewrite_content(article["title"], article["content"], analysis)
            
            print(f"📝 Изменения:")
            for change in rewrite_result["changes_made"]:
                print(f"    • {change}")
            
            final_title = rewrite_result["title"]
            final_content = rewrite_result["content"]
            rewrite_applied = True
            
        else:
            print("✅ СТАТЬЯ ОДОБРЕНА без изменений")
            final_title = article["title"]
            final_content = article["content"]
            rewrite_applied = False
        
        # Format for Telegram
        telegram_message = format_telegram_message(final_title, final_content, article["source"])
        
        processed_articles.append({
            "original_title": article["title"],
            "final_title": final_title,
            "original_content": article["content"],
            "final_content": final_content,
            "source": article["source"],
            "analysis": analysis,
            "rewrite_applied": rewrite_applied,
            "telegram_message": telegram_message
        })
        
        print("📱 СООБЩЕНИЕ ДЛЯ ТЕЛЕГРАМ:")
        print(telegram_message)
        print()
    
    # Summary
    print("=" * 80)
    print("📊 ИТОГИ ОБРАБОТКИ:")
    print(f"Всего статей обработано: {len(processed_articles)}")
    rewritten_count = sum(1 for a in processed_articles if a["rewrite_applied"])
    print(f"Статей переписано: {rewritten_count}")
    print(f"Статей одобрено без изменений: {len(processed_articles) - rewritten_count}")
    print(f"Статей отклонено: {len(SAMPLE_ARTICLES) - len(processed_articles)}")
    
    print("\n✅ Все обработанные статьи готовы к публикации в Telegram!")
    
    return processed_articles


if __name__ == "__main__":
    main()