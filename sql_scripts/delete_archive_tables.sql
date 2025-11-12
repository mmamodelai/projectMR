-- ============================================================
-- DELETE ARCHIVE TABLES - Free Up Database Space
-- ============================================================
-- 
-- ⚠️  WARNING: These commands are PERMANENT!
--    Verify each table before deleting!
-- 
-- Run these ONE AT A TIME in Supabase SQL Editor
-- Check database status after each deletion
-- 
-- ============================================================

-- Step 1: Delete blaze_api_samples (if it's just old API test data)
-- VERIFY FIRST: Check what's in this table!
-- SELECT COUNT(*) FROM public.blaze_api_samples;
-- SELECT * FROM public.blaze_api_samples LIMIT 10;
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;

-- Step 2: Delete blaze_sync_state (if it's just sync tracking)
-- VERIFY FIRST: This might be needed for syncing!
-- SELECT * FROM public.blaze_sync_state;
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;

-- Step 3: Check for other archive tables
-- Run this to see all tables:
-- SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Step 4: After deleting, check database status
-- Should become "Healthy" if space was freed

-- ============================================================
-- NOTES:
-- ============================================================
-- 
-- - DROP TABLE CASCADE will also delete:
--   * Foreign key constraints referencing this table
--   * Indexes on this table
--   * Views that depend on this table
-- 
-- - If you're not sure about a table:
--   1. Check its contents: SELECT * FROM table_name LIMIT 10;
--   2. Check its size: SELECT pg_size_pretty(pg_total_relation_size('public.table_name'));
--   3. Check if it's referenced: SELECT * FROM information_schema.table_constraints 
--      WHERE constraint_type = 'FOREIGN KEY' AND table_name = 'table_name';
-- 
-- - After deleting, run VACUUM to reclaim space:
--   VACUUM ANALYZE;
-- 
-- ============================================================

