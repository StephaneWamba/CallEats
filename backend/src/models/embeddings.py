"""Pydantic models for embedding management endpoints."""
from typing import Optional
from pydantic import BaseModel, Field


class GenerateEmbeddingsRequest(BaseModel):
    """Request model for embedding generation."""
    restaurant_id: str = Field(
        ...,
        description="Restaurant UUID",
        example="04529052-b3dd-43c1-a534-c18d8c0f4c6d"
    )
    category: Optional[str] = Field(
        None,
        description="Category to generate (menu, modifiers, hours, zones). Omit to generate all.",
        example="menu"
    )


class CacheInvalidateRequest(BaseModel):
    """Request model for cache invalidation."""
    restaurant_id: str = Field(
        ...,
        description="Restaurant UUID",
        example="04529052-b3dd-43c1-a534-c18d8c0f4c6d"
    )
    category: Optional[str] = Field(
        None,
        description="Category to invalidate (menu, modifiers, hours, zones). Omit to clear all.",
        example="menu"
    )
