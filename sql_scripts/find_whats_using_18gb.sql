-- ============================================================
-- FIND WHAT'S USING THE 18GB
-- ============================================================
-- Check actual table sizes (not just data, but indexes too)

-- All tables with total size (data + indexes)
SELECT 
    schemaname||'.'||tablename AS full_name,
    pg_size_pretty(pg_total_relation_size(format('%I.%I', schemaname, tablename))) AS total_size,
    pg_size_pretty(pg_relation_size(format('%I.%I', schemaname, tablename))) AS data_size,
    pg_size_pretty(pg_total_relation_size(format('%I.%I', schemaname, tablename)) - 
                   pg_relation_size(format('%I.%I', schemaname, tablename))) AS index_size,
    pg_total_relation_size(format('%I.%I', schemaname, tablename)) AS total_bytes
FROM pg_tables
WHERE schemaname IN ('public', 'archive')
ORDER BY pg_total_relation_size(format('%I.%I', schemaname, tablename)) DESC
LIMIT 20;

-- ============================================================
-- Check transaction_items_blaze specifically
-- ============================================================
SELECT 
    'transaction_items_blaze' AS table_name,
    pg_size_pretty(pg_total_relation_size('public.transaction_items_blaze')) AS total_size,
    pg_size_pretty(pg_relation_size('public.transaction_items_blaze')) AS data_size,
    pg_size_pretty(pg_total_relation_size('public.transaction_items_blaze') - 
                   pg_relation_size('public.transaction_items_blaze')) AS index_size,
    (SELECT COUNT(*) FROM public.transaction_items_blaze) AS row_count;

-- ============================================================
-- Check for duplicate counts (estimate)
-- ============================================================
-- This might timeout, but worth trying
SELECT 
    COUNT(*) AS total_rows,
    COUNT(DISTINCT (transaction_id, product_id, quantity, unit_price)) AS unique_rows,
    COUNT(*) - COUNT(DISTINCT (transaction_id, product_id, quantity, unit_price)) AS duplicate_rows
FROM public.transaction_items_blaze;

