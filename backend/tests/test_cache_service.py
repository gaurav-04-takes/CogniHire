import pytest
import time
from backend.core.services.cache_service import CacheService

def test_cache_set_get():
    cache = CacheService()
    cache.cache_type = "memory"
    
    cache.set("key1", "value1")
    assert cache.get("key1") == "value1"

def test_cache_ttl():
    cache = CacheService()
    cache.cache_type = "memory"
    
    cache.set("key_temp", "temp_val", ttl_seconds=1)
    assert cache.get("key_temp") == "temp_val"
    time.sleep(1.1)
    assert cache.get("key_temp") is None

def test_cache_invalidate():
    cache = CacheService()
    cache.cache_type = "memory"
    
    cache.set("key2", "value2")
    cache.invalidate("key2")
    assert cache.get("key2") is None

def test_cache_clear():
    cache = CacheService()
    cache.cache_type = "memory"
    
    cache.set("key3", "val3")
    cache.set("key4", "val4")
    cache.clear()
    assert cache.get("key3") is None
    assert cache.get("key4") is None
