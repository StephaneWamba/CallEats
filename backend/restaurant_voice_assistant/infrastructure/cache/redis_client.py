"""Redis client management for distributed caching.

This module provides a Redis client with connection pooling for distributed
caching across multiple server instances. Falls back to None if Redis is not configured.

Key Features:
    - Connection pool for better performance
    - Singleton pool instance
    - Graceful fallback if Redis unavailable
    - Automatic reconnection handling
    - Configurable pool size

Usage:
    from restaurant_voice_assistant.infrastructure.cache.redis_client import get_redis_client
    
    redis_client = get_redis_client()
    if redis_client:
        # Use Redis
        redis_client.set("key", "value", ex=60)
    else:
        # Fallback to in-memory cache
        pass
"""
import os
import redis
from redis.connection import ConnectionPool
from typing import Optional
from restaurant_voice_assistant.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

_redis_pool: Optional[ConnectionPool] = None
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """Get Redis client with connection pooling.

    Uses a connection pool for better performance and scalability.
    Pool size: 10 connections (configurable via REDIS_MAX_CONNECTIONS).

    Returns:
        Redis client instance if REDIS_URL is configured, None otherwise
    """
    global _redis_pool, _redis_client

    if _redis_client is not None:
        return _redis_client

    settings = get_settings()

    # Check for Railway's REDIS_URL first, then fall back to settings
    redis_url = os.environ.get("REDIS_URL") or settings.redis_url

    if not redis_url:
        logger.info("Redis URL not configured, using in-memory cache")
        return None

    try:
        # Get max connections from environment or use default
        max_connections = int(os.environ.get("REDIS_MAX_CONNECTIONS", "10"))

        # Create connection pool
        _redis_pool = ConnectionPool.from_url(
            redis_url,
            max_connections=max_connections,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
            health_check_interval=30
        )

        # Create client from pool
        _redis_client = redis.Redis(connection_pool=_redis_pool)

        # Test connection
        _redis_client.ping()
        logger.info(
            f"Redis connection pool established successfully (max_connections={max_connections})"
        )
        return _redis_client
    except Exception as e:
        logger.warning(
            f"Failed to connect to Redis: {e}. Falling back to in-memory cache")
        return None


def close_redis_connection() -> None:
    """Close Redis connection pool (useful for cleanup)."""
    global _redis_client, _redis_pool

    if _redis_client:
        try:
            _redis_client.close()
            logger.info("Redis client closed")
        except Exception as e:
            logger.warning(f"Error closing Redis client: {e}")
        finally:
            _redis_client = None

    if _redis_pool:
        try:
            _redis_pool.disconnect()
            logger.info("Redis connection pool closed")
        except Exception as e:
            logger.warning(f"Error closing Redis connection pool: {e}")
        finally:
            _redis_pool = None
