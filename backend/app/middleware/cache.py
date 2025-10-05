"""
Redis-based caching for expensive operations
"""
import json
import hashlib
from typing import Optional, Any
from redis import asyncio as aioredis
from app.core.config import settings


class CacheService:
    """Redis caching service"""
    
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url, decode_responses=True)
        self.default_ttl = 300  # 5 minutes
    
    def _generate_key(self, prefix: str, **kwargs) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(kwargs, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()
        return f"{prefix}:{params_hash}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get cached value"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set cached value with TTL"""
        ttl = ttl or self.default_ttl
        await self.redis.setex(key, ttl, json.dumps(value))
    
    async def delete(self, key: str) -> None:
        """Delete cached value"""
        await self.redis.delete(key)
    
    async def clear_pattern(self, pattern: str) -> None:
        """Clear all keys matching pattern"""
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await self.redis.delete(*keys)


cache_service = CacheService(settings.REDIS_URL)

