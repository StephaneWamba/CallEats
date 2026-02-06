"""Pydantic models for menu item modifier linking API.

This module defines request and response models for managing the many-to-many
relationship between menu items and modifiers. Links control which modifiers
are available for each menu item.

Models:
    - MenuItemModifierLink: Response model with link data including full modifier details
    - LinkModifierRequest: Request body for linking a modifier to a menu item

Link Properties:
    - is_required: Whether the modifier must be selected
    - display_order: Controls UI ordering of modifiers for an item

Usage:
    from restaurant_voice_assistant.shared.models.menu_item_modifiers import (
        LinkModifierRequest,
        MenuItemModifierLink
    )
    
    link = LinkModifierRequest(modifier_id="...", is_required=False, display_order=0)
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from restaurant_voice_assistant.shared.models.modifiers import ModifierResponse


class MenuItemModifierLink(BaseModel):
    """Response model for menu item modifier link."""
    id: str = Field(..., description="Link UUID")
    menu_item_id: str = Field(..., description="Menu item UUID")
    modifier_id: str = Field(..., description="Modifier UUID")
    modifier: ModifierResponse = Field(..., description="Full modifier details")
    is_required: bool = Field(False, description="Whether modifier is required")
    display_order: int = Field(0, description="Display order in UI")
    created_at: str = Field(..., description="ISO 8601 timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "menu_item_id": "item-uuid-here",
                "modifier_id": "modifier-uuid-here",
                "modifier": {
                    "id": "modifier-uuid-here",
                    "name": "Extra Cheese",
                    "description": "Additional cheese topping",
                    "price": 2.00
                },
                "is_required": False,
                "display_order": 1,
                "created_at": "2025-01-01T12:00:00Z"
            }
        }


class LinkModifierRequest(BaseModel):
    """Request model for linking a modifier to a menu item."""
    modifier_id: str = Field(..., description="Modifier UUID to link")
    is_required: bool = Field(False, description="Whether modifier is required")
    display_order: int = Field(0, description="Display order")

    class Config:
        json_schema_extra = {
            "example": {
                "modifier_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "is_required": False,
                "display_order": 1
            }
        }

