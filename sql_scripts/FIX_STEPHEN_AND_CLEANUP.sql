-- ============================================
-- FIX STEPHEN CLARE + CLEANUP NOISE
-- ============================================
-- This script:
-- 1. Merges Stephen Clare (Feb 4 -> Feb 5)
-- 2. Deletes 0-transaction noise customers
-- 3. Cleans up obvious fake phone numbers
-- ============================================

-- ===========================================
-- PART 1: FIX STEPHEN CLARE
-- ===========================================

-- Show before
SELECT 'STEPHEN CLARE - BEFORE' as status;
SELECT member_id, first_name, last_name, phone, email, date_of_birth, total_visits
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen'
AND LOWER(last_name) = 'clare';

-- Step 1: Copy phone/email from wrong DOB record to correct DOB record
UPDATE customers_blaze
SET 
    phone = '+16199773020',
    email = 'stephenclare@gmail.com',
    updated_at = NOW()
WHERE member_id = '683cea4e022c82ba434de1df'  -- Feb 5 (CORRECT DOB) record
AND (phone IS NULL OR phone = '');

SELECT 'Phone/email copied to Feb 5 record' as status;

-- Step 2: Move any transactions from wrong DOB record to correct one
UPDATE transactions_blaze
SET customer_id = '683cea4e022c82ba434de1df'
WHERE customer_id = '61394100d18e30747f2b67f7';  -- Feb 4 (WRONG DOB) record

SELECT 'Transactions moved (if any)' as status;

-- Step 3: Delete the wrong DOB record
DELETE FROM customers_blaze
WHERE member_id = '61394100d18e30747f2b67f7';  -- Feb 4 (WRONG DOB)

SELECT 'Wrong DOB record deleted' as status;

-- Step 4: Recalculate stats for Stephen
UPDATE customers_blaze
SET
    total_visits = (
        SELECT COUNT(*)
        FROM transactions_blaze
        WHERE customer_id = '683cea4e022c82ba434de1df'
        AND blaze_status = 'Completed'
    ),
    lifetime_value = (
        SELECT COALESCE(SUM(total_amount), 0)
        FROM transactions_blaze
        WHERE customer_id = '683cea4e022c82ba434de1df'
        AND blaze_status = 'Completed'
    ),
    vip_status = CASE
        WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = '683cea4e022c82ba434de1df' AND blaze_status = 'Completed') >= 16 THEN 'VIP'
        WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = '683cea4e022c82ba434de1df' AND blaze_status = 'Completed') BETWEEN 11 AND 15 THEN 'Regular2'
        WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = '683cea4e022c82ba434de1df' AND blaze_status = 'Completed') BETWEEN 5 AND 10 THEN 'Regular1'
        WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = '683cea4e022c82ba434de1df' AND blaze_status = 'Completed') BETWEEN 2 AND 4 THEN 'Casual'
        WHEN (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = '683cea4e022c82ba434de1df' AND blaze_status = 'Completed') = 1 THEN 'First'
        ELSE 'New'
    END
WHERE member_id = '683cea4e022c82ba434de1df';

SELECT 'Stephen stats recalculated' as status;

-- Show after
SELECT 'STEPHEN CLARE - AFTER' as status;
SELECT member_id, first_name, last_name, phone, email, date_of_birth, total_visits, lifetime_value
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen'
AND LOWER(last_name) = 'clare';

-- ===========================================
-- PART 2: DELETE 0-TRANSACTION NOISE
-- ===========================================

-- Show how many 0-transaction customers exist
SELECT 
    '0-TRANSACTION CUSTOMERS' as status,
    COUNT(*) as total_noise
FROM customers_blaze
WHERE (total_visits IS NULL OR total_visits = 0)
AND NOT EXISTS (
    SELECT 1 FROM transactions_blaze 
    WHERE customer_id = customers_blaze.member_id
);

-- Delete them (batch of 1000 to avoid timeout)
DELETE FROM customers_blaze
WHERE (total_visits IS NULL OR total_visits = 0)
AND NOT EXISTS (
    SELECT 1 FROM transactions_blaze 
    WHERE customer_id = customers_blaze.member_id
)
AND member_id IN (
    SELECT member_id 
    FROM customers_blaze
    WHERE (total_visits IS NULL OR total_visits = 0)
    LIMIT 1000
);

SELECT '0-transaction customers deleted (first 1000)' as status;

-- ===========================================
-- PART 3: CLEAN FAKE PHONE NUMBERS
-- ===========================================

-- Show fake phone number counts
SELECT 
    'FAKE PHONE NUMBERS' as status,
    phone,
    COUNT(*) as customer_count
FROM customers_blaze
WHERE phone IN (
    '(000) 000-0000',
    '(555) 555-5555',
    '+1',
    '(999) 999-9999',
    '(111) 111-1111',
    '(222) 222-2222',
    '(123) 456-7890',
    '(323) 456-7890'
)
GROUP BY phone
ORDER BY COUNT(*) DESC;

-- Set fake phone numbers to NULL (keep the customer record, just remove fake phone)
UPDATE customers_blaze
SET phone = NULL
WHERE phone IN (
    '(000) 000-0000',
    '(555) 555-5555',
    '+1',
    '(999) 999-9999',
    '(111) 111-1111',
    '(222) 222-2222',
    '(123) 456-7890',
    '(323) 456-7890'
);

SELECT 'Fake phone numbers cleared' as status;

-- ===========================================
-- FINAL SUMMARY
-- ===========================================

SELECT 'CLEANUP COMPLETE!' as status;

SELECT 
    'SUMMARY' as info,
    (SELECT COUNT(*) FROM customers_blaze WHERE LOWER(first_name) = 'stephen' AND LOWER(last_name) = 'clare') as stephen_clare_records,
    (SELECT COUNT(*) FROM customers_blaze WHERE total_visits = 0 OR total_visits IS NULL) as zero_visit_customers,
    (SELECT COUNT(*) FROM customers_blaze WHERE phone IS NULL OR phone = '') as customers_without_phone;

-- Run HYBRID_SOLUTION_step1_backfill.sql next to recalculate ALL stats!

