"""
SQLAlchemy Session Management.

Architectural layer:
    Infrastructure (Database).

Purpose:
    Provides the database engine and session factory configuration based on
    environment settings. Includes a FastAPI dependency generator for session lifecycle.

Data flow:
    Creates a thread-safe connection pool. Yields a scoped session per request
    and ensures the session is safely closed after the request completes.

Key dependencies:
    - sqlalchemy
    - backend.config.settings

Related modules:
    - backend.infrastructure.database.models
    - backend.api.dependencies
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config.settings import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    FastAPI dependency that provides a database session and handles teardown.
    
    Yields:
        A SQLAlchemy Session instance.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
