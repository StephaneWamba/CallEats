"""
Delivery zones API endpoints.

Provides REST endpoints for managing delivery zones including
create, read, update, and delete operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks, Query
from typing import Optional, List
from src.models.delivery_zones import (
    DeliveryZoneResponse,
    CreateDeliveryZoneRequest,
    UpdateDeliveryZoneRequest,
    SetBoundaryRequest
)
from src.services.operations.zones import (
    list_delivery_zones as list_delivery_zones_service,
    get_delivery_zone as get_delivery_zone_service,
    create_delivery_zone as create_delivery_zone_service,
    update_delivery_zone as update_delivery_zone_service,
    delete_delivery_zone as delete_delivery_zone_service
)
from src.services.infrastructure.auth import require_restaurant_access
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
def list_delivery_zones(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all delivery zones for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        items = list_delivery_zones_service(restaurant_id)
        return items
    except Exception as e:
        logger.error(
            f"Error listing delivery zones for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch delivery zones")


@router.get(
    "/restaurants/{restaurant_id}/zones/check",
    summary="Check Point in Zone",
    description="Check if coordinates (lat/lng) are within any delivery zone.",
    responses={
        200: {"description": "Zone check result"},
        401: {"description": "Invalid authentication"},
        422: {"description": "Missing lat/lng parameters"}
    }
)
def check_point_in_zone(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Check if point is in any delivery zone. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        from src.services.operations.zone_geometry import check_point_in_zone
        
        zone = check_point_in_zone(
            restaurant_id=restaurant_id,
            latitude=lat,
            longitude=lng
        )
        
        if zone:
            return {
                "in_zone": True,
                "zone": zone
            }
        else:
            return {
                "in_zone": False,
                "zone": None
            }
    except Exception as e:
        logger.error(
            f"Error checking point in zone: {e}",
            exc_info=True
        )
        return {
            "in_zone": False,
            "zone": None,
            "error": "Zone check unavailable (PostGIS may not be enabled)"
        }


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
def get_delivery_zone(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single delivery zone by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        item = get_delivery_zone_service(restaurant_id, zone_id)
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
def create_delivery_zone(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateDeliveryZoneRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new delivery zone. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        item = create_delivery_zone_service(
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
def update_delivery_zone(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    request: UpdateDeliveryZoneRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a delivery zone. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        item = update_delivery_zone_service(
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
def delete_delivery_zone(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a delivery zone. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        deleted = delete_delivery_zone_service(restaurant_id, zone_id)
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


# ============================================================================
# Geometry/Boundary Endpoints
# ============================================================================

@router.post(
    "/restaurants/{restaurant_id}/zones/{zone_id}/boundary",
    summary="Set Zone Boundary",
    description="Set the geographic boundary polygon for a delivery zone using GeoJSON. Enables spatial queries.",
    responses={
        200: {"description": "Boundary set successfully"},
        400: {"description": "Invalid GeoJSON or zone not found"},
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to set boundary"}
    }
)
def set_zone_boundary(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    request: SetBoundaryRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Set zone boundary from GeoJSON Polygon. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        from src.services.operations.zone_geometry import set_zone_boundary
        
        result = set_zone_boundary(
            restaurant_id=restaurant_id,
            zone_id=zone_id,
            geojson_boundary=request.boundary
        )
        return {"success": True, "boundary": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error setting boundary for zone {zone_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to set boundary")


@router.get(
    "/restaurants/{restaurant_id}/zones/check",
    summary="Check Point in Zone",
    description="Check if coordinates (lat/lng) are within any delivery zone.",
    responses={
        200: {"description": "Zone check result"},
        401: {"description": "Invalid authentication"},
        422: {"description": "Missing lat/lng parameters"}
    }
)
def check_point_in_zone(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    lat: float = Query(..., description="Latitude", ge=-90, le=90),
    lng: float = Query(..., description="Longitude", ge=-180, le=180),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Check if point is in any delivery zone. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        from src.services.operations.zone_geometry import check_point_in_zone
        
        zone = check_point_in_zone(
            restaurant_id=restaurant_id,
            latitude=lat,
            longitude=lng
        )
        
        if zone:
            return {
                "in_zone": True,
                "zone": zone
            }
        else:
            return {
                "in_zone": False,
                "zone": None
            }
    except Exception as e:
        logger.error(
            f"Error checking point in zone: {e}",
            exc_info=True
        )
        return {
            "in_zone": False,
            "zone": None,
            "error": "Zone check unavailable (PostGIS may not be enabled)"
        }


@router.get(
    "/restaurants/{restaurant_id}/zones/{zone_id}/map",
    summary="Get Zone Boundary GeoJSON",
    description="Get the boundary polygon as GeoJSON Feature for map display.",
    responses={
        200: {"description": "GeoJSON boundary"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Zone not found or boundary not set"}
    }
)
def get_zone_boundary_map(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    zone_id: str = Path(..., description="Delivery zone UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get zone boundary as GeoJSON for map display. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        from src.services.operations.zone_geometry import get_zone_boundary_geojson
        
        boundary = get_zone_boundary_geojson(
            restaurant_id=restaurant_id,
            zone_id=zone_id
        )
        
        if boundary:
            return boundary
        else:
            raise HTTPException(
                status_code=404,
                detail="Zone boundary not set or PostGIS not available"
            )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error getting boundary GeoJSON for zone {zone_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to get boundary")
