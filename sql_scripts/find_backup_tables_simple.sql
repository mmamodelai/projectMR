-- ============================================================
-- SIMPLE: Find backup tables (no errors)
-- ============================================================
-- Just lists table names - then check sizes manually

-- Step 1: List all tables with backup keywords
SELECT tablename
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
ORDER BY tablename;

-- ============================================================
-- Step 2: Check size of a specific table (replace TABLE_NAME)
-- ============================================================
-- SELECT pg_size_pretty(pg_total_relation_size('public.TABLE_NAME'));

-- ============================================================
-- Step 3: List ALL tables (to see what exists)
-- ============================================================
SELECT tablename
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY tablename;

