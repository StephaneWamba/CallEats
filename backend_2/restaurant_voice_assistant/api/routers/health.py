"""Health check API router.

This module provides health check endpoints for monitoring API and external
service connectivity. It checks connectivity to Supabase, OpenAI, and Vapi APIs.

Endpoints:
    - GET /api/health: Overall health check with service status

Health Check Responses:
    - healthy: Service is operational
    - unhealthy: Service is down or unreachable
    - not_configured: Service credentials not provided

Usage:
    The health endpoint is public (no authentication required) and can be
    used by monitoring systems, load balancers, and deployment pipelines.
"""
from fastapi import APIRouter
from restaurant_voice_assistant.infrastructure.health.service import (
    check_supabase,
    check_openai,
    check_vapi
)

router = APIRouter()


@router.get(
    "/health",
    summary="Health Check",
    description="Check API health and external service connectivity (Supabase, OpenAI, Vapi).",
    responses={
        200: {
            "description": "Health check results",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "services": {
                            "supabase": {"status": "healthy", "latency_ms": 45.2},
                            "openai": {"status": "healthy", "latency_ms": 234.5},
                            "vapi": {"status": "healthy", "latency_ms": 120.3, "assistants": 1}
                        }
                    }
                }
            }
        }
    }
)
async def health_check():
    """Get overall health status and external service connectivity."""
    results = {
        "status": "healthy",
        "services": {}
    }

    supabase_status = await check_supabase()
    results["services"]["supabase"] = supabase_status
    if supabase_status.get("status") != "healthy":
        results["status"] = "unhealthy"

    openai_status = await check_openai()
    results["services"]["openai"] = openai_status
    if openai_status.get("status") != "healthy":
        results["status"] = "unhealthy"

    vapi_status = await check_vapi()
    results["services"]["vapi"] = vapi_status
    # Vapi being not_configured is OK, only unhealthy is a problem
    if vapi_status.get("status") == "unhealthy":
        results["status"] = "unhealthy"

    return results
