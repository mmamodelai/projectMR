-- =============================================================
-- ASSIGN PHONE (619) 368-3370 TO LUIS ONLY
-- =============================================================

-- Track the target phone (normalize to single format)
WITH target_customers AS (
    SELECT 
        member_id,
        first_name,
        last_name,
        phone
    FROM customers_blaze
    WHERE REGEXP_REPLACE(phone, '[^0-9]', '', 'g') = '6193683370'
)

SELECT 'BEFORE' AS stage,
       COUNT(*) AS customers_sharing_phone,
       STRING_AGG(first_name || ' ' || last_name || ' (' || member_id || ')', '; ') AS names
FROM target_customers;

-- Keep the phone on Luis Bobadilla only (member_id = 5be228de062bd807c2323085)
-- Remove from every other record that shares it

UPDATE customers_blaze
SET phone = NULL,
    updated_at = NOW()
WHERE REGEXP_REPLACE(phone, '[^0-9]', '', 'g') = '6193683370'
  AND member_id <> '5be228de062bd807c2323085';

-- Make sure Luis keeps the canonical phone format
UPDATE customers_blaze
SET phone = '(619) 368-3370',
    updated_at = NOW()
WHERE member_id = '5be228de062bd807c2323085';

-- Show after state
WITH target_customers AS (
    SELECT 
        member_id,
        first_name,
        last_name,
        phone
    FROM customers_blaze
    WHERE REGEXP_REPLACE(phone, '[^0-9]', '', 'g') = '6193683370'
)
SELECT 'AFTER' AS stage,
       COUNT(*) AS customers_sharing_phone,
       STRING_AGG(first_name || ' ' || last_name || ' (' || member_id || ')', '; ') AS names
FROM target_customers;

SELECT 'PHONE ASSIGNED TO LUIS ONLY' AS status;


