"""
Redis-based caching for expensive operations
"""
# Standard library imports
import hashlib
import json
from typing import Any

# Local application imports
from app.core.config import settings
# Third-party imports
from redis import asyncio as aioredis


class CacheService:
    """
    Redis-based caching service for storing expensive operation results.

    Provides methods for getting, setting, and clearing cached values with
    automatic TTL (time-to-live) management and JSON serialization.

    Attributes:
        redis: Async Redis client instance.
        default_ttl: Default time-to-live in seconds (300s = 5 minutes).
    """

    def __init__(self, redis_url: str) -> None:
        """
        Initialize cache service with Redis connection.

        Args:
            redis_url: Redis connection URL (e.g., 'redis://localhost:6379/0').
        """
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes

    def _generate_key(self, prefix: str, **kwargs: Any) -> str:
        """
        Generate a deterministic cache key from parameters.

        Args:
            prefix: Namespace prefix for the cache key.
            **kwargs: Parameters to include in the key generation.

        Returns:
            MD5-hashed cache key string in format 'prefix:hash'.

        Example:
            >>> service = CacheService(redis_url)
            >>> key = service._generate_key("user", user_id=123, type="profile")
            >>> print(key)  # user:abc123def456...
        """
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"

    async def get(self, key: str) -> Any | None:
        """
        Retrieve cached value by key.

        Args:
            key: Cache key to retrieve.

        Returns:
            Deserialized cached value if exists, None otherwise.

        Example:
            >>> value = await cache_service.get("user:123")
            >>> if value:
            >>>     print(f"Cache hit: {value}")
        """
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """
        Store value in cache with TTL.

        Args:
            key: Cache key to set.
            value: Value to cache (must be JSON-serializable).
            ttl: Time-to-live in seconds. Defaults to 300s if not specified.

        Returns:
            None

        Example:
            >>> await cache_service.set("user:123", {"name": "John"}, ttl=600)
        """
        ttl = ttl or self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str) -> None:
        """
        Delete cached value by key.

        Args:
            key: Cache key to delete.

        Returns:
            None

        Example:
            >>> await cache_service.delete("user:123")
        """
        await self.redis.delete(key)

    async def clear_pattern(self, pattern: str) -> None:
        """
        Clear all cache keys matching a pattern.

        Args:
            pattern: Redis glob pattern to match keys (e.g., 'user:*').

        Returns:
            None

        Note:
            Uses SCAN to iterate over keys for memory efficiency.
            Pattern syntax follows Redis glob-style patterns:
            - '*' matches any characters
            - '?' matches a single character
            - '[abc]' matches a, b, or c

        Example:
            >>> await cache_service.clear_pattern("dashboard:*")
        """
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)


cache_service = CacheService(settings.REDIS_URL)
