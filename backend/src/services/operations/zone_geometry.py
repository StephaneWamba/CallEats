"""Service for delivery zone geometry operations."""
from typing import Dict, Any, Optional, List
from src.services.infrastructure.database import get_supabase_service_client
from src.services.infrastructure.cache import clear_cache
import logging

logger = logging.getLogger(__name__)


def set_zone_boundary(
    restaurant_id: str,
    zone_id: str,
    geojson_boundary: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Set the boundary polygon for a delivery zone from GeoJSON.

    Args:
        restaurant_id: Restaurant UUID (for validation)
        zone_id: Delivery zone UUID
        geojson_boundary: GeoJSON Feature or Geometry object
            Example: {"type": "Polygon", "coordinates": [[[lng, lat], ...]]}

    Returns:
        Updated zone record with boundary info

    Raises:
        ValueError: If zone doesn't exist or invalid GeoJSON
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        # Pass GeoJSON directly as dict (Supabase will convert to JSONB)
        # The SQL function expects JSONB and converts to text for ST_GeomFromGeoJSON
        result = supabase.rpc('set_zone_boundary', {
            'p_zone_id': zone_id,
            'p_restaurant_id': restaurant_id,
            'p_geojson': geojson_boundary
        }).execute()

        if not result.data:
            raise ValueError("Failed to set boundary")

        response_data = result.data if isinstance(
            result.data, dict) else result.data[0] if result.data else {}

        clear_cache(restaurant_id, "zones")

        return response_data

    except Exception as e:
        error_str = str(e).lower()
        if "zone not found" in error_str or "access denied" in error_str:
            raise ValueError(
                "Delivery zone not found or doesn't belong to restaurant")
        if "polygon" in error_str or "geometry" in error_str:
            raise ValueError(f"Invalid GeoJSON: {str(e)}")
        logger.error(
            f"Error setting boundary for zone {zone_id}: {e}",
            exc_info=True
        )
        raise


def check_point_in_zone(
    restaurant_id: str,
    latitude: float,
    longitude: float
) -> Optional[Dict[str, Any]]:
    """
    Check if a point (lat/lng) is within any delivery zone for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        latitude: Point latitude
        longitude: Point longitude

    Returns:
        Zone record if point is in zone, None otherwise

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        # Call database function via RPC
        result = supabase.rpc('check_delivery_zone', {
            'p_restaurant_id': restaurant_id,
            'p_longitude': longitude,
            'p_latitude': latitude
        }).execute()

        if result.data and len(result.data) > 0:
            return result.data[0]
        return None

    except Exception as e:
        # If function doesn't exist or PostGIS not available, return None gracefully
        error_str = str(e).lower()
        if "function" in error_str or "does not exist" in error_str:
            logger.warning(
                f"check_delivery_zone function not available (PostGIS may not be enabled): {e}")
            return None
        logger.error(
            f"Error checking point in zone for restaurant {restaurant_id}: {e}",
            exc_info=True
        )
        raise


def get_zone_boundary_geojson(
    restaurant_id: str,
    zone_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get the boundary of a delivery zone as GeoJSON.

    Args:
        restaurant_id: Restaurant UUID (for validation)
        zone_id: Delivery zone UUID

    Returns:
        GeoJSON Feature object with boundary, or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        # Call database function via RPC
        result = supabase.rpc('get_zone_boundary_geojson', {
            'p_zone_id': zone_id,
            'p_restaurant_id': restaurant_id
        }).execute()

        if result.data:
            # RPC returns data in various formats, handle both dict and list
            if isinstance(result.data, dict):
                return result.data
            elif isinstance(result.data, list) and len(result.data) > 0:
                return result.data[0]
            elif result.data:  # Single value
                return result.data
        return None

    except Exception as e:
        error_str = str(e).lower()
        if "function" in error_str or "does not exist" in error_str:
            logger.warning(
                f"get_zone_boundary_geojson function not available (PostGIS may not be enabled): {e}")
            return None
        if "not found" in error_str or "access denied" in error_str:
            raise ValueError(
                "Delivery zone not found or doesn't belong to restaurant")
        logger.error(
            f"Error getting boundary GeoJSON for zone {zone_id}: {e}",
            exc_info=True
        )
        raise
