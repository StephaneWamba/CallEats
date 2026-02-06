"""Request timeout middleware for API protection.

This module provides request timeout functionality to prevent resource exhaustion
from long-running or hanging requests.

Key Features:
    - Global request timeout (default: 30 seconds)
    - Configurable per-endpoint timeouts
    - Graceful timeout handling with proper error responses
    - Prevents resource exhaustion from slow queries

Usage:
    Middleware is automatically registered in main.py.
    Apply custom timeouts using @timeout(seconds=60) decorator.
"""
import asyncio
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from restaurant_voice_assistant.core.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Default timeout: 30 seconds
DEFAULT_TIMEOUT = 30.0


class TimeoutMiddleware(BaseHTTPMiddleware):
    """Middleware to enforce request timeouts.

    Prevents long-running requests from consuming resources indefinitely.
    Uses asyncio.wait_for to enforce timeouts on request handling.
    """

    def __init__(self, app, timeout: float = DEFAULT_TIMEOUT):
        """Initialize timeout middleware.

        Args:
            app: FastAPI application
            timeout: Default timeout in seconds (default: 30)
        """
        super().__init__(app)
        self.timeout = timeout

    async def dispatch(self, request: Request, call_next):
        """Process request with timeout enforcement.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with timeout applied
        """
        # Get custom timeout from route if set (via decorator)
        route = request.scope.get("route")
        timeout = self.timeout
        if route and hasattr(route, "endpoint") and hasattr(route.endpoint, "_timeout"):
            timeout = route.endpoint._timeout

        try:
            # Enforce timeout on request handling
            response = await asyncio.wait_for(
                call_next(request),
                timeout=timeout
            )
            return response
        except asyncio.TimeoutError:
            logger.warning(
                f"Request timeout after {timeout}s: {request.method} {request.url.path}",
                extra={"request_id": getattr(
                    request.state, "request_id", None)}
            )
            return JSONResponse(
                status_code=504,
                content={
                    "detail": f"Request timeout after {timeout} seconds",
                    "timeout": timeout
                }
            )


def timeout(seconds: float = DEFAULT_TIMEOUT):
    """Decorator to set custom timeout for an endpoint.

    Usage:
        @router.get("/slow-endpoint")
        @timeout(seconds=60)
        async def slow_endpoint():
            # This endpoint has 60 second timeout
            pass

    Args:
        seconds: Timeout in seconds

    Returns:
        Decorator function
    """
    def decorator(func):
        # Store timeout in function attribute
        func._timeout = seconds
        return func
    return decorator


def get_timeout_middleware(timeout: float = DEFAULT_TIMEOUT) -> TimeoutMiddleware:
    """Get timeout middleware instance.

    Args:
        timeout: Default timeout in seconds

    Returns:
        TimeoutMiddleware instance
    """
    return TimeoutMiddleware(None, timeout=timeout)
