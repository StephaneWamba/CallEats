"""Pydantic models for restaurant API requests and responses.

This module defines request and response models for restaurant management endpoints.
All models use Pydantic for validation and serialization.

Models:
    - CreateRestaurantRequest: Request body for creating a restaurant
    - RestaurantResponse: Response model with restaurant data
    - UpdateRestaurantRequest: Request body for updating a restaurant

Usage:
    from restaurant_voice_assistant.shared.models.restaurants import (
        CreateRestaurantRequest,
        RestaurantResponse
    )
    
    request = CreateRestaurantRequest(name="My Restaurant", assign_phone=True)
    response = RestaurantResponse(id="...", name="...", ...)
"""
from pydantic import BaseModel, Field
from typing import Optional


class CreateRestaurantRequest(BaseModel):
    """Request model for creating a restaurant."""
    name: str = Field(..., description="Restaurant name",
                      example="Le Bistro Français")
    api_key: Optional[str] = Field(
        None, description="Custom API key (auto-generated if not provided)", example="api_key_abc123")
    assign_phone: bool = Field(
        True, description="Automatically assign phone number if available")
    force_twilio: bool = Field(
        False, description="Skip existing phones, force Twilio number creation")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Le Bistro Français",
                "assign_phone": True,
                "force_twilio": False
            }
        }


class RestaurantResponse(BaseModel):
    """Response model for restaurant data."""
    id: str = Field(..., description="Restaurant UUID",
                    example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    name: str = Field(..., description="Restaurant name",
                      example="Le Bistro Français")
    api_key: str = Field(..., description="Restaurant API key",
                         example="api_key_abc123")
    phone_number: Optional[str] = Field(
        None, description="Assigned phone number in E.164 format", example="+19014994418")
    created_at: str = Field(..., description="ISO 8601 timestamp",
                            example="2025-01-01T12:00:00Z")
    updated_at: Optional[str] = Field(
        None, description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "name": "Le Bistro Français",
                "api_key": "api_key_abc123",
                "phone_number": "+19014994418",
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class UpdateRestaurantRequest(BaseModel):
    """Request model for updating a restaurant."""
    name: Optional[str] = Field(
        None, description="Restaurant name", example="Le Bistro Français - Updated")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Le Bistro Français - Updated"
            }
        }


class RestaurantStatsResponse(BaseModel):
    """Response model for restaurant dashboard statistics."""
    total_calls_today: int = Field(
        ..., description="Total number of calls today", example=15)
    menu_items_count: int = Field(
        ..., description="Total number of menu items", example=24)
    phone_status: str = Field(
        ..., description="Phone status: 'active' or 'inactive'", example="active")
    categories_count: int = Field(
        ..., description="Total number of categories", example=5)

    class Config:
        json_schema_extra = {
            "example": {
                "total_calls_today": 15,
                "menu_items_count": 24,
                "phone_status": "active",
                "categories_count": 5
            }
        }


class DeleteRestaurantResponse(BaseModel):
    """Response model for restaurant deletion."""
    success: bool = Field(..., description="Whether deletion was successful", example=True)
    message: str = Field(..., description="Deletion message", 
                         example="Restaurant and all associated data deleted successfully")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Restaurant and all associated data deleted successfully"
            }
        }
