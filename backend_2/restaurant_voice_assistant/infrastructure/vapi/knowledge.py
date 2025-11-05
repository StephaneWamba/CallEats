"""Vapi knowledge base tool call handler.

This module processes function tool requests from Vapi and returns search results
using vector similarity search. It handles the complete flow from tool call
to formatted response.

Tool Mapping:
    - get_menu_info → category: "menu"
    - get_modifiers_info → category: "modifiers"
    - get_hours_info → category: "hours"
    - get_zones_info → category: "zones"

Restaurant ID Resolution:
    Attempts to extract restaurant_id from multiple sources in order:
    1. X-Restaurant-Id header
    2. Query parameter (restaurant_id)
    3. Request metadata (metadata.restaurant_id)
    4. Phone number lookup (from message.phoneNumber)

Response Format:
    Returns structured tool results with:
    - Tool call ID for correlation
    - Formatted response text
    - Structured metadata items for TTS enhancement

Usage:
    Called from api/routers/vapi.py when processing knowledge-base webhook requests.
"""
from typing import Optional, Dict, Any, List
from restaurant_voice_assistant.shared.types import VapiRequest
from restaurant_voice_assistant.domain.embeddings.search import search_knowledge_base
from restaurant_voice_assistant.infrastructure.vapi.response import (
    build_tool_result_with_items,
    build_no_result,
    build_structured_items,
)
from restaurant_voice_assistant.domain.phones.mapping import get_restaurant_id_from_phone
from restaurant_voice_assistant.domain.phones.extraction import extract_restaurant_id_with_fallback
import asyncio
import logging

logger = logging.getLogger(__name__)

TOOL_CATEGORY_MAP = {
    "get_menu_info": "menu",
    "get_modifiers_info": "modifiers",
    "get_hours_info": "hours",
    "get_zones_info": "zones",
}


def _map_tool_to_category(tool_name: Optional[str]) -> Optional[str]:
    """Map Vapi Function Tool name to internal content category."""
    if not tool_name:
        return None
    return TOOL_CATEGORY_MAP.get(tool_name)


async def handle_knowledge_base_query(
    vapi_request: VapiRequest,
    x_restaurant_id: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None,
    message_obj: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Handle knowledge base tool call from Vapi.

    Extracts query, maps tool to category, performs vector search, and returns results.

    Args:
        vapi_request: Parsed Vapi request object
        x_restaurant_id: Optional restaurant_id from header
        query_params: Optional query parameters dict
        message_obj: Optional raw message object for phone number fallback

    Returns:
        Tool result dictionary with search results

    Raises:
        ValueError: If query or restaurant_id is missing
    """
    query_text = vapi_request.extract_query()
    tool_call_id = vapi_request.extract_tool_call_id()
    tool_name = vapi_request.extract_tool_name()

    if not query_text:
        raise ValueError("Missing query parameter")

    if not tool_call_id:
        raise ValueError("Missing toolCallId")

    restaurant_id = extract_restaurant_id_with_fallback(
        x_restaurant_id=x_restaurant_id,
        query_params=query_params,
        vapi_request=vapi_request,
        message_obj=message_obj
    )

    if not restaurant_id:
        raise ValueError(
            "restaurant_id is required. Provide via X-Restaurant-Id header, query param, metadata.restaurant_id, or ensure phone number is in call metadata."
        )

    category = _map_tool_to_category(tool_name)

    try:
        results = await asyncio.wait_for(
            search_knowledge_base(
                query=query_text,
                restaurant_id=restaurant_id,
                category=category,
                limit=5
            ),
            timeout=15.0
        )
    except asyncio.TimeoutError:
        return build_no_result(
            tool_call_id,
            "I'm experiencing a delay retrieving that information. Please try again in a moment."
        )

    if not results:
        logger.info(
            f"No results found for query: '{query_text}' (category={category}, restaurant_id={restaurant_id[:8]}...)"
        )
        return build_no_result(tool_call_id, category=category)

    logger.debug(
        f"Found {len(results)} results for query: '{query_text}' (category={category})"
    )

    response_text = "\n\n".join([doc["content"] for doc in results[:3]])
    items = build_structured_items(results, category)

    return build_tool_result_with_items(tool_call_id, response_text, items)
