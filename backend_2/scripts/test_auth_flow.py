#!/usr/bin/env python3
"""Test the authentication flow to see why get_restaurant_id is failing."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.domain.auth.service import login_user

# Test login and check user data
print("Testing login...")
result = login_user('stephane@qurisk.fr', 'Stephane123!')
print(f"Login successful. User ID: {result['user']['id']}")

# Check user in database
client = get_supabase_service_client()
user = client.table('users').select('*').eq('email', 'stephane@qurisk.fr').execute()
if user.data:
    user_data = user.data[0]
    print(f"\nUser in database:")
    print(f"  ID: {user_data['id']}")
    print(f"  Email: {user_data['email']}")
    print(f"  Restaurant ID: {user_data.get('restaurant_id')}")
    print(f"  Restaurant ID type: {type(user_data.get('restaurant_id'))}")
    print(f"  Restaurant ID is None: {user_data.get('restaurant_id') is None}")
    print(f"  Restaurant ID == 'None': {user_data.get('restaurant_id') == 'None'}")
    
    # Check restaurant
    if user_data.get('restaurant_id'):
        restaurant = client.table('restaurants').select('*').eq('id', user_data['restaurant_id']).execute()
        if restaurant.data:
            print(f"\nRestaurant found:")
            print(f"  ID: {restaurant.data[0]['id']}")
            print(f"  Name: {restaurant.data[0]['name']}")
        else:
            print(f"\nRestaurant NOT found for ID: {user_data['restaurant_id']}")

