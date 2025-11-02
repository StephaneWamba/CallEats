"""
Service for handling Vapi server webhook events.

Processes assistant-request, status-update, and end-of-call-report events.

Note: Vapi webhooks are unreliable - final "ended" webhooks never arrive. We
schedule API fetches after 30 seconds to retrieve complete call data, which
is the only reliable way to capture full transcripts, durations, and costs.
"""
from typing import Optional, Dict, Any
from src.services.calls.parser import normalize_phone_number
from src.services.phones.mapping import get_restaurant_id_from_phone
from src.services.infrastructure.cache import store_call_phone, get_call_phone
from src.services.calls.fetch import fetch_and_store_call_from_vapi
import logging
import threading
import time

logger = logging.getLogger(__name__)

# Track scheduled fetches to prevent duplicates
_scheduled_fetches: set[str] = set()
_scheduled_fetches_lock = threading.Lock()


def _extract_phone_number(message_obj: dict) -> Optional[str]:
    """
    Extract phone number from Vapi message object.

    Vapi structure: phoneNumber is at message.phoneNumber (dict with "number" field).
    Falls back to message.call.phoneNumber if needed.

    Args:
        message_obj: Message object from Vapi webhook

    Returns:
        Phone number string or None if not found
    """
    phone_value = message_obj.get("phoneNumber")
    if phone_value:
        return normalize_phone_number(phone_value)

    call_obj = message_obj.get("call")
    if call_obj:
        phone_value = call_obj.get("phoneNumber")
        if phone_value:
            return normalize_phone_number(phone_value)

    return None


def _schedule_fallback_fetch(vapi_call_id: str) -> None:
    """
    Schedule background fetch of call data after 30 seconds.

    Prevents duplicate scheduling for the same call ID.

    Args:
        vapi_call_id: Vapi call ID to fetch
    """
    # Check if already scheduled
    with _scheduled_fetches_lock:
        if vapi_call_id in _scheduled_fetches:
            logger.debug(
                f"API fetch already scheduled for call {vapi_call_id}")
            return
        _scheduled_fetches.add(vapi_call_id)

    try:
        def fetch_after_delay():
            time.sleep(30)
            try:
                fetch_and_store_call_from_vapi(vapi_call_id)
            finally:
                # Remove from tracking after fetch completes
                with _scheduled_fetches_lock:
                    _scheduled_fetches.discard(vapi_call_id)

        thread = threading.Thread(target=fetch_after_delay, daemon=True)
        thread.start()
        logger.debug(
            f"Scheduled API fetch for call {vapi_call_id} after 30s")
    except Exception as e:
        logger.debug(f"Could not schedule API fetch: {e}")
        # Remove from tracking if scheduling failed
        with _scheduled_fetches_lock:
            _scheduled_fetches.discard(vapi_call_id)


def handle_assistant_request(message_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle assistant-request event from Vapi.

    Extracts phone number, caches call_id mapping, and returns restaurant metadata.

    Args:
        message_obj: Message object from Vapi webhook

    Returns:
        Response dictionary with metadata if restaurant found, empty dict otherwise
    """
    phone_number = _extract_phone_number(message_obj)

    if not phone_number:
        return {}

    call_obj = message_obj.get("call", {})
    call_id = call_obj.get("id")
    if call_id:
        store_call_phone(call_id, phone_number)

    restaurant_id = get_restaurant_id_from_phone(phone_number)
    if restaurant_id:
        return {
            "metadata": {
                "restaurant_id": restaurant_id,
                "phoneNumber": phone_number
            }
        }

    return {}


def handle_status_update(message_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle status-update event from Vapi.

    Only processes ringing status to schedule API fetch. Other statuses are ignored.

    Args:
        message_obj: Message object from Vapi webhook

    Returns:
        Response dictionary with success status
    """
    call_obj = message_obj.get("call")
    if not call_obj or not isinstance(call_obj, dict):
        return {"success": False, "message": "Invalid status-update payload"}

    status = call_obj.get("status", "").lower()
    vapi_call_id = call_obj.get("id")

    if status == "ringing" and vapi_call_id:
        _schedule_fallback_fetch(vapi_call_id)
        return {"success": True, "message": "Scheduled API fetch"}

    return {"success": True, "message": f"Ignored status update: {status}"}


def handle_end_of_call_report(message_obj: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle end-of-call-report event from Vapi.

    Schedules API fetch only. Webhook data is not processed.

    Args:
        message_obj: Message object from Vapi webhook

    Returns:
        Response dictionary with success status
    """
    call_obj = message_obj.get("call")
    if not call_obj or not isinstance(call_obj, dict):
        logger.warning(
            "Invalid end-of-call-report: missing or invalid message.call")
        return {"success": False, "message": "Invalid webhook payload structure"}

    vapi_call_id = call_obj.get("id")
    if not vapi_call_id:
        return {"success": False, "message": "Missing call ID"}

    _schedule_fallback_fetch(vapi_call_id)
    return {"success": True, "message": "Scheduled API fetch"}
