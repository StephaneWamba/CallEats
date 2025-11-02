"""
Operating hours API endpoints.

Provides REST endpoints for managing operating hours including
read and bulk update operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks
from typing import Optional, List
from src.models.operating_hours import (
    OperatingHourResponse,
    UpdateOperatingHoursRequest
)
from src.services.operations.hours import (
    list_operating_hours,
    get_operating_hour,
    update_operating_hours,
    delete_operating_hours
)
from src.services.infrastructure.auth import verify_vapi_secret
from src.services.embeddings.service import add_embedding_task
from src.core.middleware.request_id import get_request_id
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
def list_operating_hours_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all operating hours for a restaurant."""
    verify_vapi_secret(x_vapi_secret)

    try:
        items = list_operating_hours(restaurant_id)
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
def get_operating_hour_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    hour_id: str = Path(..., description="Operating hour UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single operating hour by ID."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = get_operating_hour(restaurant_id, hour_id)
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
    description="Bulk update operating hours. Replaces all existing hours. Automatically invalidates hours cache.",
    responses={
        200: {"description": "Operating hours updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to update operating hours"}
    }
)
def update_operating_hours_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: UpdateOperatingHoursRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update operating hours (bulk update). Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        hours_data = [hour.dict() for hour in request.hours]
        items = update_operating_hours(restaurant_id, hours_data)

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
    description="Delete all operating hours for a restaurant. Automatically invalidates hours cache.",
    responses={
        200: {"description": "Operating hours deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to delete operating hours"}
    }
)
def delete_operating_hours_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete all operating hours for a restaurant. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        delete_operating_hours(restaurant_id)

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
