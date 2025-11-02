"""
Service for processing Vapi end-of-call-report webhooks.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from src.services.phones.mapping import get_restaurant_id_from_phone
import logging

logger = logging.getLogger(__name__)


def parse_vapi_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse Vapi webhook payload and extract essential call data.

    Args:
        payload: Raw webhook payload from Vapi

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
        # Extract call ID
        call_id = payload.get("id")

        # Extract phone number (camelCase)
        phone_number = payload.get("phoneNumber")

        # Extract caller number
        caller = payload.get("from")

        # Extract messages/transcript
        messages = payload.get("messages") or []

        # Parse timestamps (camelCase)
        started_at_str = payload.get("startedAt")
        ended_at_str = payload.get("endedAt")

        started_at = None
        ended_at = None

        def parse_timestamp(ts_str):
            """Parse ISO timestamp string to datetime."""
            if not ts_str:
                return None
            if isinstance(ts_str, datetime):
                return ts_str
            try:
                # Handle ISO format with or without timezone
                if ts_str.endswith('Z'):
                    ts_str = ts_str.replace('Z', '+00:00')
                return datetime.fromisoformat(ts_str)
            except Exception:
                return None

        started_at = parse_timestamp(started_at_str)
        ended_at = parse_timestamp(ended_at_str)

        # Extract duration
        duration_seconds = payload.get("duration")

        # Calculate duration if not provided but timestamps are available
        if not duration_seconds and started_at and ended_at:
            try:
                duration_seconds = int((ended_at - started_at).total_seconds())
            except Exception:
                duration_seconds = None

        # Extract outcome/status
        outcome = payload.get("status") or "completed"

        # Extract cost (optional, may not be available on free tier)
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
            "messages": messages if isinstance(messages, list) else [],
            "cost": cost
        }
    except Exception as e:
        logger.error(f"Error parsing Vapi webhook payload: {e}", exc_info=True)
        raise


def store_call_from_webhook(parsed_data: Dict[str, Any]) -> Optional[str]:
    """
    Store call record from webhook data.

    Maps phone number to restaurant_id and stores in call_history table.

    Args:
        parsed_data: Parsed call data from parse_vapi_webhook()

    Returns:
        Call record ID if successful, None if phone mapping not found
    """
    phone_number = parsed_data.get("phone_number")

    if not phone_number:
        logger.warning(
            "No phone number in webhook payload, cannot map to restaurant")
        return None

    # Map phone number to restaurant_id
    restaurant_id = get_restaurant_id_from_phone(phone_number)

    if not restaurant_id:
        logger.warning(
            f"No restaurant mapping found for phone number: {phone_number}")
        return None

    # Store call record
    from src.services.calls.service import create_call

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

        return call_id
    except Exception as e:
        logger.error(
            f"Error storing call record for phone {phone_number}: {e}",
            exc_info=True
        )
        raise
