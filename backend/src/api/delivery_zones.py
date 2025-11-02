"""
Delivery zones API endpoints.

Provides REST endpoints for managing delivery zones including
create, read, update, and delete operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks
from typing import Optional, List
from src.models.delivery_zones import (
    DeliveryZoneResponse,
    CreateDeliveryZoneRequest,
    UpdateDeliveryZoneRequest
)
from src.services.operations.zones import (
    list_delivery_zones,
    get_delivery_zone,
    create_delivery_zone,
    update_delivery_zone,
    delete_delivery_zone
)
from src.services.infrastructure.auth import verify_vapi_secret
from src.services.embeddings.service import add_embedding_task
from src.core.middleware.request_id import get_request_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/restaurants/{restaurant_id}/zones",
    response_model=List[DeliveryZoneResponse],
    summary="List Delivery Zones",
    description="List all delivery zones for a restaurant, ordered by zone name.",
    responses={
        200: {"description": "Delivery zones retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch delivery zones"}
    }
)
def list_delivery_zones_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all delivery zones for a restaurant."""
    verify_vapi_secret(x_vapi_secret)

    try:
        items = list_delivery_zones(restaurant_id)
        return items
    except Exception as e:
        logger.error(
            f"Error listing delivery zones for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch delivery zones")


@router.get(
    "/restaurants/{restaurant_id}/zones/{zone_id}",
    response_model=DeliveryZoneResponse,
    summary="Get Delivery Zone",
    description="Get a single delivery zone by ID.",
    responses={
        200: {"description": "Delivery zone retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Delivery zone not found"},
        500: {"description": "Failed to fetch delivery zone"}
    }
)
def get_delivery_zone_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single delivery zone by ID."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = get_delivery_zone(restaurant_id, zone_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Delivery zone not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching delivery zone {zone_id} for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch delivery zone")


@router.post(
    "/restaurants/{restaurant_id}/zones",
    response_model=DeliveryZoneResponse,
    summary="Create Delivery Zone",
    description="Create a new delivery zone. Automatically invalidates zones cache.",
    responses={
        201: {"description": "Delivery zone created successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to create delivery zone"}
    }
)
def create_delivery_zone_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateDeliveryZoneRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new delivery zone. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = create_delivery_zone(
            restaurant_id=restaurant_id,
            zone_name=request.zone_name,
            description=request.description,
            delivery_fee=request.delivery_fee,
            min_order=request.min_order
        )

        add_embedding_task(background_tasks, restaurant_id, "zones")

        return DeliveryZoneResponse(**item)
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error creating delivery zone for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to create delivery zone")


@router.put(
    "/restaurants/{restaurant_id}/zones/{zone_id}",
    response_model=DeliveryZoneResponse,
    summary="Update Delivery Zone",
    description="Update a delivery zone. All fields are optional. Automatically invalidates zones cache.",
    responses={
        200: {"description": "Delivery zone updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Delivery zone not found"},
        500: {"description": "Failed to update delivery zone"}
    }
)
def update_delivery_zone_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    request: UpdateDeliveryZoneRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a delivery zone. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = update_delivery_zone(
            restaurant_id=restaurant_id,
            zone_id=zone_id,
            zone_name=request.zone_name,
            description=request.description,
            delivery_fee=request.delivery_fee,
            min_order=request.min_order
        )
        if not item:
            raise HTTPException(
                status_code=404, detail="Delivery zone not found")

        add_embedding_task(background_tasks, restaurant_id, "zones")

        return DeliveryZoneResponse(**item)
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating delivery zone {zone_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update delivery zone")


@router.delete(
    "/restaurants/{restaurant_id}/zones/{zone_id}",
    summary="Delete Delivery Zone",
    description="Delete a delivery zone. Automatically invalidates zones cache.",
    responses={
        200: {"description": "Delivery zone deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Delivery zone not found"},
        500: {"description": "Failed to delete delivery zone"}
    }
)
def delete_delivery_zone_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a delivery zone. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        deleted = delete_delivery_zone(restaurant_id, zone_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Delivery zone not found")

        add_embedding_task(background_tasks, restaurant_id, "zones")

        return {"success": True, "message": "Delivery zone deleted"}
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting delivery zone {zone_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete delivery zone")
