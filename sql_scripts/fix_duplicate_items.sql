-- Fix Duplicate Transaction Items Issue
-- Run this in Supabase SQL Editor

-- ============================================================================
-- STEP 1: BACKUP - Count current state
-- ============================================================================
SELECT 
    'Before Deduplication' as status,
    COUNT(*) as total_items,
    COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as unique_items,
    COUNT(*) - COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as duplicates
FROM transaction_items_blaze;

-- ============================================================================
-- STEP 2: IDENTIFY DUPLICATES
-- ============================================================================
-- See which items are duplicated
SELECT 
    transaction_id,
    product_name,
    brand,
    quantity,
    COUNT(*) as times_inserted,
    MIN(id) as keep_id,  -- We'll keep the first one
    STRING_AGG(id::text, ', ') as all_ids
FROM transaction_items_blaze
GROUP BY transaction_id, product_id, product_name, brand, quantity, unit_price
HAVING COUNT(*) > 1
ORDER BY times_inserted DESC
LIMIT 50;

-- ============================================================================
-- STEP 3: DELETE DUPLICATES (KEEP OLDEST RECORD)
-- ============================================================================
-- WARNING: This will permanently delete duplicate items!
-- Make sure to review Step 2 results first!

/*
WITH ranked_items AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id, product_id, product_name, quantity, unit_price
            ORDER BY id  -- Keep the first inserted record (lowest id)
        ) as rn
    FROM transaction_items_blaze
)
DELETE FROM transaction_items_blaze
WHERE id IN (
    SELECT id 
    FROM ranked_items 
    WHERE rn > 1  -- Delete all but the first occurrence
);
*/

-- ============================================================================
-- STEP 4: ADD UNIQUE CONSTRAINT
-- ============================================================================
-- This prevents future duplicates
-- NOTE: This will FAIL if duplicates still exist after Step 3

/*
ALTER TABLE transaction_items_blaze
ADD CONSTRAINT unique_transaction_item
UNIQUE (transaction_id, product_id, quantity, unit_price);
*/

-- ============================================================================
-- STEP 5: VERIFY CLEANUP
-- ============================================================================
SELECT 
    'After Deduplication' as status,
    COUNT(*) as total_items,
    COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as unique_items
FROM transaction_items_blaze;

-- Check for any remaining duplicates
SELECT 
    transaction_id,
    product_name,
    COUNT(*) as count
FROM transaction_items_blaze
GROUP BY transaction_id, product_id, product_name, quantity, unit_price
HAVING COUNT(*) > 1;

-- ============================================================================
-- INSTRUCTIONS
-- ============================================================================
-- 1. Run STEP 1 to see current state
-- 2. Run STEP 2 to identify duplicates
-- 3. Uncomment and run STEP 3 to delete duplicates (BACKUP FIRST!)
-- 4. Uncomment and run STEP 4 to add unique constraint
-- 5. Run STEP 5 to verify cleanup
-- 6. Apply code fix to supabase_client.py (see docs/OCT31_DUPLICATE_ISSUE.md)



