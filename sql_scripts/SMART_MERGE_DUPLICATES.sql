-- ============================================
-- SMART DUPLICATE CUSTOMER MERGER
-- ============================================
-- This script finds and merges duplicate customers using:
-- 1. First + Last name match
-- 2. DOB match (if available)
-- 3. Phone match (if available)
-- 
-- Strategy:
-- - Keep the record with MORE data (phone, email, visits)
-- - Copy missing data from duplicate to main record
-- - Mark duplicates for deletion (or delete them)
-- ============================================

-- STEP 1: Find duplicate groups
-- ============================================
SELECT 
    '=== DUPLICATE ANALYSIS ===' as section,
    '' as info;

WITH duplicate_groups AS (
    SELECT 
        LOWER(TRIM(first_name)) as first_lower,
        LOWER(TRIM(last_name)) as last_lower,
        date_of_birth as dob,
        COUNT(*) as record_count,
        ARRAY_AGG(member_id ORDER BY 
            CASE 
                WHEN phone IS NOT NULL THEN 3
                ELSE 0
            END +
            CASE 
                WHEN email IS NOT NULL THEN 2
                ELSE 0
            END +
            COALESCE(total_visits, 0)
            DESC
        ) as member_ids,
        MAX(CASE WHEN phone IS NOT NULL THEN phone END) as best_phone,
        MAX(CASE WHEN email IS NOT NULL THEN email END) as best_email
    FROM customers_blaze
    WHERE first_name IS NOT NULL 
    AND last_name IS NOT NULL
    GROUP BY 
        LOWER(TRIM(first_name)),
        LOWER(TRIM(last_name)),
        date_of_birth
    HAVING COUNT(*) > 1
)
SELECT 
    first_lower || ' ' || last_lower as customer_name,
    dob as date_of_birth,
    record_count as duplicate_count,
    member_ids[1] as keep_this_id,
    member_ids[2:] as merge_these_ids,
    best_phone,
    best_email
FROM duplicate_groups
ORDER BY record_count DESC, customer_name
LIMIT 20;


-- STEP 2: Detailed view of duplicates
-- ============================================
SELECT 
    '=== DETAILED DUPLICATE RECORDS ===' as section,
    '' as info;

WITH ranked_dupes AS (
    SELECT 
        c.*,
        LOWER(TRIM(c.first_name)) || '_' || LOWER(TRIM(c.last_name)) || '_' || COALESCE(c.date_of_birth::TEXT, 'NODOB') as dupe_key,
        ROW_NUMBER() OVER (
            PARTITION BY 
                LOWER(TRIM(c.first_name)),
                LOWER(TRIM(c.last_name)),
                c.date_of_birth
            ORDER BY 
                -- Prioritize: phone > email > visits > date_joined
                CASE WHEN c.phone IS NOT NULL THEN 100 ELSE 0 END +
                CASE WHEN c.email IS NOT NULL THEN 50 ELSE 0 END +
                COALESCE(c.total_visits, 0) * 10 +
                CASE WHEN c.date_joined IS NOT NULL THEN 5 ELSE 0 END
            DESC
        ) as priority_rank,
        COUNT(*) OVER (
            PARTITION BY 
                LOWER(TRIM(c.first_name)),
                LOWER(TRIM(c.last_name)),
                c.date_of_birth
        ) as dupe_count
    FROM customers_blaze c
    WHERE c.first_name IS NOT NULL 
    AND c.last_name IS NOT NULL
)
SELECT 
    first_name,
    last_name,
    date_of_birth,
    phone,
    email,
    total_visits,
    lifetime_value,
    member_id,
    priority_rank,
    CASE 
        WHEN priority_rank = 1 THEN '>>> KEEP <<<'
        ELSE 'MERGE INTO #1'
    END as action
FROM ranked_dupes
WHERE dupe_count > 1
ORDER BY dupe_key, priority_rank
LIMIT 50;


-- STEP 3: MERGE SCRIPT (Run this to actually merge)
-- ============================================
-- This merges data from duplicates into the "best" record
-- ============================================

DO $$
DECLARE
    merge_count INTEGER := 0;
    r RECORD;
    best_record RECORD;
BEGIN
    -- Loop through duplicate groups
    FOR r IN (
        WITH ranked_dupes AS (
            SELECT 
                c.*,
                LOWER(TRIM(c.first_name)) as first_lower,
                LOWER(TRIM(c.last_name)) as last_lower,
                ROW_NUMBER() OVER (
                    PARTITION BY 
                        LOWER(TRIM(c.first_name)),
                        LOWER(TRIM(c.last_name)),
                        c.date_of_birth
                    ORDER BY 
                        CASE WHEN c.phone IS NOT NULL THEN 100 ELSE 0 END +
                        CASE WHEN c.email IS NOT NULL THEN 50 ELSE 0 END +
                        COALESCE(c.total_visits, 0) * 10 +
                        CASE WHEN c.date_joined IS NOT NULL THEN 5 ELSE 0 END
                    DESC
                ) as priority_rank,
                COUNT(*) OVER (
                    PARTITION BY 
                        LOWER(TRIM(c.first_name)),
                        LOWER(TRIM(c.last_name)),
                        c.date_of_birth
                ) as dupe_count
            FROM customers_blaze c
            WHERE c.first_name IS NOT NULL 
            AND c.last_name IS NOT NULL
        )
        SELECT 
            first_lower,
            last_lower,
            date_of_birth,
            member_id,
            phone,
            email,
            priority_rank,
            dupe_count
        FROM ranked_dupes
        WHERE dupe_count > 1
        ORDER BY first_lower, last_lower, date_of_birth, priority_rank
    )
    LOOP
        -- If this is the duplicate (not the keeper)
        IF r.priority_rank > 1 THEN
            -- Get the best record for this group
            SELECT * INTO best_record
            FROM customers_blaze
            WHERE LOWER(TRIM(first_name)) = r.first_lower
            AND LOWER(TRIM(last_name)) = r.last_lower
            AND (date_of_birth = r.date_of_birth OR (date_of_birth IS NULL AND r.date_of_birth IS NULL))
            AND member_id != r.member_id
            ORDER BY 
                CASE WHEN phone IS NOT NULL THEN 100 ELSE 0 END +
                CASE WHEN email IS NOT NULL THEN 50 ELSE 0 END +
                COALESCE(total_visits, 0) * 10 +
                CASE WHEN date_joined IS NOT NULL THEN 5 ELSE 0 END
            DESC
            LIMIT 1;
            
            -- Merge data: Copy non-null fields from duplicate to best record
            UPDATE customers_blaze
            SET 
                phone = COALESCE(phone, r.phone),
                email = COALESCE(email, r.email),
                street_address = COALESCE(street_address, (SELECT street_address FROM customers_blaze WHERE member_id = r.member_id)),
                city = COALESCE(city, (SELECT city FROM customers_blaze WHERE member_id = r.member_id)),
                state = COALESCE(state, (SELECT state FROM customers_blaze WHERE member_id = r.member_id)),
                zip_code = COALESCE(zip_code, (SELECT zip_code FROM customers_blaze WHERE member_id = r.member_id)),
                text_opt_in = COALESCE(text_opt_in, (SELECT text_opt_in FROM customers_blaze WHERE member_id = r.member_id)),
                email_opt_in = COALESCE(email_opt_in, (SELECT email_opt_in FROM customers_blaze WHERE member_id = r.member_id)),
                updated_at = NOW()
            WHERE member_id = best_record.member_id;
            
            merge_count := merge_count + 1;
            
            RAISE NOTICE 'Merged: % % (%) into % - Total: %', 
                r.first_lower, r.last_lower, r.member_id, best_record.member_id, merge_count;
        END IF;
    END LOOP;
    
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'MERGE COMPLETE: % records merged', merge_count;
    RAISE NOTICE '===========================================';
END $$;


-- STEP 4: DELETE DUPLICATES (OPTIONAL - Run separately after verifying merge)
-- ============================================
-- Only delete if duplicate has NO unique data after merge
-- ============================================

/*
DO $$
DECLARE
    delete_count INTEGER := 0;
    r RECORD;
BEGIN
    FOR r IN (
        WITH ranked_dupes AS (
            SELECT 
                c.member_id,
                c.phone,
                c.email,
                c.total_visits,
                ROW_NUMBER() OVER (
                    PARTITION BY 
                        LOWER(TRIM(c.first_name)),
                        LOWER(TRIM(c.last_name)),
                        c.date_of_birth
                    ORDER BY 
                        CASE WHEN c.phone IS NOT NULL THEN 100 ELSE 0 END +
                        CASE WHEN c.email IS NOT NULL THEN 50 ELSE 0 END +
                        COALESCE(c.total_visits, 0) * 10
                    DESC
                ) as priority_rank,
                COUNT(*) OVER (
                    PARTITION BY 
                        LOWER(TRIM(c.first_name)),
                        LOWER(TRIM(c.last_name)),
                        c.date_of_birth
                ) as dupe_count
            FROM customers_blaze c
            WHERE c.first_name IS NOT NULL 
            AND c.last_name IS NOT NULL
        )
        SELECT member_id
        FROM ranked_dupes
        WHERE dupe_count > 1
        AND priority_rank > 1
        AND phone IS NULL  -- Only delete if truly empty
        AND email IS NULL
        AND COALESCE(total_visits, 0) = 0
    )
    LOOP
        DELETE FROM customers_blaze WHERE member_id = r.member_id;
        delete_count := delete_count + 1;
    END LOOP;
    
    RAISE NOTICE '===========================================';
    RAISE NOTICE 'DELETED: % empty duplicate records', delete_count;
    RAISE NOTICE '===========================================';
END $$;
*/


-- STEP 5: Verify results
-- ============================================
SELECT 
    '=== REMAINING DUPLICATES AFTER MERGE ===' as section,
    '' as info;

SELECT 
    LOWER(TRIM(first_name)) || ' ' || LOWER(TRIM(last_name)) as customer_name,
    date_of_birth,
    COUNT(*) as still_duplicate
FROM customers_blaze
WHERE first_name IS NOT NULL 
AND last_name IS NOT NULL
GROUP BY 
    LOWER(TRIM(first_name)),
    LOWER(TRIM(last_name)),
    date_of_birth
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 10;

