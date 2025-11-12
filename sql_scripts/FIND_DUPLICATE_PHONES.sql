-- ==================================================================
-- FIND DUPLICATE PHONE NUMBERS IN CUSTOMERS_BLAZE
-- ==================================================================

SELECT 
    phone,
    COUNT(*) as customer_count
FROM customers_blaze
WHERE phone IS NOT NULL
  AND phone != ''
GROUP BY phone
HAVING COUNT(*) > 1
ORDER BY customer_count DESC, phone;

-- Top 50 duplicates
SELECT 
    phone,
    COUNT(*) as customer_count,
    STRING_AGG(first_name || ' ' || last_name, '; ') as customers
FROM customers_blaze
WHERE phone IS NOT NULL
  AND phone != ''
GROUP BY phone
HAVING COUNT(*) > 1
ORDER BY customer_count DESC, phone
LIMIT 50;
