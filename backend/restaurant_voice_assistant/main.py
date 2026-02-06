"""FastAPI application for Restaurant Voice Assistant.

This is the main application entry point for the Restaurant Voice Assistant API.
It provides a multi-tenant RAG (Retrieval-Augmented Generation) system with:
    - Vector similarity search using OpenAI embeddings and pgvector
    - Voice assistant integration via Vapi.ai
    - Phone number management and assignment
    - Call history tracking
    - Restaurant and menu management

Architecture:
    - Multi-tenant: All data is scoped by restaurant_id
    - Authentication: Dual auth (JWT for frontend, X-Vapi-Secret for webhooks)
    - Caching: In-memory TTL cache for search results
    - Webhooks: Unified webhook endpoint for Vapi events

Middleware Order:
    1. AuthMiddleware: Verifies JWT tokens, skips for webhooks
    2. RequestIDMiddleware: Generates request IDs for tracing
    3. CORSMiddleware: Handles CORS

Routes:
    - /api/health: Health check endpoint
    - /api/auth/*: Authentication endpoints
    - /api/vapi/*: Vapi webhook endpoints
    - /api/embeddings/*: Embedding management
    - /api/restaurants/*: Restaurant management
    - /api/calls/*: Call history
    - /api/*/menu-items/*: Menu item management
    - /api/*/categories/*: Category management
    - /api/*/modifiers/*: Modifier management
    - /api/*/operating-hours/*: Operating hours management
    - /api/*/delivery-zones/*: Delivery zone management

Environment Variables:
    See restaurant_voice_assistant.core.config for all required environment variables.

Usage:
    Run with: uvicorn restaurant_voice_assistant.main:app --reload
    Or via Docker: docker-compose up
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from restaurant_voice_assistant.api.routers import (
    health,
    auth,
    vapi,
    embeddings,
    restaurants,
    calls,
    menu_items,
    categories,
    modifiers,
    operating_hours,
    delivery_zones
)
from restaurant_voice_assistant.core.config import get_settings
from restaurant_voice_assistant.api.middleware.request_id import (
    RequestIDMiddleware,
    get_request_id
)
from restaurant_voice_assistant.api.middleware.auth import AuthMiddleware
from restaurant_voice_assistant.api.middleware.rate_limit import (
    limiter,
    _rate_limit_exceeded_handler
)
from restaurant_voice_assistant.api.middleware.timeout import (
    TimeoutMiddleware
)
from restaurant_voice_assistant.api.middleware.validation import (
    ValidationMiddleware
)
from restaurant_voice_assistant.api.middleware.security_headers import (
    SecurityHeadersMiddleware
)
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from restaurant_voice_assistant.core.logging import configure_logging
from restaurant_voice_assistant.core.exceptions import (
    NotFoundError,
    AuthenticationError,
    ValidationError,
    VapiAPIError,
    RestaurantVoiceAssistantError
)
import logging

settings = get_settings()

# Configure logging on application startup
configure_logging()

logger = logging.getLogger(__name__)

# Initialize Sentry for error tracking
if settings.sentry_dsn and settings.sentry_enabled:
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        traces_sample_rate=0.1 if settings.environment == "production" else 1.0,
        profiles_sample_rate=0.1 if settings.environment == "production" else 1.0,
        integrations=[
            FastApiIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            ),
        ],
        # Filter out common non-critical errors
        ignore_errors=[
            KeyboardInterrupt,
            SystemExit,
        ],
        # Set user context (will be set dynamically in middleware)
        before_send=lambda event, hint: event,
    )
    logging.info(f"Sentry initialized for environment: {settings.environment}")
else:
    logging.info("Sentry disabled or DSN not provided")

app = FastAPI(
    title="Restaurant Voice Assistant API",
    description="Multi-tenant RAG system for Vapi voice assistants",
    version="1.0.0"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Register rate limit exception handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add middleware - order matters!
# RequestID middleware first for request tracking
app.add_middleware(RequestIDMiddleware)
# Validation middleware early to reject invalid requests
app.add_middleware(ValidationMiddleware,
                   max_request_size=settings.max_request_size_bytes)
# Timeout middleware early to protect resources
app.add_middleware(TimeoutMiddleware, timeout=settings.request_timeout_seconds)
# Auth middleware sets user state for rate limiting
app.add_middleware(AuthMiddleware)
# Rate limiting after auth to support user-based limits
app.add_middleware(SlowAPIMiddleware)

# CORS configuration
# Single source of truth: CORS_ORIGINS environment variable
# Format: comma-separated list of origins, or "*" for all origins
# Note: When allow_credentials=True, cannot use "*" for origins
# Must specify exact origins or use allow_origin_regex for patterns

if settings.cors_origins == "*":
    # Development mode: allow all origins
    # Note: With "*" and allow_credentials=True, browsers will reject cookies
    # For local development with credentials, use specific origin like "http://localhost:5173"
    final_origins = ["*"]
else:
    # Parse comma-separated origins from environment variable
    final_origins = [
        origin.strip()
        for origin in settings.cors_origins.split(",")
        if origin.strip()  # Filter out empty strings
    ]

    # Validate: must have at least one origin
    if not final_origins:
        logger.warning(
            "CORS_ORIGINS is empty or invalid. Defaulting to localhost origins for development."
        )
        final_origins = [
            "http://localhost:5173",
            "http://localhost:3000",
            "http://127.0.0.1:5173"
        ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=final_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],  # Expose Set-Cookie header for cross-origin requests
)
# Security headers middleware (after CORS to add headers to all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Register routers
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(vapi.router, prefix="/api/vapi", tags=["Vapi"])
app.include_router(embeddings.router,
                   prefix="/api/embeddings", tags=["Embeddings"])
app.include_router(calls.router, prefix="/api", tags=["Calls"])
app.include_router(restaurants.router, prefix="/api", tags=["Restaurants"])
app.include_router(menu_items.router, prefix="/api", tags=["Menu Items"])
app.include_router(modifiers.router, prefix="/api", tags=["Modifiers"])
app.include_router(operating_hours.router, prefix="/api",
                   tags=["Operating Hours"])
app.include_router(delivery_zones.router, prefix="/api",
                   tags=["Delivery Zones"])
app.include_router(categories.router, prefix="/api", tags=["Categories"])


# Custom exception handlers (must be registered before global handler)
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    """Handle NotFoundError exceptions with 404 status."""
    request_id = get_request_id(request)
    logger.warning(
        f"Resource not found: {exc}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc) or "Resource not found",
            "request_id": request_id
        }
    )


@app.exception_handler(AuthenticationError)
async def authentication_error_handler(request: Request, exc: AuthenticationError):
    """Handle AuthenticationError exceptions with 401 status."""
    request_id = get_request_id(request)
    logger.warning(
        f"Authentication failed: {exc}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    return JSONResponse(
        status_code=401,
        content={
            "detail": str(exc) or "Authentication required",
            "request_id": request_id
        }
    )


@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handle ValidationError exceptions with 400 status."""
    request_id = get_request_id(request)
    logger.warning(
        f"Validation error: {exc}",
        extra={"request_id": request_id, "path": request.url.path}
    )
    return JSONResponse(
        status_code=400,
        content={
            "detail": str(exc) or "Validation error",
            "request_id": request_id
        }
    )


@app.exception_handler(VapiAPIError)
async def vapi_api_error_handler(request: Request, exc: VapiAPIError):
    """Handle VapiAPIError exceptions with 502 status (bad gateway)."""
    request_id = get_request_id(request)
    logger.error(
        f"Vapi API error: {exc}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True
    )
    
    # Capture in Sentry if enabled
    if settings.sentry_dsn and settings.sentry_enabled:
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("request_id", request_id)
            scope.set_tag("error_type", "vapi_api_error")
            sentry_sdk.capture_exception(exc)
    
    return JSONResponse(
        status_code=502,
        content={
            "detail": str(exc) or "External API error",
            "request_id": request_id
        }
    )


@app.exception_handler(RestaurantVoiceAssistantError)
async def restaurant_error_handler(request: Request, exc: RestaurantVoiceAssistantError):
    """Handle base RestaurantVoiceAssistantError exceptions with 500 status."""
    request_id = get_request_id(request)
    logger.error(
        f"Application error: {exc}",
        extra={"request_id": request_id, "path": request.url.path},
        exc_info=True
    )
    
    # Capture in Sentry if enabled
    if settings.sentry_dsn and settings.sentry_enabled:
        import sentry_sdk
        user = getattr(request.state, "user", None)
        if user:
            sentry_sdk.set_user({
                "id": user.get("user_id"),
                "email": user.get("email"),
            })
        
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("request_id", request_id)
            scope.set_tag("error_type", "application_error")
            sentry_sdk.capture_exception(exc)
    
    error_detail = {
        "detail": str(exc) or "An application error occurred",
        "request_id": request_id
    }
    if settings.environment != "production":
        error_detail["error"] = str(exc)
    
    return JSONResponse(
        status_code=500,
        content=error_detail
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    """Handle unexpected errors without exposing internal details."""
    logger = logging.getLogger(__name__)
    request_id = get_request_id(request)

    # Log error
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )

    # Capture in Sentry if enabled
    if settings.sentry_dsn and settings.sentry_enabled:
        import sentry_sdk
        # Get user context if available
        user = getattr(request.state, "user", None)
        if user:
            sentry_sdk.set_user({
                "id": user.get("user_id"),
                "email": user.get("email"),
            })

        # Set request context
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("request_id", request_id)
            scope.set_tag("path", request.url.path)
            scope.set_tag("method", request.method)
            scope.set_context("request", {
                "url": str(request.url),
                "method": request.method,
                "headers": dict(request.headers),
            })
            sentry_sdk.capture_exception(exc)

    error_detail = {"detail": "An internal error occurred",
                    "request_id": request_id}
    if settings.environment != "production":
        error_detail["error"] = str(exc)

    return JSONResponse(
        status_code=500,
        content=error_detail
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Restaurant Voice Assistant API",
        "docs": "/docs",
        "health": "/api/health"
    }
