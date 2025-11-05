"""Pydantic models for modifiers API.

This module defines request and response models for modifier (add-on/extra) management endpoints.
Modifiers can be linked to menu items via the menu_item_modifiers junction table.

Models:
    - ModifierResponse: Response model with modifier data
    - CreateModifierRequest: Request body for creating a modifier
    - UpdateModifierRequest: Request body for updating a modifier

Price Handling:
    - Price can be $0 for free options (e.g., "No onions")
    - Price represents additional cost when modifier is selected
    - Uses Decimal for precise financial calculations

Usage:
    from restaurant_voice_assistant.shared.models.modifiers import (
        CreateModifierRequest,
        ModifierResponse
    )
    
    request = CreateModifierRequest(name="Extra Cheese", price=2.50)
"""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class ModifierResponse(BaseModel):
    """Response model for modifier data."""
    id: str = Field(..., description="Modifier UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    restaurant_id: str = Field(..., description="Restaurant UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    name: str = Field(..., description="Modifier name", example="Extra Cheese")
    description: Optional[str] = Field(None, description="Modifier description", example="Additional cheese topping")
    price: Decimal = Field(..., description="Additional price", example=2.00)
    created_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")
    updated_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "name": "Extra Cheese",
                "description": "Additional cheese topping",
                "price": 2.00,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class CreateModifierRequest(BaseModel):
    """Request model for creating a modifier."""
    name: str = Field(..., description="Modifier name", example="Extra Cheese")
    description: Optional[str] = Field(None, description="Modifier description", example="Additional cheese topping")
    price: Decimal = Field(..., description="Additional price", ge=0, example=2.00)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Extra Cheese",
                "description": "Additional cheese topping",
                "price": 2.00
            }
        }


class UpdateModifierRequest(BaseModel):
    """Request model for updating a modifier."""
    name: Optional[str] = Field(None, description="Modifier name", example="Extra Cheese")
    description: Optional[str] = Field(None, description="Modifier description", example="Additional cheese topping")
    price: Optional[Decimal] = Field(None, description="Additional price", ge=0, example=2.00)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Extra Cheese",
                "price": 2.50
            }
        }

