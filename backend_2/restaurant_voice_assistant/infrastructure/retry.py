"""Retry logic for external API calls using tenacity.

This module provides retry decorators using the tenacity library for handling
transient failures in external API calls (OpenAI, Vapi, Supabase, etc.).

Key Features:
    - Exponential backoff (via tenacity)
    - Configurable retry attempts
    - Exception filtering
    - Async and sync support
    - Automatic retry on network errors

Usage:
    from restaurant_voice_assistant.infrastructure.retry import retry_with_backoff
    
    @retry_with_backoff
    async def call_external_api():
        # API call that may fail transiently
        pass
    
    # Or with custom configuration
    from tenacity import stop_after_attempt, wait_exponential
    
    @retry_with_backoff(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def call_external_api():
        pass
"""
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
    RetryError
)
from typing import Type, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Default retry configuration
DEFAULT_MAX_ATTEMPTS = 3
DEFAULT_MIN_WAIT = 1.0  # seconds
DEFAULT_MAX_WAIT = 60.0  # seconds
DEFAULT_MULTIPLIER = 2.0


def is_retryable_exception(exception: Exception) -> bool:
    """Determine if an exception should trigger a retry.

    Args:
        exception: The exception to check

    Returns:
        True if the exception is retryable, False otherwise
    """
    # Network-related exceptions (connection errors, timeouts)
    retryable_types = (
        ConnectionError,
        TimeoutError,
        OSError,  # Includes network errors
    )

    # Check exception type
    if isinstance(exception, retryable_types):
        return True

    # Check exception message for common retryable errors
    error_message = str(exception).lower()
    retryable_keywords = [
        "timeout",
        "connection",
        "network",
        "temporary",
        "rate limit",  # Rate limits are often temporary
        "503",  # Service unavailable
        "502",  # Bad gateway
        "504",  # Gateway timeout
    ]

    return any(keyword in error_message for keyword in retryable_keywords)


def _log_retry_attempt(retry_state):
    """Log retry attempt."""
    if retry_state.outcome and retry_state.outcome.exception():
        logger.warning(
            f"Retry attempt {retry_state.attempt_number} for {retry_state.fn.__name__}: "
            f"{retry_state.outcome.exception()}"
        )


def _log_retry_exhausted(retry_state):
    """Log when all retries are exhausted."""
    if retry_state.outcome and retry_state.outcome.failed:
        logger.error(
            f"All {DEFAULT_MAX_ATTEMPTS} retry attempts exhausted for {retry_state.fn.__name__}"
        )


# Default retry decorator with exponential backoff
retry_with_backoff = retry(
    stop=stop_after_attempt(DEFAULT_MAX_ATTEMPTS),
    wait=wait_exponential(multiplier=DEFAULT_MULTIPLIER,
                          min=DEFAULT_MIN_WAIT, max=DEFAULT_MAX_WAIT),
    retry=retry_if_exception(is_retryable_exception),
    reraise=True,  # Re-raise the last exception after all retries exhausted
    before_sleep=_log_retry_attempt,
    after=_log_retry_exhausted
)
