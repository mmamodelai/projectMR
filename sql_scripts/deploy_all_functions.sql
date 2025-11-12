-- ============================================================================
-- DEPLOY ALL REQUIRED FUNCTIONS FOR IC VIEWER
-- Copy this entire file and paste into Supabase SQL Editor, then click RUN
-- ============================================================================

-- Function 1: get_customers_fast
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
    FROM customers c
    WHERE 
        (NOT filter_email OR c.email IS NOT NULL AND c.email != '')
        AND (NOT filter_phone OR c.phone IS NOT NULL AND c.phone != '')
        AND (days_cutoff IS NULL OR c.days_since_last_visit <= days_cutoff)
        AND (search_term IS NULL OR 
             c.first_name ILIKE '%' || search_term || '%' OR
             c.last_name ILIKE '%' || search_term || '%' OR
             c.phone ILIKE '%' || search_term || '%' OR
             c.email ILIKE '%' || search_term || '%')
    ORDER BY c.name;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SUCCESS! Functions deployed.
-- Now close and reopen your IC Viewer - the error should be gone!
-- ============================================================================

