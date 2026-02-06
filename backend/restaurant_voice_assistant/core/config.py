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
    # Access settings: settings.supabase_url, settings.openai_api_key, etc.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import ConfigDict, Field, field_validator, model_validator
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    supabase_url: str = Field(..., description="Supabase project URL")
    supabase_publishable_key: str = Field(
        ..., description="Supabase publishable key (for reads, respects RLS)")
    supabase_secret_key: str = Field(
        ..., description="Supabase secret key (for writes, bypasses RLS)")
    openai_api_key: str = Field(...,
                                description="OpenAI API key for embeddings")
    vapi_secret_key: str = Field(..., description="Vapi webhook secret")
    environment: str = Field(
        default="development", description="Environment type (development/production)")
    cache_ttl_seconds: int = Field(
        default=60, ge=1, description="Cache TTL in seconds")
    embedding_model: str = Field(
        default="text-embedding-3-small", description="OpenAI embedding model")
    embedding_dimensions: int = Field(
        default=1536, ge=1, description="Embedding vector dimensions")
    cors_origins: str = Field(
        default="*", description="CORS allowed origins (comma-separated)")
    frontend_url: Optional[str] = Field(
        default=None, description="Frontend URL for password reset redirects")
    public_backend_url: Optional[str] = Field(
        default=None, description="Public backend URL (fallback for redirects)")
    sentry_dsn: Optional[str] = Field(
        default=None, description="Sentry DSN for error tracking")
    sentry_enabled: bool = Field(
        default=True, description="Enable Sentry by default if DSN is provided")
    redis_url: Optional[str] = Field(
        default=None, description="Redis connection URL (e.g., redis://localhost:6379/0). Railway provides REDIS_URL automatically. If not provided, falls back to in-memory cache.")
    request_timeout_seconds: float = Field(
        default=30.0, ge=1.0, le=300.0, description="Global request timeout in seconds (default: 30, max: 300)")
    max_request_size_bytes: int = Field(
        default=10 * 1024 * 1024, ge=1024, le=100 * 1024 * 1024, description="Maximum request body size in bytes (default: 10MB, max: 100MB)")

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        env_prefix="",
        extra="ignore"
    )

    @field_validator("supabase_url", "supabase_publishable_key", "supabase_secret_key", "openai_api_key", "vapi_secret_key")
    @classmethod
    def validate_required_strings(cls, v: str) -> str:
        """Validate that required string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Required field cannot be empty")
        return v.strip()

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ["development", "production", "staging"]
        if v not in valid_environments:
            raise ValueError(
                f"environment must be one of: {', '.join(valid_environments)}")
        return v

    @model_validator(mode="after")
    def validate_production_requirements(self):
        """Validate required settings for production environment."""
        if self.environment == "production":
            errors = []
            warnings = []

            # Required in production
            if not self.public_backend_url:
                errors.append("PUBLIC_BACKEND_URL is required in production")

            # Recommended in production
            if not self.sentry_dsn:
                warnings.append(
                    "SENTRY_DSN is not set - error tracking will be disabled in production")

            if not self.frontend_url:
                warnings.append(
                    "FRONTEND_URL is not set - password reset redirects may not work")

            if errors:
                raise ValueError(
                    f"Environment validation failed for production:\n" +
                    "\n".join(f"  - {error}" for error in errors) +
                    "\n\nPlease check your .env file and ensure all required variables are set."
                )

            if warnings:
                import logging
                logger = logging.getLogger(__name__)
                for warning in warnings:
                    logger.warning(
                        f"Production configuration warning: {warning}")

        return self


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
