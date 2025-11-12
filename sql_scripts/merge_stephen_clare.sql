-- Merge Stephen Clare records
-- Keep the one with phone number, delete the duplicate

-- First, let's see what we have
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    last_visited
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen' 
AND LOWER(last_name) = 'clare';

-- Option 1: Update the one WITHOUT phone to have the phone number
-- (If they're the same person and one just has more complete data)

UPDATE customers_blaze
SET phone = '+16199773020',
    updated_at = NOW()
WHERE member_id = '683cea4e022c82ba434de1df'  -- The one without phone
AND phone IS NULL;

-- Option 2: Delete the duplicate WITHOUT phone
-- (Only do this if Option 1 doesn't make sense)

/*
DELETE FROM customers_blaze
WHERE member_id = '683cea4e022c82ba434de1df'  -- The one without phone
AND phone IS NULL;
*/

-- Verify the fix
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen' 
AND LOWER(last_name) = 'clare';

