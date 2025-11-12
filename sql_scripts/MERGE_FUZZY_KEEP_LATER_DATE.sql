-- ============================================
-- FUZZY MERGE - KEEP LATER DATE
-- ============================================
-- Logic:
-- - If DOB differs by EXACTLY 1 day: MERGE
-- - If DOB differs by MORE than 1 day: DON'T MERGE
-- - ALWAYS keep the LATER date (it's correct!)
-- ============================================

-- Step 1: Find duplicates with EXACTLY 1-day DOB difference
DROP TABLE IF EXISTS tmp_fuzzy_base;
DROP TABLE IF EXISTS tmp_fuzzy_groups;
DROP TABLE IF EXISTS tmp_fuzzy_keepers;
DROP TABLE IF EXISTS tmp_fuzzy_dupes;

-- Normalize DOBs and names once
CREATE TEMP TABLE tmp_fuzzy_base AS
SELECT
    member_id,
    LOWER(TRIM(first_name)) AS first_lower,
    LOWER(TRIM(last_name)) AS last_lower,
    NULLIF(TRIM(date_of_birth::text), '') AS dob_text,
    CASE WHEN NULLIF(TRIM(date_of_birth::text), '') IS NOT NULL THEN TRIM(date_of_birth::text)::date END AS dob,
    phone,
    email,
    total_visits,
    lifetime_value
FROM customers_blaze
WHERE first_name IS NOT NULL
  AND last_name IS NOT NULL;

-- Identify name groups where max-min DOB = 1 day
CREATE TEMP TABLE tmp_fuzzy_groups AS
SELECT
    first_lower,
    last_lower,
    MAX(dob) AS keeper_dob,
    MIN(dob) AS min_dob
FROM tmp_fuzzy_base
WHERE dob IS NOT NULL
GROUP BY first_lower, last_lower
HAVING MAX(dob) - MIN(dob) = 1;

-- Select keeper (latest DOB) with best score per group
CREATE TEMP TABLE tmp_fuzzy_keepers AS
SELECT *
FROM (
    SELECT
        b.member_id,
        b.first_lower,
        b.last_lower,
        b.dob,
        b.phone,
        b.email,
        b.total_visits,
        b.lifetime_value,
        ROW_NUMBER() OVER (
            PARTITION BY b.first_lower, b.last_lower
            ORDER BY b.dob DESC,
                     (CASE WHEN b.email IS NOT NULL AND b.email <> '' THEN 500 ELSE 0 END + COALESCE(b.total_visits,0) * 10 + COALESCE(b.lifetime_value,0)) DESC,
                     b.member_id ASC
        ) AS rn
    FROM tmp_fuzzy_base b
    JOIN tmp_fuzzy_groups g
      ON b.first_lower = g.first_lower
     AND b.last_lower = g.last_lower
     AND b.dob = g.keeper_dob
) ranked
WHERE rn = 1;

-- All other records in the group are duplicates (1 day earlier)
CREATE TEMP TABLE tmp_fuzzy_dupes AS
SELECT
    b.member_id AS dupe_id,
    k.member_id AS keeper_id,
    b.first_lower,
    b.last_lower,
    b.dob AS dupe_dob,
    k.dob AS keeper_dob,
    b.phone AS dupe_phone,
    b.email AS dupe_email,
    b.total_visits,
    b.lifetime_value
FROM tmp_fuzzy_base b
JOIN tmp_fuzzy_groups g
  ON b.first_lower = g.first_lower
 AND b.last_lower = g.last_lower
JOIN tmp_fuzzy_keepers k
  ON b.first_lower = k.first_lower
 AND b.last_lower = k.last_lower
WHERE b.member_id <> k.member_id
  AND b.dob IS NOT NULL
  AND g.keeper_dob - b.dob = 1;

SELECT 'FUZZY DUPLICATES (±1 DAY)' as status, COUNT(*) as pairs_to_merge
FROM tmp_fuzzy_dupes;

-- Show details
SELECT 
    'MERGE DETAILS' as info,
    ck.first_name AS keeper_first,
    ck.last_name AS keeper_last,
    cd.first_name AS dupe_first,
    cd.last_name AS dupe_last,
    d.keeper_dob as keep_this_dob,
    d.dupe_dob as delete_this_dob,
    d.keeper_id,
    d.dupe_id
FROM tmp_fuzzy_dupes d
JOIN customers_blaze ck ON ck.member_id = d.keeper_id
JOIN customers_blaze cd ON cd.member_id = d.dupe_id
ORDER BY keeper_first, keeper_last;

-- Step 4: Copy missing data from duplicates to keepers
UPDATE customers_blaze c
SET 
    phone = COALESCE(c.phone, d.dupe_phone),
    email = COALESCE(c.email, d.dupe_email),
    updated_at = NOW()
FROM tmp_fuzzy_dupes d
WHERE c.member_id = d.keeper_id
AND (c.phone IS NULL OR c.phone = '' OR c.email IS NULL OR c.email = '');

SELECT 'Contact info merged' as status;

-- Step 5: Move ALL transactions from duplicates to keepers
UPDATE transactions_blaze t
SET customer_id = m.keeper_id
FROM tmp_fuzzy_dupes m
WHERE t.customer_id = m.dupe_id;

SELECT 'Transactions moved' as status;

-- Step 6: Delete the duplicates (with earlier/wrong DOB)
DELETE FROM customers_blaze c
USING tmp_fuzzy_dupes m
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
FROM (SELECT DISTINCT keeper_id FROM tmp_fuzzy_dupes) m
WHERE c.member_id = m.keeper_id;

SELECT 'Stats recalculated' as status;

-- Step 8: Show results
SELECT 
    'FUZZY MERGE COMPLETE!' as status,
    (SELECT COUNT(*) FROM tmp_fuzzy_dupes) as pairs_merged,
    'All kept LATER dates (correct DOBs)' as result,
    'Run again if more fuzzy duplicates exist' as note;

-- Example: For Stephen Clare
-- Feb 5 record (CORRECT) will be kept
-- Feb 4 record (WRONG) will be merged into it and deleted
-- Result: One record with Feb 5 DOB + all transactions + phone/email

