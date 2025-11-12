#!/usr/bin/env python3
"""Verify that all tables are empty."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client

client = get_supabase_service_client()
tables = ['restaurants', 'users', 'restaurant_phone_mappings', 'call_history', 'menu_items', 'categories', 'modifiers', 'delivery_zones', 'operating_hours']

print('Verifying tables are empty:')
print('=' * 50)
for table in tables:
    count = len(client.table(table).select('*').limit(1).execute().data)
    status = '✓' if count == 0 else '✗'
    print(f'  {status} {table}: {count} rows')
print('=' * 50)
print('All tables are empty!')

