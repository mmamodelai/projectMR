-- ==========================================================
-- CLEAR OBVIOUS FAKE PHONE NUMBERS
-- ==========================================================

-- List how many fake numbers currently exist
SELECT 
    phone,
    COUNT(*) AS customers
FROM customers_blaze
WHERE phone IN (
    '(000) 000-0000',
    '(555) 555-5555',
    '+',
    '+1',
    '(111) 111-1111',
    '(222) 222-2222',
    '(333) 333-3333',
    '(444) 444-4444',
    '(999) 999-9999',
    '(123) 456-7890',
    '(323) 456-7890'
)
GROUP BY phone
ORDER BY customers DESC, phone;

-- Clear them (set to NULL)
UPDATE customers_blaze
SET phone = NULL,
    updated_at = NOW()
WHERE phone IN (
    '(000) 000-0000',
    '(555) 555-5555',
    '+',
    '+1',
    '(111) 111-1111',
    '(222) 222-2222',
    '(333) 333-3333',
    '(444) 444-4444',
    '(999) 999-9999',
    '(123) 456-7890',
    '(323) 456-7890'
);

SELECT 'FAKE PHONE NUMBERS CLEARED' AS status;

-- Normalize remaining phone numbers to digits only (1234567890)
UPDATE customers_blaze
SET phone = CASE
        WHEN digits LIKE '1%' AND LENGTH(digits) = 11 THEN SUBSTRING(digits FROM 2)
        ELSE digits
    END,
    updated_at = NOW()
FROM (
    SELECT member_id, REGEXP_REPLACE(phone, '[^0-9]', '', 'g') AS digits
    FROM customers_blaze
    WHERE phone IS NOT NULL AND phone <> ''
) t
WHERE customers_blaze.member_id = t.member_id
  AND digits <> ''
  AND phone <> CASE
        WHEN digits LIKE '1%' AND LENGTH(digits) = 11 THEN SUBSTRING(digits FROM 2)
        ELSE digits
    END;

SELECT 'PHONE NUMBERS NORMALIZED TO DIGITS' AS status;
