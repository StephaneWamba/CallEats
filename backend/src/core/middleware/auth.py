"""
Authentication middleware for Supabase Auth JWT verification.

Verifies JWT tokens from Authorization: Bearer header and attaches user info to request.state.
Skips JWT verification for webhook endpoints (/api/vapi/*) and public endpoints.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from src.services.infrastructure.database import get_supabase_client, get_supabase_service_client


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to verify Supabase JWT tokens.

    For webhook endpoints (/api/vapi/*): Skips JWT (uses X-Vapi-Secret only)
    For public endpoints: Skips JWT verification
    For other endpoints: Verifies JWT if present, attaches user to request.state
    """

    async def dispatch(self, request: Request, call_next):
        # Skip JWT verification for webhook endpoints (they use X-Vapi-Secret)
        if request.url.path.startswith("/api/vapi/"):
            request.state.user = None
            return await call_next(request)

        # Skip for public endpoints
        public_paths = ["/api/health", "/docs", "/openapi.json", "/"]
        public_auth_paths = ["/api/auth/register",
                             "/api/auth/login", "/api/auth/logout"]

        if request.url.path in public_paths or request.url.path in public_auth_paths:
            request.state.user = None
            return await call_next(request)

        # Extract token from Authorization header
        auth_header = request.headers.get("Authorization")
        token = None
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
                        request.state.user = {
                            "user_id": user_id,
                            "email": email or user_data.get("email"),
                            "restaurant_id": user_data["restaurant_id"],
                            "role": user_data.get("role", "user")
                        }
                    else:
                        request.state.user = None
                else:
                    request.state.user = None
            except Exception:
                request.state.user = None
        else:
            request.state.user = None

        response = await call_next(request)
        return response
