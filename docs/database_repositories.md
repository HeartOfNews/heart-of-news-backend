# Database Repositories

This document describes the database repository implementations for the Heart of News backend.

## Overview

The Heart of News backend uses SQLAlchemy as its ORM (Object-Relational Mapper) and follows the repository pattern for database operations. The repositories provide a clean abstraction layer between the database and the business logic.

## Base Repository

The `CRUDBase` class provides common CRUD (Create, Read, Update, Delete) operations for all models:

```python
class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Base class with default CRUD operations
    """
    
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[ModelType]:
        """Get a record by ID"""
        
    def get_multi(self, db: Session, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Get multiple records with pagination"""
        
    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new record"""
        
    def update(self, db: Session, *, db_obj: ModelType, obj_in: Union[UpdateSchemaType, Dict[str, Any]]) -> ModelType:
        """Update a record"""
        
    def remove(self, db: Session, *, id: Any) -> ModelType:
        """Delete a record"""
```

## Article Repository

The `CRUDArticle` class extends the base class with article-specific operations:

### Methods

#### Get with Source
```python
def get_with_source(self, db: Session, id: Any) -> Optional[Article]
```

Gets an article by ID with its source data loaded through a join.

#### Get Multi with Filters
```python
def get_multi_with_filters(
    self,
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    source_id: Optional[str] = None,
    status: Optional[str] = None,
    search_term: Optional[str] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    order_by: str = "published_at",
    order_desc: bool = True
) -> List[Article]
```

Gets multiple articles with various filtering options:
- Pagination with skip and limit
- Filtering by source ID
- Filtering by article status
- Text search in title and content
- Date range filtering
- Custom sorting

#### Create with Source ID
```python
def create_with_source_id(self, db: Session, *, obj_in: ArticleCreate, source_id: str) -> Article
```

Creates a new article with a given source ID.

#### Get by URL
```python
def get_by_url(self, db: Session, url: str) -> Optional[Article]
```

Gets an article by its URL, useful for preventing duplicates.

#### Update Bias Metrics
```python
def update_bias_metrics(
    self,
    db: Session,
    *,
    db_obj: Article,
    political_bias: float,
    emotional_language: float,
    fact_opinion_ratio: float
) -> Article
```

Updates the bias metrics for an article after analysis.

#### Update Status
```python
def update_status(self, db: Session, *, db_obj: Article, status: str) -> Article
```

Updates the article status (draft, processing, published, rejected, error).

#### Get Articles for Processing
```python
def get_articles_for_processing(self, db: Session, *, limit: int = 10) -> List[Article]
```

Gets articles in 'draft' status that need to be processed.

## Source Repository

The `CRUDSource` class extends the base class with source-specific operations:

### Methods

#### Get by Name
```python
def get_by_name(self, db: Session, name: str) -> Optional[Source]
```

Gets a source by its name.

#### Get by URL
```python
def get_by_url(self, db: Session, url: str) -> Optional[Source]
```

Gets a source by its URL.

#### Get Multi with Filters
```python
def get_multi_with_filters(
    self,
    db: Session,
    *,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    search_term: Optional[str] = None,
    min_reliability: Optional[float] = None,
    max_bias: Optional[float] = None
) -> List[Source]
```

Gets multiple sources with various filtering options:
- Pagination with skip and limit
- Filtering by category
- Text search in name
- Filtering by minimum reliability score
- Filtering by maximum absolute bias score

#### Update Crawl Timestamp
```python
def update_crawl_timestamp(
    self,
    db: Session,
    *,
    db_obj: Source,
    timestamp: Optional[datetime] = None
) -> Source
```

Updates the last_crawled_at timestamp for a source.

#### Get Sources for Crawling
```python
def get_sources_for_crawling(self, db: Session, *, limit: int = 5) -> List[Source]
```

Gets sources that need to be crawled based on crawl frequency and last crawl time.

#### Update Evaluation Scores
```python
def update_evaluation_scores(
    self,
    db: Session,
    *,
    db_obj: Source,
    reliability_score: Optional[float] = None,
    bias_score: Optional[float] = None,
    sensationalism_score: Optional[float] = None
) -> Source
```

Updates the evaluation scores for a source.

## Usage Examples

### Creating a new article

```python
from app.crud import article, source
from app.schemas.article import ArticleCreate

# Check if source exists
db_source = source.get(db=db, id=source_id)
if not db_source:
    raise ValueError("Source not found")

# Check if article already exists
existing = article.get_by_url(db=db, url=article_url)
if existing:
    raise ValueError("Article already exists")

# Create article data
article_data = ArticleCreate(
    title="Article Title",
    summary="Article summary",
    content="Article content",
    url=article_url,
    published_at=datetime.utcnow(),
    source={"id": source_id}
)

# Create the article
db_article = article.create_with_source_id(
    db=db,
    obj_in=article_data,
    source_id=source_id
)
```

### Filtering articles

```python
# Get articles with filtering
filtered_articles = article.get_multi_with_filters(
    db=db,
    skip=0,
    limit=20,
    source_id="source-id",
    status="published",
    search_term="keyword",
    from_date=datetime(2025, 1, 1),
    order_by="published_at",
    order_desc=True
)
```

### Analyzing and updating an article

```python
# Get the article
db_article = article.get(db=db, id=article_id)

# Update bias metrics
db_article = article.update_bias_metrics(
    db=db,
    db_obj=db_article,
    political_bias=0.2,
    emotional_language=0.3,
    fact_opinion_ratio=0.8
)

# Update status
db_article = article.update_status(
    db=db,
    db_obj=db_article,
    status="published"
)
```

### Finding sources to crawl

```python
# Get sources for crawling
sources_to_crawl = source.get_sources_for_crawling(db=db, limit=5)

# Update the crawl timestamp after crawling
for db_source in sources_to_crawl:
    source.update_crawl_timestamp(db=db, db_obj=db_source)
```