"""
Service for retrieving phone number details and status.
"""
from typing import Optional, Dict, Any
import os
import logging
from src.services.infrastructure.database import get_supabase_service_client
from src.services.vapi.client import VapiClient
from src.services.phones.mapping import get_restaurant_id_from_phone

logger = logging.getLogger(__name__)


def get_phone_number_from_mapping(restaurant_id: str) -> Optional[str]:
    """
    Get phone number for a restaurant from mapping table.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        Phone number string or None if not found
    """
    supabase = get_supabase_service_client()

    try:
        resp = supabase.table("restaurant_phone_mappings").select(
            "phone_number"
        ).eq("restaurant_id", restaurant_id).limit(1).execute()

        if resp.data:
            return resp.data[0].get("phone_number")
    except Exception as e:
        logger.warning(
            f"Error fetching phone mapping for restaurant {restaurant_id}: {e}")

    return None


def get_phone_details(restaurant_id: str) -> Optional[Dict[str, Any]]:
    """
    Get phone number details and status for a restaurant.

    Retrieves phone number from mapping, then fetches details from Vapi API.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        Dictionary with phone details:
        - phone_number: Phone number string
        - vapi_phone_id: Phone ID in Vapi
        - assigned_assistant_id: Assistant ID phone is assigned to
        - provider: Phone provider (twilio, etc.)
        - status: Phone status
        - connected: Whether phone is connected/active
        Or None if no phone assigned
    """
    phone_number = get_phone_number_from_mapping(restaurant_id)

    if not phone_number:
        return None

    api_key = os.environ.get("VAPI_API_KEY")
    if not api_key:
        logger.warning(
            "VAPI_API_KEY not configured, cannot fetch phone details")
        return {
            "phone_number": phone_number,
            "connected": False,
            "error": "Vapi API key not configured"
        }

    try:
        client = VapiClient(api_key=api_key)
        phone_numbers = client.list_phone_numbers()

        phone_clean = phone_number.replace(" ", "").replace(
            "(", "").replace(")", "").replace("-", "")

        for pn in phone_numbers:
            pn_number = pn.get("number", "")
            pn_clean = pn_number.replace(" ", "").replace(
                "(", "").replace(")", "").replace("-", "")

            if pn_clean == phone_clean or pn_clean in phone_clean or phone_clean in pn_clean:
                return {
                    "phone_number": phone_number,
                    "vapi_phone_id": pn.get("id"),
                    "assigned_assistant_id": pn.get("assistantId"),
                    "provider": pn.get("provider"),
                    "status": pn.get("status"),
                    "connected": pn.get("assistantId") is not None,
                    "verified": True
                }

        # Phone number exists in mapping but not found in Vapi
        return {
            "phone_number": phone_number,
            "connected": False,
            "error": "Phone number not found in Vapi"
        }
    except Exception as e:
        logger.error(
            f"Error fetching phone details from Vapi: {e}", exc_info=True)
        return {
            "phone_number": phone_number,
            "connected": False,
            "error": f"Failed to fetch phone details: {str(e)}"
        }


def test_phone_connectivity(restaurant_id: str) -> Dict[str, Any]:
    """
    Test phone number connectivity and status.

    Args:
        restaurant_id: Restaurant UUID

    Returns:
        Dictionary with test results:
        - connected: Boolean indicating if phone is connected
        - status: Status message
        - details: Phone details if available
    """
    details = get_phone_details(restaurant_id)

    if not details:
        return {
            "connected": False,
            "status": "No phone number assigned to restaurant",
            "details": None
        }

    if details.get("error"):
        return {
            "connected": False,
            "status": details.get("error", "Unknown error"),
            "details": details
        }

    if not details.get("connected"):
        return {
            "connected": False,
            "status": "Phone number not assigned to assistant",
            "details": details
        }

    return {
        "connected": True,
        "status": "Phone is connected and assigned to assistant",
        "details": details
    }
