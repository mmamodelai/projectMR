-- Update customers.last_visited from their most recent transaction
-- This fixes the "stuck on Nov 5" issue

-- ============================================================================
-- CHECK FIRST: How many customers are out of date?
-- ============================================================================
SELECT 
    'Customers out of date' as status,
    COUNT(*) as count
FROM customers_blaze c
WHERE EXISTS (
    SELECT 1 
    FROM transactions_blaze t 
    WHERE t.customer_id = c.member_id 
    AND t.date::date > c.last_visited::date
);

-- ============================================================================
-- UPDATE: Set last_visited to their most recent transaction date
-- ============================================================================
UPDATE customers_blaze c
SET last_visited = (
    SELECT MAX(t.date)::date
    FROM transactions_blaze t
    WHERE t.customer_id = c.member_id
)
WHERE EXISTS (
    SELECT 1 
    FROM transactions_blaze t 
    WHERE t.customer_id = c.member_id
);

-- ============================================================================
-- VERIFY: Check most recent customers now
-- ============================================================================
SELECT 
    name,
    last_visited
FROM customers_blaze
WHERE last_visited IS NOT NULL
ORDER BY last_visited DESC
LIMIT 10;

-- ============================================================================
-- This should now show Nov 9, 2025 customers at the top!
-- ============================================================================

