"""Security headers middleware for API protection.

This module provides security headers to protect against common web vulnerabilities
and improve API security posture.

Key Features:
    - X-Content-Type-Options: Prevents MIME type sniffing
    - X-Frame-Options: Prevents clickjacking attacks
    - X-XSS-Protection: Enables XSS filtering (legacy browsers)
    - Strict-Transport-Security: Enforces HTTPS (HSTS)
    - Referrer-Policy: Controls referrer information
    - Content-Security-Policy: Restricts resource loading (API-specific)

Security Headers:
    - X-Content-Type-Options: nosniff
    - X-Frame-Options: DENY (or SAMEORIGIN for API)
    - X-XSS-Protection: 1; mode=block
    - Strict-Transport-Security: max-age=31536000; includeSubDomains (production only)
    - Referrer-Policy: strict-origin-when-cross-origin
    - Content-Security-Policy: default-src 'none' (API-specific, minimal)

Usage:
    Middleware is automatically registered in main.py.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from restaurant_voice_assistant.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses.

    Adds standard security headers to protect against common vulnerabilities.
    Headers are environment-aware (HSTS only in production with HTTPS).
    """

    async def dispatch(self, request: Request, call_next):
        """Add security headers to response.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with security headers added
        """
        response = await call_next(request)

        # X-Content-Type-Options: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # X-Frame-Options: Prevent clickjacking
        # DENY is most secure, but SAMEORIGIN allows same-origin embedding
        # For API, DENY is appropriate
        response.headers["X-Frame-Options"] = "DENY"

        # X-XSS-Protection: Enable XSS filtering (legacy browsers)
        # Modern browsers ignore this, but it doesn't hurt
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Referrer-Policy: Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content-Security-Policy: Restrict resource loading
        # For API endpoints, we use a very restrictive policy
        # This prevents any resource loading (APIs don't need it)
        response.headers["Content-Security-Policy"] = "default-src 'none'"

        # Strict-Transport-Security (HSTS): Enforce HTTPS
        # Only add in production and when using HTTPS
        if settings.environment == "production":
            # Check if request is HTTPS (or behind proxy that sets X-Forwarded-Proto)
            is_https = (
                request.url.scheme == "https" or
                request.headers.get("X-Forwarded-Proto") == "https"
            )

            if is_https:
                # HSTS: max-age=1 year, includeSubDomains
                response.headers["Strict-Transport-Security"] = (
                    "max-age=31536000; includeSubDomains"
                )

        return response


def get_security_headers_middleware() -> SecurityHeadersMiddleware:
    """Get security headers middleware instance.

    Returns:
        SecurityHeadersMiddleware instance
    """
    return SecurityHeadersMiddleware(None)
