"""Pydantic models for authentication API."""
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

