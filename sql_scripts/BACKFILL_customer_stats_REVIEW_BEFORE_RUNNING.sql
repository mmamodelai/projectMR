-- ============================================
-- BACKFILL CUSTOMER STATS
-- ============================================
-- 
-- PURPOSE: Calculate visits, lifetime_value, and vip_status
--          for ALL customers in customers_blaze table
--
-- WHAT THIS DOES:
--   1. Counts completed transactions per customer
--   2. Sums total spend per customer
--   3. Calculates VIP status (2-5=Casual, 6-14=Regular, 15+=VIP)
--   4. Updates customers_blaze table with results
--
-- SAFETY:
--   - This is a READ + UPDATE operation (no deletes)
--   - Only updates calculated fields (visits, lifetime_value, vip_status)
--   - Does NOT touch contact info (email, phone, name, etc.)
--   - Runs in ~10-15 minutes for 131K customers
--
-- HOW TO USE:
--   1. READ this entire script first
--   2. Copy/paste into Supabase SQL Editor
--   3. Click "Run" button
--   4. Wait for completion message
--
-- ============================================

-- Update all customers with calculated stats
UPDATE customers_blaze
SET
    total_visits = COALESCE(trans_stats.visit_count, 0),
    lifetime_value = COALESCE(trans_stats.total_spent, 0),
    vip_status = CASE
        WHEN COALESCE(trans_stats.visit_count, 0) >= 15 THEN 'VIP'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 6 THEN 'Regular'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 2 THEN 'Casual'
        ELSE 'New'
    END,
    updated_at = NOW()
FROM (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as visit_count,
        SUM(total_amount) as total_spent
    FROM transactions_blaze
    WHERE blaze_status = 'Completed'
    GROUP BY customer_id
) AS trans_stats
WHERE customers_blaze.member_id = trans_stats.customer_id;

-- Verify results
SELECT 
    'BACKFILL COMPLETE' as status,
    COUNT(*) as total_customers,
    COUNT(CASE WHEN total_visits > 0 THEN 1 END) as customers_with_visits,
    COUNT(CASE WHEN lifetime_value > 0 THEN 1 END) as customers_with_lifetime,
    ROUND(AVG(total_visits), 2) as avg_visits,
    ROUND(AVG(lifetime_value), 2) as avg_lifetime
FROM customers_blaze;

-- VIP status breakdown
SELECT 
    vip_status,
    COUNT(*) as customer_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) as percentage
FROM customers_blaze
GROUP BY vip_status
ORDER BY 
    CASE vip_status
        WHEN 'VIP' THEN 1
        WHEN 'Regular' THEN 2
        WHEN 'Casual' THEN 3
        WHEN 'New' THEN 4
        ELSE 5
    END;

