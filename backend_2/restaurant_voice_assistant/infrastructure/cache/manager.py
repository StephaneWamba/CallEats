"""In-memory cache management for search results and call data.

This module provides caching functionality for:
    - Vector search results (embeddings queries)
    - Call ID to phone number mappings

Key Features:
    - TTL-based cache expiration (configurable via CACHE_TTL_SECONDS)
    - Automatic cache invalidation on data changes
    - Separate cache for call phone mappings (1 hour TTL)
    - Restaurant-scoped cache keys for multi-tenancy

Cache Keys:
    - Search results: "{restaurant_id}:{category}:{query}"
    - Call mappings: "{call_id}"

Performance:
    - Reduces OpenAI API calls by caching embedding search results
    - Speeds up repeated queries for the same restaurant/category
    - Cache automatically evicts oldest entries when max size reached

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
from cachetools import TTLCache
from typing import Optional, List, Dict, Any
from restaurant_voice_assistant.core.config import get_settings

settings = get_settings()

_cache = TTLCache(maxsize=1000, ttl=settings.cache_ttl_seconds)
# Cache for call_id -> phone_number mapping (TTL: 1 hour to cover long calls)
_call_phone_cache = TTLCache(maxsize=1000, ttl=3600)


def get_cache_key(restaurant_id: str, query: str, category: Optional[str] = None) -> str:
    """Generate cache key for a query."""
    category_str = category or "all"
    return f"{restaurant_id}:{category_str}:{query}"


def get_cached_result(restaurant_id: str, query: str, category: Optional[str] = None) -> Optional[List[Dict[str, Any]]]:
    """Retrieve cached search result."""
    key = get_cache_key(restaurant_id, query, category)
    return _cache.get(key)


def set_cached_result(restaurant_id: str, query: str, results: List[Dict[str, Any]], category: Optional[str] = None) -> None:
    """Store search result in cache."""
    key = get_cache_key(restaurant_id, query, category)
    _cache[key] = results


def clear_cache(restaurant_id: str, category: Optional[str] = None) -> None:
    """Clear cache for a specific restaurant/category."""
    keys_to_delete = []

    for key in list(_cache.keys()):
        if key.startswith(f"{restaurant_id}:"):
            if category is None or f":{category}:" in key:
                keys_to_delete.append(key)

    for key in keys_to_delete:
        del _cache[key]


def store_call_phone(call_id: str, phone_number: str) -> None:
    """Store call_id -> phone_number mapping."""
    if call_id and phone_number:
        _call_phone_cache[call_id] = phone_number


def get_call_phone(call_id: str) -> Optional[str]:
    """Get phone number for a call_id."""
    return _call_phone_cache.get(call_id)

