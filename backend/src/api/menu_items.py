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
from src.models.menu_item_modifiers import LinkModifierRequest, MenuItemModifierLink
from src.services.menu.items import (
    list_menu_items as list_menu_items_service,
    get_menu_item as get_menu_item_service,
    create_menu_item as create_menu_item_service,
    update_menu_item as update_menu_item_service,
    delete_menu_item as delete_menu_item_service
)
from src.services.infrastructure.auth import require_restaurant_access
from src.services.embeddings.service import add_embedding_task
from src.core.middleware.request_id import get_request_id
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
def list_menu_items(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all menu items for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        items = list_menu_items_service(restaurant_id)
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
def get_menu_item(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single menu item by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        item = get_menu_item_service(restaurant_id, item_id)
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
def create_menu_item(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateMenuItemRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new menu item. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        item = create_menu_item_service(
            restaurant_id=restaurant_id,
            name=request.name,
            description=request.description,
            price=request.price,
            category_id=request.category_id,
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
def update_menu_item(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    request: UpdateMenuItemRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a menu item. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        item = update_menu_item_service(
            restaurant_id=restaurant_id,
            item_id=item_id,
            name=request.name,
            description=request.description,
            price=request.price,
            category_id=request.category_id,
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
def delete_menu_item(
    http_request: Request,
    background_tasks: BackgroundTasks,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a menu item. Automatically triggers background embedding generation. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        deleted = delete_menu_item_service(restaurant_id, item_id)
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


# ============================================================================
# Modifier Linking Endpoints
# ============================================================================

@router.post(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers",
    summary="Link Modifier to Menu Item",
    description="Link a modifier to a menu item. Allows customer to select this modifier when ordering the item.",
    responses={
        201: {"description": "Modifier linked successfully"},
        400: {"description": "Invalid request or modifier already linked"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item or modifier not found"},
        500: {"description": "Failed to link modifier"}
    }
)
def link_modifier_to_item(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    request: LinkModifierRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Link a modifier to a menu item. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        from src.services.menu.item_modifiers import link_modifier_to_item
        link = link_modifier_to_item(
            restaurant_id=restaurant_id,
            menu_item_id=item_id,
            modifier_id=request.modifier_id,
            is_required=request.is_required,
            display_order=request.display_order
        )
        return {"success": True, "link": link}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error linking modifier to menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to link modifier")


@router.delete(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers/{modifier_id}",
    summary="Unlink Modifier from Menu Item",
    description="Remove a modifier from a menu item.",
    responses={
        200: {"description": "Modifier unlinked successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Link not found"},
        500: {"description": "Failed to unlink modifier"}
    }
)
def unlink_modifier_from_item(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    modifier_id: str = Path(..., description="Modifier UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Unlink a modifier from a menu item. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        from src.services.menu.item_modifiers import unlink_modifier_from_item
        unlinked = unlink_modifier_from_item(
            restaurant_id=restaurant_id,
            menu_item_id=item_id,
            modifier_id=modifier_id
        )
        if not unlinked:
            raise HTTPException(
                status_code=404, detail="Modifier is not linked to this menu item")
        return {"success": True, "message": "Modifier unlinked"}
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error unlinking modifier {modifier_id} from menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to unlink modifier")


@router.get(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers",
    response_model=List[MenuItemModifierLink],
    summary="List Modifiers for Menu Item",
    description="Get all modifiers linked to a menu item.",
    responses={
        200: {"description": "Modifiers retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item not found"},
        500: {"description": "Failed to fetch modifiers"}
    }
)
def list_modifiers_for_item(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all modifiers linked to a menu item. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        from src.services.menu.item_modifiers import get_modifiers_for_item
        from src.models.menu_item_modifiers import MenuItemModifierLink

        links = get_modifiers_for_item(restaurant_id, item_id)

        # Transform to response model
        result = []
        for link in links:
            result.append(MenuItemModifierLink(
                id=link["id"],
                menu_item_id=link["menu_item_id"],
                modifier_id=link["modifier_id"],
                modifier=link["modifier"],
                is_required=link.get("is_required", False),
                display_order=link.get("display_order", 0),
                created_at=link["created_at"]
            ))

        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(
            f"Error fetching modifiers for menu item {item_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch modifiers")
