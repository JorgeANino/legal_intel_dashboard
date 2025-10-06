"""
Rate limiting middleware to prevent abuse
"""
# Standard library imports
import time

# Third-party imports
from fastapi import HTTPException, Request, status
from redis import asyncio as aioredis

# Local application imports
from app.core.config import settings


class RateLimiter:
    """
    Token bucket rate limiter using Redis for distributed rate limiting.

    Implements a sliding window rate limiter that tracks request counts
    per time window using Redis for persistence across instances.
    """

    def __init__(self, redis_url: str) -> None:
        """
        Initialize the rate limiter with Redis connection.

        Args:
            redis_url: Redis connection URL (e.g., 'redis://localhost:6379/0').
        """
        self.redis = aioredis.from_url(redis_url, decode_responses=True)

    async def check_rate_limit(
        self, key: str, max_requests: int = 100, window_seconds: int = 60
    ) -> bool:
        """
        Check if request should be rate limited

        Args:
            key: Unique identifier (user_id or IP)
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limited
        """
        current_time = int(time.time())
        window_key = f"rate_limit:{key}:{current_time // window_seconds}"

        count = await self.redis.incr(window_key)

        if count == 1:
            await self.redis.expire(window_key, window_seconds)

        return count <= max_requests


rate_limiter = RateLimiter(settings.REDIS_URL)


async def rate_limit_dependency(request: Request) -> None:
    """
    FastAPI dependency for endpoint-specific rate limiting.

    Applies different rate limits based on the endpoint being accessed:
    - /upload: 10 requests per minute
    - /query: 50 requests per minute
    - Others: 100 requests per minute

    Args:
        request: FastAPI Request object containing client information.

    Raises:
        HTTPException: 429 Too Many Requests if rate limit is exceeded.

    Returns:
        None

    Example:
        >>> @router.get("/api/endpoint")
        >>> async def endpoint(_: None = Depends(rate_limit_dependency)):
        >>>     return {"status": "ok"}
    """
    # Use user_id if authenticated, otherwise IP
    client_ip = request.client.host if request.client else "unknown"
    identifier = f"ip:{client_ip}"

    # Different limits for different endpoints
    if "/upload" in request.url.path:
        allowed = await rate_limiter.check_rate_limit(
            identifier, max_requests=10, window_seconds=60
        )
    elif "/query" in request.url.path:
        allowed = await rate_limiter.check_rate_limit(
            identifier, max_requests=50, window_seconds=60
        )
    else:
        allowed = await rate_limiter.check_rate_limit(
            identifier, max_requests=100, window_seconds=60
        )

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later.",
        )
