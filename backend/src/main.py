"""
FastAPI application for Restaurant Voice Assistant.

Multi-tenant RAG system with vector similarity search, caching,
and secure webhook endpoints for Vapi.ai integration.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.api import vapi, embeddings, health
from src.api.calls import router as calls_router
from src.api.restaurants import router as restaurants_router
from src.api.menu_items import router as menu_items_router
from src.api.modifiers import router as modifiers_router
from src.api.operating_hours import router as operating_hours_router
from src.api.delivery_zones import router as delivery_zones_router
from src.core.config import get_settings
from src.core.middleware.request_id import RequestIDMiddleware, get_request_id
from src.core.logging_config import configure_logging
import logging

settings = get_settings()

# Configure logging on application startup
configure_logging()

app = FastAPI(
    title="Restaurant Voice Assistant API",
    description="Multi-tenant RAG system for Vapi voice assistants",
    version="1.0.0"
)

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

app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(vapi.router, prefix="/api/vapi", tags=["Vapi"])
app.include_router(embeddings.router,
                   prefix="/api/embeddings", tags=["Embeddings"])
app.include_router(calls_router, prefix="/api", tags=["Calls"])
app.include_router(restaurants_router, prefix="/api", tags=["Restaurants"])
app.include_router(menu_items_router, prefix="/api", tags=["Menu Items"])
app.include_router(modifiers_router, prefix="/api", tags=["Modifiers"])
app.include_router(operating_hours_router, prefix="/api",
                   tags=["Operating Hours"])
app.include_router(delivery_zones_router, prefix="/api",
                   tags=["Delivery Zones"])


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
    return {
        "message": "Restaurant Voice Assistant API",
        "docs": "/docs",
        "health": "/api/health"
    }
