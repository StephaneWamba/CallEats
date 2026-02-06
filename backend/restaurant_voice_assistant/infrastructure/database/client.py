"""Database client management for Supabase.

This module provides singleton Supabase client instances for database operations.
It manages two types of clients:
    - Publishable client: Uses publishable key, respects RLS policies (for reads)
    - Secret client: Uses secret key, bypasses RLS (for writes/admin)

Key Features:
    - Cached client instances for performance
    - Separate clients for different security contexts

Usage:
    from restaurant_voice_assistant.infrastructure.database.client import (
        get_supabase_client,
        get_supabase_service_client
    )
    
    # For reads (respects RLS)
    client = get_supabase_client()
    
    # For writes (bypasses RLS)
    service_client = get_supabase_service_client()
"""
from supabase import create_client, Client
from restaurant_voice_assistant.core.config import get_settings
from functools import lru_cache


@lru_cache()
def get_supabase_client() -> Client:
    """Get Supabase client singleton (uses publishable key - for reads and operations allowed by RLS)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_publishable_key)


@lru_cache()
def get_supabase_service_client() -> Client:
    """Get Supabase client singleton with secret key (bypasses RLS - for writes and admin operations)."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_secret_key)
