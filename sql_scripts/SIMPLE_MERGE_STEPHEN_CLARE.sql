-- ============================================
-- SIMPLE FIX: Merge Stephen Clare
-- ============================================
-- This is a simple, fast fix for your specific case
-- ============================================

-- Step 1: See both records
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    CASE 
        WHEN phone IS NOT NULL THEN '>>> KEEP THIS ONE <<<'
        ELSE 'MERGE/DELETE THIS'
    END as recommendation
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen' 
AND LOWER(last_name) = 'clare'
ORDER BY phone NULLS LAST;

-- Step 2: Copy phone to the duplicate (if you want to keep both)
UPDATE customers_blaze
SET phone = '+16199773020',
    updated_at = NOW()
WHERE member_id = '683cea4e022c82ba434de1df'
AND phone IS NULL;

-- Step 3: OR just delete the empty duplicate
-- DELETE FROM customers_blaze
-- WHERE member_id = '683cea4e022c82ba434de1df'
-- AND phone IS NULL;

-- Step 4: Verify
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen' 
AND LOWER(last_name) = 'clare';

