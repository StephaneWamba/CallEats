"""Operating hours domain service.

This module provides business logic for managing restaurant operating hours including:
    - Day-of-week hour management
    - Bulk update operations (replace all hours)
    - Closed day handling
    - Cache invalidation on changes

Key Features:
    - Restaurant-scoped operating hours
    - Support for closed days (is_closed flag)
    - Bulk update pattern (delete + insert)
    - Automatic cache invalidation

Usage:
    from restaurant_voice_assistant.domain.operations.hours import (
        list_operating_hours,
        update_operating_hours,
        delete_operating_hours
    )
    
    hours = [
        {"day_of_week": 0, "open_time": "09:00", "close_time": "17:00", "is_closed": False},
        {"day_of_week": 1, "open_time": "09:00", "close_time": "17:00", "is_closed": False},
        # ... etc
    ]
    update_operating_hours(restaurant_id="...", hours=hours)
"""
from typing import List, Dict, Any, Optional
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.infrastructure.cache.invalidation import invalidate_cache
import logging

logger = logging.getLogger(__name__)


def list_operating_hours(restaurant_id: str) -> List[Dict[str, Any]]:
    """List all operating hours for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of operating hour records ordered by day_of_week

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
    """Get a single operating hour.

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


@invalidate_cache(category="hours")
def update_operating_hours(
    restaurant_id: str,
    hours: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Update operating hours (bulk update - replaces all hours).

    This operation deletes all existing hours and inserts new ones atomically.

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

            return resp.data
        else:
            return []
    except Exception as e:
        logger.error(
            f"Error updating operating hours for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


@invalidate_cache(category="hours")
def delete_operating_hours(restaurant_id: str) -> bool:
    """Delete all operating hours for a restaurant.

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

        return True
    except Exception as e:
        logger.error(
            f"Error deleting operating hours for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise
