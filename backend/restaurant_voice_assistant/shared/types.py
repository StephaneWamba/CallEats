"""Pydantic models for Vapi API requests and responses.

This module defines flexible models for handling Vapi webhook requests.
Vapi sends various request formats, so these models support multiple extraction methods.

Models:
    - VapiRequest: Main request model with flexible query extraction
    - VapiMessage: Message wrapper with function calls and tool calls
    - ToolCall: Tool call information
    - FunctionCall: Function call parameters

Query Extraction:
    The VapiRequest model provides multiple methods to extract the user query
    from different Vapi request formats (legacy and new formats).

Usage:
    from restaurant_voice_assistant.shared.types import VapiRequest
    
    request = VapiRequest.parse_raw(json_body)
    query = request.extract_query()
    tool_call_id = request.extract_tool_call_id()
"""
from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel


class FunctionCallParams(BaseModel):
    query: Optional[str] = None


class FunctionCall(BaseModel):
    parameters: Optional[FunctionCallParams] = None


class FunctionArgs(BaseModel):
    query: Optional[str] = None

    class Config:
        extra = "allow"  # Allow additional fields


class ToolCallFunction(BaseModel):
    name: Optional[str] = None
    # Can be FunctionArgs, dict, or JSON string
    arguments: Optional[Any] = None


class ToolCall(BaseModel):
    id: Optional[str] = None
    type: Optional[str] = None
    function: Optional[ToolCallFunction] = None


class VapiMessage(BaseModel):
    functionCall: Optional[FunctionCall] = None
    toolCalls: Optional[List[ToolCall]] = None
    timestamp: Optional[int] = None
    type: Optional[str] = None


class VapiRequest(BaseModel):
    """Flexible model to handle various Vapi request formats"""
    query: Optional[str] = None
    message: Optional[VapiMessage] = None
    messages: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None

    def extract_query(self) -> Optional[str]:
        """Extract user query from various Vapi request formats."""
        if self.query:
            return self.query
        if self.message and self.message.functionCall and self.message.functionCall.parameters:
            return self.message.functionCall.parameters.query
        if self.message and self.message.toolCalls:
            for tool_call in self.message.toolCalls:
                if tool_call.function and tool_call.function.arguments:
                    if isinstance(tool_call.function.arguments, dict):
                        return tool_call.function.arguments.get("query")
                    elif hasattr(tool_call.function.arguments, "query"):
                        return tool_call.function.arguments.query
                    elif isinstance(tool_call.function.arguments, str):
                        try:
                            import json
                            parsed = json.loads(tool_call.function.arguments)
                            if isinstance(parsed, dict):
                                return parsed.get("query")
                        except:
                            pass
        if self.messages:
            for msg in reversed(self.messages):
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
        return None

    def extract_tool_call_id(self) -> Optional[str]:
        """Extract tool call ID from request."""
        if self.message and self.message.toolCalls:
            for tool_call in self.message.toolCalls:
                if tool_call.id:
                    return tool_call.id
        return None

    def extract_tool_name(self) -> Optional[str]:
        """Extract tool name from request."""
        if self.message and self.message.toolCalls:
            for tool_call in self.message.toolCalls:
                if tool_call.function and tool_call.function.name:
                    return tool_call.function.name
        return None

    def extract_restaurant_id(self) -> Optional[str]:
        """Extract restaurant_id from metadata field."""
        if self.metadata and isinstance(self.metadata, dict):
            return self.metadata.get("restaurant_id")
        return None
