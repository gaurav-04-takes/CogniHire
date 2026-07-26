"""
Application caching service.

Architectural layer:
    Application services.

Purpose:
    Provides a centralized caching abstraction for the backend. Currently
    supports in-memory caching to avoid redundant heavy operations like
    repeated file processing or embedding.

Data flow:
    Application use cases and infrastructure services call the CacheService
    to store and retrieve temporary objects by string keys.

Key dependencies:
    - Settings (for cache configuration).
    - LoggingService.

Side effects:
    - Modifies the global `_memory_cache` dictionary if configured for memory.

Related modules:
    - backend.config.settings
"""
import time
from typing import Any, Optional, Dict
from backend.core.services.logging_service import logger
from backend.config.settings import settings

class CacheService:
    """
    Centralized caching service.
    
    Manages transient data to improve performance. The memory cache 
    exists only in the current Python process. Entries are not shared 
    between Uvicorn workers and are lost when the backend restarts.
    """
    def __init__(self):
        self._memory_cache: Dict[str, dict] = {}
        self.cache_type = settings.CACHE_TYPE
        
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: The unique string identifier for the cached item.
            
        Returns:
            The cached value if present and not expired, otherwise None.
        """
        if self.cache_type == "memory":
            item = self._memory_cache.get(key)
            if item:
                if item["expires_at"] and time.time() > item["expires_at"]:
                    del self._memory_cache[key]
                    return None
                logger.debug(f"Cache HIT for key: {key}")
                return item["value"]
            logger.debug(f"Cache MISS for key: {key}")
            return None
        return None

    def set(self, key: str, value: Any, ttl_seconds: Optional[int] = 3600):
        """
        Store a value in the cache.
        
        Args:
            key: The unique string identifier for the cached item.
            value: The data to store.
            ttl_seconds: Time-to-live in seconds. Defaults to 3600 (1 hour).
        """
        if self.cache_type == "memory":
            expires_at = time.time() + ttl_seconds if ttl_seconds else None
            self._memory_cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
            logger.debug(f"Cache SET for key: {key}")

    def invalidate(self, key: str):
        """
        Remove a specific item from the cache.
        
        Args:
            key: The unique string identifier to remove.
        """
        if self.cache_type == "memory" and key in self._memory_cache:
            del self._memory_cache[key]
            
    def clear(self):
        """Clear all entries from the cache."""
        if self.cache_type == "memory":
            self._memory_cache.clear()

# Singleton instance
cache_service = CacheService()
