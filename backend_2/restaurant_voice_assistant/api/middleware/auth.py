"""Authentication middleware for Supabase Auth JWT verification.

This middleware processes all incoming requests and:
    - Verifies JWT tokens from Authorization: Bearer header
    - Attaches user information to request.state
    - Skips verification for webhook endpoints (uses X-Vapi-Secret instead)
    - Skips verification for public endpoints (health, docs, auth endpoints)

Middleware Behavior:
    - For /api/vapi/* endpoints: Sets request.state.user = None (webhooks use X-Vapi-Secret)
    - For public endpoints: Sets request.state.user = None (no auth required)
    - For other endpoints: Verifies JWT if present, attaches user info

User Information Attached:
    - user_id: Supabase user UUID
    - email: User email address
    - restaurant_id: Associated restaurant UUID
    - role: User role (default: "user")

Note:
    This middleware does NOT raise exceptions for missing tokens.
    Individual endpoints should use require_auth() or require_restaurant_access()
    from infrastructure.auth.service to enforce authentication.

Usage:
    Middleware is automatically registered in main.py. User info is available
    via request.state.user in endpoint handlers.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from restaurant_voice_assistant.infrastructure.database.client import (
    get_supabase_client,
    get_supabase_service_client
)
import logging

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to verify Supabase JWT tokens.

    For webhook endpoints (/api/vapi/*): Skips JWT (uses X-Vapi-Secret only)
    For public endpoints: Skips JWT verification
    For other endpoints: Verifies JWT if present, attaches user to request.state
    """

    async def dispatch(self, request: Request, call_next):
        """Verify JWT token and attach user info to request state."""
        # Skip JWT verification for webhook endpoints (they use X-Vapi-Secret)
        if request.url.path.startswith("/api/vapi/"):
            request.state.user = None
            return await call_next(request)

        # Skip for public endpoints
        public_paths = ["/api/health", "/docs", "/openapi.json", "/"]
        public_auth_paths = ["/api/auth/register",
                             "/api/auth/login",
                             "/api/auth/logout",
                             "/api/auth/refresh"]  # Refresh endpoint is public

        if request.url.path in public_paths or request.url.path in public_auth_paths:
            request.state.user = None
            return await call_next(request)

        # Extract token from cookie (preferred) or Authorization header (backward compatibility)
        token = None
        auth_header = None

        # Try cookie first (new httpOnly cookie approach)
        token = request.cookies.get("access_token")

        # Fallback to Authorization header for backward compatibility
        if not token:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        # Verify JWT if present
        if token:
            try:
                supabase_client = get_supabase_client()
                user_response = supabase_client.auth.get_user(token)

                if user_response and user_response.user:
                    user_id = user_response.user.id
                    email = user_response.user.email

                    # Get restaurant info from users table
                    service_client = get_supabase_service_client()
                    user_resp = service_client.table("users").select(
                        "id, restaurant_id, role, email"
                    ).eq("id", user_id).limit(1).execute()

                    if user_resp.data:
                        user_data = user_resp.data[0]
                        restaurant_id = user_data["restaurant_id"]
                        logger.info(
                            f"AuthMiddleware: Found user {user_id}, restaurant_id: {restaurant_id}")
                        request.state.user = {
                            "user_id": user_id,
                            "email": email or user_data.get("email"),
                            "restaurant_id": restaurant_id,
                            "role": user_data.get("role", "user")
                        }
                    else:
                        logger.warning(
                            f"AuthMiddleware: User {user_id} not found in users table")
                        request.state.user = None
                else:
                    logger.warning(
                        "AuthMiddleware: Invalid user_response or user")
                    request.state.user = None
            except Exception as e:
                logger.error(
                    f"AuthMiddleware: Exception during user lookup: {e}", exc_info=True)
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)
        return response
