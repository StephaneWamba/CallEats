"""Pydantic models for authentication API.

This module defines request and response models for user authentication endpoints.
Integrates with Supabase Auth for user registration and login.

Models:
    - RegisterRequest: Request body for user registration
    - LoginRequest: Request body for user login
    - UserResponse: Response model with user information

Authentication Flow:
    - Registration creates user in Supabase Auth and links to restaurant
    - Login returns JWT tokens (access_token, refresh_token)
    - User information includes restaurant_id for multi-tenancy

Usage:
    from restaurant_voice_assistant.shared.models.auth import (
        RegisterRequest,
        LoginRequest,
        UserResponse
    )
    
    register = RegisterRequest(email="user@example.com", password="...", restaurant_id="...")
    login = LoginRequest(email="user@example.com", password="...")
"""
from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr = Field(..., description="User email address",
                            example="user@example.com")
    password: str = Field(..., description="User password",
                          min_length=6, example="SecurePass123!")
    restaurant_id: str = Field(..., description="Restaurant UUID to associate user with",
                               example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d"
            }
        }


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr = Field(..., description="User email address",
                            example="user@example.com")
    password: str = Field(..., description="User password",
                          example="SecurePass123!")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserResponse(BaseModel):
    """Response model for user information."""
    user_id: str = Field(..., description="User UUID",
                         example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    email: str = Field(..., description="User email address",
                       example="user@example.com")
    restaurant_id: str = Field(..., description="Restaurant UUID",
                               example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    role: str = Field(..., description="User role", example="user")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "email": "user@example.com",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "role": "user"
            }
        }
