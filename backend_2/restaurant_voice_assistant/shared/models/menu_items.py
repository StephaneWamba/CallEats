"""Pydantic models for menu items API.

This module defines request and response models for menu item management endpoints.
All models use Pydantic for validation and serialization with Decimal support
for precise price handling.

Models:
    - MenuItemResponse: Response model with menu item data including modifiers
    - CreateMenuItemRequest: Request body for creating a menu item
    - UpdateMenuItemRequest: Request body for updating a menu item

Usage:
    from restaurant_voice_assistant.shared.models.menu_items import (
        CreateMenuItemRequest,
        MenuItemResponse
    )
    
    request = CreateMenuItemRequest(name="Pizza", price=12.99, category_id="...")
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class MenuItemResponse(BaseModel):
    """Response model for menu item data."""
    id: str = Field(..., description="Menu item UUID",
                    example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    restaurant_id: str = Field(..., description="Restaurant UUID",
                               example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    name: str = Field(..., description="Menu item name", example="Croissant")
    description: Optional[str] = Field(
        None, description="Item description", example="Freshly baked butter croissant")
    price: Decimal = Field(..., description="Item price", example=4.50)
    category_id: Optional[str] = Field(
        None, description="Category UUID (foreign key)", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    category: Optional[str] = Field(
        None, description="Category name (legacy field, kept for backward compatibility)", example="Pastries")
    available: bool = Field(
        True, description="Whether item is currently available")
    image_url: Optional[str] = Field(
        None, description="URL to menu item image", example="https://storage.supabase.co/object/public/menu-images/restaurant-id/item-id/image.jpg")
    created_at: str = Field(..., description="ISO 8601 timestamp",
                            example="2025-01-01T12:00:00Z")
    updated_at: str = Field(..., description="ISO 8601 timestamp",
                            example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "name": "Croissant",
                "description": "Freshly baked butter croissant",
                "price": 4.50,
                "category": "Pastries",
                "available": True,
                "image_url": "https://storage.supabase.co/object/public/menu-images/restaurant-id/item-id/image.jpg",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class CreateMenuItemRequest(BaseModel):
    """Request model for creating a menu item."""
    name: str = Field(..., description="Menu item name", example="Croissant")
    description: Optional[str] = Field(
        None, description="Item description", example="Freshly baked butter croissant")
    price: Decimal = Field(..., description="Item price", ge=0, example=4.50)
    category_id: Optional[str] = Field(
        None, description="Category UUID (foreign key)", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    available: bool = Field(
        True, description="Whether item is currently available")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Croissant",
                "description": "Freshly baked butter croissant",
                "price": 4.50,
                "category": "Pastries",
                "available": True
            }
        }


class UpdateMenuItemRequest(BaseModel):
    """Request model for updating a menu item."""
    name: Optional[str] = Field(
        None, description="Menu item name", example="Croissant")
    description: Optional[str] = Field(
        None, description="Item description", example="Freshly baked butter croissant")
    price: Optional[Decimal] = Field(
        None, description="Item price", ge=0, example=4.50)
    category_id: Optional[str] = Field(
        None, description="Category UUID (foreign key)", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    available: Optional[bool] = Field(
        None, description="Whether item is currently available")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Croissant",
                "price": 5.00,
                "available": False
            }
        }
