# Scraper Service

The Heart of News scraper service is responsible for collecting articles from various news sources. This documentation explains the scraper architecture and how to use it.

## Architecture

The scraper service consists of several key components:

1. **BaseScraper**: Abstract base class defining the scraper interface
2. **RssScraper**: Implementation for RSS feed-based sources
3. **WebScraper**: Implementation for web-based sources without RSS feeds
4. **ScraperFactory**: Factory for creating appropriate scrapers based on source configuration
5. **ScraperManager**: Coordinates scraping operations across multiple sources

### Data Structures

#### ArticleData

The `ArticleData` class represents scraped article information:

```python
class ArticleData(BaseModel):
    url: HttpUrl                     # URL of the article
    title: str                       # Article title
    content: Optional[str] = None    # Full article content
    summary: Optional[str] = None    # Article summary/description
    published_at: Optional[datetime] = None  # Publication date
    author: Optional[str] = None     # Author name
    image_url: Optional[HttpUrl] = None  # Featured image URL
    tags: Optional[List[str]] = None    # Article tags/categories
    metadata: Optional[Dict[str, Any]] = None  # Additional metadata
```

#### Source Configuration

Each news source is configured with a dictionary containing:

```python
{
    "id": "unique-source-id",       # Unique ID for the source
    "name": "Source Name",          # Human-readable name
    "url": "https://example.com",   # Base URL of the source
    "type": "rss" | "web" | "auto", # Scraper type to use
    
    # RSS-specific configuration
    "feed_url": "https://example.com/feed.xml",  # URL of RSS feed
    
    # Common selectors
    "article_selector": "CSS selector for article links/elements",
    "content_selector": "CSS selector for article content",
    "title_selector": "CSS selector for article title",
    "date_selector": "CSS selector for publication date",
    "author_selector": "CSS selector for author",
    "tag_selector": "CSS selector for tags/categories",
    
    # Additional metadata
    "reliability_score": 0.8,  # Source reliability (0.0-1.0)
    "bias_score": 0.1,         # Source bias (-1.0 to 1.0)
}
```

## Usage

### Basic Usage

```python
from app.services.scraper.factory import ScraperFactory
from app.services.scraper.sources import get_default_sources

# Create a scraper for a specific source
source_config = {
    "id": "example-source",
    "name": "Example News",
    "url": "https://example.com",
    "type": "rss",
    "feed_url": "https://example.com/feed.xml"
}

scraper = ScraperFactory.create_scraper(source_config)

# Fetch articles
async def fetch_news():
    articles = await scraper.fetch_articles(limit=10)
    
    for article in articles:
        print(f"Title: {article.title}")
        print(f"URL: {article.url}")
        
        # Fetch full content if needed
        full_article = await scraper.fetch_article_content(article.url)
        if full_article and full_article.content:
            print(f"Content: {full_article.content[:100]}...")
```

### Using ScraperManager

```python
from app.services.scraper.manager import ScraperManager
from app.services.scraper.sources import get_default_sources

# Initialize manager with sources
async def init_and_run():
    manager = ScraperManager()
    await manager.initialize_scrapers(get_default_sources())
    
    # Scrape all sources
    results = await manager.scrape_all_sources(limit_per_source=5)
    
    # Save to database (if DB session was provided)
    saved = await manager.save_articles_to_db(results)
    
    # Get source statistics
    stats = await manager.get_source_stats()
```

## Extending

### Adding a New Scraper Type

To add support for a new type of source:

1. Create a new class that extends `BaseScraper`
2. Implement the required methods: `fetch_articles()` and `fetch_article_content()`
3. Register the new type with `ScraperFactory`:

```python
from app.services.scraper.factory import ScraperFactory
from app.services.scraper.custom import CustomScraper

# Register the new scraper type
ScraperFactory.register_scraper_type("custom", CustomScraper)

# Now you can create scrapers of this type
source_config = {
    "id": "custom-source",
    "name": "Custom Source",
    "url": "https://example.com",
    "type": "custom",
    # ... custom configuration ...
}

scraper = ScraperFactory.create_scraper(source_config)
```

### Customizing Selectors

For most sources, you can customize behavior by adjusting the CSS selectors in the source configuration:

```python
source_config = {
    # ... other fields ...
    "article_selector": ".story-card a, .headline a",
    "content_selector": ".article-body, .content",
    "title_selector": ".article-headline, h1",
    "date_selector": ".published-date, time",
    "author_selector": ".author-name, .byline"
}
```

## Troubleshooting

### Common Issues

1. **No articles found**: Check the `article_selector` configuration
2. **Empty content**: Verify the `content_selector` configuration
3. **Missing metadata**: Ensure the source site provides the data in expected locations
4. **Rate limiting**: Some sites block repeated requests; consider adding delays
5. **Parsing errors**: Some sites have complex HTML that requires custom handling

### Debugging

For debugging, use the test script:

```bash
./scripts/test_scraper.py --source "source-name" --limit 3 --full-content
```

## Performance Considerations

- The scraper uses `aiohttp` for asynchronous HTTP requests
- Multiple sources can be scraped concurrently
- Consider adding caching for frequently accessed sources
- Large-scale deployments should use a task queue like Celery for background processing