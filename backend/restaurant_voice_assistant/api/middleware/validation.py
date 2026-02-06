"""Request validation middleware for API security.

This module provides request size limits and path sanitization.
Note: Content-type validation is handled automatically by FastAPI/Pydantic
when using request models, so we don't duplicate that here.

Key Features:
    - Global request size limit (default: 10MB)
    - Per-endpoint size limits
    - Path sanitization (prevents path traversal)

Usage:
    Middleware is automatically registered in main.py.
    Apply custom limits using @request_size_limit(bytes=5242880) decorator.
"""
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.api.middleware.request_id import get_request_id
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Default request size limit from config
DEFAULT_MAX_REQUEST_SIZE = settings.max_request_size_bytes


class ValidationMiddleware(BaseHTTPMiddleware):
    """Middleware to validate incoming requests.

    Provides:
    - Request size limits (early rejection before parsing)
    - Path sanitization (prevents path traversal)

    Note: Content-type validation is handled by FastAPI/Pydantic automatically.
    """

    def __init__(self, app, max_request_size: int = DEFAULT_MAX_REQUEST_SIZE):
        """Initialize validation middleware.

        Args:
            app: FastAPI application
            max_request_size: Maximum request body size in bytes (default: 10MB)
        """
        super().__init__(app)
        self.max_request_size = max_request_size

    async def dispatch(self, request: Request, call_next):
        """Process request with validation.

        Args:
            request: FastAPI request object
            call_next: Next middleware/route handler

        Returns:
            Response with validation applied
        """
        # Get custom size limit from route if set (via decorator)
        route = request.scope.get("route")
        max_size = self.max_request_size
        if route and hasattr(route, "endpoint") and hasattr(route.endpoint, "_max_request_size"):
            max_size = route.endpoint._max_request_size

        # Validate request size (check content-length header)
        # This rejects large requests early, before body parsing
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > max_size:
                    request_id = getattr(
                        request.state, "request_id", None) or get_request_id(request)
                    logger.warning(
                        f"Request too large: {size} bytes (max: {max_size}) for {request.method} {request.url.path}",
                        extra={"request_id": request_id}
                    )
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Request too large. Maximum size: {max_size / (1024 * 1024):.1f}MB",
                            "max_size_bytes": max_size
                        }
                    )
            except ValueError:
                # Invalid content-length header, let it through (will be caught by FastAPI)
                pass

        # Basic path sanitization (prevent path traversal attempts)
        path = str(request.url.path)
        if ".." in path or "//" in path:
            request_id = getattr(request.state, "request_id",
                                 None) or get_request_id(request)
            logger.warning(
                f"Suspicious path detected: {path}",
                extra={"request_id": request_id}
            )
            return JSONResponse(
                status_code=400,
                content={"detail": "Invalid path"}
            )

        # Process request
        response = await call_next(request)
        return response


def request_size_limit(bytes: int = DEFAULT_MAX_REQUEST_SIZE):
    """Decorator to set custom request size limit for an endpoint.

    Usage:
        @router.post("/upload")
        @request_size_limit(bytes=52428800)  # 50MB for file uploads
        async def upload_file():
            pass

    Args:
        bytes: Maximum request size in bytes

    Returns:
        Decorator function
    """
    def decorator(func):
        # Store size limit in function attribute
        func._max_request_size = bytes
        return func
    return decorator


def get_validation_middleware(max_request_size: int = DEFAULT_MAX_REQUEST_SIZE) -> ValidationMiddleware:
    """Get validation middleware instance.

    Args:
        max_request_size: Maximum request body size in bytes

    Returns:
        ValidationMiddleware instance
    """
    return ValidationMiddleware(None, max_request_size=max_request_size)
