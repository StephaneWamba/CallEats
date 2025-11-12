#!/usr/bin/env python3
"""Check phone number assignment in Vapi."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_voice_assistant.infrastructure.vapi.client import VapiClient
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client

vapi_client = VapiClient(api_key='17e98d2e-d0c0-4fe8-8dfc-7b96ae375f61')
db_client = get_supabase_service_client()

# Get restaurant and phone mapping
restaurant = db_client.table('restaurants').select('*').eq('name', 'Bistro').execute()
if restaurant.data:
    restaurant_id = restaurant.data[0]['id']
    print(f"Restaurant: {restaurant.data[0]['name']} (ID: {restaurant_id})")
    
    mapping = db_client.table('restaurant_phone_mappings').select('*').eq('restaurant_id', restaurant_id).execute()
    if mapping.data:
        phone_number = mapping.data[0]['phone_number']
        print(f"Phone Number in DB: {phone_number}")
        
        # Check in Vapi
        phones = vapi_client.list_phone_numbers()
        for p in phones:
            if phone_number.replace('+', '').replace('-', '').replace(' ', '') in p.get('number', '').replace('+', '').replace('-', '').replace(' ', ''):
                print(f"Phone in Vapi: {p.get('number')}")
                print(f"  Phone ID: {p.get('id')}")
                print(f"  Assistant ID: {p.get('assistantId')}")
                print(f"  Is assigned: {p.get('assistantId') is not None}")
                break
    else:
        print("No phone mapping found")
else:
    print("Restaurant not found")

