-- ============================================
-- CHECK DATABASE SIZE
-- ============================================

-- Overall database size
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size;

-- Size by table
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) AS indexes_size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY size_bytes DESC;

-- Row counts for main tables
SELECT 
    'customers_blaze' as table_name,
    COUNT(*) as row_count,
    pg_size_pretty(pg_total_relation_size('customers_blaze')) as size
FROM customers_blaze
UNION ALL
SELECT 
    'transactions_blaze',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('transactions_blaze'))
FROM transactions_blaze
UNION ALL
SELECT 
    'transaction_items_blaze',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('transaction_items_blaze'))
FROM transaction_items_blaze
UNION ALL
SELECT 
    'products_blaze',
    COUNT(*),
    pg_size_pretty(pg_total_relation_size('products_blaze'))
FROM products_blaze;

-- Check if old tables exist and their sizes
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size('public.'||tablename)) as size
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('customers', 'transactions', 'transaction_items', 'products', 'messages', 'budtenders')
ORDER BY tablename;

