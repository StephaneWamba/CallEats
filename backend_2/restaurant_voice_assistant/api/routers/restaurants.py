"""Restaurant management API router.

This module provides REST endpoints for creating and managing restaurants,
including automatic phone number assignment and phone connectivity testing.

Endpoints:
    - POST /api/restaurants: Create restaurant with optional phone assignment
    - GET /api/restaurants/{restaurant_id}: Get restaurant details
    - GET /api/restaurants/me: Get current user's restaurant (JWT only)
    - PUT /api/restaurants/{restaurant_id}: Update restaurant information
    - GET /api/restaurants/{restaurant_id}/stats: Get dashboard statistics

Authentication:
    All endpoints accept JWT (frontend users) or X-Vapi-Secret (admin/scripts).
    Users can only access their own restaurant's data (enforced by require_restaurant_access).

Phone Assignment:
    Automatic phone assignment on creation:
    - By default, tries existing unassigned phones first
    - Falls back to Twilio number creation if needed
    - Set force_twilio=True to skip existing phones and directly create Twilio number

Usage:
    Create restaurant:
        POST /api/restaurants
        Body: {"name": "...", "assign_phone": true}
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request
from typing import Optional
from restaurant_voice_assistant.shared.models.restaurants import (
    CreateRestaurantRequest,
    UpdateRestaurantRequest,
    RestaurantResponse,
    RestaurantStatsResponse,
    DeleteRestaurantResponse
)
from restaurant_voice_assistant.domain.restaurants.service import (
    create_restaurant as create_restaurant_service,
    get_restaurant as get_restaurant_service,
    update_restaurant as update_restaurant_service,
    get_restaurant_stats as get_restaurant_stats_service,
    delete_restaurant as delete_restaurant_service
)
from restaurant_voice_assistant.infrastructure.auth.service import (
    require_auth,
    require_restaurant_access,
    get_restaurant_id
)
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/restaurants",
    response_model=RestaurantResponse,
    responses={
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to create restaurant"}
    },
    summary="Create Restaurant",
    description="Create a new restaurant with optional automatic phone number assignment."
)
def create_restaurant(
    request: CreateRestaurantRequest,
    http_request: Request,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new restaurant.

    Automatically assigns a phone number if assign_phone=True (default).
    Returns restaurant data including phone number if assigned.
    Accepts JWT (frontend users) or X-Vapi-Secret (admin/scripts) for authentication.
    """
    require_auth(http_request, x_vapi_secret)

    try:
        restaurant_data = create_restaurant_service(
            name=request.name,
            api_key=request.api_key,
            assign_phone=request.assign_phone,
            force_twilio=request.force_twilio
        )

        return RestaurantResponse(
            id=restaurant_data["id"],
            name=restaurant_data["name"],
            api_key=restaurant_data["api_key"],
            phone_number=restaurant_data["phone_number"],
            created_at=restaurant_data["created_at"]
        )

    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error creating restaurant: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to create restaurant")


@router.get(
    "/restaurants/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Get Restaurant",
    description="Get a single restaurant by ID, including assigned phone number.",
    responses={
        200: {"description": "Restaurant retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch restaurant"}
    }
)
def get_restaurant(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single restaurant by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        restaurant_data = get_restaurant_service(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        return RestaurantResponse(
            id=restaurant_data["id"],
            name=restaurant_data["name"],
            api_key=restaurant_data["api_key"],
            phone_number=restaurant_data["phone_number"],
            created_at=restaurant_data["created_at"],
            updated_at=restaurant_data.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch restaurant")


@router.get(
    "/restaurants/me",
    response_model=RestaurantResponse,
    summary="Get Current User's Restaurant",
    description="Get the authenticated user's restaurant automatically (no restaurant_id needed).",
    responses={
        200: {"description": "Restaurant retrieved successfully"},
        401: {"description": "Invalid authentication"},
        403: {"description": "User not associated with a restaurant"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch restaurant"}
    }
)
def get_my_restaurant(request: Request):
    """Get the current authenticated user's restaurant.

    Extracts restaurant_id from JWT token automatically.
    Only accepts JWT authentication (not X-Vapi-Secret).
    """
    # Get restaurant_id from JWT token
    restaurant_id = get_restaurant_id(request)

    try:
        restaurant_data = get_restaurant_service(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        return RestaurantResponse(
            id=restaurant_data["id"],
            name=restaurant_data["name"],
            api_key=restaurant_data["api_key"],
            phone_number=restaurant_data["phone_number"],
            created_at=restaurant_data["created_at"],
            updated_at=restaurant_data.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(request)
        logger.error(
            f"Error fetching restaurant for current user: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch restaurant")


@router.put(
    "/restaurants/{restaurant_id}",
    response_model=RestaurantResponse,
    summary="Update Restaurant",
    description="Update restaurant information. All fields are optional.",
    responses={
        200: {"description": "Restaurant updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to update restaurant"}
    }
)
def update_restaurant(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: UpdateRestaurantRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update restaurant information. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        restaurant_data = update_restaurant_service(
            restaurant_id=restaurant_id,
            name=request.name
        )

        if not restaurant_data:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        return RestaurantResponse(
            id=restaurant_data["id"],
            name=restaurant_data["name"],
            api_key=restaurant_data["api_key"],
            phone_number=restaurant_data["phone_number"],
            created_at=restaurant_data["created_at"],
            updated_at=restaurant_data.get("updated_at")
        )
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update restaurant")


@router.get(
    "/restaurants/{restaurant_id}/stats",
    response_model=RestaurantStatsResponse,
    summary="Get Restaurant Statistics",
    description="Get dashboard statistics for a restaurant.",
    responses={
        200: {"description": "Statistics retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch statistics"}
    }
)
def get_restaurant_stats(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get dashboard statistics for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        stats = get_restaurant_stats_service(restaurant_id)
        return RestaurantStatsResponse(**stats)
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(request)
        logger.error(
            f"Error fetching stats for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch statistics")


@router.delete(
    "/restaurants/{restaurant_id}",
    response_model=DeleteRestaurantResponse,
    summary="Delete Restaurant",
    description="Delete a restaurant and all associated data (cascade delete).",
    responses={
        200: {"description": "Restaurant deleted successfully"},
        401: {"description": "Invalid authentication"},
        403: {"description": "Access denied"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to delete restaurant"}
    }
)
def delete_restaurant(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a restaurant and all associated data. Accepts JWT only (user must own restaurant)."""
    # Only allow JWT authentication (not X-Vapi-Secret) for security
    require_restaurant_access(request, restaurant_id, None)

    try:
        deleted = delete_restaurant_service(restaurant_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        return DeleteRestaurantResponse(
            success=True,
            message="Restaurant and all associated data deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(request)
        logger.error(
            f"Error deleting restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete restaurant")
