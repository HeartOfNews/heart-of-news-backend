# Heart of News Backend - Refactoring Plan

## Executive Summary

This document outlines a comprehensive refactoring plan for the Heart of News backend application. The analysis identified significant architectural issues, security vulnerabilities, code duplication, and inconsistent patterns across the codebase. This plan prioritizes critical security fixes and establishes a foundation for maintainable, scalable code.

## Current Architecture Assessment

### Project Structure
- **Framework**: FastAPI with SQLAlchemy
- **Architecture**: Layered (API → Services → CRUD → Models)
- **Dependencies**: 65+ packages including AI/ML, scraping, and monitoring tools
- **Database**: PostgreSQL with Alembic migrations
- **Caching**: Redis with custom middleware
- **Monitoring**: Prometheus, Sentry, APM tools

### Critical Issues Identified

#### 1. Security Vulnerabilities (CRITICAL)
- **SQL Injection**: Raw SQL queries in `health.py:126-128`
- **Missing Authentication**: Task endpoints lack authentication
- **Missing Authorization**: Inconsistent permission checking
- **Input Validation**: Missing sanitization across endpoints

#### 2. Architectural Problems (HIGH)
- **Global Instances**: Services use singleton pattern inappropriately
- **Missing Dependency Injection**: Hardcoded dependencies throughout
- **Service Boundary Violations**: Mixed responsibilities in classes
- **No Service Interfaces**: Tight coupling between components

#### 3. Code Quality Issues (MEDIUM)
- **Massive Code Duplication**: 30%+ duplicate code across services
- **Inconsistent Error Handling**: 5 different error handling patterns
- **Missing Abstractions**: No common interfaces for similar functionality
- **Performance Issues**: Memory leaks and inefficient operations

## Refactoring Plan

### Phase 1: Critical Security & Stability (Week 1-2)

#### 1.1 Fix Security Vulnerabilities
```
Priority: CRITICAL
Effort: 3 days
Files: health.py, tasks.py, auth.py
```

**Tasks:**
- [ ] Replace raw SQL with parameterized queries (`health.py:126-128`)
- [ ] Add authentication to all task endpoints (`tasks.py`)
- [ ] Fix missing imports in auth module (`auth.py:363,376`)
- [ ] Implement input sanitization for all user inputs
- [ ] Add CSRF protection headers

**Acceptance Criteria:**
- All endpoints require authentication where appropriate
- No raw SQL queries remain
- All user inputs are validated and sanitized
- Security scan passes without critical issues

#### 1.2 Standardize Error Handling
```
Priority: HIGH
Effort: 2 days
Files: All endpoint files
```

**Create Common Utilities:**
```python
# app/core/exceptions.py
class BusinessLogicError(Exception): ...
class ValidationError(Exception): ...
class NotFoundError(Exception): ...

# app/core/responses.py
def standard_response(data, message=None, meta=None): ...
def error_response(error_type, message, details=None): ...

# app/core/dependencies.py
def get_entity_or_404(crud_model, entity_id, entity_name): ...
```

**Tasks:**
- [ ] Create standardized exception classes
- [ ] Implement common response formatters
- [ ] Create entity retrieval helper
- [ ] Update all endpoints to use standard patterns
- [ ] Add consistent logging across all errors

### Phase 2: Dependency Injection & Service Architecture (Week 3-4)

#### 2.1 Implement Dependency Injection Container
```
Priority: HIGH
Effort: 5 days
Files: New DI system, all service files
```

**Create Service Container:**
```python
# app/core/container.py
class ServiceContainer:
    def register_singleton(self, interface, implementation): ...
    def register_transient(self, interface, implementation): ...
    def resolve(self, interface): ...

# app/core/interfaces.py
class AnalysisService(Protocol): ...
class ScrapingService(Protocol): ...
class NotificationService(Protocol): ...
```

**Tasks:**
- [ ] Design service interfaces/protocols
- [ ] Implement DI container
- [ ] Convert all services to use DI
- [ ] Remove global service instances
- [ ] Update FastAPI dependencies to use container

#### 2.2 Refactor Service Layer
```
Priority: HIGH
Effort: 4 days
Files: All service files
```

**Service Boundaries:**
- **AI Services**: Bias detection, propaganda analysis, content analysis
- **Content Services**: Scraping, parsing, verification
- **Communication Services**: Telegram, email, notifications
- **Data Services**: CRUD operations, caching, search

**Tasks:**
- [ ] Extract common utilities (HTML cleaning, date parsing, etc.)
- [ ] Implement service interfaces
- [ ] Separate concerns within existing services
- [ ] Add proper async/await patterns
- [ ] Implement connection pooling for HTTP clients

### Phase 3: Code Deduplication & Performance (Week 5-6)

#### 3.1 Eliminate Code Duplication
```
Priority: MEDIUM
Effort: 4 days
Files: scraper/, ai/, telegram services
```

**Duplicate Code Areas:**
- HTML cleaning (RssScraper, WebScraper)
- Date parsing (multiple scrapers)
- Markdown escaping (Telegram services)
- Telegram API calls (both language services)
- Entity retrieval patterns (all endpoints)

**Create Shared Utilities:**
```python
# app/utils/text_processing.py
class HtmlCleaner: ...
class DateParser: ...
class MarkdownFormatter: ...

# app/utils/http_client.py
class HttpClientManager: ...

# app/utils/telegram_client.py
class TelegramApiClient: ...
```

**Tasks:**
- [ ] Extract HTML processing utilities
- [ ] Create shared date parsing functions
- [ ] Implement common Telegram API client
- [ ] Consolidate validation patterns
- [ ] Remove all duplicate code blocks

#### 3.2 Performance Optimizations
```
Priority: MEDIUM
Effort: 3 days
Files: scraper/, core/cache.py, services/
```

**Performance Issues:**
- Memory leaks in scraper URL tracking
- Regex compilation on every call
- No connection pooling
- Inefficient database queries
- Missing query optimization

**Tasks:**
- [ ] Implement connection pooling for all HTTP clients
- [ ] Add proper caching for expensive operations
- [ ] Optimize database queries with indexes
- [ ] Fix memory leaks in scrapers
- [ ] Add rate limiting for external APIs
- [ ] Implement request timeouts

### Phase 4: API Consistency & Documentation (Week 7-8)

#### 4.1 Standardize API Endpoints
```
Priority: MEDIUM
Effort: 3 days
Files: All endpoint files
```

**Consistency Issues:**
- Different parameter naming conventions
- Inconsistent response formats
- Missing pagination metadata
- Different error message formats

**Tasks:**
- [ ] Standardize parameter definitions
- [ ] Implement consistent response wrappers
- [ ] Add pagination metadata to all list endpoints
- [ ] Standardize error message formats
- [ ] Add request/response validation
- [ ] Implement consistent filtering patterns

#### 4.2 Database Model Improvements
```
Priority: MEDIUM
Effort: 2 days
Files: models/, schemas/, crud/
```

**Model Issues:**
- Missing relationships
- Inconsistent field types
- Missing indexes for performance
- No soft delete patterns

**Tasks:**
- [ ] Add missing foreign key relationships
- [ ] Implement soft delete for user-facing entities
- [ ] Add database indexes for common queries
- [ ] Standardize UUID vs integer ID usage
- [ ] Add audit fields (created_by, updated_by)

### Phase 5: Testing & Monitoring Improvements (Week 9-10)

#### 5.1 Expand Test Coverage
```
Priority: MEDIUM
Effort: 4 days
Files: tests/, new test files
```

**Current Test Gaps:**
- No integration tests for services
- Missing error case testing
- No performance tests
- Limited API endpoint coverage

**Tasks:**
- [ ] Add service layer unit tests
- [ ] Implement integration tests for key workflows
- [ ] Add error handling test cases
- [ ] Create performance benchmarks
- [ ] Add security test cases

#### 5.2 Enhanced Monitoring
```
Priority: LOW
Effort: 2 days
Files: core/monitoring.py, new monitoring files
```

**Tasks:**
- [ ] Add business metrics tracking
- [ ] Implement distributed tracing
- [ ] Add custom dashboards for key operations
- [ ] Set up alerting for critical errors
- [ ] Add performance monitoring for slow operations

## Implementation Strategy

### Development Approach
1. **Branch Strategy**: Create feature branches for each phase
2. **Testing**: All changes must include tests
3. **Code Review**: Mandatory review for architectural changes
4. **Documentation**: Update documentation as changes are made
5. **Backward Compatibility**: Maintain API compatibility during transition

### Risk Mitigation
- **Database Migrations**: All schema changes through Alembic
- **Feature Flags**: Use feature flags for major service changes
- **Gradual Rollout**: Phase rollouts with monitoring
- **Rollback Plan**: Maintain ability to rollback each phase

### Success Metrics
- **Security**: Zero critical security vulnerabilities
- **Performance**: 50% reduction in response times
- **Code Quality**: 80%+ test coverage, <5% code duplication
- **Maintainability**: 90% reduction in duplicate code patterns

## Resource Requirements

### Development Team
- **Senior Backend Developer**: Architecture and DI implementation
- **Security Engineer**: Security fixes and validation
- **DevOps Engineer**: Monitoring and deployment
- **QA Engineer**: Testing and validation

### Timeline
- **Total Duration**: 10 weeks
- **Critical Path**: Security fixes → DI implementation → Code deduplication
- **Parallel Work**: Documentation, testing, monitoring improvements

## Post-Refactoring Maintenance

### Code Quality Standards
- **Code Reviews**: Mandatory for all changes
- **Static Analysis**: Automated code quality checks
- **Security Scanning**: Regular vulnerability assessments
- **Performance Monitoring**: Continuous performance tracking

### Architectural Guidelines
- **Service Design**: All new services must implement interfaces
- **Error Handling**: Use standardized error patterns
- **Testing**: Minimum 80% test coverage for new code
- **Documentation**: API documentation must be kept current

## Conclusion

This refactoring plan addresses critical security issues while establishing a foundation for scalable, maintainable code. The phased approach ensures business continuity while systematically improving code quality, performance, and security. Success depends on team commitment to new architectural patterns and quality standards.

## Appendix

### File-Specific Changes

#### High Priority Files
- `app/api/v1/endpoints/health.py` - SQL injection fix
- `app/api/v1/endpoints/tasks.py` - Add authentication
- `app/api/v1/endpoints/auth.py` - Fix missing imports
- `app/services/scraper/manager.py` - Implement DI
- `app/services/ai/bias_detector.py` - Remove global instance

#### Code Duplication Targets
- `app/services/scraper/rss_scraper.py:306-344` and `app/services/scraper/web_scraper.py:392-430`
- `app/services/telegram_service.py:143-154` and `app/services/telegram_service_ru.py:208-219`
- All endpoint entity retrieval patterns

#### Performance Critical Areas
- `app/services/scraper/web_scraper.py:64` - URL tracking memory leak
- `app/core/cache.py` - Response caching optimization
- `app/main.py:150-240` - Middleware performance