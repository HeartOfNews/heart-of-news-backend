#!/usr/bin/env python3

"""
Script to test the scraper functionality with real news sources
"""

import sys
import asyncio
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from app.services.scraper.factory import ScraperFactory
from app.services.scraper.sources import get_default_sources, get_sources_by_reliability

# Configure argument parsing
parser = argparse.ArgumentParser(description="Test news scrapers with real sources.")
parser.add_argument("--source", "-s", help="ID or name of specific source to scrape")
parser.add_argument("--limit", "-l", type=int, default=5, help="Maximum number of articles to fetch per source")
parser.add_argument("--reliability", "-r", type=float, default=0.7, help="Minimum reliability score (0.0-1.0)")
parser.add_argument("--full-content", "-f", action="store_true", help="Fetch full article content (slower)")
parser.add_argument("--output", "-o", help="Output file for results (JSON format)")

async def test_scrapers(args):
    """
    Test scrapers with real sources
    
    Args:
        args: Command-line arguments
    """
    print(f"\n{'=' * 70}")
    print(f"TESTING NEWS SCRAPERS")
    print(f"{'=' * 70}\n")
    
    # Get sources filtered by reliability
    sources = get_sources_by_reliability(min_reliability=args.reliability)
    
    if args.source:
        # Filter to specific source if requested
        sources = [s for s in sources if args.source.lower() in (s.get("id", "").lower(), s.get("name", "").lower())]
        
        if not sources:
            print(f"Error: No source found matching '{args.source}'")
            return
    
    print(f"Testing {len(sources)} sources with minimum reliability of {args.reliability}...\n")
    
    # Create scrapers
    all_results = {}
    
    for source in sources:
        source_id = source["id"]
        source_name = source["name"]
        
        print(f"\n{'-' * 70}")
        print(f"Source: {source_name} ({source['type']})")
        print(f"URL: {source['url']}")
        print(f"{'-' * 70}")
        
        try:
            # Create scraper
            scraper = ScraperFactory.create_scraper(source)
            
            if not scraper:
                print(f"Error: Could not create scraper for {source_name}")
                continue
            
            # Fetch articles
            print(f"Fetching up to {args.limit} articles...")
            start_time = datetime.now()
            
            articles = await scraper.fetch_articles(limit=args.limit)
            
            fetch_time = (datetime.now() - start_time).total_seconds()
            print(f"Fetched {len(articles)} articles in {fetch_time:.2f} seconds")
            
            results = []
            
            # Process articles
            for i, article in enumerate(articles, 1):
                print(f"\nArticle {i}: {article.title}")
                print(f"URL: {article.url}")
                
                if article.published_at:
                    print(f"Published: {article.published_at.strftime('%Y-%m-%d %H:%M')}")
                
                if article.author:
                    print(f"Author: {article.author}")
                    
                if article.summary:
                    print(f"Summary: {article.summary[:150]}...")
                
                # Fetch full content if requested
                if args.full_content:
                    print("Fetching full content...")
                    full_article = await scraper.fetch_article_content(article.url)
                    
                    if full_article and full_article.content:
                        content_preview = full_article.content.split('\n')[0][:150]
                        print(f"Content: {content_preview}...")
                        
                        # Use the full article data
                        article_data = full_article
                    else:
                        print("Could not fetch full content")
                        article_data = article
                else:
                    article_data = article
                
                # Add to results
                results.append({
                    "title": article_data.title,
                    "url": str(article_data.url),
                    "published_at": article_data.published_at.isoformat() if article_data.published_at else None,
                    "author": article_data.author,
                    "summary": article_data.summary,
                    "content_length": len(article_data.content) if article_data.content else 0,
                    "tags": article_data.tags
                })
            
            all_results[source_id] = {
                "name": source_name,
                "url": source["url"],
                "type": source["type"],
                "articles": results
            }
            
        except Exception as e:
            print(f"Error testing {source_name}: {e}")
    
    # Output results if requested
    if args.output:
        try:
            with open(args.output, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"\nResults saved to {args.output}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    # Print summary
    print(f"\n{'=' * 70}")
    print(f"SUMMARY")
    print(f"{'=' * 70}")
    
    total_articles = sum(len(source_data["articles"]) for source_data in all_results.values())
    print(f"Scraped {total_articles} articles from {len(all_results)} sources")
    
    for source_id, source_data in all_results.items():
        print(f"- {source_data['name']}: {len(source_data['articles'])} articles")
    
    print(f"\nDone!\n")

if __name__ == "__main__":
    args = parser.parse_args()
    asyncio.run(test_scrapers(args))