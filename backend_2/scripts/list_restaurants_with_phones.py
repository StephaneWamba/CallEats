#!/usr/bin/env python3
"""List restaurants with phone numbers and check assistant ID assignments.

This script:
1. Lists all restaurants with phone numbers
2. Checks which phone numbers in Vapi have assistant IDs
3. Shows restaurants that are attached to assistants
4. Can create a user account linked to an existing restaurant
"""
import sys
import os
from typing import Dict, List, Optional, Any

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.infrastructure.vapi.client import VapiClient
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.domain.auth.service import register_user, login_user
from restaurant_voice_assistant.domain.restaurants.service import get_restaurant


def get_all_restaurants_with_phones() -> List[Dict[str, Any]]:
    """Get all restaurants with their phone numbers."""
    supabase = get_supabase_service_client()
    
    # Get all restaurants
    restaurants_resp = supabase.table("restaurants").select(
        "id, name, api_key, created_at"
    ).execute()
    
    restaurants = restaurants_resp.data or []
    
    # Get phone mappings
    phone_mappings_resp = supabase.table("restaurant_phone_mappings").select(
        "restaurant_id, phone_number"
    ).execute()
    
    phone_map = {
        mapping["restaurant_id"]: mapping["phone_number"]
        for mapping in (phone_mappings_resp.data or [])
    }
    
    # Add phone numbers to restaurants
    for restaurant in restaurants:
        restaurant["phone_number"] = phone_map.get(restaurant["id"])
    
    # Filter to only restaurants with phone numbers
    return [r for r in restaurants if r.get("phone_number")]


def get_vapi_phone_assignments(vapi_api_key: str) -> Dict[str, Dict[str, Any]]:
    """Get phone number assignments from Vapi (phone -> assistant_id mapping)."""
    client = VapiClient(api_key=vapi_api_key)
    phones = client.list_phone_numbers()
    
    phone_assignments = {}
    for phone in phones:
        phone_number = phone.get("number")
        assistant_id = phone.get("assistantId")
        phone_id = phone.get("id")
        
        if phone_number:
            # Normalize phone number
            phone_clean = phone_number.replace(" ", "").replace(
                "(", "").replace(")", "").replace("-", "")
            phone_assignments[phone_clean] = {
                "assistant_id": assistant_id,
                "phone_id": phone_id,
                "phone_number": phone_number
            }
    
    return phone_assignments


def normalize_phone(phone_number: str) -> str:
    """Normalize phone number for comparison."""
    return phone_number.replace(" ", "").replace(
        "(", "").replace(")", "").replace("-", "")


def list_restaurants_with_assistants(
    vapi_api_key: Optional[str] = None
) -> List[Dict[str, Any]]:
    """List restaurants with phone numbers and their assistant assignments."""
    print("=" * 80)
    print("RESTAURANTS WITH PHONE NUMBERS AND ASSISTANT ASSIGNMENTS")
    print("=" * 80)
    
    # Get restaurants with phones
    restaurants = get_all_restaurants_with_phones()
    
    if not restaurants:
        print("\nNo restaurants with phone numbers found.")
        return []
    
    print(f"\nFound {len(restaurants)} restaurant(s) with phone numbers:\n")
    
    # Get Vapi phone assignments if API key provided
    phone_assignments = {}
    if vapi_api_key:
        try:
            print("Fetching phone assignments from Vapi...")
            phone_assignments = get_vapi_phone_assignments(vapi_api_key)
            print(f"Found {len(phone_assignments)} phone number(s) in Vapi\n")
        except Exception as e:
            print(f"Warning: Could not fetch Vapi phone assignments: {e}\n")
    
    results = []
    
    for i, restaurant in enumerate(restaurants, 1):
        phone_number = restaurant.get("phone_number")
        phone_clean = normalize_phone(phone_number) if phone_number else None
        
        assistant_id = None
        phone_id = None
        
        if phone_clean and phone_clean in phone_assignments:
            assignment = phone_assignments[phone_clean]
            assistant_id = assignment.get("assistant_id")
            phone_id = assignment.get("phone_id")
        
        print(f"{i}. Restaurant: {restaurant['name']}")
        print(f"   ID: {restaurant['id']}")
        print(f"   Phone: {phone_number or 'N/A'}")
        print(f"   Assistant ID: {assistant_id or 'Not assigned'}")
        print(f"   Phone ID: {phone_id or 'N/A'}")
        print(f"   Created: {restaurant.get('created_at', 'N/A')}")
        print()
        
        results.append({
            "restaurant": restaurant,
            "assistant_id": assistant_id,
            "phone_id": phone_id,
            "has_assistant": assistant_id is not None
        })
    
    # Summary
    restaurants_with_assistants = [r for r in results if r["has_assistant"]]
    restaurants_without_assistants = [r for r in results if not r["has_assistant"]]
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total restaurants with phones: {len(results)}")
    print(f"Restaurants with assistant assigned: {len(restaurants_with_assistants)}")
    print(f"Restaurants without assistant: {len(restaurants_without_assistants)}")
    print()
    
    return results


def create_account_for_restaurant(
    restaurant_id: str,
    email: str,
    password: str
) -> Dict[str, Any]:
    """Create a user account and link it to an existing restaurant."""
    print(f"\nCreating account for restaurant {restaurant_id}...")
    
    # Get restaurant to verify it exists
    restaurant = get_restaurant(restaurant_id)
    if not restaurant:
        raise ValueError(f"Restaurant {restaurant_id} not found")
    
    print(f"Restaurant found: {restaurant['name']}")
    print(f"Phone: {restaurant.get('phone_number', 'N/A')}")
    
    # Register user with existing restaurant_id
    try:
        user_result = register_user(
            email=email,
            password=password,
            restaurant_id=restaurant_id
        )
        
        print(f"✓ User registered: {user_result['user_id']}")
        
        # Login user
        session_result = login_user(email=email, password=password)
        
        print(f"✓ User logged in successfully")
        print(f"\nAccount created and linked to restaurant!")
        print(f"Email: {email}")
        print(f"Restaurant: {restaurant['name']}")
        print(f"Access Token: {session_result['access_token'][:50]}...")
        
        return {
            "user": user_result,
            "restaurant": restaurant,
            "session": session_result
        }
    except Exception as e:
        print(f"✗ Error creating account: {e}")
        raise


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="List restaurants with phone numbers and assistant assignments"
    )
    parser.add_argument(
        "--vapi-api-key",
        help="Vapi API key to check assistant assignments (optional)"
    )
    parser.add_argument(
        "--create-account",
        action="store_true",
        help="Create account for a restaurant"
    )
    parser.add_argument(
        "--restaurant-id",
        help="Restaurant ID to create account for (required with --create-account)"
    )
    parser.add_argument(
        "--email",
        help="Email for new account (required with --create-account)"
    )
    parser.add_argument(
        "--password",
        help="Password for new account (required with --create-account)"
    )
    
    args = parser.parse_args()
    
    # Get Vapi API key from settings if not provided
    vapi_api_key = args.vapi_api_key
    if not vapi_api_key:
        try:
            settings = get_settings()
            vapi_api_key = settings.vapi_api_key
        except Exception:
            pass
    
    # List restaurants
    results = list_restaurants_with_assistants(vapi_api_key)
    
    # Create account if requested
    if args.create_account:
        if not args.restaurant_id:
            print("\nError: --restaurant-id is required with --create-account")
            sys.exit(1)
        if not args.email:
            print("\nError: --email is required with --create-account")
            sys.exit(1)
        if not args.password:
            print("\nError: --password is required with --create-account")
            sys.exit(1)
        
        try:
            create_account_for_restaurant(
                args.restaurant_id,
                args.email,
                args.password
            )
        except Exception as e:
            print(f"\nFailed to create account: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()

