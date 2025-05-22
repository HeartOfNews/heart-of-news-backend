"""
Configuration settings for the Heart of News backend
"""

import secrets
from typing import List, Optional, Union, Literal

from pydantic import AnyHttpUrl, PostgresDsn, validator, Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Base
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    PROJECT_NAME: str = "Heart of News"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    TESTING: bool = False
    
    # Security
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    JWT_ALGORITHM: str = "HS256"
    
    # Authentication
    VERIFY_EMAIL: bool = True
    RESET_PASSWORD_TOKEN_EXPIRE_HOURS: int = 4
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 24
    AUTH_MAX_FAILED_ATTEMPTS: int = 5
    AUTH_LOCKOUT_DURATION_MINUTES: int = 15
    FRONTEND_URL: str = "http://localhost:3000"
    
    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "heart_of_news"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict[str, any]) -> any:
        if isinstance(v, str):
            return v
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    
    # Elasticsearch
    ELASTICSEARCH_HOST: str = "localhost"
    ELASTICSEARCH_PORT: int = 9200
    
    # S3 / Storage
    STORAGE_BUCKET_NAME: str = "heart-of-news-media"
    
    # Scraper settings
    SCRAPER_USER_AGENT: str = "HeartOfNewsBot/1.0"
    SCRAPER_REQUEST_DELAY: float = 1.0  # in seconds
    
    # Monitoring and Logging
    LOG_LEVEL: str = "INFO"
    HTTPX_LOG_LEVEL: str = "WARNING"
    UVICORN_LOG_LEVEL: str = "WARNING"
    SQLALCHEMY_LOG_LEVEL: str = "WARNING"
    ENABLE_METRICS: bool = True
    PROMETHEUS_MULTIPROC_DIR: str = "/tmp/prometheus_multiproc"
    SENTRY_DSN: Optional[str] = None
    ENABLE_PERFORMANCE_TRACKING: bool = True
    METRICS_EXPORT_INTERVAL: int = 15  # seconds
    
    # Application Performance Monitoring
    ELASTIC_APM_SERVER_URL: Optional[str] = None
    ELASTIC_APM_SERVICE_NAME: str = "heart-of-news-backend"
    DATADOG_API_KEY: Optional[str] = None
    DATADOG_APP_KEY: Optional[str] = None
    
    # Health checks
    HEALTH_CHECK_INTERVAL: int = 60  # seconds
    
    class Config:
        case_sensitive = True
        env_file = ".env"

# Create settings instance
settings = Settings()