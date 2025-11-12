#!/usr/bin/env python3
"""Clear all data from all tables while keeping schemas intact.

This script deletes all records from:
- restaurant_phone_mappings
- call_history
- menu_items
- categories
- modifiers
- delivery_zones
- operating_hours
- users
- restaurants

Note: This does NOT delete the tables themselves, only the data.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client

def clear_all_data():
    """Clear all data from all tables."""
    client = get_supabase_service_client()
    
    # Tables to clear (in order to respect foreign key constraints)
    tables = [
        'restaurant_phone_mappings',  # No dependencies
        'call_history',  # Depends on restaurants
        'menu_items',  # Depends on restaurants, categories
        'categories',  # Depends on restaurants
        'modifiers',  # Depends on restaurants
        'delivery_zones',  # Depends on restaurants
        'operating_hours',  # Depends on restaurants
        'users',  # Depends on restaurants
        'restaurants',  # Base table
    ]
    
    print("Clearing all table data...")
    print("=" * 50)
    
    for table in tables:
        try:
            # Delete all rows (using a condition that's always true)
            # For tables with UUID id, use a condition that matches all
            # For restaurant_phone_mappings, delete all
            if table == 'restaurant_phone_mappings':
                result = client.table(table).delete().neq('phone_number', '').execute()
            else:
                # For UUID tables, delete all rows
                result = client.table(table).delete().neq('id', '00000000-0000-0000-0000-000000000000').execute()
            
            count = len(result.data) if result.data else 0
            print(f"  ✓ {table}: {count} rows deleted")
        except Exception as e:
            print(f"  ✗ {table}: Error - {e}")
    
    print("=" * 50)
    print("Done! All data cleared (schemas preserved).")

if __name__ == "__main__":
    clear_all_data()

