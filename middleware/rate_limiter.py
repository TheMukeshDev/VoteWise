"""
Rate Limiting Middleware for VoteWise AI

Provides distributed rate limiting using Redis.
Falls back to in-memory if Redis is unavailable.
"""

import logging
import time
from functools import wraps
from typing import Callable, Optional

from flask import jsonify, request

from config import Config

logger = logging.getLogger(__name__)

# In-memory fallback
_rate_limit_store: dict = {}


class RateLimiter:
    """Rate limiter with Redis backend and in-memory fallback."""

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url or Config.REDIS_URL
        self._redis_client = None
        self._use_redis = False

        if self.redis_url:
            try:
                import redis

                self._redis_client = redis.from_url(self.redis_url)
                self._use_redis = True
                logger.info("Rate limiter: Using Redis backend")
            except Exception as e:
                logger.warning(f"Rate limiter: Redis unavailable, using in-memory: {e}")
                self._use_redis = False

    def check_limit(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """Check if key is within rate limit."""
        now = time.time()

        if self._use_redis and self._redis_client:
            try:
                pipe = self._redis_client.pipeline()
                key_prefix = f"rate_limit:{key}"

                pipe.zremrangebyscore(key_prefix, 0, now - window_seconds)
                pipe.zadd(key_prefix, {str(now): now})
                pipe.zcard(key_prefix)
                pipe.expire(key_prefix, window_seconds)

                results = pipe.execute()
                count = results[2]

                return count <= max_requests
            except Exception as e:
                logger.warning(f"Redis rate limit check failed: {e}")

        # Fallback to in-memory
        return self._check_memory(key, max_requests, window_seconds)

    def _check_memory(self, key: str, max_requests: int, window_seconds: int) -> bool:
        """In-memory rate limit check."""
        now = time.time()

        if key not in _rate_limit_store:
            _rate_limit_store[key] = []

        # Clean old entries
        _rate_limit_store[key] = [
            ts for ts in _rate_limit_store[key] if now - ts < window_seconds
        ]

        if len(_rate_limit_store[key]) >= max_requests:
            return False

        _rate_limit_store[key].append(now)
        return True


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(max_requests: int = 30, window_seconds: int = 60):
    """
    Rate limiting decorator.

    Usage:
        @rate_limit(max_requests=10, window_seconds=60)
        def my_endpoint():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            key = f"ip:{request.remote_addr}:{request.endpoint}"

            if not _rate_limiter.check_limit(key, max_requests, window_seconds):
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Too many requests. Please try again later.",
                            "error": "rate_limit_exceeded",
                            "retry_after": window_seconds,
                        }
                    ),
                    429,
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    return _rate_limiter
