-- ============================================
-- FULL DUPLICATE MERGE - Smoosh Everything
-- ============================================
-- This merges EVERYTHING from duplicates into main account:
-- - Phone, email, address
-- - All transactions
-- - Recalculates visits & lifetime value
-- - Deletes empty duplicates
-- 
-- Processes 20 at a time to avoid timeout
-- ============================================

-- STEP 1: Find keeper vs duplicates
-- ============================================
CREATE TEMP TABLE IF NOT EXISTS merge_plan AS
WITH ranked_customers AS (
    SELECT 
        member_id,
        LOWER(TRIM(first_name)) as first_lower,
        LOWER(TRIM(last_name)) as last_lower,
        date_of_birth,
        phone,
        email,
        street_address,
        city,
        state,
        zip_code,
        text_opt_in,
        email_opt_in,
        total_visits,
        lifetime_value,
        -- Score: prioritize phone > email > visits > address
        (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
        (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
        COALESCE(total_visits, 0) * 10 +
        (CASE WHEN street_address IS NOT NULL THEN 50 ELSE 0 END) as score,
        ROW_NUMBER() OVER (
            PARTITION BY 
                LOWER(TRIM(first_name)),
                LOWER(TRIM(last_name)),
                date_of_birth
            ORDER BY 
                (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
                (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
                COALESCE(total_visits, 0) * 10 +
                (CASE WHEN street_address IS NOT NULL THEN 50 ELSE 0 END)
            DESC
        ) as rank_in_group,
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

-- STEP 2: Preview the merge plan
-- ============================================
SELECT 
    first_lower || ' ' || last_lower as customer_name,
    CASE 
        WHEN rank_in_group = 1 THEN '>>> KEEPER <<<'
        ELSE 'Will merge into keeper'
    END as status,
    member_id,
    phone,
    email,
    total_visits,
    lifetime_value,
    score
FROM merge_plan
ORDER BY first_lower, last_lower, rank_in_group
LIMIT 100;

-- STEP 3: THE FULL MERGE (processes 20 duplicate groups)
-- ============================================
DO $$
DECLARE
    v_keeper_id TEXT;
    v_dupe_id TEXT;
    v_trans_count INTEGER;
    v_group_count INTEGER := 0;
    v_max_groups INTEGER := 20;  -- Process 20 duplicate groups at a time
    v_customer_name TEXT;
    r_keeper RECORD;
    r_dupe RECORD;
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE 'STARTING FULL MERGE';
    RAISE NOTICE '========================================';
    
    -- Loop through duplicate groups
    FOR r_keeper IN (
        SELECT DISTINCT 
            first_lower,
            last_lower,
            date_of_birth,
            member_id as keeper_id
        FROM merge_plan
        WHERE rank_in_group = 1
        LIMIT 20
    )
    LOOP
        v_keeper_id := r_keeper.keeper_id;
        v_customer_name := r_keeper.first_lower || ' ' || r_keeper.last_lower;
        
        RAISE NOTICE '';
        RAISE NOTICE 'Processing: % (keeper: %)', v_customer_name, v_keeper_id;
        
        -- Loop through all duplicates for this customer
        FOR r_dupe IN (
            SELECT member_id, phone, email, street_address, city, state, zip_code, text_opt_in, email_opt_in
            FROM merge_plan
            WHERE first_lower = r_keeper.first_lower
            AND last_lower = r_keeper.last_lower
            AND (date_of_birth = r_keeper.date_of_birth OR (date_of_birth IS NULL AND r_keeper.date_of_birth IS NULL))
            AND rank_in_group > 1
        )
        LOOP
            v_dupe_id := r_dupe.member_id;
            
            -- 1. Copy missing data from duplicate to keeper
            UPDATE customers_blaze
            SET 
                phone = COALESCE(phone, r_dupe.phone),
                email = COALESCE(email, r_dupe.email),
                street_address = COALESCE(street_address, r_dupe.street_address),
                city = COALESCE(city, r_dupe.city),
                state = COALESCE(state, r_dupe.state),
                zip_code = COALESCE(zip_code, r_dupe.zip_code),
                text_opt_in = COALESCE(text_opt_in, r_dupe.text_opt_in),
                email_opt_in = COALESCE(email_opt_in, r_dupe.email_opt_in),
                updated_at = NOW()
            WHERE member_id = v_keeper_id;
            
            -- 2. Move ALL transactions from duplicate to keeper
            UPDATE transactions_blaze
            SET customer_id = v_keeper_id,
                updated_at = NOW()
            WHERE customer_id = v_dupe_id;
            
            GET DIAGNOSTICS v_trans_count = ROW_COUNT;
            
            IF v_trans_count > 0 THEN
                RAISE NOTICE '  Moved % transactions: % -> %', v_trans_count, v_dupe_id, v_keeper_id;
            END IF;
            
            -- 3. Delete the now-empty duplicate
            DELETE FROM customers_blaze WHERE member_id = v_dupe_id;
            RAISE NOTICE '  Deleted duplicate: %', v_dupe_id;
        END LOOP;
        
        -- 4. Recalculate visits & lifetime for keeper
        UPDATE customers_blaze c
        SET 
            total_visits = (
                SELECT COUNT(*)
                FROM transactions_blaze t
                WHERE t.customer_id = v_keeper_id
                AND t.blaze_status = 'Completed'
            ),
            lifetime_value = (
                SELECT COALESCE(SUM(total_amount), 0)
                FROM transactions_blaze t
                WHERE t.customer_id = v_keeper_id
                AND t.blaze_status = 'Completed'
            ),
            last_visited = (
                SELECT MAX(date::DATE)
                FROM transactions_blaze t
                WHERE t.customer_id = v_keeper_id
                AND t.blaze_status = 'Completed'
            ),
            vip_status = CASE
                WHEN (
                    SELECT COUNT(*)
                    FROM transactions_blaze t
                    WHERE t.customer_id = v_keeper_id
                    AND t.blaze_status = 'Completed'
                ) >= 16 THEN 'VIP'
                WHEN (
                    SELECT COUNT(*)
                    FROM transactions_blaze t
                    WHERE t.customer_id = v_keeper_id
                    AND t.blaze_status = 'Completed'
                ) BETWEEN 11 AND 15 THEN 'Regular2'
                WHEN (
                    SELECT COUNT(*)
                    FROM transactions_blaze t
                    WHERE t.customer_id = v_keeper_id
                    AND t.blaze_status = 'Completed'
                ) BETWEEN 5 AND 10 THEN 'Regular1'
                WHEN (
                    SELECT COUNT(*)
                    FROM transactions_blaze t
                    WHERE t.customer_id = v_keeper_id
                    AND t.blaze_status = 'Completed'
                ) BETWEEN 2 AND 4 THEN 'Casual'
                WHEN (
                    SELECT COUNT(*)
                    FROM transactions_blaze t
                    WHERE t.customer_id = v_keeper_id
                    AND t.blaze_status = 'Completed'
                ) = 1 THEN 'First'
                ELSE 'New'
            END,
            updated_at = NOW()
        WHERE member_id = v_keeper_id;
        
        RAISE NOTICE '  Recalculated stats for keeper';
        
        v_group_count := v_group_count + 1;
        
        -- Stop after processing max groups
        IF v_group_count >= v_max_groups THEN
            EXIT;
        END IF;
    END LOOP;
    
    RAISE NOTICE '';
    RAISE NOTICE '========================================';
    RAISE NOTICE 'MERGE COMPLETE!';
    RAISE NOTICE 'Processed: % customer groups', v_group_count;
    RAISE NOTICE 'Run again if more duplicates remain';
    RAISE NOTICE '========================================';
END $$;

-- STEP 4: Check what's left
-- ============================================
SELECT 
    '=== REMAINING DUPLICATES ===' as section;

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

-- Clean up temp table
DROP TABLE IF EXISTS merge_plan;

