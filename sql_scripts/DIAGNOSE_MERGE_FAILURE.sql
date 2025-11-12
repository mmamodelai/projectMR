-- ============================================
-- DIAGNOSE: Why didn't the merge work?
-- ============================================

-- Check 1: Are there still 30 medgo records?
SELECT 
    '1. CURRENT STATE' as check_type,
    COUNT(*) as total_records
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- Check 2: Show all medgo records
SELECT 
    '2. ALL MEDGO RECORDS' as check_type,
    member_id,
    phone,
    email,
    total_visits
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots'
ORDER BY total_visits DESC NULLS LAST;

-- Check 3: Do they all have the SAME first_name/last_name exactly?
SELECT 
    '3. NAME VARIATIONS' as check_type,
    first_name,
    last_name,
    LENGTH(first_name) as first_len,
    LENGTH(last_name) as last_len,
    COUNT(*) as records_with_this_exact_spelling
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots'
GROUP BY first_name, last_name;

-- Check 4: What about date_of_birth? Are they all the same?
SELECT 
    '4. DATE OF BIRTH VARIATIONS' as check_type,
    date_of_birth,
    COUNT(*) as records_with_this_dob
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots'
GROUP BY date_of_birth;

-- Check 5: Can we actually DELETE one?
-- Let's try deleting ONE record manually
WITH to_delete AS (
    SELECT member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NULL OR phone = '' THEN 0 ELSE 1 END),
        (CASE WHEN email IS NULL OR email = '' THEN 0 ELSE 1 END),
        COALESCE(total_visits, 0)
    ASC  -- Pick the WORST record
    LIMIT 1
)
SELECT 
    '5. RECORD TO DELETE' as check_type,
    c.member_id,
    c.phone,
    c.email,
    c.total_visits,
    'Will attempt to delete this one' as action
FROM customers_blaze c
JOIN to_delete d ON c.member_id = d.member_id;

-- Actually try to delete it
WITH to_delete AS (
    SELECT member_id
    FROM customers_blaze
    WHERE LOWER(TRIM(first_name)) = 'medgo'
    AND LOWER(TRIM(last_name)) = 'drots'
    ORDER BY 
        (CASE WHEN phone IS NULL OR phone = '' THEN 0 ELSE 1 END),
        (CASE WHEN email IS NULL OR email = '' THEN 0 ELSE 1 END),
        COALESCE(total_visits, 0)
    ASC
    LIMIT 1
)
DELETE FROM customers_blaze
WHERE member_id IN (SELECT member_id FROM to_delete);

-- Check 6: Did it delete?
SELECT 
    '6. AFTER DELETE ATTEMPT' as check_type,
    COUNT(*) as total_records_now
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- If it's now 29, the DELETE worked!
-- If it's still 30, something is preventing deletion

