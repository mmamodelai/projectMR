-- ============================================================
-- NUKE DUPLICATE TABLES - Free Up 10GB
-- ============================================================
-- This drops the bloated tables so you can re-sync cleanly

-- Step 1: Drop transaction_items_blaze (9.7GB)
DROP TABLE IF EXISTS public.transaction_items_blaze CASCADE;

-- Step 2: Drop transactions_blaze if it's also bloated (222MB)
-- Check first: Does it have duplicates?
-- If yes, drop it too:
DROP TABLE IF EXISTS public.transactions_blaze CASCADE;

-- Step 3: Drop products_blaze if it has duplicates (56MB)
-- DROP TABLE IF EXISTS public.products_blaze CASCADE;

-- ============================================================
-- After dropping, reclaim space (run separately)
-- ============================================================
-- VACUUM ANALYZE;

