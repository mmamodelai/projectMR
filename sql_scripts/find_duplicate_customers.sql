-- Find duplicate customers (same name, different records)
-- This happens when Blaze creates multiple member IDs for same person

SELECT 
    LOWER(first_name) as first,
    LOWER(last_name) as last,
    COUNT(*) as record_count,
    STRING_AGG(member_id, ', ') as member_ids,
    STRING_AGG(COALESCE(phone, 'NULL'), ' | ') as phones
FROM customers_blaze
GROUP BY LOWER(first_name), LOWER(last_name)
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 50;

-- Find Stephen Clare specifically
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    last_visited,
    date_joined
FROM customers_blaze
WHERE LOWER(first_name) = 'stephen' 
AND LOWER(last_name) = 'clare'
ORDER BY last_visited DESC NULLS LAST;

