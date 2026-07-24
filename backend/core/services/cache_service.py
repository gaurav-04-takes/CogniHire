import time
from typing import Any, Optional, Dict
from backend.core.services.logging_service import logger
from backend.config.settings import settings

class CacheService:
    def __init__(self):
        self._memory_cache: Dict[str, dict] = {}
        self.cache_type = settings.CACHE_TYPE
        
    def get(self, key: str) -> Optional[Any]:
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
        if self.cache_type == "memory":
            expires_at = time.time() + ttl_seconds if ttl_seconds else None
            self._memory_cache[key] = {
                "value": value,
                "expires_at": expires_at
            }
            logger.debug(f"Cache SET for key: {key}")

    def invalidate(self, key: str):
        if self.cache_type == "memory" and key in self._memory_cache:
            del self._memory_cache[key]
            
    def clear(self):
        if self.cache_type == "memory":
            self._memory_cache.clear()

# Singleton instance
cache_service = CacheService()
