-- ============================================
-- SUPABASE RPC FUNCTION: Get All Customer Stats
-- ============================================
-- 
-- PURPOSE: Return customer data + calculated stats in ONE query
--          Much faster than viewer calculating each customer individually
--
-- USAGE IN VIEWER:
--   result = supabase.rpc('get_customer_stats_fast', {
--     'has_email': True,
--     'has_phone': True, 
--     'days_since_visit': 365
--   })
--
-- ============================================

CREATE OR REPLACE FUNCTION get_customer_stats_fast(
    has_email BOOLEAN DEFAULT FALSE,
    has_phone BOOLEAN DEFAULT FALSE,
    days_since_visit INTEGER DEFAULT 365
)
RETURNS TABLE (
    member_id TEXT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    date_of_birth DATE,
    phone TEXT,
    email TEXT,
    is_medical BOOLEAN,
    text_opt_in BOOLEAN,
    email_opt_in BOOLEAN,
    loyalty_points NUMERIC,
    last_visited DATE,
    city TEXT,
    state TEXT,
    total_visits BIGINT,
    lifetime_value NUMERIC,
    vip_status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.member_id,
        c.first_name,
        c.last_name,
        c.middle_name,
        c.date_of_birth,
        c.phone,
        c.email,
        c.is_medical,
        c.text_opt_in,
        c.email_opt_in,
        c.loyalty_points,
        c.last_visited,
        c.city,
        c.state,
        -- Calculate visits and lifetime on the fly
        COALESCE(COUNT(DISTINCT t.transaction_id), 0) as total_visits,
        COALESCE(SUM(t.total_amount), 0) as lifetime_value,
        -- Calculate VIP status
        CASE
            WHEN COUNT(DISTINCT t.transaction_id) >= 15 THEN 'VIP'
            WHEN COUNT(DISTINCT t.transaction_id) >= 6 THEN 'Regular'
            WHEN COUNT(DISTINCT t.transaction_id) >= 2 THEN 'Casual'
            ELSE 'New'
        END as vip_status
    FROM customers_blaze c
    LEFT JOIN transactions_blaze t ON c.member_id = t.customer_id AND t.blaze_status = 'Completed'
    WHERE 
        -- Apply filters
        (NOT has_email OR (c.email IS NOT NULL AND c.email != ''))
        AND (NOT has_phone OR (c.phone IS NOT NULL AND c.phone != ''))
        AND (c.last_visited >= CURRENT_DATE - (days_since_visit || ' days')::INTERVAL OR days_since_visit IS NULL)
    GROUP BY 
        c.member_id, c.first_name, c.last_name, c.middle_name, c.date_of_birth,
        c.phone, c.email, c.is_medical, c.text_opt_in, c.email_opt_in,
        c.loyalty_points, c.last_visited, c.city, c.state
    ORDER BY c.last_name, c.first_name;
END;
$$ LANGUAGE plpgsql;

-- Test it
SELECT * FROM get_customer_stats_fast(
    has_email := FALSE,
    has_phone := TRUE,
    days_since_visit := 365
) LIMIT 10;

-- Check performance
EXPLAIN ANALYZE 
SELECT * FROM get_customer_stats_fast(
    has_email := FALSE,
    has_phone := TRUE,
    days_since_visit := 365
);

