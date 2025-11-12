-- Check Customer Filter Statistics
-- Run this to understand how many customers pass each filter

-- Overall customer counts
SELECT 
    COUNT(*) as total_customers,
    COUNT(CASE WHEN email IS NOT NULL AND email != '' THEN 1 END) as with_email,
    COUNT(CASE WHEN phone IS NOT NULL AND phone != '' THEN 1 END) as with_phone,
    COUNT(CASE WHEN last_visited IS NOT NULL THEN 1 END) as with_last_visit,
    COUNT(CASE WHEN last_visited >= (CURRENT_DATE - INTERVAL '180 days') THEN 1 END) as visited_last_180_days,
    COUNT(CASE WHEN last_visited >= (CURRENT_DATE - INTERVAL '365 days') THEN 1 END) as visited_last_365_days
FROM customers_blaze;

-- Filter combination stats
SELECT 
    'Email + Phone + <180 days' as filter_combo,
    COUNT(*) as customer_count
FROM customers_blaze
WHERE email IS NOT NULL AND email != ''
AND phone IS NOT NULL AND phone != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '180 days')

UNION ALL

SELECT 
    'Email + Phone + <365 days',
    COUNT(*)
FROM customers_blaze
WHERE email IS NOT NULL AND email != ''
AND phone IS NOT NULL AND phone != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '365 days')

UNION ALL

SELECT 
    'Phone ONLY + <180 days',
    COUNT(*)
FROM customers_blaze
WHERE phone IS NOT NULL AND phone != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '180 days')

UNION ALL

SELECT 
    'Phone ONLY + <365 days',
    COUNT(*)
FROM customers_blaze
WHERE phone IS NOT NULL AND phone != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '365 days')

UNION ALL

SELECT 
    'Email ONLY + <180 days',
    COUNT(*)
FROM customers_blaze
WHERE email IS NOT NULL AND email != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '180 days')

UNION ALL

SELECT 
    'Email ONLY + <365 days',
    COUNT(*)
FROM customers_blaze
WHERE email IS NOT NULL AND email != ''
AND last_visited >= (CURRENT_DATE - INTERVAL '365 days');

-- Search for Aaron Campos specifically
SELECT 
    'Aaron Campos matches' as search_type,
    COUNT(*) as customer_count
FROM customers_blaze
WHERE (first_name ILIKE '%aaron%' AND last_name ILIKE '%campos%')
OR (first_name ILIKE '%aaron campos%')
OR (last_name ILIKE '%aaron campos%');

-- Aaron Campos filter breakdown
SELECT 
    CASE 
        WHEN email IS NOT NULL AND email != '' THEN 'Has Email'
        ELSE 'NO Email'
    END as email_status,
    CASE 
        WHEN phone IS NOT NULL AND phone != '' THEN 'Has Phone'
        ELSE 'NO Phone'
    END as phone_status,
    CASE 
        WHEN last_visited IS NULL THEN 'Never Visited (NULL)'
        WHEN last_visited < (CURRENT_DATE - INTERVAL '365 days') THEN '>365 days ago'
        WHEN last_visited < (CURRENT_DATE - INTERVAL '180 days') THEN '180-365 days ago'
        ELSE '<180 days ago'
    END as visit_status,
    COUNT(*) as count
FROM customers_blaze
WHERE (first_name ILIKE '%aaron%' AND last_name ILIKE '%campos%')
GROUP BY email_status, phone_status, visit_status
ORDER BY count DESC;

