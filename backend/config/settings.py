"""
Configuration Settings.

Architectural layer:
    Infrastructure (Configuration).

Purpose:
    Defines type-safe configuration settings for the application using Pydantic.
    Handles environment variables and `.env` file loading. Provides different
    configurations based on the environment (development, testing, production).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class BaseAppSettings(BaseSettings):
    """
    Base configuration schema and default values.
    Pydantic automatically overrides these with matching environment variables.
    """
    # App Config
    APP_NAME: str = "CogniHire"
    APP_VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development" # development, testing, production
    
    # LLM Config
    LLM_PROVIDER: str = "gemini" # gemini, openai
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-pro"
    GEMINI_TEMPERATURE: float = 0.0
    GEMINI_MAX_TOKENS: int = 8192
    OPENAI_API_KEY: Optional[str] = None
    
    # Vector DB Config
    CHROMADB_DIR: str = "./chroma_db"
    
    # Relational DB Config
    DATABASE_URL: str = "sqlite:///./cognihire.db"
    
    # Observability & Evaluation
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "CogniHire"
    
    # Caching Config
    CACHE_TYPE: str = "memory" # memory, redis (future)
    
    # Security
    RATE_LIMIT: str = "100/minute"
    MAX_UPLOAD_SIZE_MB: int = 10
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="allow")

class DevelopmentSettings(BaseAppSettings):
    """Configuration overrides for the development environment."""
    ENVIRONMENT: str = "development"
    LANGCHAIN_TRACING_V2: str = "true"

class TestingSettings(BaseAppSettings):
    """Configuration overrides for the testing environment (uses in-memory DBs)."""
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite:///:memory:"
    CHROMADB_DIR: str = "./test_chroma_db"

class ProductionSettings(BaseAppSettings):
    """Configuration overrides for the production environment."""
    ENVIRONMENT: str = "production"
    # Production overrides go here

def get_settings() -> BaseAppSettings:
    """
    Factory function that inspects the ENVIRONMENT variable and returns
    the appropriate settings instance.
    """
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    return DevelopmentSettings()

# Global singleton settings object
settings = get_settings()
