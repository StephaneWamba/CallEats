"""Menu item image service.

This module provides business logic for menu item image management using Supabase Storage.
It handles image upload, deletion, and URL management.

Key Features:
    - Image upload to Supabase Storage bucket: menu-images
    - File validation (type, size)
    - Unique filename generation
    - Image URL storage in database
    - Image deletion from storage and database

Usage:
    from restaurant_voice_assistant.domain.menu.images import (
        upload_menu_item_image,
        delete_menu_item_image
    )
    
    image_url = upload_menu_item_image(
        restaurant_id="...",
        item_id="...",
        file_content=...,
        filename="image.jpg"
    )
"""
from typing import Optional
from uuid import uuid4
from restaurant_voice_assistant.infrastructure.database.client import get_supabase_service_client
import logging

logger = logging.getLogger(__name__)

# Allowed image MIME types
ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp"
}

# Maximum file size: 5MB
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB in bytes

# Storage bucket name
STORAGE_BUCKET = "menu-images"


def _validate_image_file(file_content: bytes, content_type: Optional[str]) -> None:
    """Validate image file type and size.

    Args:
        file_content: File content as bytes
        content_type: MIME type of the file

    Raises:
        ValueError: If file is invalid (wrong type or too large)
    """
    # Check file size
    if len(file_content) > MAX_FILE_SIZE:
        raise ValueError(
            f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024)}MB")

    # Check content type
    if content_type and content_type.lower() not in ALLOWED_IMAGE_TYPES:
        raise ValueError(
            f"Invalid file type. Allowed types: jpeg, jpg, png, webp")


def _generate_filename(item_id: str, original_filename: str) -> str:
    """Generate unique filename for menu item image.

    Args:
        item_id: Menu item UUID
        original_filename: Original filename from upload

    Returns:
        Unique filename: {item_id}-{uuid}.{ext}
    """
    # Extract extension from original filename
    if "." in original_filename:
        ext = original_filename.rsplit(".", 1)[-1].lower()
        # Normalize extension
        if ext == "jpg":
            ext = "jpeg"
    else:
        ext = "jpg"  # Default to jpg

    # Generate unique filename
    unique_id = uuid4().hex[:8]
    return f"{item_id}-{unique_id}.{ext}"


def upload_menu_item_image(
    restaurant_id: str,
    item_id: str,
    file_content: bytes,
    filename: str,
    content_type: Optional[str] = None
) -> str:
    """Upload menu item image to Supabase Storage and update database.

    Args:
        restaurant_id: Restaurant UUID
        item_id: Menu item UUID
        file_content: Image file content as bytes
        filename: Original filename
        content_type: MIME type of the file

    Returns:
        Public URL of the uploaded image

    Raises:
        ValueError: If file validation fails
        Exception: If upload or database update fails
    """
    supabase = get_supabase_service_client()

    # Validate file
    _validate_image_file(file_content, content_type)

    # Generate unique filename
    storage_filename = _generate_filename(item_id, filename)
    storage_path = f"{restaurant_id}/{item_id}/{storage_filename}"

    try:
        # Upload to Supabase Storage
        supabase.storage.from_(STORAGE_BUCKET).upload(
            path=storage_path,
            file=file_content,
            file_options={
                "content-type": content_type or "image/jpeg", "upsert": "true"}
        )

        # Get public URL
        image_url = supabase.storage.from_(
            STORAGE_BUCKET).get_public_url(storage_path)

        # Update menu item with image URL
        update_response = supabase.table("menu_items").update({
            "image_url": image_url
        }).eq("restaurant_id", restaurant_id).eq("id", item_id).execute()

        if not update_response.data:
            # Rollback: delete uploaded file if database update fails
            try:
                supabase.storage.from_(STORAGE_BUCKET).remove([storage_path])
            except Exception as e:
                logger.warning(f"Failed to rollback image upload: {e}")
            raise Exception("Failed to update menu item with image URL")

        logger.info(
            f"Successfully uploaded image for menu item {item_id}: {image_url}")
        return image_url

    except Exception as e:
        logger.error(
            f"Error uploading image for menu item {item_id}: {e}", exc_info=True)
        raise


def delete_menu_item_image(restaurant_id: str, item_id: str) -> bool:
    """Delete menu item image from Supabase Storage and database.

    Args:
        restaurant_id: Restaurant UUID
        item_id: Menu item UUID

    Returns:
        True if deleted successfully, False if no image exists

    Raises:
        Exception: If deletion fails
    """
    supabase = get_supabase_service_client()

    try:
        # Get current image URL
        item_response = supabase.table("menu_items").select(
            "image_url"
        ).eq("restaurant_id", restaurant_id).eq("id", item_id).limit(1).execute()

        if not item_response.data or not item_response.data[0].get("image_url"):
            return False  # No image to delete

        image_url = item_response.data[0]["image_url"]

        # Extract storage path from URL
        # URL format: https://{project}.supabase.co/storage/v1/object/public/{bucket}/{path}
        # We need to extract the path part
        if "/object/public/" in image_url:
            storage_path = image_url.split("/object/public/")[-1]
            # Remove bucket name from path if present
            if storage_path.startswith(f"{STORAGE_BUCKET}/"):
                storage_path = storage_path[len(f"{STORAGE_BUCKET}/"):]
        else:
            # Fallback: construct path from restaurant_id and item_id
            # This assumes the path structure matches our upload format
            storage_path = f"{restaurant_id}/{item_id}"

        # Delete from storage (try to delete, but don't fail if file doesn't exist)
        try:
            # List files in the directory to find the exact file
            files = supabase.storage.from_(STORAGE_BUCKET).list(
                f"{restaurant_id}/{item_id}")
            if files:
                for file_info in files:
                    file_path = f"{restaurant_id}/{item_id}/{file_info['name']}"
                    supabase.storage.from_(STORAGE_BUCKET).remove([file_path])
        except Exception as e:
            logger.warning(f"Failed to delete image file from storage: {e}")

        # Update database (set image_url to NULL)
        update_response = supabase.table("menu_items").update({
            "image_url": None
        }).eq("restaurant_id", restaurant_id).eq("id", item_id).execute()

        if update_response.data:
            logger.info(f"Successfully deleted image for menu item {item_id}")
            return True

        return False

    except Exception as e:
        logger.error(
            f"Error deleting image for menu item {item_id}: {e}", exc_info=True)
        raise
