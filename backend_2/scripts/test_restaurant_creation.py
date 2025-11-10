#!/usr/bin/env python3
"""Test script to create a restaurant via API and verify phone number assignment.

This script tests the complete workflow:
1. Creates a restaurant via API
2. Verifies phone number is returned
3. Checks Vapi to verify phone is assigned to assistant
4. Verifies database mapping exists

Usage:
    python scripts/test_restaurant_creation.py --backend-url https://your-backend.railway.app
"""
from restaurant_voice_assistant.infrastructure.vapi.client import VapiClient
import requests
import os
import sys
import argparse
from typing import Optional, Dict, Any
from pathlib import Path

# Add backend_2 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}\n{text}\n{'=' * 60}")


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 60}\n{text}\n{'-' * 60}")


def create_restaurant_via_api(
    backend_url: str,
    name: str,
    vapi_secret: str,
    force_twilio: bool = False
) -> Dict[str, Any]:
    """Create a restaurant via API.

    Args:
        backend_url: Backend API URL
        name: Restaurant name
        vapi_secret: Vapi secret key for authentication
        force_twilio: Force Twilio phone creation

    Returns:
        Restaurant data dictionary
    """
    url = f"{backend_url.rstrip('/')}/api/restaurants"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "name": name,
        "assign_phone": True,
        "force_twilio": force_twilio
    }

    print_section("Creating Restaurant via API")
    print(f"URL: {url}")
    print(f"Name: {name}")
    print(f"Force Twilio: {force_twilio}")

    response = requests.post(url, json=payload, headers=headers, timeout=30)

    if response.status_code != 200:
        error_msg = f"Failed to create restaurant: {response.status_code}"
        try:
            error_detail = response.json()
            error_msg += f" - {error_detail}"
        except:
            error_msg += f" - {response.text}"
        raise Exception(error_msg)

    restaurant_data = response.json()
    print(f"✓ Restaurant created successfully!")
    print(f"  ID: {restaurant_data.get('id')}")
    print(f"  Name: {restaurant_data.get('name')}")
    print(f"  Phone: {restaurant_data.get('phone_number', 'None')}")

    return restaurant_data


def verify_phone_in_vapi(
    phone_number: str,
    expected_assistant_id: str,
    vapi_api_key: str
) -> bool:
    """Verify phone number is assigned to assistant in Vapi.

    Args:
        phone_number: Phone number to check
        expected_assistant_id: Expected assistant ID
        vapi_api_key: Vapi API key

    Returns:
        True if phone is assigned to assistant, False otherwise
    """
    if not phone_number:
        print("⚠ No phone number to verify")
        return False

    print_section("Verifying Phone in Vapi")
    print(f"Phone: {phone_number}")
    print(f"Expected Assistant ID: {expected_assistant_id}")

    try:
        client = VapiClient(api_key=vapi_api_key)
        phones = client.list_phone_numbers()

        # Normalize phone number for comparison
        phone_clean = phone_number.replace(" ", "").replace(
            "(", "").replace(")", "").replace("-", "")

        for pn in phones:
            pn_number = pn.get("number", "")
            pn_clean = pn_number.replace(" ", "").replace(
                "(", "").replace(")", "").replace("-", "")

            if pn_clean == phone_clean or phone_clean in pn_clean or pn_clean in phone_clean:
                pn_assistant_id = pn.get("assistantId")
                pn_id = pn.get("id")

                print(f"✓ Found phone in Vapi")
                print(f"  Phone ID: {pn_id}")
                print(f"  Assigned Assistant ID: {pn_assistant_id}")

                if pn_assistant_id == expected_assistant_id:
                    print(f"✓ Phone is correctly assigned to assistant!")
                    return True
                else:
                    print(
                        f"⚠ Phone is assigned to different assistant: {pn_assistant_id}")
                    return False

        print(f"⚠ Phone number not found in Vapi")
        return False

    except Exception as e:
        print(f"⚠ Error verifying phone in Vapi: {e}")
        return False


def verify_database_mapping_via_api(
    backend_url: str,
    phone_number: str,
    restaurant_id: str,
    vapi_secret: str
) -> bool:
    """Verify phone number mapping via API (get restaurant endpoint).

    Args:
        backend_url: Backend API URL
        phone_number: Phone number to check
        restaurant_id: Expected restaurant ID
        vapi_secret: Vapi secret for authentication

    Returns:
        True if mapping exists, False otherwise
    """
    if not phone_number:
        print("⚠ No phone number to verify")
        return False

    print_section("Verifying Database Mapping via API")
    print(f"Phone: {phone_number}")
    print(f"Restaurant ID: {restaurant_id}")

    try:
        url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}"
        headers = {"X-Vapi-Secret": vapi_secret}

        response = requests.get(url, headers=headers, timeout=30)

        if response.status_code == 200:
            restaurant_data = response.json()
            api_phone = restaurant_data.get("phone_number")

            # Normalize for comparison
            phone_clean = phone_number.replace(" ", "").replace(
                "(", "").replace(")", "").replace("-", "")
            api_phone_clean = (api_phone or "").replace(" ", "").replace(
                "(", "").replace(")", "").replace("-", "")

            if api_phone_clean == phone_clean:
                print(f"✓ Database mapping verified via API!")
                return True
            else:
                print(f"⚠ API returned different phone: {api_phone}")
                return False
        else:
            print(f"⚠ Failed to get restaurant: {response.status_code}")
            return False

    except Exception as e:
        print(f"⚠ Error verifying database mapping: {e}")
        return False


def main():
    """Main test function."""
    parser = argparse.ArgumentParser(
        description="Test restaurant creation and phone assignment"
    )
    parser.add_argument(
        "--backend-url",
        type=str,
        default=os.environ.get("PUBLIC_BACKEND_URL"),
        help="Backend API URL (default: PUBLIC_BACKEND_URL env var)"
    )
    parser.add_argument(
        "--vapi-secret",
        type=str,
        default=os.environ.get("VAPI_SECRET_KEY"),
        help="Vapi secret key (default: VAPI_SECRET_KEY env var)"
    )
    parser.add_argument(
        "--vapi-api-key",
        type=str,
        default=os.environ.get("VAPI_API_KEY"),
        help="Vapi API key (default: VAPI_API_KEY env var)"
    )
    parser.add_argument(
        "--restaurant-name",
        type=str,
        default="Test Restaurant",
        help="Restaurant name (default: 'Test Restaurant')"
    )
    parser.add_argument(
        "--force-twilio",
        action="store_true",
        help="Force Twilio phone creation (skip existing phones)"
    )
    parser.add_argument(
        "--assistant-id",
        type=str,
        help="Expected assistant ID (will try to find 'Restaurant Voice Assistant' if not provided)"
    )

    args = parser.parse_args()

    if not args.backend_url:
        print("Error: --backend-url required or set PUBLIC_BACKEND_URL env var", file=sys.stderr)
        sys.exit(1)

    if not args.vapi_secret:
        print(
            "Error: --vapi-secret required or set VAPI_SECRET_KEY env var", file=sys.stderr)
        sys.exit(1)

    if not args.vapi_api_key:
        print("Error: --vapi-api-key required or set VAPI_API_KEY env var",
              file=sys.stderr)
        sys.exit(1)

    print_header("Restaurant Creation Test")
    print(f"Backend URL: {args.backend_url}")
    print(f"Restaurant Name: {args.restaurant_name}")
    print(f"Force Twilio: {args.force_twilio}")

    # Get assistant ID if not provided
    assistant_id = args.assistant_id
    if not assistant_id:
        print_section("Finding Assistant")
        try:
            client = VapiClient(api_key=args.vapi_api_key)
            assistants = client.list_assistants()
            assistant = next(
                (a for a in assistants if a.get("name")
                 == "Restaurant Voice Assistant"),
                None
            )
            if assistant:
                assistant_id = assistant.get("id")
                print(f"✓ Found assistant: {assistant_id}")
            else:
                print("⚠ Assistant 'Restaurant Voice Assistant' not found!")
                print("Available assistants:")
                for a in assistants:
                    print(f"  - {a.get('name')} ({a.get('id')})")
                sys.exit(1)
        except Exception as e:
            print(f"⚠ Error finding assistant: {e}")
            sys.exit(1)

    # Create restaurant
    try:
        restaurant = create_restaurant_via_api(
            backend_url=args.backend_url,
            name=args.restaurant_name,
            vapi_secret=args.vapi_secret,
            force_twilio=args.force_twilio
        )
    except Exception as e:
        print(f"❌ Failed to create restaurant: {e}")
        sys.exit(1)

    restaurant_id = restaurant.get("id")
    phone_number = restaurant.get("phone_number")

    # Verify phone assignment
    if phone_number:
        vapi_ok = verify_phone_in_vapi(
            phone_number, assistant_id, args.vapi_api_key)
        db_ok = verify_database_mapping_via_api(
            args.backend_url, phone_number, restaurant_id, args.vapi_secret
        )

        print_header("Test Results")
        print(f"Restaurant ID: {restaurant_id}")
        print(f"Phone Number: {phone_number}")
        print(f"Vapi Assignment: {'✓ PASS' if vapi_ok else '✗ FAIL'}")
        print(f"Database Mapping: {'✓ PASS' if db_ok else '✗ FAIL'}")

        if vapi_ok and db_ok:
            print("\n✅ All checks passed!")
            sys.exit(0)
        else:
            print("\n⚠ Some checks failed")
            sys.exit(1)
    else:
        print_header("Test Results")
        print(f"Restaurant ID: {restaurant_id}")
        print(f"Phone Number: None")
        print("⚠ No phone number was assigned")
        print("This might be expected if:")
        print("  - No phone numbers available")
        print("  - Twilio credentials not configured")
        print("  - Assistant not found")
        sys.exit(1)


if __name__ == "__main__":
    main()
