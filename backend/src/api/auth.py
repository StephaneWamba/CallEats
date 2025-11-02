"""
Authentication API endpoints.

Thin HTTP layer that delegates to authentication service.
"""
from fastapi import APIRouter, HTTPException, Depends
from src.models.auth import RegisterRequest, LoginRequest, UserResponse
from src.services.infrastructure.auth import get_current_user
from src.services.auth.service import register_user, login_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/register")
async def register(request: RegisterRequest):
    """
    Register a new user with Supabase Auth.

    Creates user in auth.users and links to restaurant in users table.
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


@router.post("/login")
async def login(request: LoginRequest):
    """
    Login user and return JWT tokens.

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


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(user: dict = Depends(get_current_user)):
    """Get current authenticated user information."""
    return UserResponse(
        user_id=user["user_id"],
        email=user["email"],
        restaurant_id=user["restaurant_id"],
        role=user["role"]
    )


@router.post("/logout")
async def logout():
    """Logout user (client should discard tokens)."""
    return {"message": "Logged out successfully. Please discard your tokens."}
