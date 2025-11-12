-- =====================================================================
-- Audit and Safe Drop Plan for Legacy *_blaze Tables
-- Project: Conductor / MoTa CRM (Supabase: public schema)
-- Date: 2025-11-07
-- Purpose:
--   - Discover any legacy parallel tables (e.g., customers_blaze, transactions_blaze)
--   - List dependent views and foreign keys
--   - Provide a safe, commented DROP plan (no changes unless you uncomment)
--
-- How to use:
--   1) Run SECTION A (Discovery) to see what's present and dependencies
--   2) Review results and confirm targets to delete
--   3) Optionally run SECTION B (Backups via RENAME) to keep a copy
--   4) If clean, uncomment the DROP statements in SECTION C and run inside a TX
--
-- Notes:
--   - This script is read-only unless you explicitly uncomment DROP/ALTER lines.
--   - Prefer running in a transaction so you can rollback if anything looks off.
-- =====================================================================

-- =====================================================================
-- SECTION A: DISCOVERY (read-only)
-- =====================================================================

-- A1) List candidate tables containing 'blaze' in the name
SELECT
  table_schema,
  table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_type = 'BASE TABLE'
  AND table_name ILIKE '%blaze%'
ORDER BY table_name;

-- A2) Approximate row counts for those candidate tables
SELECT
  relname              AS table_name,
  n_live_tup           AS approx_rows
FROM pg_stat_all_tables
WHERE schemaname = 'public'
  AND relname ILIKE '%blaze%'
ORDER BY relname;

-- A3) Column listings for candidate tables
SELECT
  c.table_name,
  c.ordinal_position,
  c.column_name,
  c.data_type,
  c.is_nullable
FROM information_schema.columns c
WHERE c.table_schema = 'public'
  AND c.table_name ILIKE '%blaze%'
ORDER BY c.table_name, c.ordinal_position;

-- A4) Views (and mat views) that reference *_blaze tables
SELECT
  v.schemaname AS view_schema,
  v.viewname   AS view_name
FROM pg_catalog.pg_views v
WHERE v.schemaname = 'public'
  AND v.definition ILIKE '%_blaze%'
ORDER BY v.viewname;

-- A5) Foreign keys involving *_blaze tables (either as parent or child)
SELECT
  tc.table_name   AS child_table,
  kcu.column_name AS child_column,
  ccu.table_name  AS parent_table,
  ccu.column_name AS parent_column,
  tc.constraint_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
  AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
  AND ccu.table_schema = tc.table_schema
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
  AND (
    tc.table_name ILIKE '%blaze%' OR
    ccu.table_name ILIKE '%blaze%'
  )
ORDER BY child_table, constraint_name;

-- =====================================================================
-- SECTION B: OPTIONAL BACKUP (RENAME) PLAN
--   Uncomment and adjust specific tables you intend to keep as backups.
--   This preserves a copy by renaming before drop.
-- =====================================================================
-- DO NOT RUN AS-IS. Replace <table_name> and <suffix>.
-- BEGIN;
-- ALTER TABLE IF EXISTS public.<table_name> RENAME TO <table_name>_old_20251107;
-- COMMIT;

-- Example (commented):
-- BEGIN;
-- ALTER TABLE IF EXISTS public.customers_blaze RENAME TO customers_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.transactions_blaze RENAME TO transactions_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.transaction_items_blaze RENAME TO transaction_items_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.products_blaze RENAME TO products_blaze_old_20251107;
-- ALTER TABLE IF EXISTS public.staff_blaze RENAME TO staff_blaze_old_20251107;
-- COMMIT;

-- =====================================================================
-- SECTION C: SAFE DROP PLAN (commented)
--   Steps:
--     1) Drop dependent views referencing *_blaze
--     2) Drop foreign key constraints that reference *_blaze (if any)
--     3) Drop *_blaze tables (AFTER confirming they are not needed)
--   Run inside a transaction; verify output; then COMMIT.
-- =====================================================================
-- DO NOT RUN AS-IS. Review, customize, then remove the leading '-- '.
-- BEGIN;

-- -- C1) Drop views that reference *_blaze (add your exact view names here)
-- DROP VIEW IF EXISTS public.<view_name_that_uses_blaze> CASCADE;
-- -- Repeat for all views listed in SECTION A4 as needed

-- -- C2) Drop FK constraints that reference *_blaze (child side)
-- -- Replace <table> and <constraint> with values from SECTION A5
-- ALTER TABLE IF EXISTS public.<child_table> DROP CONSTRAINT IF EXISTS <constraint_name>;
-- -- Repeat per constraint

-- -- C3) Drop *_blaze tables (final)
-- DROP TABLE IF EXISTS public.customers_blaze;
-- DROP TABLE IF EXISTS public.transactions_blaze;
-- DROP TABLE IF EXISTS public.transaction_items_blaze;
-- DROP TABLE IF EXISTS public.products_blaze;
-- DROP TABLE IF EXISTS public.staff_blaze;

-- COMMIT;

-- =====================================================================
-- SECTION D: POST-DROP VERIFICATION (read-only)
-- =====================================================================
-- Verify none remain
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema='public' AND table_name ILIKE '%blaze%';

-- Check that core tables still exist
-- SELECT table_name
-- FROM information_schema.tables
-- WHERE table_schema='public'
--   AND table_name IN ('customers','transactions','transaction_items','products','staff','messages','leads')
-- ORDER BY table_name;

-- End of file


