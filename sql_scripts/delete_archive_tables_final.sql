-- ============================================================
-- DELETE ARCHIVE TABLES
-- ============================================================
-- These are backups from Nov 6-7, 2025
-- Total: ~150MB (small but every bit helps)

-- Step 1: Delete archive tables (one at a time)
DROP TABLE IF EXISTS archive.transaction_items_old_20251107 CASCADE;
DROP TABLE IF EXISTS archive.customers_blaze_backup_20251106 CASCADE;
DROP TABLE IF EXISTS archive.transactions_old_20251107 CASCADE;
DROP TABLE IF EXISTS archive.customers_old_20251107 CASCADE;
DROP TABLE IF EXISTS archive.customers_blaze_old_backup CASCADE;

-- Step 2: Also delete EXCustomers if it's a backup
-- (Check size first: SELECT pg_size_pretty(pg_total_relation_size('public.EXCustomers'));)
-- DROP TABLE IF EXISTS public.EXCustomers CASCADE;

-- Step 3: Reclaim space
VACUUM ANALYZE;

-- ============================================================
-- NOTE: After deleting, foreign keys will break
-- You'll need to drop/recreate foreign keys that referenced archive.customers_old_20251107
-- ============================================================

