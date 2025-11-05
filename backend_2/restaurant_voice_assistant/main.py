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
from restaurant_voice_assistant.core.logging import configure_logging
import logging

settings = get_settings()

# Configure logging on application startup
configure_logging()

app = FastAPI(
    title="Restaurant Voice Assistant API",
    description="Multi-tenant RAG system for Vapi voice assistants",
    version="1.0.0"
)

# Add middleware - order matters!
# Auth middleware must come before RequestID to set user state
app.add_middleware(AuthMiddleware)
app.add_middleware(RequestIDMiddleware)

cors_origins = (
    ["*"] if settings.cors_origins == "*"
    else [origin.strip() for origin in settings.cors_origins.split(",")]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc):
    """Handle unexpected errors without exposing internal details."""
    logger = logging.getLogger(__name__)
    request_id = get_request_id(request)
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={"request_id": request_id}
    )

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
