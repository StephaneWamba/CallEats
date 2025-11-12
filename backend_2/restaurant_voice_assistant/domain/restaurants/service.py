"""Restaurant domain service.

This module provides business logic for restaurant management including:
    - Restaurant CRUD operations
    - Phone number assignment integration
    - Multi-tenant data isolation
    - Dashboard statistics

Key Features:
    - Automatic phone number assignment on creation
    - Restaurant-scoped queries (multi-tenancy)
    - Phone number lookup and association
    - API key generation
    - Dashboard statistics aggregation

Usage:
    from restaurant_voice_assistant.domain.restaurants.service import (
        create_restaurant,
        get_restaurant,
        update_restaurant,
        get_restaurant_stats
    )
    
    restaurant = create_restaurant(
        name="My Restaurant",
        assign_phone=True
    )
    stats = get_restaurant_stats(restaurant_id="...")
"""
from typing import Optional, Dict, Any
from uuid import uuid4
from datetime import datetime, timezone
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.infrastructure.database.transactions import transaction
from restaurant_voice_assistant.domain.phones.service import assign_phone_to_restaurant
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.infrastructure.vapi.client import VapiClient
from restaurant_voice_assistant.core.exceptions import VapiAPIError, RestaurantVoiceAssistantError
import logging

logger = logging.getLogger(__name__)


def create_restaurant(
    name: str,
    api_key: Optional[str] = None,
    assign_phone: bool = True,
    force_twilio: bool = False
) -> Dict[str, Any]:
    """Create a new restaurant.

    Uses transaction context to ensure atomicity. If phone assignment fails,
    the restaurant creation is still committed (phone assignment is non-critical).

    Args:
        name: Restaurant name
        api_key: Optional custom API key (auto-generated if not provided)
        assign_phone: Whether to automatically assign phone number
        force_twilio: Force Twilio phone creation (skip existing phones)

    Returns:
        Dictionary with restaurant data including phone_number if assigned

    Raises:
        RestaurantVoiceAssistantError: If restaurant creation fails
    """
    final_api_key = api_key or f"api_key_{uuid4().hex[:16]}"

    # Use transaction context for atomic operations
    with transaction() as supabase:
        result = supabase.table("restaurants").insert({
            "name": name,
            "api_key": final_api_key
        }).execute()

        if not result.data:
            raise RestaurantVoiceAssistantError("Failed to create restaurant")

        restaurant_data = result.data[0]
        restaurant_id = restaurant_data["id"]

    # Phone assignment is done outside transaction as it's non-critical
    # and involves external API calls (Vapi/Twilio)
    phone_number = None
    if assign_phone:
        try:
            phone_number = assign_phone_to_restaurant(
                restaurant_id, force_twilio=force_twilio)
        except Exception as e:
            logger.warning(
                f"Failed to assign phone number to restaurant {restaurant_id}: {e}")
            # Restaurant is still created, just without phone number

    return {
        "id": restaurant_id,
        "name": restaurant_data["name"],
        "api_key": restaurant_data["api_key"],
        "phone_number": phone_number,
        "created_at": restaurant_data["created_at"],
        "updated_at": restaurant_data.get("updated_at")
    }


def get_restaurant(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """Get a single restaurant by ID.

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
            logger.warning(
                f"Error fetching phone mapping for restaurant {restaurant_id}: {e}")

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
    """Update a restaurant.

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
            logger.warning(
                f"Error fetching phone mapping for restaurant {restaurant_id}: {e}")

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


def get_restaurant_stats(restaurant_id: str) -> Dict[str, Any]:
    """Get dashboard statistics for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        Dictionary with statistics:
        - total_calls_today: Count of calls today
        - menu_items_count: Total menu items
        - phone_status: "active" or "inactive"
        - categories_count: Total categories

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        # Get start of today (UTC)
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        today_start_iso = today_start.isoformat()

        # Count calls today
        calls_resp = supabase.table("call_history").select(
            "id", count="exact"
        ).eq("restaurant_id", restaurant_id).gte(
            "started_at", today_start_iso
        ).execute()
        total_calls_today = calls_resp.count if hasattr(
            calls_resp, 'count') else len(calls_resp.data or [])

        # Count menu items
        menu_items_resp = supabase.table("menu_items").select(
            "id", count="exact"
        ).eq("restaurant_id", restaurant_id).execute()
        menu_items_count = menu_items_resp.count if hasattr(
            menu_items_resp, 'count') else len(menu_items_resp.data or [])

        # Check phone status
        phone_mappings = supabase.table("restaurant_phone_mappings").select(
            "phone_number"
        ).eq("restaurant_id", restaurant_id).limit(1).execute()
        phone_status = "active" if phone_mappings.data else "inactive"

        # Count categories
        categories_resp = supabase.table("categories").select(
            "id", count="exact"
        ).eq("restaurant_id", restaurant_id).execute()
        categories_count = categories_resp.count if hasattr(
            categories_resp, 'count') else len(categories_resp.data or [])

        return {
            "total_calls_today": total_calls_today,
            "menu_items_count": menu_items_count,
            "phone_status": phone_status,
            "categories_count": categories_count
        }
    except Exception as e:
        logger.error(
            f"Error fetching stats for restaurant {restaurant_id}: {e}", exc_info=True)
        raise


def delete_restaurant(restaurant_id: str) -> bool:
    """Delete a restaurant and all associated data.

    Cascade deletion order:
    1. Get phone number from restaurant_phone_mappings
    2. Unassign phone number from Vapi assistant (set assistantId to None)
    3. Delete restaurant (cascade delete handles all related records)

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        True if deleted successfully, False if not found

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        # Step 1: Get phone number before deletion
        phone_mappings = supabase.table("restaurant_phone_mappings").select(
            "phone_number"
        ).eq("restaurant_id", restaurant_id).limit(1).execute()

        phone_number = None
        if phone_mappings.data:
            phone_number = phone_mappings.data[0].get("phone_number")

        # Step 2: Unassign phone number from Vapi assistant if exists
        if phone_number:
            try:
                settings = get_settings()
                if settings.vapi_api_key:
                    client = VapiClient(api_key=settings.vapi_api_key)
                    phone_numbers = client.list_phone_numbers()

                    # Find matching phone number
                    phone_clean = phone_number.replace(" ", "").replace(
                        "(", "").replace(")", "").replace("-", "")

                    for pn in phone_numbers:
                        pn_number = pn.get("number", "")
                        pn_clean = pn_number.replace(" ", "").replace(
                            "(", "").replace(")", "").replace("-", "")

                        if pn_clean == phone_clean or pn_clean in phone_clean or phone_clean in pn_clean:
                            phone_id = pn.get("id")
                            if phone_id:
                                # Unassign from assistant (set assistantId to None)
                                client.update_phone_number(
                                    phone_id, {"assistantId": None})
                                logger.info(
                                    f"Unassigned phone number {phone_number} from Vapi assistant")
                            break
            except VapiAPIError as e:
                logger.warning(
                    f"Failed to unassign phone number from Vapi: {e}")
            except Exception as e:
                logger.warning(f"Error unassigning phone number: {e}")

        # Step 3: Delete restaurant (cascade delete handles all related records)
        resp = supabase.table("restaurants").delete().eq(
            "id", restaurant_id).execute()

        if resp.data:
            logger.info(f"Successfully deleted restaurant {restaurant_id}")
            return True
        return False

    except Exception as e:
        logger.error(
            f"Error deleting restaurant {restaurant_id}: {e}", exc_info=True)
        raise
