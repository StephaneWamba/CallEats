"""Modifiers domain service.

This module provides business logic for modifier management including:
    - Modifier CRUD operations
    - Price management
    - Cache invalidation on changes

Key Features:
    - Restaurant-scoped modifiers
    - Additional price tracking
    - Automatic cache invalidation

Usage:
    from restaurant_voice_assistant.domain.menu.modifiers import (
        create_modifier,
        list_modifiers,
        update_modifier,
        delete_modifier
    )
    
    modifier = create_modifier(
        restaurant_id="...",
        name="Extra Cheese",
        price=2.50
    )
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.infrastructure.cache.invalidation import invalidate_cache
import logging

logger = logging.getLogger(__name__)


def list_modifiers(restaurant_id: str) -> List[Dict[str, Any]]:
    """List all modifiers for a restaurant.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        List of modifier records

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("modifiers").select(
            "id, restaurant_id, name, description, price, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).order("name").execute()

        return resp.data or []
    except Exception as e:
        logger.error(
            f"Error fetching modifiers for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def get_modifier(restaurant_id: str, modifier_id: str) -> Optional[Dict[str, Any]]:
    """Get a single modifier.

    Args:
        restaurant_id: Restaurant UUID
        modifier_id: Modifier UUID

    Returns:
        Modifier record or None if not found

    Raises:
        Exception: If database operation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("modifiers").select(
            "id, restaurant_id, name, description, price, created_at, updated_at"
        ).eq("restaurant_id", restaurant_id).eq("id", modifier_id).limit(1).execute()

        if resp.data:
            return resp.data[0]
        return None
    except Exception as e:
        logger.error(
            f"Error fetching modifier {modifier_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


@invalidate_cache(category="modifiers")
def create_modifier(
    restaurant_id: str,
    name: str,
    description: Optional[str] = None,
    price: Decimal = Decimal("0.00")
) -> Dict[str, Any]:
    """Create a new modifier.

    Args:
        restaurant_id: Restaurant UUID
        name: Modifier name
        description: Modifier description
        price: Additional price

    Returns:
        Created modifier record

    Raises:
        Exception: If creation fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("modifiers").insert({
            "restaurant_id": restaurant_id,
            "name": name,
            "description": description,
            "price": float(price)
        }).execute()

        if not resp.data:
            raise Exception("Failed to create modifier")

        modifier = resp.data[0]

        return modifier
    except Exception as e:
        logger.error(
            f"Error creating modifier for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


@invalidate_cache(category="modifiers")
def update_modifier(
    restaurant_id: str,
    modifier_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[Decimal] = None
) -> Optional[Dict[str, Any]]:
    """Update a modifier.

    Args:
        restaurant_id: Restaurant UUID
        modifier_id: Modifier UUID
        name: New name (optional)
        description: New description (optional)
        price: New price (optional)

    Returns:
        Updated modifier record or None if not found

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

    if not update_data:
        return get_modifier(restaurant_id, modifier_id)

    try:
        resp = supabase.table("modifiers").update(update_data).eq(
            "restaurant_id", restaurant_id).eq("id", modifier_id).execute()

        if not resp.data:
            return None

        return resp.data[0]
    except Exception as e:
        logger.error(
            f"Error updating modifier {modifier_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


@invalidate_cache(category="modifiers")
def delete_modifier(restaurant_id: str, modifier_id: str) -> bool:
    """Delete a modifier.

    Args:
        restaurant_id: Restaurant UUID
        modifier_id: Modifier UUID

    Returns:
        True if deleted, False if not found

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("modifiers").delete().eq(
            "restaurant_id", restaurant_id).eq("id", modifier_id).execute()

        if resp.data:
            return True
        return False
    except Exception as e:
        logger.error(
            f"Error deleting modifier {modifier_id} for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise

