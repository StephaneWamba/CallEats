"""Call data fetching service from Vapi API.

This module provides functionality for fetching call data from Vapi API and
storing it in the database. It implements the fallback mechanism for retrieving
complete call data when webhooks fail.

Key Features:
    - Fetches complete call data from Vapi API
    - Handles phone number resolution from cache or API
    - Only processes ended calls
    - Automatic call record storage

Webhook Reliability:
    Vapi webhooks are unreliable - final "ended" webhooks often don't arrive.
    This module is called by infrastructure/vapi/server.py after a 30-second
    delay to ensure complete call data is captured.

Usage:
    from restaurant_voice_assistant.domain.calls.service import fetch_and_store_call_from_vapi
    
    call_id = fetch_and_store_call_from_vapi(vapi_call_id="...")
"""
from typing import Optional, Dict, Any
from restaurant_voice_assistant.infrastructure.vapi.client import VapiClient, VapiAPIError
from restaurant_voice_assistant.domain.calls.parser import (
    parse_vapi_call_data,
    store_call_record,
    normalize_phone_number
)
from restaurant_voice_assistant.infrastructure.cache.manager import get_call_phone
import os
import logging

logger = logging.getLogger(__name__)


def fetch_and_store_call_from_vapi(vapi_call_id: str) -> Optional[str]:
    """Fetch call data from Vapi API and store it.

    Args:
        vapi_call_id: Vapi call ID

    Returns:
        Call record ID if successful, None otherwise
    """
    api_key = os.environ.get("VAPI_API_KEY")
    if not api_key:
        logger.error("VAPI_API_KEY not set, cannot fetch call from Vapi API")
        return None

    try:
        client = VapiClient(api_key)
        call_data = client.get_call(vapi_call_id)

        status = call_data.get("status", "").lower()
        logger.info(
            f"Fetched call from Vapi API: id={vapi_call_id}, status={status}")

        # Only process if call is actually ended
        if status not in ["ended", "completed", "failed"]:
            logger.debug(
                f"Call {vapi_call_id} not ended yet (status={status})")
            return None

        # Get phone number - try cache first, then from call data
        phone_number = get_call_phone(vapi_call_id)

        if not phone_number:
            # Try to get from call data - Vapi API might have it in phoneNumber or phoneNumberId
            phone_obj = call_data.get("phoneNumber")
            if phone_obj:
                phone_number = normalize_phone_number(phone_obj)

            # If still no phone, try phoneNumberId
            if not phone_number:
                phone_number_id = call_data.get("phoneNumberId")
                if phone_number_id:
                    try:
                        phone_client = VapiClient(api_key)
                        phone_data = phone_client.get_phone_number(
                            phone_number_id)
                        phone_number = phone_data.get("number")
                    except Exception as e:
                        logger.debug(
                            f"Could not fetch phone number details: {e}")

        if phone_number:
            call_data["phoneNumber"] = phone_number
        else:
            logger.warning(f"No phone number found for call {vapi_call_id}")
            return None

        parsed_data = parse_vapi_call_data(call_data)
        call_id = store_call_record(parsed_data)

        if call_id:
            logger.info(
                f"Fetched and stored call from Vapi API: id={call_id}, duration={parsed_data.get('duration_seconds')}s, messages={len(parsed_data.get('messages', []))}"
            )

        return call_id

    except VapiAPIError as e:
        logger.warning(
            f"Could not fetch call {vapi_call_id} from Vapi API: {e}")
        return None
    except Exception as e:
        logger.error(
            f"Error fetching call {vapi_call_id} from Vapi API: {e}", exc_info=True)
        return None

