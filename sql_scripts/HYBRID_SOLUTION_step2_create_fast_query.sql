-- ============================================
-- HYBRID SOLUTION - STEP 2: FAST QUERY FUNCTION
-- ============================================
-- 
-- PURPOSE: Server-side function that returns filtered customers
--          Uses pre-calculated fields + dynamic date filtering
--
-- USAGE IN VIEWER:
--   result = supabase.rpc('get_customers_fast', {
--     'filter_email': False,
--     'filter_phone': True,
--     'days_cutoff': 365
--   })
--
-- ============================================

CREATE OR REPLACE FUNCTION get_customers_fast(
    filter_email BOOLEAN DEFAULT FALSE,
    filter_phone BOOLEAN DEFAULT FALSE,
    days_cutoff INTEGER DEFAULT 365,
    search_term TEXT DEFAULT NULL
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
    total_visits INTEGER,
    lifetime_value NUMERIC,
    vip_status TEXT,
    last_visited DATE,
    days_since_last_visit INTEGER,
    city TEXT,
    state TEXT,
    zip_code TEXT
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
        c.total_visits,
        c.lifetime_value,
        c.vip_status,
        c.last_visited,
        c.days_since_last_visit,
        c.city,
        c.state,
        c.zip_code
    FROM customers_blaze c
    WHERE 
        -- Email filter
        (NOT filter_email OR (c.email IS NOT NULL AND c.email != ''))
        -- Phone filter
        AND (NOT filter_phone OR (c.phone IS NOT NULL AND c.phone != ''))
        -- Date filter (dynamic!)
        AND (days_cutoff IS NULL OR c.last_visited >= CURRENT_DATE - (days_cutoff || ' days')::INTERVAL)
        -- Search filter (all tokens must match somewhere)
        AND (
            search_term IS NULL
            OR NOT EXISTS (
                SELECT 1
                FROM regexp_split_to_table(trim(search_term), '\s+') AS token
                WHERE token <> '' AND NOT (
                    LOWER(c.first_name) LIKE LOWER('%' || token || '%')
                    OR LOWER(c.last_name) LIKE LOWER('%' || token || '%')
                    OR LOWER(c.email) LIKE LOWER('%' || token || '%')
                    OR c.phone LIKE '%' || token || '%'
                )
            )
        )
    ORDER BY c.last_visited DESC NULLS LAST, c.lifetime_value DESC;
END;
$$ LANGUAGE plpgsql STABLE;

-- Test it with different filters
SELECT COUNT(*) as customer_count, 'No filters' as filter_type
FROM get_customers_fast(FALSE, FALSE, NULL)
UNION ALL
SELECT COUNT(*), 'Phone only, <365 days'
FROM get_customers_fast(FALSE, TRUE, 365)
UNION ALL
SELECT COUNT(*), 'Email + Phone, <180 days'
FROM get_customers_fast(TRUE, TRUE, 180)
UNION ALL
SELECT COUNT(*), 'Phone only, <180 days'
FROM get_customers_fast(FALSE, TRUE, 180);

-- Performance test
EXPLAIN ANALYZE
SELECT * FROM get_customers_fast(FALSE, TRUE, 365) LIMIT 1000;

-- Sample results
SELECT 
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    vip_status,
    days_since_last_visit
FROM get_customers_fast(FALSE, TRUE, 365)
LIMIT 20;

