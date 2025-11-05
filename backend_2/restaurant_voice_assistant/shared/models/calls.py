"""Pydantic models for call history API.

This module defines response models for call history endpoints.
Call records include transcripts, timestamps, and cost information from Vapi calls.

Models:
    - CallResponse: Response model with full call record data

Message Filtering:
    Messages are filtered to include only user and assistant interactions.
    System messages and tool calls are excluded for cleaner display.

Usage:
    from restaurant_voice_assistant.shared.models.calls import CallResponse
    
    call = CallResponse(
        id="...",
        restaurant_id="...",
        started_at=datetime.now(),
        caller="+1234567890",
        messages=[...]
    )
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CallResponse(BaseModel):
    """Response model for a single call record."""
    id: str = Field(..., description="Call record UUID")
    restaurant_id: str = Field(..., description="Restaurant UUID")
    started_at: Optional[datetime] = Field(None, description="Call start time")
    ended_at: Optional[datetime] = Field(None, description="Call end time")
    duration_seconds: Optional[int] = Field(
        None, description="Call duration in seconds")
    caller: Optional[str] = Field(None, description="Caller phone number")
    outcome: Optional[str] = Field(None, description="Call outcome")
    messages: Optional[List[Dict[str, Any]]] = Field(
        None, description="Full call transcript/messages")
    cost: Optional[float] = Field(None, description="Call cost")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "4c3321ef-3c14-46a3-a962-0d0185dfae8b",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "started_at": "2025-01-01T12:00:00Z",
                "ended_at": "2025-01-01T12:05:00Z",
                "duration_seconds": 300,
                "caller": "+1234567890",
                "outcome": "completed",
                "cost": 0.025,
                "messages": [
                    {"role": "user", "content": "What's on your menu?"},
                    {"role": "assistant", "content": "We have croissants..."}
                ]
            }
        }

