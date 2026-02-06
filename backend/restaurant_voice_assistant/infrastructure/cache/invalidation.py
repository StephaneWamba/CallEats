"""Automatic cache invalidation decorator.

This module provides decorators to automatically invalidate cache when data changes,
eliminating the need for manual clear_cache() calls.

Key Features:
    - Automatic cache invalidation after successful operations
    - Works with both sync and async functions
    - Supports restaurant_id and category parameters
    - Extracts restaurant_id from function arguments or return values
    - Handles errors gracefully (doesn't break if cache invalidation fails)

Usage:
    from restaurant_voice_assistant.infrastructure.cache.invalidation import invalidate_cache
    
    @invalidate_cache(category="menu")
    async def create_menu_item(restaurant_id: str, ...):
        # Cache automatically cleared after successful creation
        pass
    
    # Or with dynamic category extraction
    @invalidate_cache(category=lambda result: result.get("category"))
    async def create_item(restaurant_id: str, ...):
        pass
"""
import functools
import inspect
from typing import Optional, Callable, Any, Union
from restaurant_voice_assistant.infrastructure.cache.manager import clear_cache
import logging

logger = logging.getLogger(__name__)


def _extract_restaurant_id(args: tuple, kwargs: dict, func: Callable) -> Optional[str]:
    """Extract restaurant_id from function arguments.

    Tries to find restaurant_id in:
    1. Keyword arguments (kwargs)
    2. Positional arguments (by parameter name)
    3. Return value (if function already executed)

    Args:
        args: Function positional arguments
        kwargs: Function keyword arguments
        func: Function object

    Returns:
        restaurant_id if found, None otherwise
    """
    # Check kwargs first
    if "restaurant_id" in kwargs:
        return kwargs["restaurant_id"]

    # Check positional arguments by parameter name
    sig = inspect.signature(func)
    param_names = list(sig.parameters.keys())

    for i, arg_value in enumerate(args):
        if i < len(param_names) and param_names[i] == "restaurant_id":
            return arg_value

    return None


def _get_category_value(
    category: Union[str, Callable, None],
    result: Any,
    args: tuple,
    kwargs: dict
) -> Optional[str]:
    """Get category value from various sources.

    Args:
        category: Category string, callable, or None
        result: Function return value
        args: Function arguments
        kwargs: Function keyword arguments

    Returns:
        Category string or None
    """
    if category is None:
        return None

    if isinstance(category, str):
        return category

    if callable(category):
        # Category is a function/lambda - call it with result
        try:
            return category(result, *args, **kwargs)
        except Exception as e:
            logger.warning(f"Error extracting category from callable: {e}")
            return None

    return None


def invalidate_cache(
    category: Union[str, Callable, None] = None,
    restaurant_id_param: str = "restaurant_id"
):
    """Decorator to automatically invalidate cache after function execution.

    Automatically calls clear_cache() after the decorated function succeeds.
    Extracts restaurant_id from function arguments.

    Args:
        category: Cache category to invalidate. Can be:
            - String: Fixed category (e.g., "menu", "modifiers")
            - Callable: Function that extracts category from result/args
            - None: Invalidates all categories for the restaurant
        restaurant_id_param: Parameter name for restaurant_id (default: "restaurant_id")

    Usage:
        # Fixed category
        @invalidate_cache(category="menu")
        async def create_menu_item(restaurant_id: str, ...):
            pass

        # Dynamic category from result
        @invalidate_cache(category=lambda result: result.get("category"))
        async def create_item(restaurant_id: str, ...):
            return {"category": "menu", ...}

        # All categories
        @invalidate_cache()
        async def delete_restaurant(restaurant_id: str, ...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        # Check if function is async
        is_async = inspect.iscoroutinefunction(func)

        if is_async:
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Execute the function
                result = await func(*args, **kwargs)

                # Extract restaurant_id
                restaurant_id = _extract_restaurant_id(args, kwargs, func)

                if restaurant_id:
                    # Get category value
                    cat_value = _get_category_value(
                        category, result, args, kwargs)

                    # Invalidate cache
                    try:
                        clear_cache(restaurant_id, cat_value)
                        logger.debug(
                            f"Cache invalidated for restaurant {restaurant_id}, "
                            f"category: {cat_value or 'all'}"
                        )
                    except Exception as e:
                        # Don't fail the request if cache invalidation fails
                        logger.warning(
                            f"Failed to invalidate cache for restaurant {restaurant_id}: {e}"
                        )
                else:
                    logger.warning(
                        f"Could not extract restaurant_id for cache invalidation "
                        f"in {func.__name__}"
                    )

                return result

            return async_wrapper
        else:
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Execute the function
                result = func(*args, **kwargs)

                # Extract restaurant_id
                restaurant_id = _extract_restaurant_id(args, kwargs, func)

                if restaurant_id:
                    # Get category value
                    cat_value = _get_category_value(
                        category, result, args, kwargs)

                    # Invalidate cache
                    try:
                        clear_cache(restaurant_id, cat_value)
                        logger.debug(
                            f"Cache invalidated for restaurant {restaurant_id}, "
                            f"category: {cat_value or 'all'}"
                        )
                    except Exception as e:
                        # Don't fail the request if cache invalidation fails
                        logger.warning(
                            f"Failed to invalidate cache for restaurant {restaurant_id}: {e}"
                        )
                else:
                    logger.warning(
                        f"Could not extract restaurant_id for cache invalidation "
                        f"in {func.__name__}"
                    )

                return result

            return sync_wrapper

    return decorator

