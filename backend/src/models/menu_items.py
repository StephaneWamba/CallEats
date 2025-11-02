"""Pydantic models for menu items API."""
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
    category: str = Field(
        "General", description="Item category", example="Pastries")
    available: bool = Field(
        True, description="Whether item is currently available")
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
    category: str = Field(
        "General", description="Item category", example="Pastries")
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
    category: Optional[str] = Field(
        None, description="Item category", example="Pastries")
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
