"""Embedding management API router.

This module provides REST endpoints for generating embeddings and managing
the search cache. Embeddings are used for vector similarity search in the
knowledge base.

Endpoints:
    - POST /api/embeddings/generate: Generate embeddings for restaurant content
    - POST /api/embeddings/cache/invalidate: Invalidate cache entries

Authentication:
    All endpoints require X-Vapi-Secret header for authentication.
    This is separate from JWT authentication (for admin/script access).

Embedding Generation:
    Generates OpenAI embeddings for:
    - Menu items (name, description, price)
    - Modifiers (name, description, price)
    - Operating hours (day, times)
    - Delivery zones (name, fee)

Cache Invalidation:
    Clears cached search results for a restaurant/category.
    Useful when data changes and you want fresh search results.

Usage:
    Generate embeddings after data changes:
        POST /api/embeddings/generate
        Body: {"restaurant_id": "...", "category": "menu"}
    
    Invalidate cache:
        POST /api/embeddings/cache/invalidate
        Body: {"restaurant_id": "...", "category": "menu"}
"""
from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from restaurant_voice_assistant.shared.models.embeddings import (
    GenerateEmbeddingsRequest,
    CacheInvalidateRequest
)
from restaurant_voice_assistant.infrastructure.openai.embeddings import (
    generate_embeddings_for_restaurant
)
from restaurant_voice_assistant.infrastructure.cache.manager import clear_cache
from restaurant_voice_assistant.infrastructure.auth.service import verify_vapi_secret
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/generate",
    summary="Generate Embeddings",
    description="Generate embeddings for restaurant data. Requires X-Vapi-Secret header for authentication.",
    responses={
        200: {
            "description": "Embeddings generated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                        "embeddings_generated": 23
                    }
                }
            }
        },
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to generate embeddings"}
    }
)
async def generate_embeddings(
    request: GenerateEmbeddingsRequest,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret")
):
    """Generate embeddings for restaurant content.

    Categories: menu, modifiers, hours, zones (or None for all).
    """
    verify_vapi_secret(x_vapi_secret)

    try:
        result = await generate_embeddings_for_restaurant(
            restaurant_id=request.restaurant_id,
            category=request.category
        )
        return result
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate embeddings"
        )


@router.post(
    "/cache/invalidate",
    summary="Invalidate Cache",
    description="Force invalidate cache for a restaurant. Requires X-Vapi-Secret header for authentication.",
    responses={
        200: {
            "description": "Cache invalidated successfully",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "message": "Cache cleared for restaurant 04529052-b3dd-43c1-a534-c18d8c0f4c6d"
                    }
                }
            }
        },
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to invalidate cache"}
    }
)
async def invalidate_cache(
    request: CacheInvalidateRequest,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret")
):
    """Force invalidate cache for a restaurant/category.

    Clears cached search results. Use after data changes.
    """
    verify_vapi_secret(x_vapi_secret)

    try:
        clear_cache(request.restaurant_id, request.category)
        return {
            "status": "success",
            "message": f"Cache cleared for restaurant {request.restaurant_id}"
        }
    except Exception as e:
        logger.error(f"Error invalidating cache: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to invalidate cache"
        )

