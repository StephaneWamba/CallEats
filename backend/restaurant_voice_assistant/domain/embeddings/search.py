"""Vector similarity search service for knowledge base queries.

This module performs semantic search using pgvector against restaurant-specific
document embeddings with automatic caching and tenant isolation.

Key Features:
    - Semantic search using OpenAI embeddings and pgvector
    - Automatic caching (60s TTL) to reduce API calls
    - Multi-tenant isolation (restaurant_id filtering)
    - Category filtering (menu, modifiers, hours, zones)
    - Configurable result limit

Search Flow:
    1. Check cache for existing results
    2. Generate embedding for query (if cache miss)
    3. Perform vector similarity search in Supabase
    4. Cache results for future queries
    5. Return formatted results with scores

Usage:
    from restaurant_voice_assistant.domain.embeddings.search import search_knowledge_base
    
    results = await search_knowledge_base(
        query="What's on your menu?",
        restaurant_id="...",
        category="menu",
        limit=5
    )
"""
from typing import Optional, List, Dict, Any
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_client
from restaurant_voice_assistant.infrastructure.openai.embeddings import generate_embedding
from restaurant_voice_assistant.infrastructure.cache.manager import (
    get_cached_result,
    set_cached_result
)
import logging

logger = logging.getLogger(__name__)


async def search_knowledge_base(
    query: str,
    restaurant_id: str,
    category: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """Search knowledge base using vector similarity search.

    Uses OpenAI embeddings and pgvector for semantic search with automatic
    caching (60s TTL) and multi-tenant isolation.

    Args:
        query: Search query text
        restaurant_id: Restaurant UUID for tenant isolation
        category: Optional category filter (menu, modifiers, hours, zones)
        limit: Maximum number of results (default: 5)

    Returns:
        List of documents with keys: content, metadata, score
    """
    cached = get_cached_result(restaurant_id, query, category)
    if cached is not None:
        logger.debug(
            f"Cache hit for query: '{query[:50]}...' (restaurant={restaurant_id}, category={category})")
        return cached

    logger.debug(
        f"Cache miss, generating embedding for query: '{query}' (restaurant_id={restaurant_id[:8]}..., category={category})")
    query_embedding = await generate_embedding(query)

    rpc_params = {
        "query_embedding": query_embedding,
        "query_restaurant_id": restaurant_id,
        "match_count": limit
    }

    if category:
        rpc_params["query_category"] = category

    supabase = get_supabase_client()
    response = supabase.rpc("search_documents", rpc_params).execute()

    results = [
        {
            "content": doc["content"],
            "metadata": doc["metadata"],
            "score": doc["similarity"]
        }
        for doc in response.data
    ]

    set_cached_result(restaurant_id, query, results, category)

    return results

