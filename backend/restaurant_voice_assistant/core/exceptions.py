"""Custom exceptions for the application.

This module defines a hierarchy of custom exceptions used throughout
the application for better error handling and debugging.

Exception Hierarchy:
    RestaurantVoiceAssistantError (base exception)
    ├── AuthenticationError
    ├── NotFoundError
    ├── ValidationError
    └── VapiAPIError

Usage:
    from restaurant_voice_assistant.core.exceptions import NotFoundError
    
    if not restaurant:
        raise NotFoundError("Restaurant not found")
"""


class RestaurantVoiceAssistantError(Exception):
    """Base exception for all application errors."""
    pass


class AuthenticationError(RestaurantVoiceAssistantError):
    """Raised when authentication fails."""
    pass


class NotFoundError(RestaurantVoiceAssistantError):
    """Raised when a resource is not found."""
    pass


class ValidationError(RestaurantVoiceAssistantError):
    """Raised when validation fails."""
    pass


class VapiAPIError(RestaurantVoiceAssistantError):
    """Raised when Vapi API operations fail."""
    pass
