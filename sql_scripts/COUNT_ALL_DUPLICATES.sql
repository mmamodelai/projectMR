-- How bad is the duplicate problem?

-- Total customers
SELECT 'Total customer records' as metric, COUNT(*) as count
FROM customers_blaze
UNION ALL
-- Unique customers (by name)
SELECT 'Unique customers (by name)', COUNT(DISTINCT LOWER(TRIM(first_name)) || '_' || LOWER(TRIM(last_name)))
FROM customers_blaze
WHERE first_name IS NOT NULL AND last_name IS NOT NULL
UNION ALL
-- Duplicate groups
SELECT 'Duplicate groups', COUNT(*)
FROM (
    SELECT LOWER(TRIM(first_name)), LOWER(TRIM(last_name))
    FROM customers_blaze
    WHERE first_name IS NOT NULL AND last_name IS NOT NULL
    GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name))
    HAVING COUNT(*) > 1
) d
UNION ALL
-- Total duplicate records (extras that need merging)
SELECT 'Total duplicate records to merge', COUNT(*) - COUNT(DISTINCT LOWER(TRIM(first_name)) || '_' || LOWER(TRIM(last_name)))
FROM customers_blaze
WHERE first_name IS NOT NULL AND last_name IS NOT NULL;

-- Top 20 worst offenders
SELECT 
    LOWER(TRIM(first_name)) || ' ' || LOWER(TRIM(last_name)) as customer_name,
    COUNT(*) as duplicate_count,
    STRING_AGG(member_id, ', ') as all_member_ids
FROM customers_blaze
WHERE first_name IS NOT NULL AND last_name IS NOT NULL
GROUP BY LOWER(TRIM(first_name)), LOWER(TRIM(last_name))
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 20;

