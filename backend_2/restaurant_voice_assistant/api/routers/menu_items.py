"""Menu items API router.

This module provides REST endpoints for managing menu items including
CRUD operations, modifier linking, and automatic embedding generation.

Endpoints:
    - GET /api/restaurants/{restaurant_id}/menu-items: List all menu items
    - GET /api/restaurants/{restaurant_id}/menu-items/{item_id}: Get single item
    - POST /api/restaurants/{restaurant_id}/menu-items: Create menu item
    - PUT /api/restaurants/{restaurant_id}/menu-items/{item_id}: Update menu item
    - DELETE /api/restaurants/{restaurant_id}/menu-items/{item_id}: Delete menu item
    - POST /api/restaurants/{restaurant_id}/menu-items/{item_id}/image: Upload menu item image
    - DELETE /api/restaurants/{restaurant_id}/menu-items/{item_id}/image: Delete menu item image
    - POST /api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers: Link modifier
    - DELETE /api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers/{modifier_id}: Unlink modifier

Authentication:
    All endpoints accept JWT (frontend users) or X-Vapi-Secret (admin/scripts).
    Users can only access their own restaurant's menu items.

Embedding Generation:
    Create/update/delete operations automatically trigger background embedding
    generation to keep the knowledge base up-to-date for voice assistant queries.

Cache Management:
    All data changes automatically invalidate the menu cache to ensure fresh
    search results.

Usage:
    Create menu item:
        POST /api/restaurants/{restaurant_id}/menu-items
        Body: {"name": "...", "description": "...", "price": 12.99, "category_id": "..."}
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request, BackgroundTasks, UploadFile, File
from typing import Optional, List
from restaurant_voice_assistant.shared.models.menu_items import (
    MenuItemResponse,
    CreateMenuItemRequest,
    UpdateMenuItemRequest
)
from restaurant_voice_assistant.shared.models.menu_item_modifiers import (
    LinkModifierRequest,
    MenuItemModifierLink
)
from restaurant_voice_assistant.domain.menu.items import (
    list_menu_items as list_menu_items_service,
    get_menu_item as get_menu_item_service,
    create_menu_item as create_menu_item_service,
    update_menu_item as update_menu_item_service,
    delete_menu_item as delete_menu_item_service
)
from restaurant_voice_assistant.domain.menu.images import (
    upload_menu_item_image,
    delete_menu_item_image
)
from restaurant_voice_assistant.domain.menu.item_modifiers import (
    link_modifier_to_item,
    unlink_modifier_from_item,
    get_modifiers_for_item
)
from restaurant_voice_assistant.infrastructure.auth.service import (
    require_restaurant_access
)
from restaurant_voice_assistant.infrastructure.openai.embeddings import (
    add_embedding_task
)
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
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
    description="Get a single menu item by ID with linked modifiers.",
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
    """Get a single menu item by ID with linked modifiers. Accepts JWT or X-Vapi-Secret."""
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
    description="Create a new menu item. Automatically triggers background embedding generation.",
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
    description="Update a menu item. All fields are optional. Automatically triggers background embedding generation.",
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
    description="Delete a menu item. Automatically triggers background embedding generation.",
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
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete menu item")


@router.post(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers",
    response_model=MenuItemModifierLink,
    summary="Link Modifier to Menu Item",
    description="Link a modifier to a menu item. Creates a many-to-many relationship.",
    responses={
        201: {"description": "Modifier linked successfully"},
        400: {"description": "Modifier already linked or invalid request"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item or modifier not found"},
        500: {"description": "Failed to link modifier"}
    }
)
def link_modifier(
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
        link = link_modifier_to_item(
            restaurant_id=restaurant_id,
            menu_item_id=item_id,
            modifier_id=request.modifier_id,
            is_required=request.is_required,
            display_order=request.display_order
        )
        return MenuItemModifierLink(**link)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error linking modifier {request.modifier_id} to menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to link modifier")


@router.delete(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers/{modifier_id}",
    summary="Unlink Modifier from Menu Item",
    description="Unlink a modifier from a menu item.",
    responses={
        200: {"description": "Modifier unlinked successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Link not found"},
        500: {"description": "Failed to unlink modifier"}
    }
)
def unlink_modifier(
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
        unlinked = unlink_modifier_from_item(
            restaurant_id=restaurant_id,
            menu_item_id=item_id,
            modifier_id=modifier_id
        )
        if not unlinked:
            raise HTTPException(
                status_code=404, detail="Modifier link not found")
        return {"success": True, "message": "Modifier unlinked"}
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error unlinking modifier {modifier_id} from menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to unlink modifier")


@router.post(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/image",
    summary="Upload Menu Item Image",
    description="Upload an image for a menu item. Stores image in Supabase Storage and updates database.",
    responses={
        200: {"description": "Image uploaded successfully"},
        400: {"description": "Invalid file type or size"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item not found"},
        500: {"description": "Failed to upload image"}
    }
)
async def upload_image(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    file: UploadFile = File(...,
                            description="Image file (jpg, png, webp, max 5MB)"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Upload an image for a menu item. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        # Verify menu item exists
        item = get_menu_item_service(restaurant_id, item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Menu item not found")

        # Read file content
        file_content = await file.read()

        # Upload image
        image_url = upload_menu_item_image(
            restaurant_id=restaurant_id,
            item_id=item_id,
            file_content=file_content,
            filename=file.filename or "image.jpg",
            content_type=file.content_type
        )

        return {
            "image_url": image_url,
            "message": "Image uploaded successfully"
        }
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error uploading image for menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to upload image")


@router.delete(
    "/restaurants/{restaurant_id}/menu-items/{item_id}/image",
    summary="Delete Menu Item Image",
    description="Delete an image for a menu item. Removes image from Supabase Storage and updates database.",
    responses={
        200: {"description": "Image deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Menu item or image not found"},
        500: {"description": "Failed to delete image"}
    }
)
def delete_image(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    item_id: str = Path(..., description="Menu item UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete an image for a menu item. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        deleted = delete_menu_item_image(restaurant_id, item_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Image not found")

        return {
            "success": True,
            "message": "Image deleted successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting image for menu item {item_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete image")

