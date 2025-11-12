-- =====================================================================
-- Plan: Remove legacy Blaze-parallel tables and obvious test/backup tables
-- Date: 2025-11-07
-- Source: Derived from live schema excerpt pasted in chat
--
-- What this does:
--   1) Optional: Verify candidates exist and have no dependencies
--   2) Optional: Rename (backup) before drop
--   3) Drop legacy *_blaze and test tables (no CASCADE, fail if deps exist)
--
-- SAFE USAGE:
--   - Run the checks first (Section A)
--   - If you want a safety net, run Section B (rename backups)
--   - Then run Section C (drops). Keep in a transaction to rollback if needed.
--
-- Assumptions from your schema:
--   - Canonical tables in use: customers, transactions, transaction_items,
--     products, staff, messages, leads, campaign_*, customer_* patterns/affinity
--   - Legacy/raw ingestion tables to remove: *_blaze plus old backups
--   - messages_test and EXCustomers are test tables
--   - blaze_api_samples is sample storage (optional - confirm usage)
--   - blaze_sync_state may be used by sync jobs (confirm usage before drop)
-- =====================================================================

-- =====================================================================
-- SECTION A: Pre-flight checks (read-only)
-- =====================================================================
-- List all blaze-named base tables
SELECT table_name
FROM information_schema.tables
WHERE table_schema='public' AND table_type='BASE TABLE' AND table_name ILIKE '%blaze%'
ORDER BY table_name;

-- Dependencies on blaze tables (should be none; review if any appear)
SELECT
  tc.table_name   AS child_table,
  kcu.column_name AS child_column,
  ccu.table_name  AS parent_table,
  ccu.column_name AS parent_column,
  tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND (tc.table_name ILIKE '%blaze%' OR ccu.table_name ILIKE '%blaze%')
ORDER BY child_table, constraint_name;

-- Views referencing blaze
SELECT viewname, definition
FROM pg_catalog.pg_views
WHERE schemaname='public' AND definition ILIKE '%_blaze%';

-- Quick approx rowcounts (FYI)
SELECT relname AS table_name, n_live_tup AS approx_rows
FROM pg_stat_all_tables
WHERE schemaname='public' AND relname ILIKE '%blaze%'
ORDER BY relname;

-- =====================================================================
-- SECTION B: Optional backups (rename instead of immediate drop)
-- =====================================================================
-- BEGIN;
-- ALTER TABLE IF EXISTS public.customers_blaze            RENAME TO customers_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.transactions_blaze         RENAME TO transactions_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.transaction_items_blaze    RENAME TO transaction_items_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.products_blaze             RENAME TO products_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.employees_blaze            RENAME TO employees_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.vendors_blaze              RENAME TO vendors_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.regions_blaze              RENAME TO regions_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.terminals_blaze            RENAME TO terminals_blaze_old_20251107;
-- -- preexisting backups (optional to drop directly instead of rename):
-- -- customers_blaze_backup_20251106
-- -- customers_blaze_old_backup
-- COMMIT;

-- =====================================================================
-- SECTION C: Drop statements (no CASCADE; will error if deps exist)
--   Run inside a transaction after reviewing Section A outputs.
-- =====================================================================
BEGIN;

-- Obvious test/backup tables
DROP TABLE IF EXISTS public.messages_test;
DROP TABLE IF EXISTS public.EXCustomers;
DROP TABLE IF EXISTS public.customers_blaze_backup_20251106;
DROP TABLE IF EXISTS public.customers_blaze_old_backup;

-- Blaze ingestion/raw tables (duplicates of canonical)
DROP TABLE IF EXISTS public.customers_blaze;
DROP TABLE IF EXISTS public.transactions_blaze;
DROP TABLE IF EXISTS public.transaction_items_blaze;
DROP TABLE IF EXISTS public.products_blaze;
DROP TABLE IF EXISTS public.employees_blaze;
DROP TABLE IF EXISTS public.vendors_blaze;
DROP TABLE IF EXISTS public.regions_blaze;
DROP TABLE IF EXISTS public.terminals_blaze;

-- Optional (confirm usage before dropping)
-- If you are not using these, uncomment to remove:
-- DROP TABLE IF EXISTS public.blaze_api_samples;
-- DROP TABLE IF EXISTS public.blaze_sync_state;

COMMIT;

-- =====================================================================
-- POST-VERIFY
-- =====================================================================
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema='public' AND table_name ILIKE '%blaze%';
-- SELECT table_name FROM information_schema.tables
-- WHERE table_schema='public' AND table_name IN
--   ('customers','transactions','transaction_items','products','staff','messages','leads');
-- =====================================================================




