-- ============================================
-- BULK MERGE ALL DUPLICATES - ONE SHOT
-- ============================================
-- This finds ALL duplicates and merges them in bulk
-- Run this multiple times until no duplicates remain
-- ============================================

-- Step 1: Create a temp table with "keeper" records
-- (The best record from each duplicate group)
CREATE TEMP TABLE keepers AS
SELECT DISTINCT ON (
    LOWER(TRIM(first_name)),
    LOWER(TRIM(last_name)),
    date_of_birth
)
    member_id as keeper_id,
    LOWER(TRIM(first_name)) as first_lower,
    LOWER(TRIM(last_name)) as last_lower,
    date_of_birth as dob
FROM customers_blaze
WHERE first_name IS NOT NULL 
AND last_name IS NOT NULL
ORDER BY 
    LOWER(TRIM(first_name)),
    LOWER(TRIM(last_name)),
    date_of_birth,
    -- Score: pick best record (has phone, email, most visits)
    (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
    (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
    COALESCE(total_visits, 0) * 10
    DESC;

-- Step 2: Create a temp table with ALL duplicates (not keepers)
CREATE TEMP TABLE duplicates AS
SELECT 
    c.member_id as dupe_id,
    k.keeper_id,
    LOWER(TRIM(c.first_name)) as first_lower,
    LOWER(TRIM(c.last_name)) as last_lower,
    c.phone,
    c.email
FROM customers_blaze c
JOIN keepers k 
    ON LOWER(TRIM(c.first_name)) = k.first_lower
    AND LOWER(TRIM(c.last_name)) = k.last_lower
    AND (c.date_of_birth = k.dob OR (c.date_of_birth IS NULL AND k.dob IS NULL))
WHERE c.member_id != k.keeper_id;

-- Step 3: Show what we're about to do
SELECT 
    'DUPLICATES TO MERGE' as action,
    COUNT(*) as total_duplicates,
    COUNT(DISTINCT keeper_id) as groups
FROM duplicates;

-- Step 4: Move ALL transactions from duplicates to keepers
UPDATE transactions_blaze t
SET customer_id = d.keeper_id
FROM duplicates d
WHERE t.customer_id = d.dupe_id;

SELECT 'Transactions moved' as status;

-- Step 5: Copy any missing contact info to keepers
UPDATE customers_blaze c
SET 
    phone = COALESCE(c.phone, d.phone),
    email = COALESCE(c.email, d.email),
    updated_at = NOW()
FROM duplicates d
WHERE c.member_id = d.keeper_id
AND (c.phone IS NULL OR c.phone = '' OR c.email IS NULL OR c.email = '');

SELECT 'Contact info updated' as status;

-- Step 6: DELETE all duplicate records (in batches of 1000 to avoid timeout)
-- First batch
DELETE FROM customers_blaze
WHERE member_id IN (
    SELECT dupe_id 
    FROM duplicates 
    LIMIT 1000
);

SELECT 'Deleted first batch of duplicates' as status;

-- Step 7: Recalculate stats for keepers (sample of 100 to avoid timeout)
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
    last_visited = (
        SELECT MAX(date::DATE)
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
WHERE c.member_id IN (
    SELECT keeper_id 
    FROM duplicates 
    LIMIT 100
);

SELECT 'Stats recalculated for keepers' as status;

-- Step 8: Show results
SELECT 
    'MERGE COMPLETE!' as status,
    (SELECT COUNT(*) FROM duplicates) - 1000 as remaining_duplicates_to_delete,
    'Run again to delete more if remaining > 0' as note;

-- Clean up temp tables
DROP TABLE IF EXISTS keepers;
DROP TABLE IF EXISTS duplicates;

