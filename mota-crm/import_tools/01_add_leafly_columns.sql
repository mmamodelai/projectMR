-- ============================================================================
-- Leafly Integration - Add Columns to Products Table
-- ============================================================================
-- Purpose: Enhance products table with rich Leafly strain data
-- Data Source: Data/inventory_enhanced_v2.json (24 strains)
-- Run in: Supabase SQL Editor
-- ============================================================================

BEGIN;

-- Basic Leafly fields
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_strain_type TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_description TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_rating DECIMAL(3, 2);
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_review_count INTEGER;

-- Arrays for multi-value fields (PostgreSQL native arrays)
ALTER TABLE products ADD COLUMN IF NOT EXISTS effects TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS helps_with TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS negatives TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS flavors TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS terpenes TEXT[];

-- Lineage information
ALTER TABLE products ADD COLUMN IF NOT EXISTS parent_strains TEXT[];
ALTER TABLE products ADD COLUMN IF NOT EXISTS lineage TEXT;

-- Media
ALTER TABLE products ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_url TEXT;

-- Metadata
ALTER TABLE products ADD COLUMN IF NOT EXISTS leafly_data_updated_at TIMESTAMPTZ;

-- ============================================================================
-- Create GIN indexes for array searches (enables fast filtering)
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_products_effects 
ON products USING GIN(effects);

CREATE INDEX IF NOT EXISTS idx_products_helps_with 
ON products USING GIN(helps_with);

CREATE INDEX IF NOT EXISTS idx_products_flavors 
ON products USING GIN(flavors);

CREATE INDEX IF NOT EXISTS idx_products_terpenes 
ON products USING GIN(terpenes);

-- Index for checking which products have Leafly data
CREATE INDEX IF NOT EXISTS idx_products_has_leafly 
ON products(leafly_description) WHERE leafly_description IS NOT NULL;

COMMIT;

-- ============================================================================
-- Create Helper View for AI Queries
-- ============================================================================

CREATE OR REPLACE VIEW products_with_leafly AS
SELECT 
    p.id,
    p.product_id,
    p.name,
    p.brand,
    p.category,
    p.strain,
    
    -- Cannabis Profile (combine existing + Leafly)
    p.flower_type,
    p.thc_percent,
    p.cbd_percent,
    COALESCE(p.leafly_strain_type, p.flower_type) as strain_type,
    
    -- Leafly Rich Data
    p.leafly_description,
    p.leafly_rating,
    p.leafly_review_count,
    p.effects,
    p.helps_with,
    p.negatives,
    p.flavors,
    p.terpenes,
    p.parent_strains,
    p.lineage,
    p.image_url,
    p.leafly_url,
    
    -- Stock & Pricing
    p.retail_price,
    p.current_stock,
    p.is_in_stock,
    p.is_low_stock,
    
    -- Useful flags
    CASE 
        WHEN p.leafly_description IS NOT NULL THEN true 
        ELSE false 
    END as has_leafly_data,
    
    -- Timestamps
    p.created_at,
    p.updated_at,
    p.leafly_data_updated_at
    
FROM products p;

-- Grant access to authenticated users
GRANT SELECT ON products_with_leafly TO authenticated;

-- ============================================================================
-- Verification Queries
-- ============================================================================

-- Check that columns were added
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'products' 
AND column_name LIKE '%leafly%' OR column_name IN ('effects', 'helps_with', 'flavors', 'terpenes');

-- Check indexes
SELECT indexname, indexdef 
FROM pg_indexes 
WHERE tablename = 'products' 
AND indexname LIKE '%leafly%' OR indexname LIKE '%effect%' OR indexname LIKE '%helps%';

-- Test view
SELECT COUNT(*) as total_products, 
       COUNT(leafly_description) as products_with_leafly 
FROM products_with_leafly;

-- ============================================================================
-- Success Message
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'LEAFLY COLUMNS ADDED SUCCESSFULLY';
    RAISE NOTICE '=================================================================';
    RAISE NOTICE 'New columns: leafly_strain_type, leafly_description, effects, etc.';
    RAISE NOTICE 'GIN indexes created for fast array searches';
    RAISE NOTICE 'View created: products_with_leafly';
    RAISE NOTICE '';
    RAISE NOTICE 'Next step: Run import_leafly_data.py to populate data';
    RAISE NOTICE '=================================================================';
END $$;



