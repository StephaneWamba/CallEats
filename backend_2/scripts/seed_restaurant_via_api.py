#!/usr/bin/env python3
"""Seed restaurant data via API.

This script seeds a restaurant with sample data using the REST API endpoints.
It creates categories, menu items, modifiers, operating hours, and delivery zones.

Usage:
    python scripts/seed_restaurant_via_api.py --restaurant-id <restaurant_id> --backend-url <url>
"""
import requests
import argparse
import sys
import os
from pathlib import Path
from decimal import Decimal
from typing import Dict, Any, List, Optional

# Add backend_2 to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}\n{text}\n{'=' * 60}")


def print_section(text: str):
    """Print a formatted section header."""
    print(f"\n{'-' * 60}\n{text}\n{'-' * 60}")


def create_category(
    backend_url: str,
    restaurant_id: str,
    name: str,
    description: Optional[str] = None,
    display_order: int = 0,
    vapi_secret: str = None
) -> Optional[Dict[str, Any]]:
    """Create a category via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/categories"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "name": name,
        "description": description,
        "display_order": display_order
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(
            f"  ⚠ Failed to create category '{name}': {response.status_code} - {response.text}")
        return None


def create_menu_item(
    backend_url: str,
    restaurant_id: str,
    name: str,
    price: Decimal,
    category_id: Optional[str] = None,
    description: Optional[str] = None,
    available: bool = True,
    vapi_secret: str = None
) -> Optional[Dict[str, Any]]:
    """Create a menu item via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/menu-items"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "name": name,
        "price": float(price),
        "description": description,
        "available": available
    }
    if category_id:
        payload["category_id"] = category_id

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(
            f"  ⚠ Failed to create menu item '{name}': {response.status_code} - {response.text}")
        return None


def create_modifier(
    backend_url: str,
    restaurant_id: str,
    name: str,
    price: Decimal,
    description: Optional[str] = None,
    vapi_secret: str = None
) -> Optional[Dict[str, Any]]:
    """Create a modifier via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/modifiers"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "name": name,
        "price": float(price),
        "description": description
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(
            f"  ⚠ Failed to create modifier '{name}': {response.status_code} - {response.text}")
        return None


def link_modifier_to_item(
    backend_url: str,
    restaurant_id: str,
    item_id: str,
    modifier_id: str,
    vapi_secret: str = None,
    is_required: bool = False,
    display_order: int = 0
) -> bool:
    """Link a modifier to a menu item via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/menu-items/{item_id}/modifiers"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "modifier_id": modifier_id,
        "is_required": is_required,
        "display_order": display_order
    }

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    return response.status_code in [200, 201]


def update_operating_hours(
    backend_url: str,
    restaurant_id: str,
    hours: List[Dict[str, Any]],
    vapi_secret: str = None
) -> bool:
    """Update operating hours via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/hours"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {"hours": hours}

    response = requests.put(url, json=payload, headers=headers, timeout=30)
    return response.status_code in [200, 201]


def create_delivery_zone(
    backend_url: str,
    restaurant_id: str,
    zone_name: str,
    delivery_fee: Decimal,
    description: Optional[str] = None,
    min_order: Optional[Decimal] = None,
    vapi_secret: str = None
) -> Optional[Dict[str, Any]]:
    """Create a delivery zone via API."""
    url = f"{backend_url.rstrip('/')}/api/restaurants/{restaurant_id}/zones"
    headers = {
        "Content-Type": "application/json",
        "X-Vapi-Secret": vapi_secret
    }
    payload = {
        "zone_name": zone_name,
        "delivery_fee": float(delivery_fee),
        "description": description
    }
    if min_order:
        payload["min_order"] = float(min_order)

    response = requests.post(url, json=payload, headers=headers, timeout=30)
    if response.status_code in [200, 201]:
        return response.json()
    else:
        print(
            f"  ⚠ Failed to create delivery zone '{zone_name}': {response.status_code} - {response.text}")
        return None


def seed_restaurant(
    backend_url: str,
    restaurant_id: str,
    vapi_secret: str
):
    """Seed a restaurant with sample data."""
    print_header(f"Seeding Restaurant: {restaurant_id}")

    # Sample data
    categories_data = [
        {"name": "Appetizers", "description": "Start your meal right", "display_order": 0},
        {"name": "Main Courses", "description": "Hearty main dishes", "display_order": 1},
        {"name": "Desserts", "description": "Sweet endings", "display_order": 2},
        {"name": "Beverages", "description": "Drinks and refreshments", "display_order": 3}
    ]

    menu_items_data = [
        {"name": "Caesar Salad", "description": "Fresh romaine lettuce with Caesar dressing",
            "price": 8.99, "category": "Appetizers"},
        {"name": "Bruschetta", "description": "Toasted bread with tomatoes and basil",
            "price": 7.50, "category": "Appetizers"},
        {"name": "Grilled Chicken", "description": "Tender grilled chicken breast with herbs",
            "price": 16.99, "category": "Main Courses"},
        {"name": "Pasta Carbonara", "description": "Creamy pasta with bacon and parmesan",
            "price": 14.99, "category": "Main Courses"},
        {"name": "Chocolate Cake", "description": "Rich chocolate layer cake",
            "price": 6.99, "category": "Desserts"},
        {"name": "Tiramisu", "description": "Classic Italian dessert",
            "price": 7.50, "category": "Desserts"},
        {"name": "Coca Cola", "description": "Classic soft drink",
            "price": 2.50, "category": "Beverages"},
        {"name": "Fresh Orange Juice", "description": "Freshly squeezed orange juice",
            "price": 3.99, "category": "Beverages"}
    ]

    modifiers_data = [
        {"name": "Extra Cheese", "description": "Additional cheese", "price": 1.50},
        {"name": "No Onions", "description": "Remove onions", "price": 0.00},
        {"name": "Extra Sauce", "description": "Extra sauce on the side", "price": 0.50},
        {"name": "Gluten Free", "description": "Gluten-free option", "price": 2.00}
    ]

    operating_hours_data = [
        {"day_of_week": "Monday", "open_time": "09:00:00",
            "close_time": "22:00:00", "is_closed": False},
        {"day_of_week": "Tuesday", "open_time": "09:00:00",
            "close_time": "22:00:00", "is_closed": False},
        {"day_of_week": "Wednesday", "open_time": "09:00:00",
            "close_time": "22:00:00", "is_closed": False},
        {"day_of_week": "Thursday", "open_time": "09:00:00",
            "close_time": "22:00:00", "is_closed": False},
        {"day_of_week": "Friday", "open_time": "09:00:00",
            "close_time": "23:00:00", "is_closed": False},
        {"day_of_week": "Saturday", "open_time": "10:00:00",
            "close_time": "23:00:00", "is_closed": False},
        {"day_of_week": "Sunday", "open_time": "10:00:00",
            "close_time": "21:00:00", "is_closed": False}
    ]

    delivery_zones_data = [
        {"zone_name": "Downtown", "description": "Downtown area",
            "delivery_fee": 5.00, "min_order": 15.00},
        {"zone_name": "Suburbs", "description": "Suburban areas",
            "delivery_fee": 8.00, "min_order": 20.00},
        {"zone_name": "City Center", "description": "City center delivery",
            "delivery_fee": 4.00, "min_order": 12.00}
    ]

    # Create categories
    print_section("Creating Categories")
    category_map = {}
    for cat_data in categories_data:
        category = create_category(
            backend_url, restaurant_id,
            cat_data["name"], cat_data.get("description"),
            cat_data.get("display_order", 0), vapi_secret
        )
        if category:
            category_map[cat_data["name"]] = category["id"]
            print(f"  ✓ Created category: {cat_data['name']}")

    # Create menu items
    print_section("Creating Menu Items")
    item_map = {}
    for item_data in menu_items_data:
        category_id = category_map.get(item_data["category"])
        item = create_menu_item(
            backend_url, restaurant_id,
            item_data["name"], Decimal(str(item_data["price"])),
            category_id, item_data.get("description"),
            True, vapi_secret
        )
        if item:
            item_map[item_data["name"]] = item["id"]
            print(
                f"  ✓ Created menu item: {item_data['name']} (${item_data['price']})")

    # Create modifiers
    print_section("Creating Modifiers")
    modifier_map = {}
    for mod_data in modifiers_data:
        modifier = create_modifier(
            backend_url, restaurant_id,
            mod_data["name"], Decimal(str(mod_data["price"])),
            mod_data.get("description"), vapi_secret
        )
        if modifier:
            modifier_map[mod_data["name"]] = modifier["id"]
            print(
                f"  ✓ Created modifier: {mod_data['name']} (${mod_data['price']})")

    # Link modifiers to items
    print_section("Linking Modifiers to Items")
    # Link "Extra Cheese" to pasta items
    if "Pasta Carbonara" in item_map and "Extra Cheese" in modifier_map:
        if link_modifier_to_item(backend_url, restaurant_id, item_map["Pasta Carbonara"], modifier_map["Extra Cheese"], vapi_secret):
            print(f"  ✓ Linked 'Extra Cheese' to 'Pasta Carbonara'")
        else:
            print(f"  ⚠ Failed to link 'Extra Cheese' to 'Pasta Carbonara'")

    # Link "No Onions" to salad
    if "Caesar Salad" in item_map and "No Onions" in modifier_map:
        if link_modifier_to_item(backend_url, restaurant_id, item_map["Caesar Salad"], modifier_map["No Onions"], vapi_secret):
            print(f"  ✓ Linked 'No Onions' to 'Caesar Salad'")
        else:
            print(f"  ⚠ Failed to link 'No Onions' to 'Caesar Salad'")

    # Update operating hours
    print_section("Setting Operating Hours")
    if update_operating_hours(backend_url, restaurant_id, operating_hours_data, vapi_secret):
        print(f"  ✓ Set operating hours for all days")
    else:
        print(f"  ⚠ Failed to set operating hours")

    # Create delivery zones
    print_section("Creating Delivery Zones")
    for zone_data in delivery_zones_data:
        zone = create_delivery_zone(
            backend_url, restaurant_id,
            zone_data["zone_name"], Decimal(str(zone_data["delivery_fee"])),
            zone_data.get("description"), Decimal(str(zone_data["min_order"])),
            vapi_secret
        )
        if zone:
            print(
                f"  ✓ Created delivery zone: {zone_data['zone_name']} (${zone_data['delivery_fee']} fee, ${zone_data['min_order']} min)")

    print_header("Seeding Complete!")
    print(f"✓ Categories: {len(category_map)}")
    print(f"✓ Menu Items: {len(item_map)}")
    print(f"✓ Modifiers: {len(modifier_map)}")
    print(f"✓ Operating Hours: {len(operating_hours_data)} days")
    print(f"✓ Delivery Zones: {len(delivery_zones_data)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Seed restaurant data via API")
    parser.add_argument(
        "--restaurant-id",
        type=str,
        required=True,
        help="Restaurant UUID to seed"
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

    args = parser.parse_args()

    if not args.backend_url:
        print("Error: --backend-url required or set PUBLIC_BACKEND_URL env var", file=sys.stderr)
        sys.exit(1)

    if not args.vapi_secret:
        print(
            "Error: --vapi-secret required or set VAPI_SECRET_KEY env var", file=sys.stderr)
        sys.exit(1)

    seed_restaurant(args.backend_url, args.restaurant_id, args.vapi_secret)


if __name__ == "__main__":
    main()
