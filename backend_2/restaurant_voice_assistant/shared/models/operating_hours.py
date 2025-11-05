"""Pydantic models for operating hours API.

This module defines request and response models for operating hours management endpoints.
Operating hours are stored per day of the week with support for closed days.

Models:
    - OperatingHourResponse: Response model with operating hour data
    - OperatingHourRequest: Request model for a single day's hours
    - UpdateOperatingHoursRequest: Bulk update request (replaces all hours)

Time Format:
    - Times are stored as strings in HH:MM:SS format
    - Day of week can be numeric (0-6) or string (Monday-Sunday)

Bulk Update Pattern:
    The update endpoint uses a bulk pattern: DELETE all + INSERT new.
    This ensures atomic replacement of all hours.

Usage:
    from restaurant_voice_assistant.shared.models.operating_hours import (
        UpdateOperatingHoursRequest,
        OperatingHourRequest
    )
    
    request = UpdateOperatingHoursRequest(hours=[
        OperatingHourRequest(day_of_week="Monday", open_time="09:00", close_time="17:00")
    ])
"""
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
