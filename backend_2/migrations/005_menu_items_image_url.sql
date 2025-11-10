-- Migration: 005 - Menu Items Image URL
-- Adds image_url column to menu_items table for storing menu item images
-- Images are stored in Supabase Storage bucket: menu-images
ALTER TABLE menu_items
ADD COLUMN IF NOT EXISTS image_url TEXT;

-- Add index for faster queries when filtering by image_url
CREATE INDEX IF NOT EXISTS idx_menu_items_image_url ON menu_items (image_url)
WHERE
    image_url IS NOT NULL;

-- Add comment

