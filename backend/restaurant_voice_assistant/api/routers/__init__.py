"""API routers package.

This package contains all FastAPI route handlers organized by domain.
Each router module handles a specific domain (restaurants, menu, calls, etc.)
and delegates business logic to domain services.

Router Modules:
    - health: Health check endpoints
    - auth: Authentication endpoints
    - vapi: Vapi webhook endpoints
    - embeddings: Embedding management endpoints
    - restaurants: Restaurant management endpoints
    - calls: Call history endpoints
    - menu_items: Menu item CRUD endpoints
    - categories: Category management endpoints
    - modifiers: Modifier management endpoints
    - operating_hours: Operating hours management endpoints
    - delivery_zones: Delivery zone management endpoints
"""
# Empty __init__.py - routers are imported directly in main.py
