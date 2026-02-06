"""Middleware for request ID tracking.

This middleware generates or extracts request IDs for all incoming requests.
Request IDs are used for:
    - Request tracing and debugging
    - Log correlation across services
    - Error tracking and diagnostics

Request ID Source:
    - Uses X-Request-ID header if provided by client
    - Generates new UUID if header not present
    - Always attached to response headers

Usage:
    Middleware is automatically registered in main.py. Request ID is available
    via request.state.request_id or get_request_id(request) helper function.
"""
import uuid
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and track request IDs for debugging."""

    async def dispatch(self, request: Request, call_next):
        """Generate or extract request ID and attach to request state."""
        request_id = request.headers.get(
            REQUEST_ID_HEADER) or str(uuid.uuid4())

        request.state.request_id = request_id

        logger.debug(
            f"{request.method} {request.url.path}",
            extra={"request_id": request_id}
        )

        response = await call_next(request)
        response.headers[REQUEST_ID_HEADER] = request_id
        return response


def get_request_id(request: Request) -> str:
    """Get request ID from request state."""
    return getattr(request.state, "request_id", "unknown")
