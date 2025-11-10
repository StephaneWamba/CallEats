"""Authentication domain service.

This module provides business logic for user authentication and registration
using Supabase Auth. It handles user creation, login, and restaurant association.

Key Features:
    - User registration with Supabase Auth
    - Email confirmation handling
    - Password-based authentication
    - Password reset via email
    - Password change for authenticated users
    - Token refresh for session management
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
        request_password_reset,
        change_password,
        refresh_token,
        get_user_by_id
    )
    
    user = register_user(
        email="user@example.com",
        password="...",
        restaurant_id="..."
    )
    
    session = login_user(email="user@example.com", password="...")
    reset_result = request_password_reset(email="user@example.com")
    change_result = change_password(user_id="...", email="...", current_password="...", new_password="...")
    refresh_result = refresh_token(refresh_token="...")
"""
from typing import Dict, Any, Optional
from restaurant_voice_assistant.infrastructure.database.client import (
    get_supabase_client,
    get_supabase_service_client
)
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.domain.restaurants.service import create_restaurant
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


def request_password_reset(email: str) -> Dict[str, Any]:
    """Request password reset email via Supabase Auth.

    Uses Supabase Auth's reset_password_for_email method which:
    - Generates a secure reset token
    - Sends email with reset link automatically
    - Token expires after configured time (default: 1 hour)

    Args:
        email: User email address

    Returns:
        dict with success message (always returns success to prevent email enumeration)

    Raises:
        Exception: If Supabase operation fails (but still returns success message)
    """
    supabase = get_supabase_client()
    settings = get_settings()

    # Use FRONTEND_URL if set, otherwise fall back to PUBLIC_BACKEND_URL
    # Frontend will handle the reset password page
    redirect_url = settings.frontend_url or settings.public_backend_url or 'http://localhost:3000'
    reset_redirect_url = f"{redirect_url.rstrip('/')}/reset-password"

    try:
        # Supabase automatically sends password reset email
        # The email contains a link with token that redirects to reset_redirect_url
        supabase.auth.reset_password_for_email(
            email,
            {
                "redirect_to": reset_redirect_url
            }
        )

        # Always return success to prevent email enumeration attacks
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }
    except Exception as e:
        logger.error(f"Password reset request error: {e}", exc_info=True)
        # Still return success message for security (don't reveal if email exists)
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }


def change_password(
    user_id: str,
    email: str,
    current_password: str,
    new_password: str
) -> Dict[str, Any]:
    """Change user password after verifying current password.

    Args:
        user_id: User UUID from JWT
        email: User email from JWT
        current_password: Current password to verify
        new_password: New password to set

    Returns:
        Success message

    Raises:
        ValueError: If current password is invalid or new password doesn't meet requirements
    """
    supabase = get_supabase_client()
    service_client = get_supabase_service_client()

    # Step 1: Verify current password by attempting sign-in
    try:
        verify_response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": current_password
        })

        if not verify_response.user:
            raise ValueError("Invalid current password")
    except Exception as e:
        error_str = str(e).lower()
        if "invalid" in error_str or "credentials" in error_str or "password" in error_str:
            raise ValueError("Invalid current password")
        raise

    # Step 2: Validate new password requirements
    if len(new_password) < 6:
        raise ValueError("New password must be at least 6 characters long")

    # Step 3: Update password using Admin API
    try:
        service_client.auth.admin.update_user_by_id(
            user_id,
            {"password": new_password}
        )

        logger.info(f"Password changed successfully for user {user_id}")

        return {
            "message": "Password changed successfully"
        }
    except Exception as e:
        logger.error(
            f"Password change error for user {user_id}: {e}", exc_info=True)
        raise ValueError("Failed to update password")


def refresh_token(refresh_token_str: str) -> Dict[str, Any]:
    """Refresh an expired access token using a refresh token.

    Uses Supabase Auth's refresh_session method to get new tokens.
    Creates a new client instance with the refresh token to refresh the session.

    Args:
        refresh_token_str: Refresh token from previous login

    Returns:
        dict with keys: access_token, refresh_token, expires_in, token_type, user

    Raises:
        ValueError: If refresh token is invalid or expired
    """
    settings = get_settings()
    supabase = get_supabase_client()

    try:
        # Set session with refresh token (access_token can be empty for refresh)
        # Then refresh to get new tokens
        supabase.auth.set_session(
            access_token="",  # Empty, we only have refresh token
            refresh_token=refresh_token_str
        )

        # Refresh the session to get new tokens
        refresh_response = supabase.auth.refresh_session()

        if not refresh_response.session:
            raise ValueError("Invalid or expired refresh token")

        session = refresh_response.session
        user = refresh_response.user

        return {
            "access_token": session.access_token,
            "refresh_token": session.refresh_token,
            "expires_in": session.expires_in,
            "token_type": "Bearer",
            "user": {
                "id": user.id if user else None,
                "email": user.email if user else None
            }
        }
    except Exception as e:
        error_str = str(e).lower()
        if "invalid" in error_str or "expired" in error_str or "token" in error_str:
            raise ValueError("Invalid or expired refresh token")
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise ValueError("Failed to refresh token")


def register_with_restaurant(email: str, password: str, restaurant_name: str) -> Dict[str, Any]:
    """Register a new user and create restaurant in a single transaction.

    Creates restaurant first, then registers user, then logs in automatically.
    If user registration fails, rolls back by deleting the restaurant.

    Args:
        email: User email address
        password: User password
        restaurant_name: Restaurant name

    Returns:
        dict with keys: user, restaurant, session
        - user: {user_id, email}
        - restaurant: {id, name, phone_number, api_key}
        - session: {access_token, refresh_token, expires_in, token_type}

    Raises:
        ValueError: If email already registered or registration fails
        Exception: For other errors
    """
    service_client = get_supabase_service_client()
    restaurant_id = None
    user_id = None

    try:
        # Step 1: Create restaurant (with phone assignment)
        restaurant_data = create_restaurant(
            name=restaurant_name,
            assign_phone=True
        )
        restaurant_id = restaurant_data["id"]

        # Step 2: Register user with restaurant_id
        user_result = register_user(
            email=email,
            password=password,
            restaurant_id=restaurant_id
        )
        user_id = user_result["user_id"]

        # Step 3: Login user automatically
        session_result = login_user(email=email, password=password)

        # Step 4: Return combined response
        return {
            "user": {
                "user_id": user_result["user_id"],
                "email": user_result["email"]
            },
            "restaurant": {
                "id": restaurant_data["id"],
                "name": restaurant_data["name"],
                "phone_number": restaurant_data.get("phone_number"),
                "api_key": restaurant_data["api_key"]
            },
            "session": {
                "access_token": session_result["access_token"],
                "refresh_token": session_result["refresh_token"],
                "expires_in": session_result["expires_in"],
                "token_type": session_result["token_type"]
            }
        }

    except Exception as e:
        # Rollback: Delete restaurant if it was created but user registration failed
        if restaurant_id and not user_id:
            try:
                # Delete restaurant (cascade delete will handle related data)
                service_client.table("restaurants").delete().eq(
                    "id", restaurant_id).execute()
                logger.info(
                    f"Rolled back restaurant {restaurant_id} due to registration failure")
            except Exception as rollback_error:
                logger.error(
                    f"Failed to rollback restaurant {restaurant_id}: {rollback_error}",
                    exc_info=True
                )

        # Re-raise the original error
        raise
