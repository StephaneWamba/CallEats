"""
Menu items API endpoints.

Provides REST endpoints for managing menu items including
create, read, update, and delete operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks
from typing import Optional, List
from src.models.menu_items import (
    MenuItemResponse,
    CreateMenuItemRequest,
    UpdateMenuItemRequest
)
from src.services.menu_service import (
    list_menu_items,
    get_menu_item,
    create_menu_item,
    update_menu_item,
    delete_menu_item
)
from src.services.auth import verify_vapi_secret
from src.services.embedding_service import add_embedding_task
from src.middleware.request_id import get_request_id
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=List[MenuItemResponse],
    summary="List Menu Items",
    description="List all menu items for a restaurant, ordered by category and name.",
    responses={
        200: {"description": "Menu items retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to fetch menu items"}
    }
)
def list_menu_items_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all menu items for a restaurant."""
    verify_vapi_secret(x_vapi_secret)

    try:
        items = list_menu_items(restaurant_id)
        return items
    except Exception as e:
        logger.error(
            f"Error listing menu items for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch menu items")


@router.get(
    "/restaurants/{restaurant_id}/menu-items/{item_id}",
    response_model=MenuItemResponse,
    summary="Get Menu Item",
    description="Get a single menu item by ID.",
    responses={
        200: {"description": "Menu item retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item not found"},
        500: {"description": "Failed to fetch menu item"}
    }
)
def get_menu_item_endpoint(
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single menu item by ID."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = get_menu_item(restaurant_id, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Menu item not found")
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching menu item {item_id} for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch menu item")


@router.post(
    "/restaurants/{restaurant_id}/menu-items",
    response_model=MenuItemResponse,
    summary="Create Menu Item",
    description="Create a new menu item. Automatically invalidates menu cache.",
    responses={
        201: {"description": "Menu item created successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Restaurant not found"},
        500: {"description": "Failed to create menu item"}
    }
)
def create_menu_item_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateMenuItemRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new menu item. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = create_menu_item(
            restaurant_id=restaurant_id,
            name=request.name,
            description=request.description,
            price=request.price,
            category=request.category,
            available=request.available
        )

        add_embedding_task(background_tasks, restaurant_id, "menu")

        return MenuItemResponse(**item)
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error creating menu item for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to create menu item")


@router.put(
    "/restaurants/{restaurant_id}/menu-items/{item_id}",
    response_model=MenuItemResponse,
    summary="Update Menu Item",
    description="Update a menu item. All fields are optional. Automatically invalidates menu cache.",
    responses={
        200: {"description": "Menu item updated successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item not found"},
        500: {"description": "Failed to update menu item"}
    }
)
def update_menu_item_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    request: UpdateMenuItemRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a menu item. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        item = update_menu_item(
            restaurant_id=restaurant_id,
            item_id=item_id,
            name=request.name,
            description=request.description,
            price=request.price,
            category=request.category,
            available=request.available
        )
        if not item:
            raise HTTPException(
                status_code=404, detail="Menu item not found")

        add_embedding_task(background_tasks, restaurant_id, "menu")

        return MenuItemResponse(**item)
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating menu item {item_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update menu item")


@router.delete(
    "/restaurants/{restaurant_id}/menu-items/{item_id}",
    summary="Delete Menu Item",
    description="Delete a menu item. Automatically invalidates menu cache.",
    responses={
        200: {"description": "Menu item deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item not found"},
        500: {"description": "Failed to delete menu item"}
    }
)
def delete_menu_item_endpoint(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a menu item. Automatically triggers background embedding generation."""
    verify_vapi_secret(x_vapi_secret)

    try:
        deleted = delete_menu_item(restaurant_id, item_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Menu item not found")

        add_embedding_task(background_tasks, restaurant_id, "menu")

        return {"success": True, "message": "Menu item deleted"}
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting menu item {item_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id} if request_id else {}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete menu item")
