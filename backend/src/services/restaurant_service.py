"""Service for restaurant management."""
from typing import Optional, Dict, Any
from uuid import uuid4
from src.services.supabase_client import get_supabase_service_client
from src.services.phone_service import assign_phone_to_restaurant
import logging

logger = logging.getLogger(__name__)


def create_restaurant(
    name: str,
    api_key: Optional[str] = None,
    assign_phone: bool = True,
    force_twilio: bool = False
) -> Dict[str, Any]:
    """
    Create a new restaurant.

    Args:
        name: Restaurant name
        api_key: Optional custom API key (auto-generated if not provided)
        assign_phone: Whether to automatically assign phone number
        force_twilio: Force Twilio phone creation (skip existing phones)

    Returns:
        Dictionary with restaurant data including phone_number if assigned

    Raises:
        Exception: If restaurant creation fails
    """
    supabase = get_supabase_service_client()

    final_api_key = api_key or f"api_key_{uuid4().hex[:16]}"

    result = supabase.table("restaurants").insert({
        "name": name,
        "api_key": final_api_key
    }).execute()

    if not result.data:
        raise Exception("Failed to create restaurant")

    restaurant_data = result.data[0]
    restaurant_id = restaurant_data["id"]
    phone_number = None

    if assign_phone:
        try:
            phone_number = assign_phone_to_restaurant(
                restaurant_id, force_twilio=force_twilio)
        except Exception as e:
            logger.warning(
                f"Failed to assign phone number to restaurant {restaurant_id}: {e}")

    return {
        "id": restaurant_id,
        "name": restaurant_data["name"],
        "api_key": restaurant_data["api_key"],
        "phone_number": phone_number,
        "created_at": restaurant_data["created_at"],
        "updated_at": restaurant_data.get("updated_at")
    }


def get_restaurant(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single restaurant by ID.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        Dictionary with restaurant data including phone_number if assigned, None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("restaurants").select(
            "id, name, api_key, created_at, updated_at"
        ).eq("id", restaurant_id).limit(1).execute()

        if not resp.data:
            return None

        restaurant_data = resp.data[0]
        
        phone_number = None
        try:
            phone_mappings = supabase.table("restaurant_phone_mappings").select(
                "phone_number"
            ).eq("restaurant_id", restaurant_id).limit(1).execute()
            
            if phone_mappings.data:
                phone_number = phone_mappings.data[0].get("phone_number")
        except Exception as e:
            logger.warning(f"Error fetching phone mapping for restaurant {restaurant_id}: {e}")

        return {
            "id": restaurant_data["id"],
            "name": restaurant_data["name"],
            "api_key": restaurant_data["api_key"],
            "phone_number": phone_number,
            "created_at": restaurant_data["created_at"],
            "updated_at": restaurant_data.get("updated_at")
        }
    except Exception as e:
        logger.error(
            f"Error fetching restaurant {restaurant_id}: {e}", exc_info=True)
        raise


def update_restaurant(
    restaurant_id: str,
    name: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Update a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        name: New restaurant name (optional)

    Returns:
        Updated restaurant data or None if not found

    Raises:
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    update_data = {}
    if name is not None:
        update_data["name"] = name

    if not update_data:
        return get_restaurant(restaurant_id)

    try:
        resp = supabase.table("restaurants").update(update_data).eq(
            "id", restaurant_id).execute()

        if not resp.data:
            return None

        restaurant_data = resp.data[0]
        
        phone_number = None
        try:
            phone_mappings = supabase.table("restaurant_phone_mappings").select(
                "phone_number"
            ).eq("restaurant_id", restaurant_id).limit(1).execute()
            
            if phone_mappings.data:
                phone_number = phone_mappings.data[0].get("phone_number")
        except Exception as e:
            logger.warning(f"Error fetching phone mapping for restaurant {restaurant_id}: {e}")

        return {
            "id": restaurant_data["id"],
            "name": restaurant_data["name"],
            "api_key": restaurant_data["api_key"],
            "phone_number": phone_number,
            "created_at": restaurant_data["created_at"],
            "updated_at": restaurant_data.get("updated_at")
        }
    except Exception as e:
        logger.error(
            f"Error updating restaurant {restaurant_id}: {e}", exc_info=True)
        raise

