-- ============================================
-- SUPER SIMPLE TEST: Merge "medgo artea drots"
-- ============================================
-- This will merge THE MOST duplicated person
-- and show CLEAR before/after results
-- ============================================

-- STEP 1: Show BEFORE state
SELECT '=== BEFORE MERGE ===' as status;

SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    'BEFORE' as when_captured
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots'
ORDER BY 
    (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
    (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
    COALESCE(total_visits, 0) * 10
DESC;

-- Count them
SELECT COUNT(*) as total_medgo_records_before
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- STEP 2: Pick the KEEPER (best record)
-- We'll use a CTE to be explicit
WITH keeper AS (
    SELECT 
        member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
        COALESCE(total_visits, 0) * 10
    DESC
    LIMIT 1
),
duplicates AS (
    SELECT 
        c.member_id,
        c.phone,
        c.email
    FROM customers_blaze c
    CROSS JOIN keeper k
    WHERE LOWER(TRIM(c.first_name)) = 'medgo'
    AND LOWER(TRIM(c.last_name)) = 'drots'
    AND c.member_id != k.member_id
)
-- Show what we're about to do
SELECT 
    k.member_id as keeper_id,
    d.member_id as duplicate_id,
    d.phone as dupe_phone,
    d.email as dupe_email,
    'WILL DELETE' as action
FROM keeper k
CROSS JOIN duplicates d;

-- STEP 3: Actually do the merge
-- Move transactions from duplicates to keeper
WITH keeper AS (
    SELECT 
        member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
        COALESCE(total_visits, 0) * 10
    DESC
    LIMIT 1
)
UPDATE transactions_blaze t
SET customer_id = (SELECT member_id FROM keeper)
WHERE customer_id IN (
    SELECT c.member_id
    FROM customers_blaze c
    CROSS JOIN keeper k
    WHERE LOWER(TRIM(c.first_name)) = 'medgo'
    AND LOWER(TRIM(c.last_name)) = 'drots'
    AND c.member_id != k.member_id
);

-- Show how many transactions we moved
SELECT '=== TRANSACTIONS MOVED ===' as status;

-- Copy missing data to keeper
WITH keeper AS (
    SELECT 
        member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
        COALESCE(total_visits, 0) * 10
    DESC
    LIMIT 1
),
best_data AS (
    SELECT 
        MAX(CASE WHEN phone IS NOT NULL AND phone != '' THEN phone END) as best_phone,
        MAX(CASE WHEN email IS NOT NULL AND email != '' THEN email END) as best_email
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
)
UPDATE customers_blaze c
SET 
    phone = COALESCE(c.phone, b.best_phone),
    email = COALESCE(c.email, b.best_email),
    updated_at = NOW()
FROM keeper k, best_data b
WHERE c.member_id = k.member_id;

-- Delete the duplicates
WITH keeper AS (
    SELECT 
        member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
        COALESCE(total_visits, 0) * 10
    DESC
    LIMIT 1
)
DELETE FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots'
AND member_id != (SELECT member_id FROM keeper);

SELECT '=== DUPLICATES DELETED ===' as status;

-- Recalculate stats for keeper
WITH keeper AS (
    SELECT 
        member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    LIMIT 1
)
UPDATE customers_blaze c
SET
    total_visits = (
        SELECT COUNT(*)
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
        AND t.blaze_status = 'Completed'
    ),
    lifetime_value = (
        SELECT COALESCE(SUM(total_amount), 0)
        FROM transactions_blaze t
        WHERE t.customer_id = c.member_id
        AND t.blaze_status = 'Completed'
    ),
    vip_status = CASE
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
            AND t.blaze_status = 'Completed'
        ) >= 16 THEN 'VIP'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
            AND t.blaze_status = 'Completed'
        ) BETWEEN 11 AND 15 THEN 'Regular2'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
            AND t.blaze_status = 'Completed'
        ) BETWEEN 5 AND 10 THEN 'Regular1'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
            AND t.blaze_status = 'Completed'
        ) BETWEEN 2 AND 4 THEN 'Casual'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = c.member_id
            AND t.blaze_status = 'Completed'
        ) = 1 THEN 'First'
        ELSE 'New'
    END,
    updated_at = NOW()
FROM keeper k
WHERE c.member_id = k.member_id;

-- STEP 4: Show AFTER state
SELECT '=== AFTER MERGE ===' as status;

SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    vip_status,
    'AFTER' as when_captured
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- Count them
SELECT COUNT(*) as total_medgo_records_after
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- Should be 1 now!
SELECT 
    CASE 
        WHEN COUNT(*) = 1 THEN '✓ SUCCESS! Merged into 1 record'
        ELSE '✗ FAILED! Still have duplicates'
    END as result
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

