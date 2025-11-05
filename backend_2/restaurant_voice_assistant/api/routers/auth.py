"""Authentication API router.

This module provides REST endpoints for user authentication and registration
using Supabase Auth. It handles user creation, login, session management, and
user information retrieval.

Endpoints:
    - POST /api/auth/register: Register a new user
    - POST /api/auth/login: Login user and get JWT tokens
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
    UserResponse
)
from restaurant_voice_assistant.infrastructure.auth.service import get_current_user
from restaurant_voice_assistant.domain.auth.service import register_user, login_user
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
