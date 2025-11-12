-- =====================================================
-- CUSTOMER SEARCH INDEXES FOR IC VIEWER v5
-- =====================================================
-- Run once after major cleanups to accelerate get_customers_fast
--
-- Includes expression indexes for lower(first_name), lower(last_name),
-- lower(email), normalized phone digits, and last_visited date.
-- =====================================================

-- Index for last visited filtering
CREATE INDEX IF NOT EXISTS idx_customers_last_visited
    ON customers_blaze (last_visited DESC NULLS LAST);

-- Expression indexes for case-insensitive search
CREATE INDEX IF NOT EXISTS idx_customers_first_lower
    ON customers_blaze (LOWER(first_name));

CREATE INDEX IF NOT EXISTS idx_customers_last_lower
    ON customers_blaze (LOWER(last_name));

CREATE INDEX IF NOT EXISTS idx_customers_email_lower
    ON customers_blaze (LOWER(email));

-- Phone digits index (matches REGEXP_REPLACE usage)
CREATE INDEX IF NOT EXISTS idx_customers_phone_digits
    ON customers_blaze (REGEXP_REPLACE(phone, '[^0-9]', '', 'g'));

-- Analyze table to update planner stats
ANALYZE customers_blaze;

SELECT 'CUSTOMER SEARCH INDEXES CREATED/UPDATED' AS status;
