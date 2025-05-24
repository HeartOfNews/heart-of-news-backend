"""
Simple configuration for local demo without Docker
"""

import os
from typing import List

class Settings:
    # Base
    API_V1_STR: str = "/api/v1"
    VERSION: str = "0.1.0"
    PROJECT_NAME: str = "Heart of News"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Security
    SECRET_KEY: str = "development_secret_key_change_in_production_2024"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ALGORITHM: str = "HS256"
    JWT_SECRET_KEY: str = "jwt_secret_key_development_2024"
    
    # Database (SQLite for demo)
    DATABASE_URL: str = "sqlite:///./heartofnews.db"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
    
    # Demo mode settings
    DEMO_MODE: bool = True
    SKIP_REDIS: bool = True
    SKIP_ELASTICSEARCH: bool = True
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File uploads
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 10
    
    # OpenAI (demo key)
    OPENAI_API_KEY: str = "demo-key-for-testing"

# Create settings instance
settings = Settings()