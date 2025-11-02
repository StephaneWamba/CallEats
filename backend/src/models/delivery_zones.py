"""Pydantic models for delivery zones API."""
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class DeliveryZoneResponse(BaseModel):
    """Response model for delivery zone data."""
    id: str = Field(..., description="Delivery zone UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    restaurant_id: str = Field(..., description="Restaurant UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    zone_name: str = Field(..., description="Zone name", example="Downtown")
    description: Optional[str] = Field(None, description="Zone description", example="Downtown area delivery")
    delivery_fee: Decimal = Field(..., description="Delivery fee for this zone", example=5.00)
    min_order: Optional[Decimal] = Field(None, description="Minimum order amount for delivery", example=15.00)
    created_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")
    updated_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "zone_name": "Downtown",
                "description": "Downtown area delivery",
                "delivery_fee": 5.00,
                "min_order": 15.00,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class CreateDeliveryZoneRequest(BaseModel):
    """Request model for creating a delivery zone."""
    zone_name: str = Field(..., description="Zone name", example="Downtown")
    description: Optional[str] = Field(None, description="Zone description", example="Downtown area delivery")
    delivery_fee: Decimal = Field(..., description="Delivery fee for this zone", ge=0, example=5.00)
    min_order: Optional[Decimal] = Field(None, description="Minimum order amount for delivery", ge=0, example=15.00)

    class Config:
        json_schema_extra = {
            "example": {
                "zone_name": "Downtown",
                "description": "Downtown area delivery",
                "delivery_fee": 5.00,
                "min_order": 15.00
            }
        }


class UpdateDeliveryZoneRequest(BaseModel):
    """Request model for updating a delivery zone."""
    zone_name: Optional[str] = Field(None, description="Zone name", example="Downtown")
    description: Optional[str] = Field(None, description="Zone description", example="Downtown area delivery")
    delivery_fee: Optional[Decimal] = Field(None, description="Delivery fee for this zone", ge=0, example=5.00)
    min_order: Optional[Decimal] = Field(None, description="Minimum order amount for delivery", ge=0, example=15.00)

    class Config:
        json_schema_extra = {
            "example": {
                "zone_name": "Downtown",
                "delivery_fee": 6.00,
                "min_order": 20.00
            }
        }

