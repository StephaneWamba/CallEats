"""
Vector similarity search service for knowledge base queries.

Performs semantic search using pgvector against restaurant-specific
document embeddings with automatic caching and tenant isolation.
"""
from typing import Optional, List, Dict, Any
from src.services.infrastructure.database import get_supabase_client
from src.services.embeddings.service import generate_embedding
from src.services.infrastructure.cache import get_cached_result, set_cached_result
import logging

logger = logging.getLogger(__name__)


async def search_knowledge_base(
    query: str,
    restaurant_id: str,
    category: Optional[str] = None,
    limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search knowledge base using vector similarity search.

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
        f"Cache miss, generating embedding for query: '{query[:50]}...'")
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

    logger.info(
        f"Vector search: {len(results)} results for query='{query[:50]}...' "
        f"(restaurant={restaurant_id}, category={category})"
    )
    set_cached_result(restaurant_id, query, results, category)

    return results
