-- ============================================
-- QUICK UPDATE: VIP SEGMENTATION
-- ============================================
-- Run this AFTER the backfill to update all customers
-- to the new segmentation rules
-- 
-- NEW RULES:
-- 0 visits   = New
-- 1 visit    = First
-- 2-4 visits = Casual
-- 5-10       = Regular1
-- 11-15      = Regular2
-- 16+        = VIP
-- ============================================

UPDATE customers_blaze
SET vip_status = CASE 
    WHEN total_visits >= 16 THEN 'VIP'
    WHEN total_visits BETWEEN 11 AND 15 THEN 'Regular2'
    WHEN total_visits BETWEEN 5 AND 10 THEN 'Regular1'
    WHEN total_visits BETWEEN 2 AND 4 THEN 'Casual'
    WHEN total_visits = 1 THEN 'First'
    ELSE 'New'
END;

-- Verify the distribution
SELECT 
    vip_status,
    COUNT(*) as customer_count,
    ROUND(AVG(total_visits), 1) as avg_visits,
    ROUND(AVG(lifetime_value), 2) as avg_lifetime_value
FROM customers_blaze
GROUP BY vip_status
ORDER BY 
    CASE vip_status
        WHEN 'VIP' THEN 6
        WHEN 'Regular2' THEN 5
        WHEN 'Regular1' THEN 4
        WHEN 'Casual' THEN 3
        WHEN 'First' THEN 2
        WHEN 'New' THEN 1
    END DESC;

