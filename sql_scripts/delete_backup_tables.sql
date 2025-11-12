-- ============================================================
-- DELETE BACKUP/ARCHIVE TABLES
-- ============================================================
-- 
-- ⚠️  WARNING: These commands are PERMANENT!
--    Run these ONE AT A TIME
--    Check database status after each deletion
-- 
-- ============================================================

-- Step 1: Delete blaze_api_samples (old API test data)
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;

-- Wait 30 seconds, check database status, then continue...

-- Step 2: Delete blaze_sync_state (sync tracking - can be recreated)
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;

-- Wait 30 seconds, check database status

-- ============================================================
-- After deleting, reclaim space:
-- ============================================================
VACUUM ANALYZE;

-- ============================================================
-- Check database size reduction:
-- ============================================================
-- SELECT pg_size_pretty(pg_database_size(current_database()));

