-- ============================================
-- SIMPLE MERGE - ONE GROUP AT A TIME
-- ============================================
-- This merges ONE duplicate group per run
-- Keep running until no duplicates remain!
-- ============================================

DO $$
DECLARE
    v_keeper_id TEXT;
    v_keeper_first TEXT;
    v_keeper_last TEXT;
    v_keeper_dob DATE;
    v_dupe_id TEXT;
    v_dupe_phone TEXT;
    v_dupe_email TEXT;
    v_dupe_address TEXT;
    v_transactions_moved INTEGER := 0;
    v_dupes_deleted INTEGER := 0;
    v_found BOOLEAN := FALSE;
BEGIN
    -- Step 1: Find the FIRST duplicate group
    SELECT 
        member_id,
        first_name,
        last_name,
        date_of_birth
    INTO v_keeper_id, v_keeper_first, v_keeper_last, v_keeper_dob
    FROM (
        SELECT 
            member_id,
            first_name,
            last_name,
            date_of_birth,
            phone,
            email,
            total_visits,
            -- Score: phone > email > visits
            (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
            (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
            COALESCE(total_visits, 0) * 10 as score,
            ROW_NUMBER() OVER (
                PARTITION BY 
                    LOWER(TRIM(first_name)),
                    LOWER(TRIM(last_name)),
                    date_of_birth
                ORDER BY 
                    (CASE WHEN phone IS NOT NULL AND phone != '' THEN 1000 ELSE 0 END) +
                    (CASE WHEN email IS NOT NULL AND email != '' THEN 500 ELSE 0 END) +
                    COALESCE(total_visits, 0) * 10
                DESC
            ) as rank,
            COUNT(*) OVER (
                PARTITION BY 
                    LOWER(TRIM(first_name)),
                    LOWER(TRIM(last_name)),
                    date_of_birth
            ) as dup_count
        FROM customers_blaze
        WHERE first_name IS NOT NULL 
        AND last_name IS NOT NULL
    ) ranked
    WHERE dup_count > 1
    AND rank = 1
    LIMIT 1;

    -- Check if we found a duplicate group
    IF v_keeper_id IS NULL THEN
        RAISE NOTICE '====================================';
        RAISE NOTICE 'NO DUPLICATES FOUND!';
        RAISE NOTICE 'Your database is clean!';
        RAISE NOTICE '====================================';
        RETURN;
    END IF;

    v_found := TRUE;
    
    RAISE NOTICE '====================================';
    RAISE NOTICE 'Merging: % %', v_keeper_first, v_keeper_last;
    RAISE NOTICE 'Keeper ID: %', v_keeper_id;
    RAISE NOTICE '====================================';

    -- Step 2: Loop through all duplicates for this person
    FOR v_dupe_id, v_dupe_phone, v_dupe_email, v_dupe_address IN
        SELECT 
            member_id,
            phone,
            email,
            street_address
        FROM customers_blaze
        WHERE LOWER(TRIM(first_name)) = LOWER(TRIM(v_keeper_first))
        AND LOWER(TRIM(last_name)) = LOWER(TRIM(v_keeper_last))
        AND (
            (date_of_birth = v_keeper_dob) 
            OR (date_of_birth IS NULL AND v_keeper_dob IS NULL)
        )
        AND member_id != v_keeper_id
    LOOP
        RAISE NOTICE '  Processing duplicate: %', v_dupe_id;
        
        -- Copy any missing data from duplicate to keeper
        UPDATE customers_blaze
        SET 
            phone = COALESCE(phone, v_dupe_phone),
            email = COALESCE(email, v_dupe_email),
            street_address = COALESCE(street_address, v_dupe_address),
            updated_at = NOW()
        WHERE member_id = v_keeper_id;
        
        -- Move ALL transactions from duplicate to keeper
        UPDATE transactions_blaze
        SET customer_id = v_keeper_id
        WHERE customer_id = v_dupe_id;
        
        GET DIAGNOSTICS v_transactions_moved = ROW_COUNT;
        
        IF v_transactions_moved > 0 THEN
            RAISE NOTICE '    Moved % transactions', v_transactions_moved;
        END IF;
        
        -- Delete the empty duplicate
        DELETE FROM customers_blaze
        WHERE member_id = v_dupe_id;
        
        v_dupes_deleted := v_dupes_deleted + 1;
        RAISE NOTICE '    Deleted duplicate';
    END LOOP;

    -- Step 3: Recalculate stats for keeper
    RAISE NOTICE '  Recalculating stats...';
    
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

    RAISE NOTICE '====================================';
    RAISE NOTICE 'MERGE COMPLETE!';
    RAISE NOTICE 'Deleted % duplicate records', v_dupes_deleted;
    RAISE NOTICE 'RUN AGAIN to merge more duplicates!';
    RAISE NOTICE '====================================';

END $$;

-- Show remaining duplicates
SELECT 
    LOWER(TRIM(first_name)) || ' ' || LOWER(TRIM(last_name)) as customer_name,
    COUNT(*) as still_duplicate
FROM customers_blaze
WHERE first_name IS NOT NULL 
AND last_name IS NOT NULL
GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name)), date_of_birth
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 20;

