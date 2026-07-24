from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
import os

class BaseAppSettings(BaseSettings):
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
    ENVIRONMENT: str = "development"
    LANGCHAIN_TRACING_V2: str = "true"

class TestingSettings(BaseAppSettings):
    ENVIRONMENT: str = "testing"
    DATABASE_URL: str = "sqlite:///:memory:"
    CHROMADB_DIR: str = "./test_chroma_db"

class ProductionSettings(BaseAppSettings):
    ENVIRONMENT: str = "production"
    # Production overrides go here

def get_settings() -> BaseAppSettings:
    env = os.getenv("ENVIRONMENT", "development").lower()
    if env == "testing":
        return TestingSettings()
    elif env == "production":
        return ProductionSettings()
    return DevelopmentSettings()

settings = get_settings()
