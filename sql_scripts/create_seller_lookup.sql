-- Create Seller/Budtender Lookup Table
-- This helps resolve seller_id from transactions_blaze to actual names

-- ============================================
-- OPTION 1: Create lookup from existing transactions
-- ============================================
-- Extract unique seller IDs and try to map to staff/budtenders table

CREATE TABLE IF NOT EXISTS sellers_blaze (
    id BIGSERIAL PRIMARY KEY,
    seller_id TEXT UNIQUE NOT NULL,
    seller_name TEXT,
    is_active BOOLEAN DEFAULT true,
    total_transactions INTEGER DEFAULT 0,
    total_sales DECIMAL(10, 2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Populate with unique seller_ids from transactions
INSERT INTO sellers_blaze (seller_id, total_transactions, total_sales)
SELECT 
    seller_id,
    COUNT(*) as total_transactions,
    SUM(total_amount) as total_sales
FROM transactions_blaze
WHERE seller_id IS NOT NULL 
AND seller_id != ''
AND blaze_status = 'Completed'
GROUP BY seller_id
ON CONFLICT (seller_id) DO UPDATE SET
    total_transactions = EXCLUDED.total_transactions,
    total_sales = EXCLUDED.total_sales,
    updated_at = NOW();

-- ============================================
-- OPTION 2: AUTO-MAP USING employees_blaze TABLE!
-- ============================================
DO $$
BEGIN
    -- PRIMARY STRATEGY: Map seller_id to employees_blaze.employee_id
    UPDATE sellers_blaze s
    SET seller_name = e.name
    FROM employees_blaze e
    WHERE s.seller_id = e.employee_id
    AND e.is_disabled = false;  -- Only active employees

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Mapped % seller_ids to employees_blaze (ACTIVE EMPLOYEES)', v_count;

    -- SECONDARY: If still unmapped, try disabled employees too
    UPDATE sellers_blaze s
    SET seller_name = e.name || ' (Inactive)'
    FROM employees_blaze e
    WHERE s.seller_id = e.employee_id
    AND s.seller_name IS NULL;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Mapped % seller_ids to employees_blaze (INACTIVE EMPLOYEES)', v_count;

    -- FALLBACK: Staff table (if any remain unmapped)
    UPDATE sellers_blaze s
    SET seller_name = st.staff_name
    FROM staff st
    WHERE s.seller_id ~ '^[0-9]+$'  -- Only numeric seller_ids
    AND st.id = s.seller_id::INTEGER
    AND s.seller_name IS NULL;

    GET DIAGNOSTICS v_count = ROW_COUNT;
    RAISE NOTICE 'Mapped % seller_ids to staff table', v_count;

    RAISE NOTICE 'Auto-mapping complete! Most seller_ids should now be resolved.';
END $$;

-- ============================================
-- View current seller data
-- ============================================
SELECT 
    seller_id,
    seller_name,
    total_transactions,
    ROUND(total_sales, 2) as total_sales,
    ROUND(total_sales / NULLIF(total_transactions, 0), 2) as avg_transaction,
    is_active
FROM sellers_blaze
ORDER BY total_sales DESC
LIMIT 50;

-- ============================================
-- Function to get seller name (fallback to ID)
-- ============================================
CREATE OR REPLACE FUNCTION get_seller_name(p_seller_id TEXT)
RETURNS TEXT AS $$
DECLARE
    v_name TEXT;
BEGIN
    SELECT seller_name INTO v_name
    FROM sellers_blaze
    WHERE seller_id = p_seller_id;
    
    RETURN COALESCE(v_name, 'Seller #' || p_seller_id);
END;
$$ LANGUAGE plpgsql;

-- Test the function
SELECT 
    seller_id,
    get_seller_name(seller_id) as seller_display_name,
    COUNT(*) as transaction_count
FROM transactions_blaze
WHERE seller_id IS NOT NULL
GROUP BY seller_id
ORDER BY transaction_count DESC
LIMIT 10;

-- ============================================
-- MANUAL NAME ENTRY (if needed)
-- ============================================
-- Use this to manually add seller names:

/*
UPDATE sellers_blaze SET seller_name = 'John Doe' WHERE seller_id = '12345';
UPDATE sellers_blaze SET seller_name = 'Jane Smith' WHERE seller_id = '67890';
-- etc...
*/

-- ============================================
-- Create index for fast lookups
-- ============================================
CREATE INDEX IF NOT EXISTS idx_sellers_blaze_seller_id ON sellers_blaze(seller_id);
CREATE INDEX IF NOT EXISTS idx_sellers_blaze_name ON sellers_blaze(seller_name);

