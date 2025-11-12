-- ============================================================
-- FIND LARGE TABLES - WORKING VERSION
-- ============================================================
-- This handles case-sensitive table names correctly

-- Method 1: Use pg_class directly (more reliable)
SELECT 
    schemaname||'.'||tablename AS full_name,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes
FROM pg_tables t
JOIN pg_class c ON c.relname = t.tablename
WHERE t.schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC NULLS LAST
LIMIT 30;

-- ============================================================
-- Method 2: Simpler - just use format() to handle quotes
-- ============================================================
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(format('public.%I', tablename))) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(format('public.%I', tablename)) DESC NULLS LAST
LIMIT 30;

-- ============================================================
-- Method 3: Find backup tables specifically
-- ============================================================
SELECT 
    tablename,
    pg_size_pretty(pg_total_relation_size(format('public.%I', tablename))) AS size
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
)
ORDER BY pg_total_relation_size(format('public.%I', tablename)) DESC NULLS LAST;

