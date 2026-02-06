"""Pydantic models for authentication API.

This module defines request and response models for user authentication endpoints.
Integrates with Supabase Auth for user registration and login.

Models:
    - RegisterRequest: Request body for user registration
    - LoginRequest: Request body for user login
    - ResetPasswordRequest: Request body for password reset
    - ChangePasswordRequest: Request body for changing password
    - RefreshTokenRequest: Request body for refreshing access token
    - UserResponse: Response model with user information

Authentication Flow:
    - Registration creates user in Supabase Auth and links to restaurant
    - Login returns JWT tokens (access_token, refresh_token)
    - User information includes restaurant_id for multi-tenancy

Usage:
    from restaurant_voice_assistant.shared.models.auth import (
        RegisterRequest,
        LoginRequest,
        ResetPasswordRequest,
        ChangePasswordRequest,
        RefreshTokenRequest,
        UserResponse
    )
    
    register = RegisterRequest(email="user@example.com", password="...", restaurant_id="...")
    login = LoginRequest(email="user@example.com", password="...")
    reset = ResetPasswordRequest(email="user@example.com")
    change = ChangePasswordRequest(current_password="...", new_password="...")
    refresh = RefreshTokenRequest(refresh_token="...")
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Dict, Any


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


class ResetPasswordRequest(BaseModel):
    """Request model for password reset."""
    email: EmailStr = Field(..., description="User email address",
                            example="user@example.com")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Request model for changing password."""
    current_password: str = Field(..., description="Current password", min_length=1,
                                  example="oldPassword123")
    new_password: str = Field(..., description="New password", min_length=6,
                              example="newPassword456")

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldPassword123",
                "new_password": "newPassword456"
            }
        }


class RefreshTokenRequest(BaseModel):
    """Request model for refreshing access token."""
    refresh_token: str = Field(..., description="Refresh token from login",
                               example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
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


class RegisterWithRestaurantRequest(BaseModel):
    """Request model for one-step registration (user + restaurant)."""
    email: EmailStr = Field(..., description="User email address",
                            example="user@example.com")
    password: str = Field(..., description="User password",
                          min_length=6, example="SecurePass123!")
    restaurant_name: str = Field(..., description="Restaurant name",
                                 example="My Restaurant")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!",
                "restaurant_name": "My Restaurant"
            }
        }


class RegisterWithRestaurantResponse(BaseModel):
    """Response model for one-step registration."""
    user: Dict[str, Any] = Field(..., description="User information")
    restaurant: Dict[str, Any] = Field(...,
                                       description="Restaurant information")
    session: Dict[str, Any] = Field(..., description="Session tokens")

    class Config:
        json_schema_extra = {
            "example": {
                "user": {
                    "user_id": "user-uuid",
                    "email": "user@example.com"
                },
                "restaurant": {
                    "id": "restaurant-uuid",
                    "name": "My Restaurant",
                    "phone_number": "+19014994418",
                    "api_key": "api_key_abc123"
                },
                "session": {
                    "access_token": "jwt_token_here",
                    "refresh_token": "refresh_token_here",
                    "expires_in": 3600,
                    "token_type": "Bearer"
                }
            }
        }
