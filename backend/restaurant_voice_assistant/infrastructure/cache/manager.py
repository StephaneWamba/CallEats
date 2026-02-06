"""Distributed cache management for search results and call data.

This module provides caching functionality using Redis (preferred) or in-memory
fallback. Supports distributed caching across multiple server instances.

This module provides caching functionality for:
    - Vector search results (embeddings queries)
    - Call ID to phone number mappings

Key Features:
    - Redis-based distributed caching (if REDIS_URL configured)
    - In-memory fallback for development
    - TTL-based cache expiration (configurable via CACHE_TTL_SECONDS)
    - Automatic cache invalidation on data changes
    - Separate cache for call phone mappings (1 hour TTL)
    - Restaurant-scoped cache keys for multi-tenancy

Cache Keys:
    - Search results: "cache:{restaurant_id}:{category}:{query}"
    - Call mappings: "call_phone:{call_id}"

Performance:
    - Reduces OpenAI API calls by caching embedding search results
    - Speeds up repeated queries for the same restaurant/category
    - Shared cache across multiple server instances (with Redis)
    - Persistent cache survives application restarts (with Redis)

Usage:
    from restaurant_voice_assistant.infrastructure.cache.manager import (
        get_cached_result,
        set_cached_result,
        clear_cache
    )
    
    # Check cache
    cached = get_cached_result(restaurant_id, query, category)
    if cached:
        return cached
    
    # Store result
    set_cached_result(restaurant_id, query, results, category)
    
    # Invalidate on data change
    clear_cache(restaurant_id, category)
"""
import json
from cachetools import TTLCache
from typing import Optional, List, Dict, Any
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.infrastructure.cache.redis_client import get_redis_client
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# In-memory fallback cache (used if Redis is not available)
_fallback_cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)
_fallback_call_phone_cache = TTLCache(maxsize=1000, ttl=3600)


def get_cache_key(restaurant_id: str, query: str, category: Optional[str] = None) -> str:
    """Generate cache key for a query."""
    category_str = category or "all"
    return f"cache:{restaurant_id}:{category_str}:{query}"


def get_cached_result(restaurant_id: str, query: str, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Retrieve cached search result from Redis or in-memory fallback."""
    key = get_cache_key(restaurant_id, query, category)
    redis_client = get_redis_client()

    if redis_client:
        try:
            cached_data = redis_client.get(key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Redis get error, falling back to in-memory: {e}")
            return _fallback_cache.get(key)
    else:
        return _fallback_cache.get(key)


def set_cached_result(restaurant_id: str, query: str, results: List[Dict[str, Any]], category: Optional[str] = None) -> None:
    """Store search result in Redis or in-memory fallback."""
    key = get_cache_key(restaurant_id, query, category)
    redis_client = get_redis_client()

    if redis_client:
        try:
            redis_client.setex(
                key,
                settings.cache_ttl_seconds,
                json.dumps(results)
            )
        except Exception as e:
            logger.warning(f"Redis set error, falling back to in-memory: {e}")
            _fallback_cache[key] = results
    else:
        _fallback_cache[key] = results


def clear_cache(restaurant_id: str, category: Optional[str] = None) -> None:
    """Clear cache for a specific restaurant/category."""
    redis_client = get_redis_client()

    if redis_client:
        try:
            if category:
                pattern = f"cache:{restaurant_id}:{category}:*"
            else:
                pattern = f"cache:{restaurant_id}:*"

            keys = redis_client.keys(pattern)
            if keys:
                redis_client.delete(*keys)
        except Exception as e:
            logger.warning(
                f"Redis delete error, falling back to in-memory: {e}")
            _clear_fallback_cache(restaurant_id, category)
    else:
        _clear_fallback_cache(restaurant_id, category)


def _clear_fallback_cache(restaurant_id: str, category: Optional[str] = None) -> None:
    """Clear in-memory fallback cache."""
    keys_to_delete = []
    for key in list(_fallback_cache.keys()):
        if key.startswith(f"cache:{restaurant_id}:"):
            if category is None or f":{category}:" in key:
                keys_to_delete.append(key)

    for key in keys_to_delete:
        del _fallback_cache[key]


def store_call_phone(call_id: str, phone_number: str) -> None:
    """Store call_id -> phone_number mapping in Redis or in-memory fallback."""
    if not call_id or not phone_number:
        return

    key = f"call_phone:{call_id}"
    redis_client = get_redis_client()

    if redis_client:
        try:
            redis_client.setex(key, 3600, phone_number)  # 1 hour TTL
        except Exception as e:
            logger.warning(
                f"Redis set error for call phone, falling back to in-memory: {e}")
            _fallback_call_phone_cache[call_id] = phone_number
    else:
        _fallback_call_phone_cache[call_id] = phone_number


def get_call_phone(call_id: str) -> Optional[str]:
    """Get phone number for a call_id from Redis or in-memory fallback."""
    if not call_id:
        return None

    key = f"call_phone:{call_id}"
    redis_client = get_redis_client()

    if redis_client:
        try:
            return redis_client.get(key)
        except Exception as e:
            logger.warning(
                f"Redis get error for call phone, falling back to in-memory: {e}")
            return _fallback_call_phone_cache.get(call_id)
    else:
        return _fallback_call_phone_cache.get(call_id)
