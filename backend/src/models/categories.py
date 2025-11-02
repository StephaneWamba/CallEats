"""Pydantic models for categories API."""
from pydantic import BaseModel, Field
from typing import Optional


class CategoryResponse(BaseModel):
    """Response model for category data."""
    id: str = Field(..., description="Category UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    restaurant_id: str = Field(..., description="Restaurant UUID", example="04529052-b3dd-43c1-a534-c18d8c0f4c6d")
    name: str = Field(..., description="Category name", example="Main Course")
    description: Optional[str] = Field(None, description="Category description", example="Main dishes and entrees")
    display_order: int = Field(0, description="Display order for sorting", example=1)
    created_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")
    updated_at: str = Field(..., description="ISO 8601 timestamp", example="2025-01-01T12:00:00Z")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "restaurant_id": "04529052-b3dd-43c1-a534-c18d8c0f4c6d",
                "name": "Main Course",
                "description": "Main dishes and entrees",
                "display_order": 1,
                "created_at": "2025-01-01T12:00:00Z",
                "updated_at": "2025-01-01T12:00:00Z"
            }
        }


class CreateCategoryRequest(BaseModel):
    """Request model for creating a category."""
    name: str = Field(..., description="Category name", example="Main Course")
    description: Optional[str] = Field(None, description="Category description", example="Main dishes and entrees")
    display_order: int = Field(0, description="Display order for sorting", ge=0, example=1)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Main Course",
                "description": "Main dishes and entrees",
                "display_order": 1
            }
        }


class UpdateCategoryRequest(BaseModel):
    """Request model for updating a category."""
    name: Optional[str] = Field(None, description="Category name", example="Main Course")
    description: Optional[str] = Field(None, description="Category description", example="Main dishes and entrees")
    display_order: Optional[int] = Field(None, description="Display order for sorting", ge=0, example=1)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Main Dishes",
                "display_order": 2
            }
        }


