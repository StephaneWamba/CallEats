"""Operating hours API router.

This module provides REST endpoints for managing restaurant operating hours
including listing hours and bulk updates. Operating hours are stored per day
of the week.

Endpoints:
    - GET /api/restaurants/{restaurant_id}/hours: List all operating hours
    - GET /api/restaurants/{restaurant_id}/hours/{hour_id}: Get single hour record
    - PUT /api/restaurants/{restaurant_id}/hours: Bulk update (replace all hours)
    - DELETE /api/restaurants/{restaurant_id}/hours: Delete all hours

Authentication:
    All endpoints accept JWT (frontend users) or X-Vapi-Secret (admin/scripts).
    Users can only access their own restaurant's operating hours.

Operating Hours Management:
    - Bulk update pattern: DELETE all + INSERT new (atomic operation)
    - Each day has: day_of_week (0-6), open_time, close_time, is_closed
    - Cache is automatically invalidated on changes
    - Embeddings are regenerated in background after changes

Usage:
    Update all hours:
        PUT /api/restaurants/{restaurant_id}/hours
        Body: {
            "hours": [
                {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00", "is_closed": false},
                {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00", "is_closed": false},
                ...
            ]
        }
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks
from typing import Optional, List
from restaurant_voice_assistant.shared.models.operating_hours import (
    OperatingHourResponse,
    UpdateOperatingHoursRequest
)
from restaurant_voice_assistant.domain.operations.hours import (
    list_operating_hours as list_operating_hours_service,
    get_operating_hour as get_operating_hour_service,
    update_operating_hours as update_operating_hours_service,
    delete_operating_hours as delete_operating_hours_service
)
from restaurant_voice_assistant.infrastructure.auth.service import (
    require_restaurant_access
)
from restaurant_voice_assistant.infrastructure.openai.embeddings import (
    add_embedding_task
)
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/restaurants/{restaurant_id}/hours",
    response_model=List[OperatingHourResponse],
    summary="List Operating Hours",
    description="List all operating hours for a restaurant, ordered by day of week.",
    responses={
        200: {"description": "Operating hours retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch operating hours"}
    }
)
async def list_operating_hours(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all operating hours for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        items = await asyncio.to_thread(list_operating_hours_service, restaurant_id)
        return items
    except Exception as e:
        logger.error(
            f"Error listing operating hours for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch operating hours")


@router.get(
    "/restaurants/{restaurant_id}/hours/{hour_id}",
    response_model=OperatingHourResponse,
    summary="Get Operating Hour",
    description="Get a single operating hour by ID.",
    responses={
        200: {"description": "Operating hour retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Operating hour not found"},
        500: {"description": "Failed to fetch operating hour"}
    }
)
async def get_operating_hour(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    hour_id: str = Path(..., description="Operating hour UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single operating hour by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        item = await asyncio.to_thread(get_operating_hour_service, restaurant_id, hour_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Operating hour not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching operating hour {hour_id} for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch operating hour")


@router.put(
    "/restaurants/{restaurant_id}/hours",
    response_model=List[OperatingHourResponse],
    summary="Update Operating Hours",
    description="Bulk update operating hours. Replaces all existing hours. Automatically triggers background embedding generation.",
    responses={
        200: {"description": "Operating hours updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to update operating hours"}
    }
)
async def update_operating_hours(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: UpdateOperatingHoursRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update operating hours (bulk update). Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        hours_data = [hour.dict() for hour in request.hours]
        items = await asyncio.to_thread(update_operating_hours_service, restaurant_id, hours_data)

        add_embedding_task(background_tasks, restaurant_id, "hours")

        return items
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating operating hours for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update operating hours")


@router.delete(
    "/restaurants/{restaurant_id}/hours",
    summary="Delete Operating Hours",
    description="Delete all operating hours for a restaurant. Automatically triggers background embedding generation.",
    responses={
        200: {"description": "Operating hours deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to delete operating hours"}
    }
)
async def delete_operating_hours(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete all operating hours for a restaurant. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        await asyncio.to_thread(delete_operating_hours_service, restaurant_id)

        add_embedding_task(background_tasks, restaurant_id, "hours")

        return {"success": True, "message": "Operating hours deleted"}
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting operating hours for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete operating hours")

