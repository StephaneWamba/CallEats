-- Clear all database tables for testing
-- Run this in Supabase SQL Editor

-- Clear tables in order (respecting foreign key constraints)
DELETE FROM call_history;
DELETE FROM document_embeddings;
DELETE FROM menu_item_modifiers;
DELETE FROM menu_items;
DELETE FROM modifiers;
DELETE FROM categories;
DELETE FROM delivery_zones;
DELETE FROM operating_hours;
DELETE FROM restaurant_phone_mappings;
DELETE FROM restaurants;
DELETE FROM users;

-- Verify tables are empty
SELECT 'call_history' as table_name, COUNT(*) as count FROM call_history
UNION ALL
SELECT 'document_embeddings', COUNT(*) FROM document_embeddings
UNION ALL
SELECT 'menu_item_modifiers', COUNT(*) FROM menu_item_modifiers
UNION ALL
SELECT 'menu_items', COUNT(*) FROM menu_items
UNION ALL
SELECT 'modifiers', COUNT(*) FROM modifiers
UNION ALL
SELECT 'categories', COUNT(*) FROM categories
UNION ALL
SELECT 'delivery_zones', COUNT(*) FROM delivery_zones
UNION ALL
SELECT 'operating_hours', COUNT(*) FROM operating_hours
UNION ALL
SELECT 'restaurant_phone_mappings', COUNT(*) FROM restaurant_phone_mappings
UNION ALL
SELECT 'restaurants', COUNT(*) FROM restaurants
UNION ALL
SELECT 'users', COUNT(*) FROM users;


