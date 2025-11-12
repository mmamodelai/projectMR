-- ============================================
-- FAST DUPLICATE FINDER (No Timeout)
-- ============================================
-- Step 1: Just find and display duplicates
-- Run this first to see what needs merging
-- ============================================

-- Simple duplicate count by name
SELECT 
    LOWER(TRIM(first_name)) as first,
    LOWER(TRIM(last_name)) as last,
    COUNT(*) as duplicate_count
FROM customers_blaze
WHERE first_name IS NOT NULL 
AND last_name IS NOT NULL
GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name))
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 50;

