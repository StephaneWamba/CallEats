"""Delivery zones domain service.

This module provides business logic for managing restaurant delivery zones including:
    - Delivery zone CRUD operations
    - Zone boundary management (PostGIS)
    - Delivery fee and minimum order configuration
    - Cache invalidation on changes

Key Features:
    - Restaurant-scoped delivery zones
    - Geographic boundary support (PostGIS)
    - Delivery fee and minimum order tracking
    - Automatic cache invalidation

Geographic Queries:
    Zone boundaries are stored as PostGIS geometry and can be queried using
    the zone_geometry module for location-based zone determination.

Usage:
    from restaurant_voice_assistant.domain.operations.zones import (
        create_delivery_zone,
        list_delivery_zones,
        update_delivery_zone,
        delete_delivery_zone
    )
    
    zone = create_delivery_zone(
        restaurant_id="...",
        zone_name="Downtown",
        delivery_fee=5.00,
        min_order=15.00
    )
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.infrastructure.cache.manager import clear_cache
import logging

logger = logging.getLogger(__name__)


def list_delivery_zones(restaurant_id: str) -> List[Dict[str, Any]]:
    """List all delivery zones for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of delivery zone records ordered by zone_name

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("delivery_zones").select(
            "id, restaurant_id, zone_name, description, delivery_fee, min_order, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("zone_name").execute()

        return resp.data or []
    except Exception as e:
        logger.error(
            f"Error fetching delivery zones for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def get_delivery_zone(restaurant_id: str, zone_id: str) -> Optional[Dict[str, Any]]:
    """Get a single delivery zone.

    Args:
        restaurant_id: Restaurant UUID
        zone_id: Delivery zone UUID

    Returns:
        Delivery zone record or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("delivery_zones").select(
            "id, restaurant_id, zone_name, description, delivery_fee, min_order, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", zone_id).limit(1).execute()

        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(
            f"Error fetching delivery zone {zone_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def create_delivery_zone(
    restaurant_id: str,
    zone_name: str,
    description: Optional[str] = None,
    delivery_fee: Decimal = Decimal("0.00"),
    min_order: Optional[Decimal] = None
) -> Dict[str, Any]:
    """Create a new delivery zone.

    Args:
        restaurant_id: Restaurant UUID
        zone_name: Zone name
        description: Zone description
        delivery_fee: Delivery fee
        min_order: Minimum order amount (optional)

    Returns:
        Created delivery zone record

    Raises:
        Exception: If creation fails
    """
    supabase = get_supabase_service_client()

    try:
        record = {
            "restaurant_id": restaurant_id,
            "zone_name": zone_name,
            "description": description,
            "delivery_fee": float(delivery_fee)
        }
        if min_order is not None:
            record["min_order"] = float(min_order)

        resp = supabase.table("delivery_zones").insert(record).execute()

        if not resp.data:
            raise Exception("Failed to create delivery zone")

        zone = resp.data[0]

        clear_cache(restaurant_id, "zones")

        return zone
    except Exception as e:
        logger.error(
            f"Error creating delivery zone for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def update_delivery_zone(
    restaurant_id: str,
    zone_id: str,
    zone_name: Optional[str] = None,
    description: Optional[str] = None,
    delivery_fee: Optional[Decimal] = None,
    min_order: Optional[Decimal] = None
) -> Optional[Dict[str, Any]]:
    """Update a delivery zone.

    Args:
        restaurant_id: Restaurant UUID
        zone_id: Delivery zone UUID
        zone_name: New zone name (optional)
        description: New description (optional)
        delivery_fee: New delivery fee (optional)
        min_order: New minimum order (optional)

    Returns:
        Updated delivery zone record or None if not found

    Raises:
        Exception: If update fails
    """
    supabase = get_supabase_service_client()

    update_data = {}
    if zone_name is not None:
        update_data["zone_name"] = zone_name
    if description is not None:
        update_data["description"] = description
    if delivery_fee is not None:
        update_data["delivery_fee"] = float(delivery_fee)
    if min_order is not None:
        update_data["min_order"] = float(min_order)

    if not update_data:
        return get_delivery_zone(restaurant_id, zone_id)

    try:
        resp = supabase.table("delivery_zones").update(update_data).eq(
            "restaurant_id", restaurant_id).eq("id", zone_id).execute()

        if not resp.data:
            return None

        clear_cache(restaurant_id, "zones")

        return resp.data[0]
    except Exception as e:
        logger.error(
            f"Error updating delivery zone {zone_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def delete_delivery_zone(restaurant_id: str, zone_id: str) -> bool:
    """Delete a delivery zone.

    Args:
        restaurant_id: Restaurant UUID
        zone_id: Delivery zone UUID

    Returns:
        True if deleted, False if not found

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("delivery_zones").delete().eq(
            "restaurant_id", restaurant_id).eq("id", zone_id).execute()

        if resp.data:
            clear_cache(restaurant_id, "zones")
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error deleting delivery zone {zone_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise
