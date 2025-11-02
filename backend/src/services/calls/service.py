"""Service for call history management."""
from typing import Optional, List, Dict, Any
from datetime import datetime
from src.services.infrastructure.database import get_supabase_client, get_supabase_service_client
import logging

logger = logging.getLogger(__name__)


def _filter_messages(messages: Optional[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Filter messages to only include user and assistant (bot) messages.
    Keep only essential fields: role and content.
    """
    if not messages:
        return []

    filtered = []
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") in ["user", "assistant", "bot"]:
            # Extract only essential fields: role and content
            content = msg.get("content") or msg.get("message", "")
            if content:  # Only include messages with content
                filtered.append({
                    "role": msg.get("role"),
                    "content": content
                })

    return filtered


def get_call(call_id: str, restaurant_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Get a single call record by ID.

    Args:
        call_id: Call record UUID
        restaurant_id: Optional restaurant UUID for verification (security check)

    Returns:
        Call record with full transcript, None if not found
    """
    supabase = get_supabase_service_client()

    try:
        query = supabase.table("call_history").select(
            "id, restaurant_id, started_at, ended_at, duration_seconds, caller, outcome, messages, cost"
        ).eq("id", call_id)

        if restaurant_id:
            query = query.eq("restaurant_id", restaurant_id)

        resp = query.limit(1).execute()

        if not resp.data:
            return None

        call = resp.data[0]
        # Filter messages to exclude system/tool messages
        if call.get("messages"):
            call["messages"] = _filter_messages(call["messages"])

        return call
    except Exception as e:
        logger.error(
            f"Error fetching call {call_id}: {e}", exc_info=True)
        raise


def list_calls(restaurant_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    List call history for a restaurant.

    Args:
        restaurant_id: Restaurant UUID
        limit: Maximum number of results

    Returns:
        List of call records
    """
    supabase = get_supabase_client()

    try:
        resp = supabase.table("call_history").select(
            "id, started_at, ended_at, duration_seconds, caller, outcome, messages, cost"
        ).eq("restaurant_id", restaurant_id).order("started_at", desc=True).limit(limit).execute()

        calls = resp.data or []
        # Filter messages for each call to exclude system/tool messages
        for call in calls:
            if call.get("messages"):
                call["messages"] = _filter_messages(call["messages"])

        return calls
    except Exception as e:
        logger.error(
            f"Error fetching calls for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise


def create_call(
    restaurant_id: str,
    started_at: datetime,
    ended_at: Optional[datetime] = None,
    duration_seconds: Optional[int] = None,
    caller: Optional[str] = None,
    outcome: Optional[str] = None,
    messages: Optional[List[Dict[str, Any]]] = None,
    cost: Optional[float] = None
) -> str:
    """
    Create a call history record.

    Args:
        restaurant_id: Restaurant UUID
        started_at: Call start time
        ended_at: Call end time (optional)
        duration_seconds: Call duration in seconds (optional)
        caller: Caller phone number (optional)
        outcome: Call outcome (optional)
        messages: Call messages/transcript (optional)
        cost: Total call cost (optional)

    Returns:
        Call record ID
    """
    # Convert datetime objects to ISO strings for Supabase
    started_at_iso = started_at.isoformat() if isinstance(
        started_at, datetime) else started_at
    ended_at_iso = ended_at.isoformat() if isinstance(
        ended_at, datetime) else ended_at

    record = {
        "restaurant_id": restaurant_id,
        "started_at": started_at_iso,
        "ended_at": ended_at_iso,
        "duration_seconds": duration_seconds,
        "caller": caller,
        "outcome": outcome,
        "messages": messages or [],
        "cost": cost,
    }

    supabase = get_supabase_service_client()
    try:
        resp = supabase.table("call_history").insert(record).execute()

        if not resp.data:
            raise Exception("Failed to create call record")

        return resp.data[0].get("id")
    except Exception as e:
        logger.error(
            f"Error creating call record for restaurant_id={restaurant_id}: {e}", exc_info=True)
        raise
