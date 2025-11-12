-- ============================================
-- HYBRID SOLUTION - STEP 1: BACKFILL
-- ============================================
-- 
-- PURPOSE: Fill total_visits and lifetime_value ONCE
--          Then trigger keeps them updated automatically
--
-- RUN TIME: ~10-15 minutes for 131K customers
--
-- SAFETY: Only updates calculated fields, doesn't touch contact info
--
-- ============================================

-- Backfill visits and lifetime for all customers
UPDATE customers_blaze c
SET
    total_visits = COALESCE(trans_stats.visit_count, 0),
    lifetime_value = COALESCE(trans_stats.total_spent, 0),
    last_visited = trans_stats.most_recent_visit,
    vip_status = CASE
        WHEN COALESCE(trans_stats.visit_count, 0) >= 16 THEN 'VIP'
        WHEN COALESCE(trans_stats.visit_count, 0) BETWEEN 11 AND 15 THEN 'Regular2'
        WHEN COALESCE(trans_stats.visit_count, 0) BETWEEN 5 AND 10 THEN 'Regular1'
        WHEN COALESCE(trans_stats.visit_count, 0) BETWEEN 2 AND 4 THEN 'Casual'
        WHEN COALESCE(trans_stats.visit_count, 0) = 1 THEN 'First'
        ELSE 'New'
    END,
    days_since_last_visit = CASE
        WHEN trans_stats.most_recent_visit IS NOT NULL 
        THEN EXTRACT(DAY FROM NOW() - trans_stats.most_recent_visit)::INTEGER
        ELSE NULL
    END,
    updated_at = NOW()
FROM (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as visit_count,
        SUM(total_amount) as total_spent,
        MAX(date::DATE) as most_recent_visit
    FROM transactions_blaze
    WHERE blaze_status = 'Completed'
    GROUP BY customer_id
) AS trans_stats
WHERE c.member_id = trans_stats.customer_id;

-- Also update customers with NO transactions (set to 0)
UPDATE customers_blaze
SET
    total_visits = 0,
    lifetime_value = 0,
    vip_status = 'New',
    updated_at = NOW()
WHERE total_visits IS NULL;

-- Verify results
SELECT 
    '✓ BACKFILL COMPLETE' as status,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN total_visits > 0 THEN 1 END) as with_visits,
    COUNT(CASE WHEN lifetime_value > 0 THEN 1 END) as with_lifetime,
    ROUND(AVG(NULLIF(total_visits, 0)), 2) as avg_visits,
    ROUND(AVG(NULLIF(lifetime_value, 0)), 2) as avg_lifetime_value
FROM customers_blaze;

-- VIP breakdown
SELECT 
    vip_status,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 1) as percentage
FROM customers_blaze
GROUP BY vip_status
ORDER BY 
    CASE vip_status
        WHEN 'VIP' THEN 1
        WHEN 'Regular' THEN 2
        WHEN 'Casual' THEN 3
        WHEN 'New' THEN 4
    END;

-- Sample of updated customers
SELECT 
    first_name,
    last_name,
    total_visits,
    lifetime_value,
    vip_status,
    last_visited,
    days_since_last_visit
FROM customers_blaze
WHERE total_visits > 0
ORDER BY lifetime_value DESC
LIMIT 20;

