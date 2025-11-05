"""Call history API router.

This module provides REST endpoints for accessing voice assistant call records,
including listing call history and retrieving individual call details with transcripts.

Endpoints:
    - GET /api/calls: List call history for a restaurant
    - GET /api/calls/{call_id}: Get detailed call record with transcript

Authentication:
    All endpoints accept JWT (frontend users) or X-Vapi-Secret (admin/scripts).
    Users can only access calls for their own restaurant.

Call Data:
    Call records include:
    - Call timestamps (started_at, ended_at)
    - Duration (duration_seconds)
    - Caller phone number
    - Outcome (completed, failed, etc.)
    - Messages (filtered transcript: user and assistant messages only)
    - Cost information

Message Filtering:
    Only includes user and assistant messages in transcripts.
    System messages and tool calls are excluded for cleaner display.

Usage:
    List calls:
        GET /api/calls?restaurant_id=...&limit=50
    
    Get call details:
        GET /api/calls/{call_id}?restaurant_id=...
"""
from fastapi import APIRouter, HTTPException, Header, Query, Path, Request
from typing import Optional
from restaurant_voice_assistant.shared.models.calls import CallResponse
from restaurant_voice_assistant.domain.calls.service import (
    list_calls as list_calls_service,
    get_call as get_call_service
)
from restaurant_voice_assistant.infrastructure.auth.service import (
    require_restaurant_access
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/calls",
    summary="List Call History",
    description="List call history for a restaurant, ordered by most recent first.",
    responses={
        200: {
            "description": "Call history retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "data": [
                            {
                                "id": "call_abc123",
                                "started_at": "2025-01-01T12:00:00Z",
                                "ended_at": "2025-01-01T12:05:00Z",
                                "duration_seconds": 300,
                                "caller": "+1234567890",
                                "outcome": "completed",
                                "messages": []
                            }
                        ]
                    }
                }
            }
        },
        422: {"description": "restaurant_id is required"},
        500: {"description": "Failed to fetch call history"}
    }
)
def list_calls(
    request: Request,
    x_restaurant_id: Optional[str] = Header(
        None, alias="X-Restaurant-Id", description="Restaurant UUID (alternative to query param)"),
    restaurant_id_q: Optional[str] = Query(
        None, alias="restaurant_id", description="Restaurant UUID"),
    limit: int = Query(
        50, ge=1, le=200, description="Maximum number of results"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List call history for a restaurant, ordered by most recent first.

    Supports restaurant_id from header (X-Restaurant-Id) or query parameter.
    Accepts JWT (frontend users) or X-Vapi-Secret (admin/scripts) for authentication.
    """
    restaurant_id = (x_restaurant_id or restaurant_id_q or "").strip()
    if not restaurant_id:
        raise HTTPException(
            status_code=422, detail="restaurant_id is required")

    # Authenticate and verify restaurant access
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        calls = list_calls_service(restaurant_id, limit)
        return {"data": calls}
    except Exception as e:
        logger.error(
            f"Error fetching calls for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch call history")


@router.get(
    "/calls/{call_id}",
    response_model=CallResponse,
    summary="Get Call Details",
    description="Get a single call record with full transcript by call ID.",
    responses={
        200: {"description": "Call record retrieved successfully"},
        404: {"description": "Call not found"},
        422: {"description": "restaurant_id required for security verification"},
        500: {"description": "Failed to fetch call record"}
    }
)
def get_call(
    request: Request,
    call_id: str = Path(..., description="Call record UUID"),
    x_restaurant_id: Optional[str] = Header(
        None, alias="X-Restaurant-Id", description="Restaurant UUID (alternative to query param)"),
    restaurant_id_q: Optional[str] = Query(
        None, alias="restaurant_id", description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single call record with full transcript.

    Requires restaurant_id for security verification (ensures users can only access their own calls).
    Supports restaurant_id from header (X-Restaurant-Id) or query parameter.
    """
    restaurant_id = (x_restaurant_id or restaurant_id_q or "").strip()
    if not restaurant_id:
        raise HTTPException(
            status_code=422, detail="restaurant_id is required for security verification")

    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        call = get_call_service(call_id, restaurant_id)
        if not call:
            raise HTTPException(
                status_code=404, detail="Call not found")
        return call
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching call {call_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail="Failed to fetch call record")
