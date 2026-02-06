"""Vapi webhook API router.

This module provides webhook endpoints for Vapi.ai voice assistant integration.
It handles server events, knowledge base queries, cache invalidation, and
embedding generation.

Endpoints:
    - POST /api/vapi/server: Unified server webhook (assistant-request, status-update, end-of-call-report)
    - POST /api/vapi/knowledge-base: Knowledge base tool calls (vector search)
    - POST /api/vapi/cache/invalidate: Invalidate cache entries
    - POST /api/vapi/embeddings/generate: Generate embeddings for restaurant content

Authentication:
    All endpoints require X-Vapi-Secret header for authentication.
    This is separate from JWT authentication used by frontend endpoints.

Webhook Events:
    - assistant-request: Maps phone numbers to restaurant IDs
    - status-update: Monitors call status and schedules API fetches
    - end-of-call-report: Triggers call data retrieval (fallback mechanism)

Knowledge Base:
    Performs vector similarity search using OpenAI embeddings and pgvector.
    Returns structured results with metadata for TTS enhancement.

Usage:
    Vapi webhooks are configured in Vapi dashboard to point to these endpoints.
    The unified server endpoint routes events based on message.type.
"""
from fastapi import APIRouter, Request, HTTPException, Header
from typing import Optional
from pydantic import ValidationError
from restaurant_voice_assistant.shared.types import VapiRequest
from restaurant_voice_assistant.shared.models.embeddings import (
    CacheInvalidateRequest,
    GenerateEmbeddingsRequest
)
from restaurant_voice_assistant.infrastructure.cache.manager import clear_cache
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
from restaurant_voice_assistant.infrastructure.openai.embeddings import (
    generate_embeddings_for_restaurant
)
from restaurant_voice_assistant.infrastructure.auth.service import verify_vapi_secret
from restaurant_voice_assistant.infrastructure.vapi.server import (
    handle_assistant_request,
    handle_end_of_call_report,
    handle_status_update
)
from restaurant_voice_assistant.infrastructure.vapi.knowledge import (
    handle_knowledge_base_query
)
import logging
import json

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/cache/invalidate",
    summary="Invalidate Cache",
    description="Invalidate cache entries for a restaurant/category.",
    responses={
        200: {"description": "Cache invalidated successfully"},
        401: {"description": "Invalid authentication"}
    }
)
async def invalidate_cache(
    request: CacheInvalidateRequest,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret")
):
    """Invalidate cache entries for a restaurant/category."""
    verify_vapi_secret(x_vapi_secret)
    clear_cache(request.restaurant_id, request.category)
    return {"success": True}


@router.post(
    "/embeddings/generate",
    summary="Generate Embeddings",
    description="Generate embeddings for restaurant content.",
    responses={
        200: {"description": "Embeddings generated successfully"},
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to generate embeddings"}
    }
)
async def generate_embeddings(
    request: GenerateEmbeddingsRequest,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret")
):
    """Generate embeddings for restaurant content."""
    verify_vapi_secret(x_vapi_secret)
    result = await generate_embeddings_for_restaurant(
        restaurant_id=request.restaurant_id,
        category=request.category
    )
    return result


@router.post(
    "/server",
    summary="Vapi Unified Server Webhook",
    description="Unified webhook endpoint that routes Vapi server events based on message type. Handles assistant-request, end-of-call-report, and other server events.",
    responses={
        200: {"description": "Event processed successfully"}
    }
)
async def vapi_unified_server(request: Request):
    """Unified Vapi server webhook endpoint.

    Routes messages based on message.type:
    - "assistant-request" → processes restaurant_id mapping
    - "status-update" → schedules API fetch for call data
    - "end-of-call-report" → processes call data storage
    - Other types → logged and returns empty response
    """
    verify_vapi_secret(request.headers.get("X-Vapi-Secret"))

    try:
        body = await request.json()
        message_obj = body.get("message", {})
        message_type = message_obj.get("type")

        if message_type == "assistant-request":
            return handle_assistant_request(message_obj)

        elif message_type == "status-update":
            return handle_status_update(message_obj)

        elif message_type == "end-of-call-report":
            return handle_end_of_call_report(message_obj)

        else:
            logger.debug(
                f"Unhandled Vapi server event: type={message_type}",
                extra={"request_id": get_request_id(request)}
            )
            return {}

    except Exception as e:
        request_id = get_request_id(request)
        logger.error(
            f"Error processing Vapi server webhook: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        return {}


@router.post(
    "/knowledge-base",
    summary="Vapi Knowledge Base",
    description="Main Vapi webhook endpoint for Function Tool calls. Performs vector similarity search and returns restaurant-specific results.",
    responses={
        200: {"description": "Tool result with search results"},
        401: {"description": "Invalid authentication"},
        422: {"description": "Missing restaurant_id or invalid request format"},
        500: {"description": "Internal server error"}
    }
)
async def vapi_knowledge_base(
    request: Request,
    x_restaurant_id: Optional[str] = Header(
        None, alias="X-Restaurant-Id", description="Restaurant UUID (can also be in metadata)"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret")
):
    """Main Vapi webhook endpoint for Function Tool calls.

    Performs vector similarity search using OpenAI embeddings and pgvector.
    Returns structured results with metadata for TTS enhancement.
    """
    settings = get_settings()
    request_id = get_request_id(request)

    try:
        if not x_vapi_secret or x_vapi_secret != settings.vapi_secret_key:
            raise HTTPException(
                status_code=401, detail="Invalid authentication")

        body_bytes = await request.body()

        try:
            vapi_request = VapiRequest.parse_raw(body_bytes)
        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid request format: {str(e)}"
            )

        try:
            body_dict = json.loads(body_bytes.decode('utf-8'))
            message_obj = body_dict.get("message", {})
        except Exception:
            message_obj = None

        result = await handle_knowledge_base_query(
            vapi_request=vapi_request,
            x_restaurant_id=x_restaurant_id,
            query_params=dict(request.query_params),
            message_obj=message_obj
        )
        return result

    except ValidationError as e:
        logger.error(
            f"Validation error: {e.errors()}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=422, detail=f"Invalid request format: {e.errors()}")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error processing knowledge-base request: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(status_code=500, detail=str(e))

