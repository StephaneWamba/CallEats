"""
Authentication utilities for API endpoints.

Supports two authentication methods:
1. X-Vapi-Secret: For webhook endpoints and admin/script access
2. JWT (Supabase Auth): For frontend user authentication
"""
from fastapi import HTTPException, Request
from typing import Optional, Dict, Any
from src.core.config import get_settings


def verify_vapi_secret(x_vapi_secret: Optional[str]) -> None:
    """
    Verify Vapi secret header matches configured secret.
    
    Used for:
    - Webhook endpoints (/api/vapi/*)
    - Admin scripts and automation
    """
    settings = get_settings()
    if not x_vapi_secret or x_vapi_secret != settings.vapi_secret_key:
        raise HTTPException(status_code=401, detail="Invalid authentication")


def get_current_user(request: Request) -> Dict[str, Any]:
    """
    Get current authenticated user from request state (set by AuthMiddleware).
    
    Raises 401 if user is not authenticated.
    
    Returns:
        dict with keys: user_id, email, restaurant_id, role
    """
    user = getattr(request.state, "user", None)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please provide a valid JWT token in Authorization header."
        )
    return user


def get_restaurant_id(request: Request) -> str:
    """
    Get restaurant_id from authenticated user.
    
    Raises 401 if user is not authenticated.
    Raises 403 if user has no restaurant association.
    """
    user = get_current_user(request)
    restaurant_id = user.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(
            status_code=403,
            detail="User is not associated with a restaurant"
        )
    return restaurant_id


def require_auth(request: Request, x_vapi_secret: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Flexible authentication: accepts either JWT (user) or X-Vapi-Secret (webhook/admin).
    
    For endpoints that should work with both frontend users and webhooks/admin scripts.
    
    Args:
        request: FastAPI request object
        x_vapi_secret: Optional X-Vapi-Secret header value
        
    Returns:
        user dict if JWT authenticated, None if X-Vapi-Secret authenticated
        
    Raises:
        HTTPException: If neither authentication method is valid
    """
    # Check if JWT auth present (set by middleware)
    user = getattr(request.state, "user", None)
    
    # Check if X-Vapi-Secret present
    has_vapi_secret = x_vapi_secret is not None
    
    # Accept either authentication method
    if user:
        # JWT authenticated - return user info
        return user
    elif has_vapi_secret:
        # X-Vapi-Secret authenticated (webhook/admin)
        verify_vapi_secret(x_vapi_secret)
        return None  # No user context, but authenticated
    else:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Provide either JWT token (Authorization: Bearer) or X-Vapi-Secret header."
        )


def require_restaurant_access(request: Request, restaurant_id: str, x_vapi_secret: Optional[str] = None) -> None:
    """
    Require authentication AND verify restaurant access.
    
    For endpoints where users should only access their own restaurant.
    
    Args:
        request: FastAPI request object
        restaurant_id: Restaurant ID from path parameter
        x_vapi_secret: Optional X-Vapi-Secret header (bypasses restaurant check)
    """
    # If X-Vapi-Secret provided, allow access (admin/script)
    if x_vapi_secret:
        verify_vapi_secret(x_vapi_secret)
        return
    
    # Otherwise require JWT and check restaurant access
    user = get_current_user(request)
    user_restaurant_id = user.get("restaurant_id")
    
    if user_restaurant_id != restaurant_id:
        raise HTTPException(
            status_code=403,
            detail=f"Access denied. You can only access restaurant {user_restaurant_id}"
        )
