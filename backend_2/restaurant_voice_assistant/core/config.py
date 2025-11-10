"""Application configuration and settings management.

This module provides centralized configuration management using Pydantic Settings.
All environment variables are loaded and validated on application startup.

Key Features:
    - Environment variable loading from .env file
    - Type validation and conversion
    - Cached settings instance for performance
    - Support for development and production environments

Environment Variables:
    SUPABASE_URL: Supabase project URL
    SUPABASE_PUBLISHABLE_KEY: Supabase publishable key (for reads, respects RLS)
    SUPABASE_SECRET_KEY: Supabase secret key (for writes, bypasses RLS)
    OPENAI_API_KEY: OpenAI API key for embeddings
    VAPI_SECRET_KEY: Vapi webhook secret
    ENVIRONMENT: Environment type (development/production)
    CACHE_TTL_SECONDS: Cache TTL in seconds (default: 60)
    EMBEDDING_MODEL: OpenAI embedding model (default: text-embedding-3-small)
    EMBEDDING_DIMENSIONS: Embedding vector dimensions (default: 1536)
    CORS_ORIGINS: CORS allowed origins (default: *)
    FRONTEND_URL: Frontend URL for password reset redirects (optional)
    PUBLIC_BACKEND_URL: Public backend URL, fallback for redirects (optional)

Usage:
    from restaurant_voice_assistant.core.config import get_settings
    
    settings = get_settings()
    print(settings.supabase_url)
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    supabase_url: str
    supabase_publishable_key: str  # Publishable key (for reads, respects RLS)
    supabase_secret_key: str  # Secret key (for writes, bypasses RLS)
    openai_api_key: str
    vapi_secret_key: str
    environment: str = "development"
    cache_ttl_seconds: int = 60
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
    cors_origins: str = "*"
    frontend_url: Optional[str] = None  # Frontend URL for password reset redirects
    public_backend_url: Optional[str] = None  # Public backend URL (fallback for redirects)

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
