"""Service for operating hours management."""
from typing import List, Dict, Any, Optional
from src.services.infrastructure.database import get_supabase_service_client
from src.services.infrastructure.cache import clear_cache
import logging

logger = logging.getLogger(__name__)


def list_operating_hours(restaurant_id: str) -> List[Dict[str, Any]]:
    """
    List all operating hours for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of operating hour records

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("operating_hours").select(
            "id, restaurant_id, day_of_week, open_time, close_time, is_closed, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("day_of_week").execute()

        return resp.data or []
    except Exception as e:
        logger.error(
            f"Error fetching operating hours for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def get_operating_hour(restaurant_id: str, hour_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single operating hour.

    Args:
        restaurant_id: Restaurant UUID
        hour_id: Operating hour UUID

    Returns:
        Operating hour record or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("operating_hours").select(
            "id, restaurant_id, day_of_week, open_time, close_time, is_closed, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", hour_id).limit(1).execute()

        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(
            f"Error fetching operating hour {hour_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def update_operating_hours(
    restaurant_id: str,
    hours: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Update operating hours (bulk update - replaces all hours).

    Args:
        restaurant_id: Restaurant UUID
        hours: List of hour dictionaries with day_of_week, open_time, close_time, is_closed

    Returns:
        List of updated operating hour records

    Raises:
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    try:
        # Delete existing hours
        supabase.table("operating_hours").delete().eq(
            "restaurant_id", restaurant_id).execute()

        # Insert new hours
        if hours:
            records = []
            for hour in hours:
                records.append({
                    "restaurant_id": restaurant_id,
                    "day_of_week": hour.get("day_of_week"),
                    "open_time": hour.get("open_time"),
                    "close_time": hour.get("close_time"),
                    "is_closed": hour.get("is_closed", False)
                })

            resp = supabase.table("operating_hours").insert(records).execute()

            if not resp.data:
                raise Exception("Failed to update operating hours")

            clear_cache(restaurant_id, "hours")
            return resp.data
        else:
            clear_cache(restaurant_id, "hours")
            return []
    except Exception as e:
        logger.error(
            f"Error updating operating hours for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def delete_operating_hours(restaurant_id: str) -> bool:
    """
    Delete all operating hours for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        True if deleted

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        supabase.table("operating_hours").delete().eq(
            "restaurant_id", restaurant_id).execute()

        clear_cache(restaurant_id, "hours")
        return True
    except Exception as e:
        logger.error(
            f"Error deleting operating hours for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise
