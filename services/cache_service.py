"""
Redis Caching Service for VoteWise AI

Provides distributed caching using Redis.
Falls back to in-memory if Redis is unavailable.
"""

import json
import logging
from functools import wraps
from typing import Any, Callable, Optional

from config import Config

logger = logging.getLogger(__name__)


class CacheService:
    """Caching service with Redis backend and in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url: Optional[str] = redis_url or Config.REDIS_URL
        self._redis_client: Any = None
        self._use_redis: bool = False

        if self.redis_url:
            try:
                import redis

                self._redis_client = redis.from_url(self.redis_url)
                self._use_redis = True
                logger.info("Cache: Using Redis backend")
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Cache: Redis unavailable, using in-memory: %s", e)
                self._use_redis = False

        # In-memory cache fallback
        self._memory_cache: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self._use_redis and self._redis_client:
            try:
                value: Optional[str] = self._redis_client.get(key)
                return json.loads(value) if value else None
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Redis cache get failed: %s", e)

        return self._memory_cache.get(key)

    def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """Set value in cache with TTL in seconds."""
        if self._use_redis and self._redis_client:
            try:
                serialized: str = json.dumps(value)
                self._redis_client.setex(key, ttl, serialized)
                return True
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Redis cache set failed: %s", e)

        self._memory_cache[key] = value
        return True

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if self._use_redis and self._redis_client:
            try:
                self._redis_client.delete(key)
                return True
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Redis cache delete failed: %s", e)

        self._memory_cache.pop(key, None)
        return True

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        count: int = 0
        if self._use_redis and self._redis_client:
            try:
                keys: Any = self._redis_client.keys(f"cache:{pattern}:*")
                count = len(keys)
                for key in keys:
                    self._redis_client.delete(key)
                return count
            except (RuntimeError, ConnectionError, ValueError) as e:
                logger.warning("Redis cache clear failed: %s", e)

        # In-memory fallback
        keys_to_delete: list[str] = [k for k in self._memory_cache if k.startswith(f"cache:{pattern}:")]
        for key in keys_to_delete:
            del self._memory_cache[key]
        return len(keys_to_delete)


# Global cache instance
_cache_service = CacheService()


def cache_get(key: str) -> Optional[Any]:
    """Get value from cache."""
    return _cache_service.get(key)


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """Set value in cache."""
    return _cache_service.set(key, value, ttl)


def cache_delete(key: str) -> bool:
    """Delete key from cache."""
    return _cache_service.delete(key)


def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Caching decorator.

    Usage:
        @cached(ttl=60, key_func=lambda args: f"user:{args[0]}")
        def get_user(user_id):
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key_func(*args, **kwargs) if key_func else f"cache:{f.__name__}:{args}"

            cached_value = cache_get(cache_key)
            if cached_value is not None:
                return cached_value

            result = f(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result

        return decorated_function

    return decorator


def get_cache_service() -> CacheService:
    """Get the global cache service instance."""
    return _cache_service


# Backward compatibility aliases
get_cached = cache_get
set_cached = cache_set
delete_cached = cache_delete

CACHE_KEYS = {
    "faqs": "faqs",
    "reminders": "reminders",
    "analytics": "analytics",
    "user": "user",
    "election": "election",
}

TTL_VALUES = {
    "faqs": 3600,
    "reminders": 3600,
    "analytics": 3600,
    "user": 3600,
    "election": 3600,
}
