-- ============================================================
-- FIND ALL BACKUP TABLES AND THEIR SIZES
-- ============================================================
-- Run this in Supabase SQL Editor to find large backup tables

-- Find tables with backup/archive keywords (FIXED - handles non-existent tables)
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename))) AS size,
    pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename)) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
AND (
    tablename ILIKE '%backup%' 
    OR tablename ILIKE '%_backup%' 
    OR tablename ILIKE '%backup_%'
    OR tablename ILIKE '%_old%' 
    OR tablename ILIKE '%_archive%'
    OR tablename ILIKE '%_bak%' 
    OR tablename ILIKE '%_copy%'
    OR tablename ILIKE '%copy_%'
    OR tablename ILIKE '%old_%'
    OR tablename ILIKE '%archive_%'
)
ORDER BY pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename)) DESC NULLS LAST;

-- ============================================================
-- ALSO CHECK: All tables sorted by size (to find large ones)
-- ============================================================
-- This shows ALL tables, sorted by size (largest first)

SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename))) AS size,
    pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename)) AS size_bytes
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(quote_ident('public')||'.'||quote_ident(tablename)) DESC NULLS LAST
LIMIT 30;

