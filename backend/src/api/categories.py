"""
Categories API endpoints.

Provides REST endpoints for managing menu item categories including
create, read, update, and delete operations.
"""
from fastapi import APIRouter, HTTPException, Header, Path, Request
from typing import Optional, List
from src.models.categories import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest
)
from src.services.menu.categories import (
    list_categories as list_categories_service,
    get_category as get_category_service,
    create_category as create_category_service,
    update_category as update_category_service,
    delete_category as delete_category_service
)
from src.services.infrastructure.auth import require_restaurant_access
from src.core.middleware.request_id import get_request_id
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
def list_categories(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """List all categories for a restaurant. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        categories = list_categories_service(restaurant_id)
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
def get_category(
    request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    category_id: str = Path(..., description="Category UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Get a single category by ID. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(request, restaurant_id, x_vapi_secret)

    try:
        category = get_category_service(restaurant_id, category_id)
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
def create_category(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    request: CreateCategoryRequest = ...,
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Create a new category. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        category = create_category_service(
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
def update_category(
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
        category = update_category_service(
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
def delete_category(
    http_request: Request,
    restaurant_id: str = Path(..., description="Restaurant UUID"),
    category_id: str = Path(..., description="Category UUID"),
    x_vapi_secret: Optional[str] = Header(
        None, alias="X-Vapi-Secret", description="Vapi webhook secret for authentication")
):
    """Delete a category. Accepts JWT or X-Vapi-Secret."""
    require_restaurant_access(http_request, restaurant_id, x_vapi_secret)

    try:
        deleted = delete_category_service(restaurant_id, category_id)
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
            extra={"request_id": request_id} if request_id else {}
        )
        raise HTTPException(
            status_code=500, detail="Failed to delete category")


