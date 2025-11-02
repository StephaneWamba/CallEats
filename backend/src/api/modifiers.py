"""
Modifiers API endpoints.

Provides REST endpoints for managing modifiers including
create, read, update, and delete operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks
from typing import Optional, List
from src.models.modifiers import (
    ModifierResponse,
    CreateModifierRequest,
    UpdateModifierRequest
)
from src.services.menu.modifiers import (
    list_modifiers,
    get_modifier,
    create_modifier,
    update_modifier,
    delete_modifier
)
from src.services.infrastructure.auth import verify_vapi_secret
from src.services.embeddings.service import add_embedding_task
from src.core.middleware.request_id import get_request_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/restaurants/{restaurant_id}/modifiers",
    response_model=List[ModifierResponse],
    summary="List Modifiers",
    description="List all modifiers for a restaurant, ordered by name.",
    responses={
        200: {"description": "Modifiers retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch modifiers"}
    }
)
def list_modifiers_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all modifiers for a restaurant."""
    verify_vapi_secret(x_vapi_secret)

    try:
        items = list_modifiers(restaurant_id)
        return items
    except Exception as e:
        logger.error(
            f"Error listing modifiers for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch modifiers")


@router.get(
    "/restaurants/{restaurant_id}/modifiers/{modifier_id}",
    response_model=ModifierResponse,
    summary="Get Modifier",
    description="Get a single modifier by ID.",
    responses={
        200: {"description": "Modifier retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Modifier not found"},
        500: {"description": "Failed to fetch modifier"}
    }
)
def get_modifier_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    modifier_id: str = Path(..., description="Modifier UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single modifier by ID."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = get_modifier(restaurant_id, modifier_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Modifier not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching modifier {modifier_id} for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch modifier")


@router.post(
    "/restaurants/{restaurant_id}/modifiers",
    response_model=ModifierResponse,
    summary="Create Modifier",
    description="Create a new modifier. Automatically invalidates modifiers cache.",
    responses={
        201: {"description": "Modifier created successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to create modifier"}
    }
)
def create_modifier_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateModifierRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new modifier. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = create_modifier(
            restaurant_id=restaurant_id,
            name=request.name,
            description=request.description,
            price=request.price
        )

        add_embedding_task(background_tasks, restaurant_id, "modifiers")

        return ModifierResponse(**item)
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error creating modifier for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to create modifier")


@router.put(
    "/restaurants/{restaurant_id}/modifiers/{modifier_id}",
    response_model=ModifierResponse,
    summary="Update Modifier",
    description="Update a modifier. All fields are optional. Automatically invalidates modifiers cache.",
    responses={
        200: {"description": "Modifier updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Modifier not found"},
        500: {"description": "Failed to update modifier"}
    }
)
def update_modifier_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    modifier_id: str = Path(..., description="Modifier UUID"),
    request: UpdateModifierRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a modifier. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = update_modifier(
            restaurant_id=restaurant_id,
            modifier_id=modifier_id,
            name=request.name,
            description=request.description,
            price=request.price
        )
        if not item:
            raise HTTPException(
                status_code=404, detail="Modifier not found")

        add_embedding_task(background_tasks, restaurant_id, "modifiers")

        return ModifierResponse(**item)
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating modifier {modifier_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update modifier")


@router.delete(
    "/restaurants/{restaurant_id}/modifiers/{modifier_id}",
    summary="Delete Modifier",
    description="Delete a modifier. Automatically invalidates modifiers cache.",
    responses={
        200: {"description": "Modifier deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Modifier not found"},
        500: {"description": "Failed to delete modifier"}
    }
)
def delete_modifier_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    modifier_id: str = Path(..., description="Modifier UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a modifier. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        deleted = delete_modifier(restaurant_id, modifier_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Modifier not found")

        add_embedding_task(background_tasks, restaurant_id, "modifiers")

        return {"success": True, "message": "Modifier deleted"}
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting modifier {modifier_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete modifier")
