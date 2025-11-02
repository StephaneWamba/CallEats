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
