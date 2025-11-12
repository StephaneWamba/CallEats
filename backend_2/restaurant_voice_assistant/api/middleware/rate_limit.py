"""Rate limiting middleware for API protection.

This module provides rate limiting to prevent API abuse and protect against
DDoS attacks. Uses slowapi for FastAPI integration.

Key Features:
    - Per-endpoint rate limits
    - Per-IP rate limiting
    - Per-user rate limiting for authenticated requests
    - Configurable limits via environment variables
    - Redis-backed storage for distributed systems (with memory fallback)

Rate Limits:
    - Default: 100 requests per minute per IP/user
    - Authenticated users: 200 requests per minute
    - Health endpoint: 60 requests per minute (higher limit)
    - Embedding generation: 10 requests per minute (expensive operation)

Storage:
    - Uses Redis if REDIS_URL is configured (for distributed systems)
    - Falls back to in-memory storage if Redis is unavailable
    - Memory storage is suitable for single-instance deployments

Usage:
    Middleware is automatically registered in main.py.
    Apply limits to endpoints using @limiter.limit() decorator.
"""
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi import Request
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.infrastructure.cache.redis_client import get_redis_client
import logging
import os

logger = logging.getLogger(__name__)

settings = get_settings()


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key based on authentication status.

    Uses IP address for unauthenticated requests, user_id for authenticated.
    This allows higher limits for authenticated users.
    """
    # Check if user is authenticated
    user = getattr(request.state, "user", None)
    if user and user.get("user_id"):
        return f"user:{user['user_id']}"

    # Fallback to IP address
    return get_remote_address(request)


def _get_storage_uri() -> str:
    """Get storage URI for rate limiter.

    Returns Redis URI if available, otherwise falls back to memory.
    """
    # Check for Redis URL in environment or settings
    redis_url = os.environ.get("REDIS_URL") or settings.redis_url

    if redis_url:
        # Convert Redis URL to slowapi format
        # slowapi expects: redis://host:port/db or redis://:password@host:port/db
        try:
            # Test Redis connection
            redis_client = get_redis_client()
            if redis_client:
                logger.info("Using Redis for rate limiting storage")
                return redis_url
            else:
                logger.warning(
                    "Redis URL configured but connection failed, falling back to memory")
        except Exception as e:
            logger.warning(
                f"Redis connection test failed: {e}, falling back to memory")

    logger.info(
        "Using in-memory storage for rate limiting (single instance only)")
    return "memory://"


# Initialize rate limiter with custom key function and storage
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=["100/minute"],
    storage_uri=_get_storage_uri(),
    headers_enabled=True
)


def get_rate_limiter() -> Limiter:
    """Get rate limiter instance."""
    return limiter
