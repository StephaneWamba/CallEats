"""Categories API router.

This module provides REST endpoints for managing menu item categories including
CRUD operations and display order management.

Endpoints:
    - GET /api/restaurants/{restaurant_id}/categories: List all categories
    - GET /api/restaurants/{restaurant_id}/categories/{category_id}: Get single category
    - POST /api/restaurants/{restaurant_id}/categories: Create category
    - PUT /api/restaurants/{restaurant_id}/categories/{category_id}: Update category
    - DELETE /api/restaurants/{restaurant_id}/categories/{category_id}: Delete category

Authentication:
    All endpoints accept JWT (frontend users) or X-Vapi-Secret (admin/scripts).
    Users can only access their own restaurant's categories.

Category Management:
    - Categories are unique per restaurant (name uniqueness enforced)
    - Display order controls UI sorting
    - Deleting a category sets menu items' category_id to NULL (cascade behavior)
    - Cache is automatically invalidated on changes

Usage:
    Create category:
        POST /api/restaurants/{restaurant_id}/categories
        Body: {"name": "Appetizers", "description": "...", "display_order": 0}
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request
from typing import Optional, List
from restaurant_voice_assistant.shared.models.categories import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest
)
from restaurant_voice_assistant.domain.menu.categories import (
    list_categories as list_categories_service,
    get_category as get_category_service,
    create_category as create_category_service,
    update_category as update_category_service,
    delete_category as delete_category_service
)
from restaurant_voice_assistant.infrastructure.auth.service import (
    require_restaurant_access
)
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get(
    "/restaurants/{restaurant_id}/categories",
    response_model=List[CategoryResponse],
    summary="List Categories",
    description="List all categories for a restaurant, ordered by display_order and name.",
    responses={
        200: {"description": "Categories retrieved successfully"},
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to fetch categories"}
    }
)
async def list_categories(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all categories for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        categories = await asyncio.to_thread(list_categories_service, restaurant_id)
        return categories
    except Exception as e:
        logger.error(
            f"Error listing categories for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch categories")


@router.get(
    "/restaurants/{restaurant_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Get Category",
    description="Get a single category by ID.",
    responses={
        200: {"description": "Category retrieved successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Category not found"},
        500: {"description": "Failed to fetch category"}
    }
)
async def get_category(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    category_id: str = Path(..., description="Category UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single category by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        category = await asyncio.to_thread(get_category_service, restaurant_id, category_id)
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found")
        return category
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching category {category_id} for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise HTTPException(
            status_code=500, detail="Failed to fetch category")


@router.post(
    "/restaurants/{restaurant_id}/categories",
    response_model=CategoryResponse,
    summary="Create Category",
    description="Create a new category for menu items.",
    responses={
        201: {"description": "Category created successfully"},
        400: {"description": "Category name already exists"},
        401: {"description": "Invalid authentication"},
        500: {"description": "Failed to create category"}
    }
)
async def create_category(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateCategoryRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new category. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        category = await asyncio.to_thread(
            create_category_service,
            restaurant_id=restaurant_id,
            name=request.name,
            description=request.description,
            display_order=request.display_order
        )
        return CategoryResponse(**category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error creating category for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to create category")


@router.put(
    "/restaurants/{restaurant_id}/categories/{category_id}",
    response_model=CategoryResponse,
    summary="Update Category",
    description="Update a category. All fields are optional.",
    responses={
        200: {"description": "Category updated successfully"},
        400: {"description": "Category name conflicts with existing"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Category not found"},
        500: {"description": "Failed to update category"}
    }
)
async def update_category(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    category_id: str = Path(..., description="Category UUID"),
    request: UpdateCategoryRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Update a category. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        category = await asyncio.to_thread(
            update_category_service,
            restaurant_id=restaurant_id,
            category_id=category_id,
            name=request.name,
            description=request.description,
            display_order=request.display_order
        )
        if not category:
            raise HTTPException(
                status_code=404, detail="Category not found")
        return CategoryResponse(**category)
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error updating category {category_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to update category")


@router.delete(
    "/restaurants/{restaurant_id}/categories/{category_id}",
    summary="Delete Category",
    description="Delete a category. Menu items with this category will have category_id set to NULL.",
    responses={
        200: {"description": "Category deleted successfully"},
        401: {"description": "Invalid authentication"},
        404: {"description": "Category not found"},
        500: {"description": "Failed to delete category"}
    }
)
async def delete_category(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    category_id: str = Path(..., description="Category UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a category. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        deleted = await asyncio.to_thread(delete_category_service, restaurant_id, category_id)
        if not deleted:
            raise HTTPException(
                status_code=404, detail="Category not found")
        return {"success": True, "message": "Category deleted"}
    except HTTPException:
        raise
    except Exception as e:
        request_id = get_request_id(http_request)
        logger.error(
            f"Error deleting category {category_id} for restaurant {restaurant_id}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete category")
