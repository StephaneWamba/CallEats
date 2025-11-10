"""Authentication API router.

This module provides REST endpoints for user authentication and registration
using Supabase Auth. It handles user creation, login, session management, and
user information retrieval.

Endpoints:
    - POST /api/auth/register: Register a new user
    - POST /api/auth/register-with-restaurant: One-step registration (user + restaurant)
    - POST /api/auth/login: Login user and get JWT tokens
    - POST /api/auth/reset-password: Request password reset email
    - POST /api/auth/change-password: Change authenticated user's password
    - POST /api/auth/refresh: Refresh expired access token
    - GET /api/auth/me: Get current authenticated user info
    - POST /api/auth/logout: Logout (client-side token discard)

Authentication:
    - Registration/Login: Public endpoints (no auth required)
    - /me endpoint: Requires JWT token in Authorization header
    - All endpoints use Supabase Auth for user management

Usage:
    Register a user:
        POST /api/auth/register
        Body: {"email": "...", "password": "...", "restaurant_id": "..."}
    
    Login:
        POST /api/auth/login
        Body: {"email": "...", "password": "..."}
        Returns: {"access_token": "...", "refresh_token": "...", ...}
"""
from fastapi import APIRouter, HTTPException, Depends
from restaurant_voice_assistant.shared.models.auth import (
    RegisterRequest,
    LoginRequest,
    ResetPasswordRequest,
    ChangePasswordRequest,
    RefreshTokenRequest,
    UserResponse,
    RegisterWithRestaurantRequest,
    RegisterWithRestaurantResponse
)
from restaurant_voice_assistant.infrastructure.auth.service import get_current_user
from restaurant_voice_assistant.domain.auth.service import (
    register_user,
    login_user,
    request_password_reset,
    change_password,
    refresh_token,
    register_with_restaurant
)
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/register",
    summary="Register User",
    description="Register a new user with Supabase Auth and link to restaurant.",
    responses={
        200: {"description": "Registration successful"},
        400: {"description": "Registration failed (email already exists or invalid data)"}
    }
)
async def register(request: RegisterRequest):
    """Register a new user with Supabase Auth.

    Creates user in auth.users and links to restaurant in users table.
    Handles existing unconfirmed users by confirming and linking them.
    """
    try:
        result = register_user(
            email=request.email,
            password=request.password,
            restaurant_id=request.restaurant_id
        )

        return {
            "message": "Registration successful.",
            "user_id": result["user_id"],
            "email": result["email"]
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail="Registration failed. Please try again.")


@router.post(
    "/register-with-restaurant",
    response_model=RegisterWithRestaurantResponse,
    summary="One-Step Registration",
    description="Create both restaurant and user account in a single API call, then auto-login.",
    responses={
        200: {"description": "Registration successful"},
        400: {"description": "Registration failed (email already exists or invalid data)"}
    }
)
async def register_with_restaurant_endpoint(request: RegisterWithRestaurantRequest):
    """One-step registration: creates restaurant and user account, then logs in automatically.

    Creates restaurant first (with phone assignment), then registers user,
    then logs in user automatically. Returns user, restaurant, and session data.
    If user registration fails, rolls back by deleting the restaurant.
    """
    try:
        result = register_with_restaurant(
            email=request.email,
            password=request.password,
            restaurant_name=request.restaurant_name
        )

        return RegisterWithRestaurantResponse(**result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"One-step registration error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail="Registration failed. Please try again.")


@router.post(
    "/login",
    summary="Login User",
    description="Login user and return JWT tokens (access_token and refresh_token).",
    responses={
        200: {"description": "Login successful"},
        401: {"description": "Invalid email or password"}
    }
)
async def login(request: LoginRequest):
    """Login user and return JWT tokens.

    Returns access_token and refresh_token for use in Authorization header.
    """
    try:
        return login_user(email=request.email, password=request.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Login error: {e}", exc_info=True)
        raise HTTPException(
            status_code=401, detail="Invalid email or password")


@router.post(
    "/reset-password",
    summary="Request Password Reset",
    description="Sends password reset email to user. Always returns success to prevent email enumeration.",
    responses={
        200: {"description": "Password reset email sent (if email exists)"}
    }
)
async def reset_password(request: ResetPasswordRequest):
    """Request password reset email.

    Public endpoint - no authentication required.
    Uses Supabase Auth's built-in password reset functionality.
    Always returns success message regardless of whether email exists to prevent email enumeration attacks.

    Frontend will handle token verification and password update using Supabase client SDK.
    """
    try:
        result = request_password_reset(email=request.email)
        return result
    except Exception as e:
        logger.error(f"Password reset error: {e}", exc_info=True)
        # Return success anyway for security (don't reveal if email exists)
        return {
            "message": "If an account with that email exists, a password reset link has been sent."
        }


@router.post(
    "/change-password",
    summary="Change Password",
    description="Change authenticated user's password. Requires current password verification.",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Invalid current password or new password doesn't meet requirements"},
        401: {"description": "Authentication required"}
    }
)
async def change_user_password(
    request: ChangePasswordRequest,
    user: dict = Depends(get_current_user)
):
    """Change user password.

    Requires authentication. Verifies current password before updating.
    """
    try:
        result = change_password(
            user_id=user["user_id"],
            email=user["email"],
            current_password=request.current_password,
            new_password=request.new_password
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Password change error: {e}", exc_info=True)
        raise HTTPException(
            status_code=400, detail="Failed to change password")


@router.post(
    "/refresh",
    summary="Refresh Token",
    description="Refresh an expired access token using a refresh token.",
    responses={
        200: {"description": "Token refreshed successfully"},
        401: {"description": "Invalid or expired refresh token"}
    }
)
async def refresh_access_token(request: RefreshTokenRequest):
    """Refresh an expired access token.

    Public endpoint - no authentication required (uses refresh_token for auth).
    Returns new access_token and refresh_token.
    """
    try:
        return refresh_token(refresh_token_str=request.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        logger.error(f"Token refresh error: {e}", exc_info=True)
        raise HTTPException(
            status_code=401, detail="Invalid or expired refresh token")


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User",
    description="Get current authenticated user information. Requires JWT token.",
    responses={
        200: {"description": "User information retrieved"},
        401: {"description": "Authentication required"}
    }
)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        restaurant_id=user["restaurant_id"],
        role=user["role"]
    )


@router.post(
    "/logout",
    summary="Logout User",
    description="Logout user. Client should discard tokens on their side.",
    responses={
        200: {"description": "Logout successful"}
    }
)
async def logout():
    """Logout user (client should discard tokens)."""
    return {"message": "Logged out successfully. Please discard your tokens."}
