"""
Restaurant management API endpoints.

Provides REST endpoints for creating and managing restaurants,
including automatic phone number assignment.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request
from typing import Optional
from src.models.restaurants import (
    CreateRestaurantRequest,
    UpdateRestaurantRequest,
    RestaurantResponse
)
from src.services.restaurants.service import (
    create_restaurant as create_restaurant_service,
    get_restaurant as get_restaurant_service,
    update_restaurant as update_restaurant_service
)
from src.services.phones.details import get_phone_details, test_phone_connectivity
from src.services.infrastructure.auth import require_auth, require_restaurant_access
from src.core.middleware.request_id import get_request_id
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
    """
    Create a new restaurant.

    Automatically assigns a phone number if assign_phone=True (default).
    - By default, tries existing unassigned phones first, then creates Twilio if needed.
    - Set force_twilio=True to skip existing phones and directly create a Twilio number.

    Phone creation succeeds if:
    - VAPI_API_KEY and PUBLIC_BACKEND_URL are configured
    - TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are configured (for new numbers)
    - Shared assistant exists
    - Twilio account has available numbers/quota

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
    """Update a restaurant. Accepts JWT or X-Vapi-Secret."""
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
    "/restaurants/{restaurant_id}/phone",
    summary="Get Phone Details",
    description="Get phone number details and status for a restaurant.",
    responses={
        200: {"description": "Phone details retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch phone details"}
    }
)
def get_phone(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """
    Get phone number details and status for a restaurant.

    Returns phone number, Vapi assignment status, provider, and connection status.
    Accepts JWT or X-Vapi-Secret.
    """
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        # Verify restaurant exists
        restaurant_data = get_restaurant_service(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        phone_details = get_phone_details(restaurant_id)

        if not phone_details:
            return {
                "phone_number": None,
                "connected": False,
                "status": "No phone number assigned to restaurant"
            }

        return phone_details
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching phone details for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch phone details")


@router.post(
    "/restaurants/{restaurant_id}/phone/test",
    summary="Test Phone Connectivity",
    description="Test phone number connectivity and verify assignment status.",
    responses={
        200: {"description": "Phone connectivity test completed"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to test phone connectivity"}
    }
)
def test_phone(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """
    Test phone number connectivity and status.

    Verifies that the phone number is assigned to the Vapi assistant and is operational.
    Accepts JWT or X-Vapi-Secret.
    """
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        # Verify restaurant exists
        restaurant_data = get_restaurant_service(restaurant_id)
        if not restaurant_data:
            raise HTTPException(
                status_code=404, detail="Restaurant not found")

        test_result = test_phone_connectivity(restaurant_id)
        return test_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error testing phone connectivity for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to test phone connectivity")
