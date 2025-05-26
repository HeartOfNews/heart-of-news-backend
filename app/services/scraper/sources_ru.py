"""
Russian news sources configuration
Focused on Russian-language political news, EU-Russia relations, and international politics
"""

import uuid
from typing import Dict, List, Any

# Russian-language news sources focused on politics
RUSSIAN_SOURCES = [
    # === RUSSIAN INDEPENDENT MEDIA ===
    
    # Meduza (Independent, Latvia-based)
    {
        "id": str(uuid.uuid4()),
        "name": "Медуза",
        "name_en": "Meduza",
        "url": "https://meduza.io",
        "type": "rss",
        "feed_url": "https://meduza.io/rss/all",
        "article_selector": ".GeneralMaterial-body",
        "reliability_score": 0.9,
        "bias_score": -0.1,
        "categories": ["Политика", "Россия", "Международные отношения"],
        "priority": "high",
        "language": "ru"
    },
    
    # The Bell (Independent economic/political news)
    {
        "id": str(uuid.uuid4()),
        "name": "The Bell",
        "url": "https://thebell.io",
        "type": "rss", 
        "feed_url": "https://thebell.io/feed",
        "article_selector": ".post-content",
        "reliability_score": 0.85,
        "bias_score": 0.0,
        "categories": ["Политика", "Экономика", "Россия"],
        "priority": "high",
        "language": "ru"
    },
    
    # === INTERNATIONAL RUSSIAN SERVICES ===
    
    # BBC Russian Service
    {
        "id": str(uuid.uuid4()),
        "name": "BBC Русская служба",
        "name_en": "BBC Russian",
        "url": "https://www.bbc.com/russian",
        "type": "rss",
        "feed_url": "https://feeds.bbci.co.uk/russian/rss.xml",
        "article_selector": ".story-body__inner",
        "reliability_score": 0.95,
        "bias_score": 0.0,
        "categories": ["Политика", "Международные отношения", "Россия"],
        "priority": "high",
        "language": "ru"
    },
    
    # Deutsche Welle Russian
    {
        "id": str(uuid.uuid4()),
        "name": "Deutsche Welle на русском",
        "name_en": "DW Russian",
        "url": "https://www.dw.com/ru",
        "type": "rss",
        "feed_url": "https://rss.dw.com/rdf/rss-ru-all",
        "article_selector": ".article-content",
        "reliability_score": 0.9,
        "bias_score": 0.0,
        "categories": ["Политика", "Европа", "Международные отношения"],
        "priority": "high",
        "language": "ru"
    },
    
    # Radio Free Europe/Radio Liberty Russian
    {
        "id": str(uuid.uuid4()),
        "name": "Радио Свобода",
        "name_en": "Radio Svoboda",
        "url": "https://www.svoboda.org",
        "type": "rss",
        "feed_url": "https://www.svoboda.org/api/epiqq",
        "article_selector": ".article-content",
        "reliability_score": 0.85,
        "bias_score": -0.2,
        "categories": ["Политика", "Права человека", "Россия"],
        "priority": "medium",
        "language": "ru"
    },
    
    # === EUROPEAN RUSSIAN-LANGUAGE SOURCES ===
    
    # EurAsia Daily (Moscow-based, pro-government perspective)
    {
        "id": str(uuid.uuid4()),
        "name": "EurAsia Daily",
        "url": "https://eadaily.com",
        "type": "rss",
        "feed_url": "https://eadaily.com/ru/rss",
        "article_selector": ".article-text",
        "reliability_score": 0.7,
        "bias_score": 0.4,
        "categories": ["Политика", "Евразия", "Геополитика"],
        "priority": "medium",
        "language": "ru"
    },
    
    # === RUSSIAN POLITICAL ANALYSIS ===
    
    # Carnegie Moscow Center (until closure)
    {
        "id": str(uuid.uuid4()),
        "name": "Московский центр Карнеги",
        "name_en": "Carnegie Moscow",
        "url": "https://carnegie.ru",
        "type": "web",
        "article_selector": ".article-content",
        "reliability_score": 0.9,
        "bias_score": 0.0,
        "categories": ["Политика", "Аналитика", "Международные отношения"],
        "priority": "medium",
        "language": "ru"
    },
    
    # === RUSSIAN ECONOMY & POLITICS ===
    
    # RBC (РБК) - Business and politics
    {
        "id": str(uuid.uuid4()),
        "name": "РБК",
        "name_en": "RBC",
        "url": "https://www.rbc.ru",
        "type": "rss",
        "feed_url": "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
        "article_selector": ".article__text",
        "reliability_score": 0.8,
        "bias_score": 0.1,
        "categories": ["Политика", "Экономика", "Россия"],
        "priority": "medium",
        "language": "ru"
    },
    
    # === REGIONAL PERSPECTIVES ===
    
    # Current Time (Настоящее Время)
    {
        "id": str(uuid.uuid4()),
        "name": "Настоящее Время",
        "name_en": "Current Time",
        "url": "https://www.currenttime.tv",
        "type": "rss",
        "feed_url": "https://www.currenttime.tv/api/epiqq",
        "article_selector": ".article-content",
        "reliability_score": 0.85,
        "bias_score": -0.1,
        "categories": ["Политика", "Общество", "Россия"],
        "priority": "medium",
        "language": "ru"
    }
]

def get_russian_sources() -> List[Dict[str, Any]]:
    """
    Get Russian-language news sources configuration
    
    Returns:
        List of Russian source configurations
    """
    return RUSSIAN_SOURCES

def get_russian_sources_by_priority(priority: str = "high") -> List[Dict[str, Any]]:
    """
    Get Russian sources filtered by priority
    
    Args:
        priority: Priority level ("high", "medium", "low")
            
    Returns:
        List of source configurations
    """
    return [
        source for source in RUSSIAN_SOURCES
        if source.get("priority", "medium") == priority
    ]

def get_russian_sources_by_category(categories: List[str]) -> List[Dict[str, Any]]:
    """
    Get Russian sources that cover specific categories
    
    Args:
        categories: List of categories to filter by
            
    Returns:
        List of source configurations
    """
    result = []
    for source in RUSSIAN_SOURCES:
        source_categories = source.get("categories", [])
        if any(cat in source_categories for cat in categories):
            result.append(source)
    return result

def get_russian_political_sources() -> List[Dict[str, Any]]:
    """
    Get sources specifically focused on Russian political news
    
    Returns:
        List of political source configurations
    """
    return get_russian_sources_by_category(["Политика"])

# Regional focus mappings for Russian audience
RUSSIAN_REGION_KEYWORDS = {
    "russia": ["россия", "российский", "путин", "кремль", "москва", "санкт-петербург"],
    "ukraine": ["украина", "украинский", "киев", "зеленский"],
    "belarus": ["беларусь", "белорусский", "минск", "лукашенко"],
    "eu": ["европейский союз", "ес", "брюссель", "европа", "евросоюз"],
    "usa": ["сша", "соединенные штаты", "америка", "вашингтон", "байден", "трамп"],
    "china": ["китай", "китайский", "пекин", "си цзиньпин"]
}