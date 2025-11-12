-- ============================================================
-- FIND ALL TABLES IN ARCHIVE SCHEMA
-- ============================================================
-- This is where the backup tables are!

-- List all tables in archive schema
SELECT tablename
FROM pg_tables
WHERE schemaname = 'archive'
ORDER BY tablename;

-- ============================================================
-- Get sizes of archive tables
-- ============================================================
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(format('archive.%I', tablename))) AS size,
    pg_total_relation_size(format('archive.%I', tablename)) AS size_bytes
FROM pg_tables
WHERE schemaname = 'archive'
ORDER BY pg_total_relation_size(format('archive.%I', tablename)) DESC NULLS LAST;

-- ============================================================
-- Also check EXCustomers size
-- ============================================================
SELECT 
    'EXCustomers' AS tablename,
    pg_size_pretty(pg_total_relation_size('public.EXCustomers')) AS size,
    pg_total_relation_size('public.EXCustomers') AS size_bytes;

