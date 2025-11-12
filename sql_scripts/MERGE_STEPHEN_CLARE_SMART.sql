-- ============================================
-- SMART MERGE FOR STEPHEN CLARE
-- ============================================
-- Keep the record with transactions (better DOB)
-- Copy phone from the other record
-- ============================================

-- Step 1: Show both records
SELECT 
    'BEFORE MERGE' as status,
    member_id,
    first_name,
    last_name,
    date_of_birth,
    phone,
    email,
    total_visits,
    lifetime_value
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen'
AND LOWER(last_name) = 'clare';

-- Step 2: Copy phone from "wrong DOB" record to "correct DOB" record
-- The record with transactions (683cea...) gets the phone from the other one
UPDATE customers_blaze
SET 
    phone = '+16199773020',
    email = COALESCE(email, 'stephenclare@gmail.com'),
    updated_at = NOW()
WHERE member_id = '683cea4e022c82ba434de1df';  -- The one with Feb 5 DOB and transactions

SELECT 'Phone copied to correct record' as status;

-- Step 3: Move any transactions from "wrong DOB" record (shouldn't be any, but just in case)
UPDATE transactions_blaze
SET customer_id = '683cea4e022c82ba434de1df'
WHERE customer_id = '61394100d18e30747f2b67f7';

SELECT 'Transactions moved (if any)' as status;

-- Step 4: Delete the "wrong DOB" duplicate
DELETE FROM customers_blaze
WHERE member_id = '61394100d18e30747f2b67f7';  -- The one with Feb 4 DOB (wrong)

SELECT 'Duplicate deleted' as status;

-- Step 5: Recalculate stats for the keeper
UPDATE customers_blaze
SET
    total_visits = (
        SELECT COUNT(*)
        FROM transactions_blaze t
        WHERE t.customer_id = '683cea4e022c82ba434de1df'
        AND t.blaze_status = 'Completed'
    ),
    lifetime_value = (
        SELECT COALESCE(SUM(total_amount), 0)
        FROM transactions_blaze t
        WHERE t.customer_id = '683cea4e022c82ba434de1df'
        AND t.blaze_status = 'Completed'
    ),
    last_visited = (
        SELECT MAX(date::DATE)
        FROM transactions_blaze t
        WHERE t.customer_id = '683cea4e022c82ba434de1df'
        AND t.blaze_status = 'Completed'
    ),
    vip_status = CASE
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = '683cea4e022c82ba434de1df'
            AND t.blaze_status = 'Completed'
        ) >= 16 THEN 'VIP'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = '683cea4e022c82ba434de1df'
            AND t.blaze_status = 'Completed'
        ) BETWEEN 11 AND 15 THEN 'Regular2'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = '683cea4e022c82ba434de1df'
            AND t.blaze_status = 'Completed'
        ) BETWEEN 5 AND 10 THEN 'Regular1'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = '683cea4e022c82ba434de1df'
            AND t.blaze_status = 'Completed'
        ) BETWEEN 2 AND 4 THEN 'Casual'
        WHEN (
            SELECT COUNT(*)
            FROM transactions_blaze t
            WHERE t.customer_id = '683cea4e022c82ba434de1df'
            AND t.blaze_status = 'Completed'
        ) = 1 THEN 'First'
        ELSE 'New'
    END,
    updated_at = NOW()
WHERE member_id = '683cea4e022c82ba434de1df';

SELECT 'Stats recalculated' as status;

-- Step 6: Show final result
SELECT 
    'AFTER MERGE' as status,
    member_id,
    first_name,
    last_name,
    date_of_birth,
    phone,
    email,
    total_visits,
    lifetime_value,
    vip_status
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen'
AND LOWER(last_name) = 'clare';

-- Result should be:
-- 1 record: STEPHEN CLARE
-- DOB: 1983-02-05 (CORRECT!)
-- Phone: +16199773020 (ADDED!)
-- Email: stephenclare@gmail.com (ADDED!)
-- Visits: 3
-- Lifetime: $148.80

