-- Fix VIP Status Calculation & Unknown Brand Issue
-- Run this in Supabase SQL Editor

-- ============================================
-- PART 1: FIX VIP STATUS LOGIC
-- ============================================
-- New VIP logic:
-- 2-5 visits = Casual
-- 6-14 visits = Regular
-- 15+ visits = VIP

-- Update VIP status for all customers based on transaction count
UPDATE customers_blaze
SET vip_status = CASE
    WHEN (
        SELECT COUNT(DISTINCT transaction_id)
        FROM transactions_blaze
        WHERE customer_id = customers_blaze.member_id
        AND blaze_status = 'Completed'
    ) >= 15 THEN 'VIP'
    WHEN (
        SELECT COUNT(DISTINCT transaction_id)
        FROM transactions_blaze
        WHERE customer_id = customers_blaze.member_id
        AND blaze_status = 'Completed'
    ) >= 6 THEN 'Regular'
    WHEN (
        SELECT COUNT(DISTINCT transaction_id)
        FROM transactions_blaze
        WHERE customer_id = customers_blaze.member_id
        AND blaze_status = 'Completed'
    ) >= 2 THEN 'Casual'
    ELSE 'New'
END,
updated_at = NOW();

-- ============================================
-- PART 2: UPDATE VIP TRIGGER FUNCTION
-- ============================================
-- Replace existing function with new VIP logic
CREATE OR REPLACE FUNCTION update_customer_calculated_fields()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE customers_blaze
    SET
        total_visits = (
            SELECT COUNT(DISTINCT transaction_id)
            FROM transactions_blaze
            WHERE customer_id = NEW.customer_id
            AND blaze_status = 'Completed'
        ),
        lifetime_value = (
            SELECT COALESCE(SUM(total_amount), 0)
            FROM transactions_blaze
            WHERE customer_id = NEW.customer_id
            AND blaze_status = 'Completed'
        ),
        last_visited = (
            SELECT MAX(date::DATE)
            FROM transactions_blaze
            WHERE customer_id = NEW.customer_id
            AND blaze_status = 'Completed'
        ),
        days_since_last_visit = (
            SELECT CASE
                WHEN MAX(date::DATE) IS NOT NULL
                THEN EXTRACT(DAY FROM NOW() - MAX(date::DATE))::INTEGER
                ELSE NULL
            END
            FROM transactions_blaze
            WHERE customer_id = NEW.customer_id
            AND blaze_status = 'Completed'
        ),
        vip_status = CASE
            WHEN (
                SELECT COUNT(DISTINCT transaction_id)
                FROM transactions_blaze
                WHERE customer_id = NEW.customer_id
                AND blaze_status = 'Completed'
            ) >= 15 THEN 'VIP'
            WHEN (
                SELECT COUNT(DISTINCT transaction_id)
                FROM transactions_blaze
                WHERE customer_id = NEW.customer_id
                AND blaze_status = 'Completed'
            ) >= 6 THEN 'Regular'
            WHEN (
                SELECT COUNT(DISTINCT transaction_id)
                FROM transactions_blaze
                WHERE customer_id = NEW.customer_id
                AND blaze_status = 'Completed'
            ) >= 2 THEN 'Casual'
            ELSE 'New'
        END,
        churn_risk = CASE
            WHEN (
                SELECT EXTRACT(DAY FROM NOW() - MAX(date::DATE))
                FROM transactions_blaze
                WHERE customer_id = NEW.customer_id
                AND blaze_status = 'Completed'
            ) >= 60 THEN 'High'
            WHEN (
                SELECT EXTRACT(DAY FROM NOW() - MAX(date::DATE))
                FROM transactions_blaze
                WHERE customer_id = NEW.customer_id
                AND blaze_status = 'Completed'
            ) >= 30 THEN 'Medium'
            ELSE 'Low'
        END,
        updated_at = NOW()
    WHERE member_id = NEW.customer_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- PART 3: INVESTIGATE UNKNOWN BRAND ISSUE
-- ============================================

-- Check for NULL/empty brands in transaction_items_blaze
SELECT 
    COALESCE(brand, 'Unknown') as brand_name,
    COUNT(*) as item_count,
    SUM(total_price) as total_revenue,
    COUNT(DISTINCT transaction_id) as transaction_count
FROM transaction_items_blaze
WHERE brand IS NULL OR brand = '' OR brand = 'Unknown'
GROUP BY brand_name
ORDER BY total_revenue DESC;

-- Find transactions with NULL brands
SELECT 
    ti.transaction_id,
    ti.product_name,
    ti.brand,
    ti.total_price,
    t.customer_id,
    t.date
FROM transaction_items_blaze ti
JOIN transactions_blaze t ON ti.transaction_id = t.transaction_id
WHERE ti.brand IS NULL OR ti.brand = '' OR ti.brand = 'Unknown'
ORDER BY ti.total_price DESC
LIMIT 100;

-- ============================================
-- PART 4: VERIFY RESULTS
-- ============================================

-- Check VIP status distribution
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

-- Check a specific customer (Ronald Hershey - 323-342-3761)
SELECT 
    c.member_id,
    c.first_name,
    c.last_name,
    c.phone,
    c.total_visits,
    c.lifetime_value,
    c.vip_status,
    (SELECT COUNT(*) FROM transactions_blaze WHERE customer_id = c.member_id AND blaze_status = 'Completed') as actual_visits,
    (SELECT SUM(total_amount) FROM transactions_blaze WHERE customer_id = c.member_id AND blaze_status = 'Completed') as actual_lifetime
FROM customers_blaze c
WHERE c.phone LIKE '%323342376%' OR c.phone LIKE '%3233423761%';

-- Check Ronald's revenue by brand
SELECT 
    COALESCE(ti.brand, 'Unknown') as brand,
    COUNT(*) as purchase_count,
    SUM(ti.total_price) as total_revenue,
    ROUND(AVG(ti.total_price), 2) as avg_purchase
FROM customers_blaze c
JOIN transactions_blaze t ON t.customer_id = c.member_id
JOIN transaction_items_blaze ti ON ti.transaction_id = t.transaction_id
WHERE c.phone LIKE '%323342376%'
AND t.blaze_status = 'Completed'
GROUP BY ti.brand
ORDER BY total_revenue DESC;

-- ============================================
-- SUCCESS MESSAGE
-- ============================================
DO $$
BEGIN
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'VIP STATUS UPDATE COMPLETE!';
    RAISE NOTICE '==============================================';
    RAISE NOTICE 'New VIP Logic:';
    RAISE NOTICE '  - 2-5 visits: Casual';
    RAISE NOTICE '  - 6-14 visits: Regular';
    RAISE NOTICE '  - 15+ visits: VIP';
    RAISE NOTICE '';
    RAISE NOTICE 'Run the SELECT queries above to verify results.';
    RAISE NOTICE '==============================================';
END $$;

