"""Pydantic models for embedding management endpoints.

This module defines request models for embedding generation and cache invalidation.
These endpoints are used to manage the knowledge base embeddings for voice assistant queries.

Models:
    - GenerateEmbeddingsRequest: Request body for generating embeddings
    - CacheInvalidateRequest: Request body for invalidating search cache

Categories:
    Supported categories: "menu", "modifiers", "hours", "zones"
    Omit category to process all categories.

Usage:
    from restaurant_voice_assistant.shared.models.embeddings import (
        GenerateEmbeddingsRequest,
        CacheInvalidateRequest
    )
    
    generate = GenerateEmbeddingsRequest(restaurant_id="...", category="menu")
    invalidate = CacheInvalidateRequest(restaurant_id="...", category="menu")
"""
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

