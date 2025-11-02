-- Migration: 019 - Add menu_item_modifiers junction table
-- Enables many-to-many relationship between menu items and modifiers

CREATE TABLE IF NOT EXISTS menu_item_modifiers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    menu_item_id UUID NOT NULL REFERENCES menu_items(id) ON DELETE CASCADE,
    modifier_id UUID NOT NULL REFERENCES modifiers(id) ON DELETE CASCADE,
    is_required BOOLEAN DEFAULT false,
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(menu_item_id, modifier_id)
);

CREATE INDEX IF NOT EXISTS idx_menu_item_modifiers_menu_item ON menu_item_modifiers(menu_item_id);
CREATE INDEX IF NOT EXISTS idx_menu_item_modifiers_modifier ON menu_item_modifiers(modifier_id);

-- Enable RLS
ALTER TABLE menu_item_modifiers ENABLE ROW LEVEL SECURITY;

-- Service role has full access
CREATE POLICY "Service role has full access to menu_item_modifiers"
ON menu_item_modifiers FOR ALL TO service_role
USING (true) WITH CHECK (true);

-- Public read access (for API)
CREATE POLICY "Public read access to menu_item_modifiers"
ON menu_item_modifiers FOR SELECT TO anon, authenticated
USING (true);


