"""
Service for parsing and storing Vapi call data.

Parses Vapi API responses (which have the same structure as webhook payloads)
and stores call records to the database.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from src.services.phones.mapping import get_restaurant_id_from_phone
import logging

logger = logging.getLogger(__name__)


def normalize_phone_number(phone_value: Any) -> Optional[str]:
    """
    Normalize phone number from various formats to string.

    Handles:
    - String: returns as-is
    - Dict with "number" field (Vapi format)
    - Other types: converts to string

    Args:
        phone_value: Phone number in any format

    Returns:
        Phone number as string or None
    """
    if phone_value is None:
        return None
    if isinstance(phone_value, str):
        return phone_value
    if isinstance(phone_value, dict):
        return phone_value.get("number")
    return str(phone_value)


def parse_vapi_call_data(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Vapi API response and extract essential call data.

    Handles Vapi's field variations:
    - startedAt or createdAt for call start
    - endedAt or updatedAt for call end (only if status is ended)
    - from or customer.number for caller
    - messages array at call level

    Args:
        payload: Vapi API response (or webhook payload - same structure)

    Returns:
        Dictionary with parsed call data:
        - call_id
        - phone_number
        - started_at
        - ended_at
        - duration_seconds
        - caller
        - outcome
        - messages
        - cost
    """
    try:
        call_id = payload.get("id")
        phone_number = normalize_phone_number(payload.get("phoneNumber"))

        # Extract caller - try 'from' first, then 'customer' object
        caller = payload.get("from")
        if not caller:
            customer = payload.get("customer")
            if isinstance(customer, dict):
                caller = customer.get("number") or customer.get("phoneNumber")

        messages = payload.get("messages") or []

        # Filter to only include user and assistant (bot) messages, excluding system messages
        # Also keep only essential fields: role and content
        filtered_messages = []
        for msg in messages:
            if isinstance(msg, dict) and msg.get("role") in ["user", "assistant", "bot"]:
                # Extract only essential fields
                clean_msg = {
                    "role": msg.get("role"),
                    "content": msg.get("content") or msg.get("message", "")
                }
                # Only add if we have content
                if clean_msg["content"]:
                    filtered_messages.append(clean_msg)

        # Parse timestamps - Vapi uses startedAt/endedAt or createdAt/updatedAt
        started_at_str = payload.get("startedAt") or payload.get("createdAt")
        ended_at_str = payload.get("endedAt")

        # Only use updatedAt as ended_at if status indicates call ended
        status = payload.get("status", "").lower()
        if not ended_at_str and status in ["ended", "completed", "failed"]:
            ended_at_str = payload.get("updatedAt")

        def parse_timestamp(ts_str):
            """Parse ISO timestamp string to datetime."""
            if not ts_str:
                return None
            if isinstance(ts_str, datetime):
                return ts_str
            try:
                if ts_str.endswith('Z'):
                    ts_str = ts_str.replace('Z', '+00:00')
                return datetime.fromisoformat(ts_str)
            except Exception:
                return None

        started_at = parse_timestamp(started_at_str)
        ended_at = parse_timestamp(ended_at_str)

        # Calculate duration
        duration_seconds = payload.get("duration")
        if not duration_seconds and started_at and ended_at:
            try:
                duration_seconds = int((ended_at - started_at).total_seconds())
            except Exception:
                duration_seconds = None

        outcome = status or "completed"

        cost = payload.get("cost")
        if cost is not None:
            try:
                cost = float(cost)
            except (ValueError, TypeError):
                cost = None

        return {
            "call_id": call_id,
            "phone_number": phone_number,
            "started_at": started_at,
            "ended_at": ended_at,
            "duration_seconds": duration_seconds,
            "caller": caller,
            "outcome": outcome,
            "messages": filtered_messages,
            "cost": cost
        }
    except Exception as e:
        logger.error(f"Error parsing Vapi call data: {e}", exc_info=True)
        raise


def store_call_record(parsed_data: Dict[str, Any]) -> Optional[str]:
    """
    Store call record from parsed Vapi data.

    Maps phone number to restaurant_id and creates a new call record.

    Args:
        parsed_data: Parsed call data from parse_vapi_call_data()

    Returns:
        Call record ID if successful, None if phone mapping not found
    """
    phone_number = parsed_data.get("phone_number")
    phone_number = normalize_phone_number(phone_number)

    if not phone_number:
        logger.warning(
            "No phone number in call data, cannot map to restaurant")
        return None

    restaurant_id = get_restaurant_id_from_phone(phone_number)

    if not restaurant_id:
        logger.warning(
            f"No restaurant mapping found for phone number: {phone_number}")
        return None

    from src.services.calls.service import create_call
    from src.services.infrastructure.database import get_supabase_service_client

    try:
        call_id = create_call(
            restaurant_id=restaurant_id,
            started_at=parsed_data.get("started_at"),
            ended_at=parsed_data.get("ended_at"),
            duration_seconds=parsed_data.get("duration_seconds"),
            caller=parsed_data.get("caller"),
            outcome=parsed_data.get("outcome"),
            messages=parsed_data.get("messages"),
            cost=parsed_data.get("cost")
        )

        logger.info(
            f"Call stored: id={call_id}, restaurant={restaurant_id}, phone={phone_number[:10]}..."
        )

        return call_id
    except Exception as e:
        logger.error(
            f"Error storing call record for phone {phone_number}: {e}",
            exc_info=True
        )
        raise
