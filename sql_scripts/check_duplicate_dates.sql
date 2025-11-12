-- ============================================================
-- CHECK WHEN DUPLICATES WERE CREATED
-- ============================================================
-- See if duplicates are in old data (can delete) or recent data

-- Check date distribution of transaction_items_blaze
-- (This might timeout, but worth trying)
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT (transaction_id, product_id, quantity, unit_price)) AS unique_rows,
    COUNT(*) - COUNT(DISTINCT (transaction_id, product_id, quantity, unit_price)) AS duplicates
FROM public.transaction_items_blaze
WHERE created_at IS NOT NULL
GROUP BY DATE(created_at)
ORDER BY DATE(created_at) DESC
LIMIT 30;

-- ============================================================
-- Check if we can delete old data
-- ============================================================
-- See oldest and newest dates
SELECT 
    MIN(created_at) AS oldest,
    MAX(created_at) AS newest,
    COUNT(*) AS total_rows
FROM public.transaction_items_blaze;

-- ============================================================
-- Estimate: How many rows are older than 3 months?
-- ============================================================
SELECT 
    COUNT(*) AS rows_older_than_3_months,
    pg_size_pretty(SUM(pg_column_size(ROW(transaction_items_blaze.*)))) AS estimated_size
FROM public.transaction_items_blaze
WHERE created_at < NOW() - INTERVAL '3 months';

-- ============================================================
-- Check: Are duplicates concentrated in old data?
-- ============================================================
-- This is a simpler check - just see date ranges
SELECT 
    CASE 
        WHEN created_at < NOW() - INTERVAL '3 months' THEN 'Older than 3 months'
        WHEN created_at < NOW() - INTERVAL '1 month' THEN '1-3 months old'
        ELSE 'Less than 1 month'
    END AS age_group,
    COUNT(*) AS row_count
FROM public.transaction_items_blaze
WHERE created_at IS NOT NULL
GROUP BY 
    CASE 
        WHEN created_at < NOW() - INTERVAL '3 months' THEN 'Older than 3 months'
        WHEN created_at < NOW() - INTERVAL '1 month' THEN '1-3 months old'
        ELSE 'Less than 1 month'
    END;

