-- Migration: 021 - Add categories table and migrate existing category data
-- Converts menu_items.category from TEXT to category_id UUID foreign key
-- Create categories table
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid (),
    restaurant_id UUID NOT NULL REFERENCES restaurants (id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW (),
        updated_at TIMESTAMP
    WITH
        TIME ZONE DEFAULT NOW (),
        UNIQUE (restaurant_id, name)
);

CREATE INDEX IF NOT EXISTS idx_categories_restaurant ON categories (restaurant_id);

CREATE INDEX IF NOT EXISTS idx_categories_display_order ON categories (restaurant_id, display_order);

-- Add category_id column to menu_items (nullable initially for migration)
ALTER TABLE menu_items
ADD COLUMN IF NOT EXISTS category_id UUID REFERENCES categories (id) ON DELETE SET NULL;

CREATE INDEX IF NOT EXISTS idx_menu_items_category_id ON menu_items (category_id);

-- Migrate existing category text values to categories table
-- Create categories from unique category strings in menu_items
-- Use ON CONFLICT to handle duplicates gracefully
INSERT INTO
    categories (restaurant_id, name, display_order)
SELECT DISTINCT
    restaurant_id,
    category,
    ROW_NUMBER() OVER (
        PARTITION BY
            restaurant_id
        ORDER BY
            category
    ) - 1 as display_order
FROM
    menu_items
WHERE
    category IS NOT NULL
    AND category != '' ON CONFLICT (restaurant_id, name) DO NOTHING;

-- Update menu_items to reference categories
UPDATE menu_items mi
SET
    category_id = c.id
FROM
    categories c
WHERE
    mi.restaurant_id = c.restaurant_id
    AND mi.category = c.name
    AND mi.category_id IS NULL;

-- Keep category TEXT column for now (can be removed in future migration if desired)
-- This allows backward compatibility during transition
-- Enable RLS
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role has full access to categories" ON categories FOR ALL TO service_role USING (true)
WITH
    CHECK (true);

-- Public read access
CREATE POLICY "Public read access to categories" ON categories FOR
SELECT
    TO anon,
    authenticated USING (true);

-- Auto-update trigger
CREATE TRIGGER update_categories_updated_at BEFORE
UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column ();