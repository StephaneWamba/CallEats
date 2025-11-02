"""Service for menu items management."""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from src.services.infrastructure.database import get_supabase_service_client
from src.services.embeddings.service import generate_embedding
from src.services.infrastructure.cache import clear_cache
import logging
import asyncio

logger = logging.getLogger(__name__)


def list_menu_items(restaurant_id: str) -> List[Dict[str, Any]]:
    """
    List all menu items for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of menu item records

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("menu_items").select(
            "id, restaurant_id, name, description, price, category, available, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("category").order("name").execute()

        return resp.data or []
    except Exception as e:
        logger.error(
            f"Error fetching menu items for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def get_menu_item(restaurant_id: str, item_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single menu item.

    Args:
        restaurant_id: Restaurant UUID
        item_id: Menu item UUID

    Returns:
        Menu item record or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("menu_items").select(
            "id, restaurant_id, name, description, price, category, available, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", item_id).limit(1).execute()

        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(
            f"Error fetching menu item {item_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def create_menu_item(
    restaurant_id: str,
    name: str,
    description: Optional[str] = None,
    price: Decimal = Decimal("0.00"),
    category: str = "General",
    available: bool = True
) -> Dict[str, Any]:
    """
    Create a new menu item.

    Args:
        restaurant_id: Restaurant UUID
        name: Menu item name
        description: Item description
        price: Item price
        category: Item category
        available: Whether item is available

    Returns:
        Created menu item record

    Raises:
        Exception: If creation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("menu_items").insert({
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "price": float(price),
            "category": category,
            "available": available
        }).execute()

        if not resp.data:
            raise Exception("Failed to create menu item")

        item = resp.data[0]

        clear_cache(restaurant_id, "menu")

        return item
    except Exception as e:
        logger.error(
            f"Error creating menu item for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def update_menu_item(
    restaurant_id: str,
    item_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[Decimal] = None,
    category: Optional[str] = None,
    available: Optional[bool] = None
) -> Optional[Dict[str, Any]]:
    """
    Update a menu item.

    Args:
        restaurant_id: Restaurant UUID
        item_id: Menu item UUID
        name: New name (optional)
        description: New description (optional)
        price: New price (optional)
        category: New category (optional)
        available: New availability status (optional)

    Returns:
        Updated menu item record or None if not found

    Raises:
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = float(price)
    if category is not None:
        update_data["category"] = category
    if available is not None:
        update_data["available"] = available

    if not update_data:
        return get_menu_item(restaurant_id, item_id)

    try:
        resp = supabase.table("menu_items").update(update_data).eq(
            "restaurant_id", restaurant_id).eq("id", item_id).execute()

        if not resp.data:
            return None

        clear_cache(restaurant_id, "menu")

        return resp.data[0]
    except Exception as e:
        logger.error(
            f"Error updating menu item {item_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def delete_menu_item(restaurant_id: str, item_id: str) -> bool:
    """
    Delete a menu item.

    Args:
        restaurant_id: Restaurant UUID
        item_id: Menu item UUID

    Returns:
        True if deleted, False if not found

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("menu_items").delete().eq(
            "restaurant_id", restaurant_id).eq("id", item_id).execute()

        if resp.data:
            clear_cache(restaurant_id, "menu")
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error deleting menu item {item_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise
