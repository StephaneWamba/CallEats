"""Pydantic models for operating hours API."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import time


class OperatingHourResponse(BaseModel):
    """Response model for operating hour data."""
    id: str = Field(..., description="Operating hour UUID",
                    example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    restaurant_id: str = Field(..., description="Restaurant UUID",
                               example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    day_of_week: str = Field(
        ..., description="Day of week (Monday, Tuesday, etc.)", example="Monday")
    open_time: str = Field(...,
                           description="Opening time in HH:MM:SS format", example="09:00:00")
    close_time: str = Field(...,
                            description="Closing time in HH:MM:SS format", example="17:00:00")
    is_closed: bool = Field(
        False, description="Whether the restaurant is closed on this day")
    created_at: str = Field(..., description="ISO 8601 timestamp",
                            example="2025-01-01T12:00:00Z")
    updated_at: str = Field(..., description="ISO 8601 timestamp",
                            example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "day_of_week": "Monday",
                "open_time": "09:00:00",
                "close_time": "17:00:00",
                "is_closed": False,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class OperatingHourRequest(BaseModel):
    """Request model for a single operating hour."""
    day_of_week: str = Field(..., description="Day of week", example="Monday")
    open_time: str = Field(...,
                           description="Opening time in HH:MM:SS format", example="09:00:00")
    close_time: str = Field(...,
                            description="Closing time in HH:MM:SS format", example="17:00:00")
    is_closed: bool = Field(
        False, description="Whether the restaurant is closed on this day")

    class Config:
        json_schema_extra = {
            "example": {
                "day_of_week": "Monday",
                "open_time": "09:00:00",
                "close_time": "17:00:00",
                "is_closed": False
            }
        }


class UpdateOperatingHoursRequest(BaseModel):
    """Request model for updating operating hours (bulk update)."""
    hours: List[OperatingHourRequest] = Field(
        ..., description="List of operating hours for each day")

    class Config:
        json_schema_extra = {
            "example": {
                "hours": [
                    {"day_of_week": "Monday", "open_time": "09:00:00",
                        "close_time": "17:00:00", "is_closed": False},
                    {"day_of_week": "Tuesday", "open_time": "09:00:00",
                        "close_time": "17:00:00", "is_closed": False}
                ]
            }
        }
