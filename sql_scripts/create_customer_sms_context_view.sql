-- Create customer_sms_context view for IC Viewer
-- This view provides fast customer lookups for SMS conversations

-- Drop existing view first
DROP VIEW IF EXISTS customer_sms_context;

-- Create new view
CREATE VIEW customer_sms_context AS
SELECT 
    member_id,
    name,
    phone,
    email,
    loyalty_points,
    total_visits,
    lifetime_value,
    vip_status,
    last_visited,
    days_since_last_visit,
    churn_risk
FROM customers_blaze
WHERE phone IS NOT NULL AND phone != '';

-- Grant access
GRANT SELECT ON customer_sms_context TO anon, authenticated;

