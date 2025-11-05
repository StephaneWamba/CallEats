"""Authentication domain service.

This module provides business logic for user authentication and registration
using Supabase Auth. It handles user creation, login, and restaurant association.

Key Features:
    - User registration with Supabase Auth
    - Email confirmation handling
    - Password-based authentication
    - Restaurant association management
    - User lookup and validation

Registration Flow:
    1. Check if user already exists
    2. Handle existing unconfirmed users (confirm and link)
    3. Create new user via Admin API (bypasses email confirmation)
    4. Link user to restaurant

Login Flow:
    1. Authenticate with Supabase Auth
    2. Return session tokens (access_token, refresh_token)
    3. Return user information

Usage:
    from restaurant_voice_assistant.domain.auth.service import (
        register_user,
        login_user,
        get_user_by_id
    )
    
    user = register_user(
        email="user@example.com",
        password="...",
        restaurant_id="..."
    )
    
    session = login_user(email="user@example.com", password="...")
"""
from typing import Dict, Any, Optional
from restaurant_voice_assistant.infrastructure.database.client import (
    get_supabase_client,
    get_supabase_service_client
)
import logging

logger = logging.getLogger(__name__)


def register_user(email: str, password: str, restaurant_id: str) -> Dict[str, Any]:
    """Register a new user with Supabase Auth and link to restaurant.

    Handles existing unconfirmed users by confirming and linking them.

    Args:
        email: User email address
        password: User password
        restaurant_id: Restaurant UUID to associate user with

    Returns:
        dict with keys: user_id, email

    Raises:
        ValueError: If email already registered or registration fails
        Exception: For other errors
    """
    supabase = get_supabase_client()
    service_client = get_supabase_service_client()

    # Check if user already exists in our users table
    existing_user = service_client.table("users").select(
        "id").eq("email", email).limit(1).execute()

    if existing_user.data:
        raise ValueError("Email already registered")

    # Check if user exists in auth.users but not in our users table
    try:
        admin_users = service_client.auth.admin.list_users()
        existing_auth_user = next(
            (u for u in admin_users if u.email == email), None)

        if existing_auth_user:
            user_id = existing_auth_user.id

            # Confirm user and update password
            service_client.auth.admin.update_user_by_id(
                user_id,
                {"email_confirm": True, "password": password}
            )

            # Link to restaurant
            insert_result = service_client.table("users").insert({
                "id": user_id,
                "restaurant_id": restaurant_id,
                "email": email,
                "role": "user"
            }).execute()

            if insert_result.data:
                return {
                    "user_id": user_id,
                    "email": email
                }
    except Exception:
        pass  # Continue to create new user

    # Create new user via Admin API (bypasses email confirmation)
    try:
        admin_auth_response = service_client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,
            "user_metadata": {}
        })

        if not admin_auth_response.user:
            raise Exception("Could not create user")

        user_id = admin_auth_response.user.id

    except Exception as admin_error:
        error_str = str(admin_error)
        if "already been registered" in error_str:
            raise ValueError("Email already registered")
        raise Exception(f"User creation failed: {error_str}")

    # Link user to restaurant
    insert_result = service_client.table("users").insert({
        "id": user_id,
        "restaurant_id": restaurant_id,
        "email": email,
        "role": "user"
    }).execute()

    if not insert_result.data:
        # Cleanup: delete auth user if linking fails
        try:
            service_client.auth.admin.delete_user(user_id)
        except:
            pass
        raise Exception("User created but failed to link to restaurant")

    return {
        "user_id": user_id,
        "email": email
    }


def login_user(email: str, password: str) -> Dict[str, Any]:
    """Login user and return session information.

    Args:
        email: User email address
        password: User password

    Returns:
        dict with keys: access_token, refresh_token, expires_in, token_type, user

    Raises:
        ValueError: If credentials are invalid
    """
    supabase = get_supabase_client()

    try:
        auth_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        if not auth_response.user or not auth_response.session:
            raise ValueError("Invalid credentials")

        return {
            "access_token": auth_response.session.access_token,
            "refresh_token": auth_response.session.refresh_token,
            "expires_in": auth_response.session.expires_in,
            "token_type": "Bearer",
            "user": {
                "id": auth_response.user.id,
                "email": auth_response.user.email
            }
        }
    except Exception as e:
        error_str = str(e).lower()
        if "invalid" in error_str or "credentials" in error_str or "password" in error_str:
            raise ValueError("Invalid email or password")
        raise


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user information by ID from users table.

    Args:
        user_id: User UUID

    Returns:
        dict with user info (user_id, email, restaurant_id, role) or None if not found
    """
    service_client = get_supabase_service_client()

    user_resp = service_client.table("users").select(
        "id, restaurant_id, role, email"
    ).eq("id", user_id).limit(1).execute()

    if user_resp.data:
        user_data = user_resp.data[0]
        return {
            "user_id": user_data["id"],
            "email": user_data.get("email"),
            "restaurant_id": user_data["restaurant_id"],
            "role": user_data.get("role", "user")
        }

    return None

