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
            "id, restaurant_id, name, description, price, category_id, category, available, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("category").order("name").execute()
        
        # Fetch category names for items that have category_id
        if resp.data:
            category_ids = {item.get("category_id") for item in resp.data if item.get("category_id")}
            if category_ids:
                cat_resp = supabase.table("categories").select("id, name").in_("id", list(category_ids)).execute()
                category_map = {cat["id"]: cat["name"] for cat in (cat_resp.data or [])}
                
                # Add category name to items
                for item in resp.data:
                    if item.get("category_id") and item["category_id"] in category_map:
                        item["category"] = category_map[item["category_id"]]
                    elif not item.get("category"):
                        item["category"] = None

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
            "id, restaurant_id, name, description, price, category_id, category, available, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", item_id).limit(1).execute()

        if resp.data:
            item = resp.data[0]
            
            # Get category name if category_id exists
            if item.get("category_id"):
                cat_resp = supabase.table("categories").select("name").eq("id", item["category_id"]).limit(1).execute()
                if cat_resp.data:
                    item["category"] = cat_resp.data[0]["name"]
            
            # Get linked modifiers
            from src.services.menu.item_modifiers import get_modifiers_for_item
            try:
                modifiers = get_modifiers_for_item(restaurant_id, item_id)
                item["modifiers"] = [link["modifier"] for link in modifiers]
            except Exception:
                item["modifiers"] = []
            return item
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
    category_id: Optional[str] = None,
    available: bool = True
) -> Dict[str, Any]:
    """
    Create a new menu item.

    Args:
        restaurant_id: Restaurant UUID
        name: Menu item name
        description: Item description
        price: Item price
        category_id: Category UUID (optional)
        available: Whether item is available

    Returns:
        Created menu item record

    Raises:
        Exception: If creation fails
    """
    supabase = get_supabase_service_client()

    # Validate category_id if provided
    if category_id:
        cat_resp = supabase.table("categories").select("id").eq(
            "id", category_id).eq("restaurant_id", restaurant_id).limit(1).execute()
        if not cat_resp.data:
            raise ValueError(f"Category {category_id} not found or doesn't belong to restaurant")

    try:
        insert_data = {
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "price": float(price),
            "available": available
        }
        if category_id:
            insert_data["category_id"] = category_id
        
        resp = supabase.table("menu_items").insert(insert_data).execute()

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
    category_id: Optional[str] = None,
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
        category_id: New category UUID (optional)
        available: New availability status (optional)

    Returns:
        Updated menu item record or None if not found

    Raises:
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    # Validate category_id if provided
    if category_id is not None:
        if category_id:  # If not None and not empty string
            cat_resp = supabase.table("categories").select("id").eq(
                "id", category_id).eq("restaurant_id", restaurant_id).limit(1).execute()
            if not cat_resp.data:
                raise ValueError(f"Category {category_id} not found or doesn't belong to restaurant")

    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = float(price)
    if category_id is not None:
        update_data["category_id"] = category_id
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
