"""Authentication utilities for API endpoints.

This module provides authentication helpers that support dual authentication:
    1. JWT (Supabase Auth): For frontend user authentication
    2. X-Vapi-Secret: For webhook endpoints and admin/script access

Key Functions:
    - verify_vapi_secret(): Verify Vapi webhook secret
    - get_current_user(): Get authenticated user from request
    - get_restaurant_id(): Extract restaurant_id from authenticated user
    - require_auth(): Flexible auth (accepts JWT or X-Vapi-Secret)
    - require_restaurant_access(): Require auth + verify restaurant access

Authentication Flow:
    - JWT tokens are verified by AuthMiddleware and attached to request.state
    - X-Vapi-Secret is checked on-demand for webhook/admin endpoints
    - Users can only access their own restaurant's data (enforced by require_restaurant_access)

Usage:
    from restaurant_voice_assistant.infrastructure.auth.service import (
        require_auth,
        require_restaurant_access
    )
    
    @router.get("/restaurants/{restaurant_id}")
    def get_restaurant(request: Request, restaurant_id: str, x_vapi_secret: Optional[str] = None):
        require_restaurant_access(request, restaurant_id, x_vapi_secret)
        # ... endpoint logic
"""
from fastapi import HTTPException, Request
from typing import Optional, Dict, Any
from restaurant_voice_assistant.core.config import get_settings


def verify_vapi_secret(x_vapi_secret: Optional[str]) -> None:
    """Verify Vapi secret header matches configured secret.

    Used for:
    - Webhook endpoints (/api/vapi/*)
    - Admin scripts and automation

    Raises:
        HTTPException: If secret doesn't match
    """
    settings = get_settings()
    if not x_vapi_secret or x_vapi_secret != settings.vapi_secret_key:
        raise HTTPException(status_code=401, detail="Invalid authentication")


def get_current_user(request: Request) -> Dict[str, Any]:
    """Get current authenticated user from request state (set by AuthMiddleware).

    Raises:
        HTTPException: If user is not authenticated (401)

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
    """Get restaurant_id from authenticated user.

    Raises:
        HTTPException: If user is not authenticated (401) or has no restaurant association (403)
    """
    import logging
    import sys
    logger = logging.getLogger(__name__)
    
    # Force log to stderr to ensure it's captured
    print(f"get_restaurant_id: FUNCTION CALLED", file=sys.stderr, flush=True)
    
    # Debug: Check request.state.user directly - use ERROR level to ensure it's logged
    state_user = getattr(request.state, "user", None)
    print(f"get_restaurant_id: request.state.user exists: {state_user is not None}", file=sys.stderr, flush=True)
    logger.error(f"get_restaurant_id: request.state.user exists: {state_user is not None}")
    if state_user:
        print(f"get_restaurant_id: request.state.user content: {state_user}", file=sys.stderr, flush=True)
        print(f"get_restaurant_id: restaurant_id in state_user: {state_user.get('restaurant_id')}", file=sys.stderr, flush=True)
        logger.error(f"get_restaurant_id: request.state.user content: {state_user}")
        logger.error(f"get_restaurant_id: restaurant_id in state_user: {state_user.get('restaurant_id')}")
        logger.error(f"get_restaurant_id: restaurant_id type: {type(state_user.get('restaurant_id'))}")
        logger.error(f"get_restaurant_id: restaurant_id is None: {state_user.get('restaurant_id') is None}")
        logger.error(f"get_restaurant_id: restaurant_id bool check: {bool(state_user.get('restaurant_id'))}")
    
    try:
        user = get_current_user(request)
        print(f"get_restaurant_id: After get_current_user - user={user.get('user_id')}", file=sys.stderr, flush=True)
        restaurant_id = user.get("restaurant_id")
        print(f"get_restaurant_id: restaurant_id={restaurant_id}, type={type(restaurant_id)}", file=sys.stderr, flush=True)
        logger.error(f"get_restaurant_id: After get_current_user - user={user.get('user_id')}, restaurant_id={restaurant_id}, restaurant_id type={type(restaurant_id)}")
        if not restaurant_id:
            print(f"get_restaurant_id: User {user.get('user_id')} has no restaurant_id. User dict: {user}", file=sys.stderr, flush=True)
            logger.error(f"get_restaurant_id: User {user.get('user_id')} has no restaurant_id. User dict: {user}")
            raise HTTPException(
                status_code=403,
                detail="User is not associated with a restaurant"
            )
        return restaurant_id
    except HTTPException:
        print(f"get_restaurant_id: HTTPException raised", file=sys.stderr, flush=True)
        raise
    except Exception as e:
        print(f"get_restaurant_id: Exception: {e}", file=sys.stderr, flush=True)
        logger.error(f"get_restaurant_id: Exception: {e}", exc_info=True)
        raise


def require_auth(request: Request, x_vapi_secret: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Flexible authentication: accepts either JWT (user) or X-Vapi-Secret (webhook/admin).

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
    """Require authentication AND verify restaurant access.

    For endpoints where users should only access their own restaurant.

    Args:
        request: FastAPI request object
        restaurant_id: Restaurant ID from path parameter
        x_vapi_secret: Optional X-Vapi-Secret header (bypasses restaurant check)

    Raises:
        HTTPException: If not authenticated or access denied
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
