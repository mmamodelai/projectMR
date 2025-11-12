-- Fix Missing Product Names in Transaction Items
-- Backfill product_name and brand from products_blaze table

-- ============================================================================
-- STEP 1: CHECK CURRENT STATE
-- ============================================================================
SELECT 
    'Current State' as status,
    COUNT(*) as total_items,
    COUNT(product_name) as items_with_name,
    COUNT(*) - COUNT(product_name) as items_missing_name,
    COUNT(brand) as items_with_brand,
    COUNT(*) - COUNT(brand) as items_missing_brand
FROM transaction_items_blaze;

-- ============================================================================
-- STEP 2: SEE WHICH ITEMS CAN BE FIXED
-- ============================================================================
-- Items that have product_id but no product_name
SELECT 
    'Fixable Items' as category,
    COUNT(*) as count
FROM transaction_items_blaze ti
WHERE ti.product_name IS NULL
AND ti.product_id IS NOT NULL
AND EXISTS (
    SELECT 1 FROM products_blaze p 
    WHERE p.product_id = ti.product_id
);

-- ============================================================================
-- STEP 3: BACKFILL PRODUCT NAMES (DO THIS IN BATCHES)
-- ============================================================================
-- Update items with missing product_name by looking up in products_blaze

/*
-- BATCH 1: First 50,000 items
UPDATE transaction_items_blaze ti
SET 
    product_name = p.name,
    brand = COALESCE(ti.brand, 'Unknown')  -- Keep existing brand if present
FROM products_blaze p
WHERE ti.product_id = p.product_id
AND ti.product_name IS NULL
AND ti.id IN (
    SELECT id 
    FROM transaction_items_blaze 
    WHERE product_name IS NULL 
    AND product_id IS NOT NULL
    LIMIT 50000
);
*/

-- ============================================================================
-- STEP 4: CHECK WHAT'S LEFT
-- ============================================================================
-- After running the UPDATE, check what couldn't be fixed
SELECT 
    'After Backfill' as status,
    COUNT(*) as total_items,
    COUNT(product_name) as items_with_name,
    COUNT(*) - COUNT(product_name) as items_still_missing_name
FROM transaction_items_blaze;

-- Items that can't be fixed (product_id doesn't exist in products_blaze)
SELECT 
    'Unfixable - No Product Match' as category,
    COUNT(*) as count
FROM transaction_items_blaze ti
WHERE ti.product_name IS NULL
AND (ti.product_id IS NULL OR NOT EXISTS (
    SELECT 1 FROM products_blaze p 
    WHERE p.product_id = ti.product_id
));

-- ============================================================================
-- STEP 5: SAMPLE CHECK
-- ============================================================================
-- Show sample of fixed items
SELECT 
    ti.transaction_id,
    ti.product_id,
    ti.product_name as item_product_name,
    p.name as products_table_name,
    ti.quantity,
    ti.total_price
FROM transaction_items_blaze ti
LEFT JOIN products_blaze p ON p.product_id = ti.product_id
WHERE ti.product_name IS NOT NULL
LIMIT 10;

-- ============================================================================
-- INSTRUCTIONS
-- ============================================================================
-- 1. Run STEP 1 to see current state (done - 582,435 missing!)
-- 2. Run STEP 2 to see how many can be fixed
-- 3. Uncomment and run STEP 3 multiple times (50k at a time) until done
-- 4. Run STEP 4 to verify
-- 5. Run STEP 5 to sample check

-- NOTE: This will take a while with 582k items to fix!
-- Run the UPDATE in batches of 50k to avoid timeout

