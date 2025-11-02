"""
Pydantic models for Vapi webhook payloads.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CallMessage(BaseModel):
    """Individual message in call transcript."""
    role: Optional[str] = Field(
        None, description="Message role (user/assistant/system)")
    content: Optional[str] = Field(None, description="Message content/text")
    timestamp: Optional[str] = Field(
        None, description="Message timestamp (ISO 8601)")


class EndOfCallReportRequest(BaseModel):
    """
    Vapi end-of-call-report webhook payload.

    Field names verified from actual Vapi webhook payloads.
    Reference: https://docs.vapi.ai
    """
    call_id: Optional[str] = Field(
        None, description="Vapi call ID", alias="id")
    phone_number_id: Optional[str] = Field(None, description="Phone number ID")
    phone_number: Optional[str] = Field(
        None, description="Phone number (E.164 format)")
    assistant_id: Optional[str] = Field(None, description="Assistant ID")
    started_at: Optional[str] = Field(
        None, description="Call start time (ISO 8601)")
    ended_at: Optional[str] = Field(
        None, description="Call end time (ISO 8601)")
    duration: Optional[int] = Field(
        None, description="Call duration in seconds")
    caller_number: Optional[str] = Field(
        None, description="Caller phone number", alias="from")
    status: Optional[str] = Field(
        None, description="Call status (ended/completed/failed)")
    messages: Optional[List[Dict[str, Any]]] = Field(
        None, description="Call transcript/messages")
    transcript: Optional[List[Dict[str, Any]]] = Field(
        None, description="Alternative transcript field")
    cost: Optional[float] = Field(
        None, description="Total call cost (if available)")

    class Config:
        populate_by_name = True
        extra = "allow"  # Accept unknown fields until structure is verified
        json_schema_extra = {
            "example": {
                "id": "call_abc123",
                "phone_number": "+19014994418",
                "started_at": "2025-01-01T12:00:00Z",
                "ended_at": "2025-01-01T12:05:00Z",
                "duration": 300,
                "from": "+1234567890",
                "status": "ended",
                "messages": [
                    {"role": "user", "content": "What's on your menu?",
                        "timestamp": "2025-01-01T12:00:30Z"},
                    {"role": "assistant", "content": "We have...",
                        "timestamp": "2025-01-01T12:00:35Z"}
                ],
                "cost": 0.025
            }
        }
