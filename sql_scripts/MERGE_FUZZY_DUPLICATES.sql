-- ============================================
-- AGGRESSIVE MERGE - DOB WITHIN 1 DAY
-- ============================================
-- Merges duplicates where:
-- - Same first name (case-insensitive)
-- - Same last name (case-insensitive)
-- - DOB within ±1 day (or both NULL)
-- ============================================

-- Step 1: Find ALL potential duplicate pairs
-- This is more aggressive than the previous merge
WITH potential_dupes AS (
    SELECT 
        c1.member_id as id1,
        c2.member_id as id2,
        c1.first_name,
        c1.last_name,
        c1.date_of_birth as dob1,
        c2.date_of_birth as dob2,
        c1.phone as phone1,
        c2.phone as phone2,
        c1.email as email1,
        c2.email as email2,
        c1.total_visits as visits1,
        c2.total_visits as visits2,
        -- Score each record (higher = better)
        (CASE WHEN c1.phone IS NOT NULL AND c1.phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN c1.email IS NOT NULL AND c1.email != '' THEN 500 ELSE 0 END) +
        COALESCE(c1.total_visits, 0) * 10 as score1,
        (CASE WHEN c2.phone IS NOT NULL AND c2.phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN c2.email IS NOT NULL AND c2.email != '' THEN 500 ELSE 0 END) +
        COALESCE(c2.total_visits, 0) * 10 as score2
    FROM customers_blaze c1
    JOIN customers_blaze c2
        ON LOWER(TRIM(c1.first_name)) = LOWER(TRIM(c2.first_name))
        AND LOWER(TRIM(c1.last_name)) = LOWER(TRIM(c2.last_name))
        AND c1.member_id < c2.member_id  -- Avoid duplicate pairs
        AND (
            -- DOB within 1 day OR both NULL
            (c1.date_of_birth IS NULL AND c2.date_of_birth IS NULL)
            OR ABS(EXTRACT(DAY FROM c1.date_of_birth - c2.date_of_birth)) <= 1
        )
    WHERE c1.first_name IS NOT NULL 
    AND c1.last_name IS NOT NULL
    LIMIT 100  -- Process 100 pairs at a time
),
-- Step 2: Determine keeper for each pair (higher score wins)
merge_plan AS (
    SELECT 
        CASE WHEN score1 >= score2 THEN id1 ELSE id2 END as keeper_id,
        CASE WHEN score1 >= score2 THEN id2 ELSE id1 END as dupe_id,
        first_name,
        last_name,
        CASE WHEN score1 >= score2 THEN dob1 ELSE dob2 END as keeper_dob,
        CASE WHEN score1 >= score2 THEN dob2 ELSE dob1 END as dupe_dob,
        CASE WHEN score1 >= score2 THEN phone2 ELSE phone1 END as dupe_phone,
        CASE WHEN score1 >= score2 THEN email2 ELSE email1 END as dupe_email
    FROM potential_dupes
)
-- Step 3: Show what we're about to merge
SELECT 
    'FUZZY DUPLICATES TO MERGE' as action,
    COUNT(*) as pairs_to_merge,
    COUNT(DISTINCT keeper_id) as unique_keepers
FROM merge_plan;

-- Step 4: Copy any missing data from dupes to keepers
UPDATE customers_blaze c
SET 
    phone = COALESCE(c.phone, m.dupe_phone),
    email = COALESCE(c.email, m.dupe_email),
    updated_at = NOW()
FROM merge_plan m
WHERE c.member_id = m.keeper_id
AND (c.phone IS NULL OR c.phone = '' OR c.email IS NULL OR c.email = '');

SELECT 'Contact info merged' as status;

-- Step 5: Move ALL transactions from duplicates to keepers
UPDATE transactions_blaze t
SET customer_id = m.keeper_id
FROM merge_plan m
WHERE t.customer_id = m.dupe_id;

SELECT 'Transactions moved' as status;

-- Step 6: Delete the duplicates
DELETE FROM customers_blaze c
USING merge_plan m
WHERE c.member_id = m.dupe_id;

SELECT 'Duplicates deleted' as status;

-- Step 7: Recalculate stats for keepers
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
FROM merge_plan m
WHERE c.member_id = m.keeper_id;

SELECT 'Stats recalculated' as status;

-- Step 8: Show results
SELECT 
    'FUZZY MERGE COMPLETE!' as status,
    (SELECT COUNT(*) FROM merge_plan) as pairs_merged,
    'Run again if more fuzzy duplicates exist' as note;

-- Example: This will merge:
-- - "STEPHEN CLARE" (DOB: 1983-02-05) with "stephen clare" (DOB: 1983-02-04)
-- - Any other names where DOB differs by exactly 1 day

