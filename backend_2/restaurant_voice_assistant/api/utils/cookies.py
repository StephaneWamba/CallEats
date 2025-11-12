"""Cookie configuration utilities for authentication.

This module provides utilities for setting httpOnly cookies with proper
configuration for both development and production environments.
"""
from dataclasses import dataclass
from fastapi import Request
from fastapi.responses import JSONResponse
from restaurant_voice_assistant.core.config import get_settings


@dataclass
class CookieConfig:
    """Cookie configuration for authentication cookies."""
    secure: bool
    samesite: str


def get_cookie_config(request: Request) -> CookieConfig:
    """Get cookie configuration based on environment.

    In development (HTTP):
    - Secure=False (allows HTTP)
    - SameSite=Lax (works for same-origin requests)

    In production (HTTPS):
    - Secure=True (HTTPS only)
    - SameSite=None (required for cross-origin cookies)

    Args:
        request: FastAPI request object (for potential future use)

    Returns:
        CookieConfig with appropriate settings for environment
    """
    settings = get_settings()
    is_production = settings.environment == "production"

    # Check if request is HTTPS
    is_https = request.url.scheme == "https"

    # In production or when using HTTPS, use secure cookies
    if is_production or is_https:
        return CookieConfig(
            secure=True,
            samesite="none"
        )
    else:
        # Development with HTTP - use lax for same-origin
        return CookieConfig(
            secure=False,
            samesite="lax"
        )


def set_auth_cookies(
    response: JSONResponse,
    access_token: str,
    refresh_token: str,
    access_token_max_age: int,
    cookie_config: CookieConfig
) -> None:
    """Set access_token and refresh_token cookies on response.

    Args:
        response: JSONResponse to set cookies on
        access_token: JWT access token value
        refresh_token: JWT refresh token value
        access_token_max_age: Max age in seconds for access token cookie
        cookie_config: Cookie configuration (secure, samesite)
    """
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=cookie_config.secure,
        samesite=cookie_config.samesite,
        max_age=access_token_max_age,
        path="/"
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=cookie_config.secure,
        samesite=cookie_config.samesite,
        max_age=604800,  # 7 days
        path="/api/auth/refresh"
    )
