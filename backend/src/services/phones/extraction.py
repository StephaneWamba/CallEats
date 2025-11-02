"""
Service for extracting restaurant_id from various request sources.

Consolidates restaurant_id extraction logic with fallback chain:
1. Header (X-Restaurant-Id)
2. Query parameter (restaurant_id)
3. Request metadata (metadata.restaurant_id)
4. Phone number lookup (from message.phoneNumber)
"""
from typing import Optional, Dict, Any
from src.models.vapi.requests import VapiRequest
from src.services.phones.mapping import get_restaurant_id_from_phone
from src.services.calls.parser import normalize_phone_number
import logging

logger = logging.getLogger(__name__)


def _extract_phone_number_from_message(message_obj: Optional[Dict[str, Any]]) -> Optional[str]:
    """
    Extract phone number from Vapi message object.

    Args:
        message_obj: Message object from Vapi webhook

    Returns:
        Phone number string or None if not found
    """
    if not message_obj or not isinstance(message_obj, dict):
        return None

    phone_value = message_obj.get("phoneNumber")
    if phone_value:
        return normalize_phone_number(phone_value)

    call_obj = message_obj.get("call")
    if call_obj and isinstance(call_obj, dict):
        phone_value = call_obj.get("phoneNumber")
        if phone_value:
            return normalize_phone_number(phone_value)

    return None


def extract_restaurant_id_with_fallback(
    x_restaurant_id: Optional[str] = None,
    query_params: Optional[Dict[str, Any]] = None,
    vapi_request: Optional[VapiRequest] = None,
    message_obj: Optional[Dict[str, Any]] = None
) -> Optional[str]:
    """
    Extract restaurant_id with fallback chain.

    Tries sources in order:
    1. Header (x_restaurant_id)
    2. Query parameter (restaurant_id)
    3. Request metadata (vapi_request.metadata.restaurant_id)
    4. Phone number lookup (from message_obj)

    Args:
        x_restaurant_id: Restaurant ID from X-Restaurant-Id header
        query_params: Query parameters dict
        vapi_request: Parsed Vapi request object
        message_obj: Raw message object for phone number extraction

    Returns:
        Restaurant ID if found, None otherwise
    """
    # Try header
    if x_restaurant_id:
        return x_restaurant_id.strip()

    # Try query parameter
    if query_params:
        query_restaurant_id = query_params.get("restaurant_id")
        if query_restaurant_id:
            return query_restaurant_id.strip()

    # Try request metadata
    if vapi_request:
        metadata_restaurant_id = vapi_request.extract_restaurant_id()
        if metadata_restaurant_id:
            return metadata_restaurant_id.strip()

    # Fallback to phone number lookup
    if message_obj:
        try:
            phone_number = _extract_phone_number_from_message(message_obj)
            if phone_number:
                return get_restaurant_id_from_phone(phone_number)
        except Exception as e:
            logger.error(
                f"Error extracting restaurant_id from phone number: {e}",
                exc_info=True
            )

    return None

