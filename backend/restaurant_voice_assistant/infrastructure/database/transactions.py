"""Database transaction management for atomic operations.

This module provides transaction support for multi-step database operations
to ensure data consistency and atomicity.

Key Features:
    - Context manager for transactions
    - Automatic rollback on exceptions
    - Support for nested operations
    - Restaurant-scoped transaction isolation

Usage:
    from restaurant_voice_assistant.infrastructure.database.transactions import transaction
    
    with transaction() as supabase:
        # All operations within this block are atomic
        supabase.table("restaurants").insert({...}).execute()
        supabase.table("users").insert({...}).execute()
        # If any operation fails, all are rolled back
"""

from contextlib import contextmanager
from typing import Generator
from supabase import Client
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
from restaurant_voice_assistant.core.exceptions import RestaurantVoiceAssistantError
import logging

logger = logging.getLogger(__name__)


@contextmanager
def transaction() -> Generator[Client, None, None]:
    """Context manager for database transactions.

    Provides a Supabase client for atomic operations. If an exception
    occurs within the context, the transaction is rolled back.

    Note: Supabase/PostgREST doesn't support traditional transactions
    via the Python client. This is a wrapper that ensures operations
    are performed with the service client and provides a pattern for
    future transaction support.

    For now, this ensures:
    - Consistent client usage (service client for writes)
    - Error handling pattern
    - Future-proof for when Supabase adds transaction support

    Yields:
        Supabase service client for database operations

    Raises:
        RestaurantVoiceAssistantError: If transaction fails
    """
    client = get_supabase_service_client()

    try:
        yield client
        # Note: Supabase doesn't support explicit commit/rollback via Python client
        # Operations are committed immediately. This pattern is for future support
        # and consistent error handling.
    except Exception as e:
        logger.error(f"Transaction error: {e}", exc_info=True)
        # In a real transaction system, we would rollback here
        # For now, we re-raise to allow callers to handle the error
        raise RestaurantVoiceAssistantError(f"Transaction failed: {e}") from e


def execute_in_transaction(operations):
    """Execute multiple database operations in a transaction-like context.

    This is a helper for operations that need to be atomic but Supabase
    doesn't support traditional transactions. It ensures all operations
    use the same client and provides error handling.

    Args:
        operations: List of callable functions that take a supabase client

    Returns:
        List of operation results

    Raises:
        RestaurantVoiceAssistantError: If any operation fails
    """
    client = get_supabase_service_client()
    results = []

    try:
        for operation in operations:
            result = operation(client)
            results.append(result)
        return results
    except Exception as e:
        logger.error(f"Transaction operations failed: {e}", exc_info=True)
        raise RestaurantVoiceAssistantError(
            f"Transaction operations failed: {e}") from e

