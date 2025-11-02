"""Service for menu item modifier linking."""
from typing import List, Dict, Any, Optional
from src.services.infrastructure.database import get_supabase_service_client
from src.services.infrastructure.cache import clear_cache
import logging

logger = logging.getLogger(__name__)


def link_modifier_to_item(
    restaurant_id: str,
    menu_item_id: str,
    modifier_id: str,
    is_required: bool = False,
    display_order: int = 0
) -> Dict[str, Any]:
    """
    Link a modifier to a menu item.

    Args:
        restaurant_id: Restaurant UUID (for validation)
        menu_item_id: Menu item UUID
        modifier_id: Modifier UUID
        is_required: Whether modifier is required
        display_order: Display order

    Returns:
        Created link record

    Raises:
        ValueError: If menu item or modifier doesn't exist or belongs to different restaurant
        Exception: If linking fails
    """
    supabase = get_supabase_service_client()

    # Verify menu item exists and belongs to restaurant
    item_resp = supabase.table("menu_items").select("id").eq(
        "id", menu_item_id).eq("restaurant_id", restaurant_id).limit(1).execute()
    if not item_resp.data:
        raise ValueError("Menu item not found or doesn't belong to restaurant")

    # Verify modifier exists and belongs to restaurant
    mod_resp = supabase.table("modifiers").select("id").eq(
        "id", modifier_id).eq("restaurant_id", restaurant_id).limit(1).execute()
    if not mod_resp.data:
        raise ValueError("Modifier not found or doesn't belong to restaurant")

    try:
        resp = supabase.table("menu_item_modifiers").insert({
            "menu_item_id": menu_item_id,
            "modifier_id": modifier_id,
            "is_required": is_required,
            "display_order": display_order
        }).execute()

        if not resp.data:
            raise Exception("Failed to create link")

        link = resp.data[0]
        clear_cache(restaurant_id, "menu")

        return link
    except Exception as e:
        error_str = str(e).lower()
        if "unique" in error_str or "duplicate" in error_str:
            raise ValueError("Modifier is already linked to this menu item")
        logger.error(
            f"Error linking modifier {modifier_id} to menu item {menu_item_id}: {e}",
            exc_info=True
        )
        raise


def unlink_modifier_from_item(
    restaurant_id: str,
    menu_item_id: str,
    modifier_id: str
) -> bool:
    """
    Unlink a modifier from a menu item.

    Args:
        restaurant_id: Restaurant UUID (for validation)
        menu_item_id: Menu item UUID
        modifier_id: Modifier UUID

    Returns:
        True if unlinked, False if not found

    Raises:
        Exception: If unlinking fails
    """
    supabase = get_supabase_service_client()

    # Verify menu item belongs to restaurant
    item_resp = supabase.table("menu_items").select("id").eq(
        "id", menu_item_id).eq("restaurant_id", restaurant_id).limit(1).execute()
    if not item_resp.data:
        raise ValueError("Menu item not found or doesn't belong to restaurant")

    try:
        resp = supabase.table("menu_item_modifiers").delete().eq(
            "menu_item_id", menu_item_id).eq("modifier_id", modifier_id).execute()

        if resp.data:
            clear_cache(restaurant_id, "menu")
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error unlinking modifier {modifier_id} from menu item {menu_item_id}: {e}",
            exc_info=True
        )
        raise


def get_modifiers_for_item(
    restaurant_id: str,
    menu_item_id: str
) -> List[Dict[str, Any]]:
    """
    Get all modifiers linked to a menu item.

    Args:
        restaurant_id: Restaurant UUID (for validation)
        menu_item_id: Menu item UUID

    Returns:
        List of linked modifiers with full details

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    # Verify menu item belongs to restaurant
    item_resp = supabase.table("menu_items").select("id").eq(
        "id", menu_item_id).eq("restaurant_id", restaurant_id).limit(1).execute()
    if not item_resp.data:
        raise ValueError("Menu item not found or doesn't belong to restaurant")

    try:
        # Join with modifiers table to get full modifier details
        resp = supabase.table("menu_item_modifiers").select(
            "id, menu_item_id, modifier_id, is_required, display_order, created_at, "
            "modifiers(id, restaurant_id, name, description, price, created_at, updated_at)"
        ).eq("menu_item_id", menu_item_id).order("display_order").order("created_at").execute()

        if not resp.data:
            return []

        # Flatten the response structure
        results = []
        for link in resp.data:
            modifier_data = link.get("modifiers", {})
            if modifier_data:
                results.append({
                    "id": link["id"],
                    "menu_item_id": link["menu_item_id"],
                    "modifier_id": link["modifier_id"],
                    "is_required": link.get("is_required", False),
                    "display_order": link.get("display_order", 0),
                    "created_at": link["created_at"],
                    "modifier": modifier_data
                })

        return results
    except Exception as e:
        logger.error(
            f"Error fetching modifiers for menu item {menu_item_id}: {e}",
            exc_info=True
        )
        raise


