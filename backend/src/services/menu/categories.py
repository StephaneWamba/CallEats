"""Service for categories management."""
from typing import List, Dict, Any, Optional
from src.services.infrastructure.database import get_supabase_service_client
from src.services.infrastructure.cache import clear_cache
import logging

logger = logging.getLogger(__name__)


def list_categories(restaurant_id: str) -> List[Dict[str, Any]]:
    """
    List all categories for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of category records, ordered by display_order then name

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("categories").select(
            "id, restaurant_id, name, description, display_order, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("display_order").order("name").execute()

        return resp.data or []
    except Exception as e:
        logger.error(
            f"Error fetching categories for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def get_category(restaurant_id: str, category_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single category.

    Args:
        restaurant_id: Restaurant UUID
        category_id: Category UUID

    Returns:
        Category record or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("categories").select(
            "id, restaurant_id, name, description, display_order, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", category_id).limit(1).execute()

        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(
            f"Error fetching category {category_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def create_category(
    restaurant_id: str,
    name: str,
    description: Optional[str] = None,
    display_order: int = 0
) -> Dict[str, Any]:
    """
    Create a new category.

    Args:
        restaurant_id: Restaurant UUID
        name: Category name
        description: Category description
        display_order: Display order

    Returns:
        Created category record

    Raises:
        ValueError: If category name already exists for restaurant
        Exception: If creation fails
    """
    supabase = get_supabase_service_client()

    # Check if category name already exists for this restaurant
    existing = supabase.table("categories").select("id").eq(
        "restaurant_id", restaurant_id).eq("name", name).limit(1).execute()
    if existing.data:
        raise ValueError(f"Category '{name}' already exists for this restaurant")

    try:
        resp = supabase.table("categories").insert({
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "display_order": display_order
        }).execute()

        if not resp.data:
            raise Exception("Failed to create category")

        category = resp.data[0]

        clear_cache(restaurant_id, "menu")  # Categories affect menu items

        return category
    except ValueError:
        raise
    except Exception as e:
        logger.error(
            f"Error creating category for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def update_category(
    restaurant_id: str,
    category_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    display_order: Optional[int] = None
) -> Optional[Dict[str, Any]]:
    """
    Update a category.

    Args:
        restaurant_id: Restaurant UUID
        category_id: Category UUID
        name: New name (optional)
        description: New description (optional)
        display_order: New display order (optional)

    Returns:
        Updated category record or None if not found

    Raises:
        ValueError: If new name conflicts with existing category
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    update_data = {}
    if name is not None:
        # Check if new name conflicts with existing category
        existing = supabase.table("categories").select("id").eq(
            "restaurant_id", restaurant_id).eq("name", name).neq("id", category_id).limit(1).execute()
        if existing.data:
            raise ValueError(f"Category '{name}' already exists for this restaurant")
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if display_order is not None:
        update_data["display_order"] = display_order

    if not update_data:
        return get_category(restaurant_id, category_id)

    try:
        resp = supabase.table("categories").update(update_data).eq(
            "restaurant_id", restaurant_id).eq("id", category_id).execute()

        if not resp.data:
            return None

        clear_cache(restaurant_id, "menu")

        return resp.data[0]
    except ValueError:
        raise
    except Exception as e:
        logger.error(
            f"Error updating category {category_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def delete_category(restaurant_id: str, category_id: str) -> bool:
    """
    Delete a category.

    Args:
        restaurant_id: Restaurant UUID
        category_id: Category UUID

    Returns:
        True if deleted, False if not found

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("categories").delete().eq(
            "restaurant_id", restaurant_id).eq("id", category_id).execute()

        if resp.data:
            clear_cache(restaurant_id, "menu")
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error deleting category {category_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


