-- ============================================
-- BATCH DUPLICATE MERGER (For all customers)
-- ============================================
-- This processes duplicates in manageable batches
-- Run multiple times if needed
-- ============================================

-- STEP 1: Create a temp table with duplicate analysis
-- ============================================
CREATE TEMP TABLE duplicate_analysis AS
WITH ranked_customers AS (
    SELECT 
        member_id,
        LOWER(TRIM(first_name)) as first_lower,
        LOWER(TRIM(last_name)) as last_lower,
        date_of_birth,
        phone,
        email,
        total_visits,
        lifetime_value,
        -- Score each record
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 100 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 50 ELSE 0 END) +
        COALESCE(total_visits, 0) * 5 as score,
        -- Rank within duplicate group
        ROW_NUMBER() OVER (
            PARTITION BY 
                LOWER(TRIM(first_name)),
                LOWER(TRIM(last_name)),
                date_of_birth
            ORDER BY 
                (CASE WHEN phone IS NOT NULL AND phone != '' THEN 100 ELSE 0 END) +
                (CASE WHEN email IS NOT NULL AND email != '' THEN 50 ELSE 0 END) +
                COALESCE(total_visits, 0) * 5
            DESC
        ) as rank_in_group,
        -- Count duplicates
        COUNT(*) OVER (
            PARTITION BY 
                LOWER(TRIM(first_name)),
                LOWER(TRIM(last_name)),
                date_of_birth
        ) as group_size
    FROM customers_blaze
    WHERE first_name IS NOT NULL 
    AND last_name IS NOT NULL
)
SELECT *
FROM ranked_customers
WHERE group_size > 1;

-- STEP 2: See the analysis
-- ============================================
SELECT 
    first_lower || ' ' || last_lower as customer_name,
    date_of_birth,
    phone,
    email,
    total_visits,
    score,
    CASE 
        WHEN rank_in_group = 1 THEN '>>> KEEP <<<'
        ELSE 'Merge to #1'
    END as action,
    member_id
FROM duplicate_analysis
ORDER BY first_lower, last_lower, rank_in_group
LIMIT 100;

-- STEP 3: Merge data (process 50 at a time)
-- ============================================
DO $$
DECLARE
    v_keeper_id TEXT;
    v_dupe_id TEXT;
    v_dupe_phone TEXT;
    v_dupe_email TEXT;
    v_count INTEGER := 0;
    v_max_count INTEGER := 50;  -- Process only 50 at a time
    r RECORD;
BEGIN
    FOR r IN (
        SELECT 
            d1.member_id as keeper_id,
            d2.member_id as dupe_id,
            d2.phone as dupe_phone,
            d2.email as dupe_email,
            d1.first_lower,
            d1.last_lower
        FROM duplicate_analysis d1
        JOIN duplicate_analysis d2 
            ON d1.first_lower = d2.first_lower 
            AND d1.last_lower = d2.last_lower
            AND (d1.date_of_birth = d2.date_of_birth OR (d1.date_of_birth IS NULL AND d2.date_of_birth IS NULL))
        WHERE d1.rank_in_group = 1  -- Keeper
        AND d2.rank_in_group > 1     -- Duplicate
        LIMIT 50
    )
    LOOP
        -- Copy missing data from duplicate to keeper
        UPDATE customers_blaze
        SET 
            phone = COALESCE(phone, r.dupe_phone),
            email = COALESCE(email, r.dupe_email),
            updated_at = NOW()
        WHERE member_id = r.keeper_id
        AND (phone IS NULL OR phone = '');
        
        v_count := v_count + 1;
        
        RAISE NOTICE 'Merged: % % (%) -> (%)', 
            r.first_lower, r.last_lower, r.dupe_id, r.keeper_id;
        
        -- Stop after max_count
        IF v_count >= v_max_count THEN
            EXIT;
        END IF;
    END LOOP;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'Processed: % duplicate records', v_count;
    RAISE NOTICE 'Run again if there are more duplicates';
    RAISE NOTICE '========================================';
END $$;

-- STEP 4: Optional - Delete empty duplicates
-- ============================================
-- Only run after verifying merge worked
/*
DELETE FROM customers_blaze
WHERE member_id IN (
    SELECT member_id
    FROM duplicate_analysis
    WHERE rank_in_group > 1
    AND (phone IS NULL OR phone = '')
    AND (email IS NULL OR email = '')
    AND COALESCE(total_visits, 0) = 0
    LIMIT 50
);
*/

-- STEP 5: Check remaining duplicates
-- ============================================
SELECT 
    LOWER(TRIM(first_name)) || ' ' || LOWER(TRIM(last_name)) as customer_name,
    COUNT(*) as still_duplicate
FROM customers_blaze
WHERE first_name IS NOT NULL 
AND last_name IS NOT NULL
GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name))
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 20;

