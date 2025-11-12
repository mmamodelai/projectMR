-- ============================================================
-- DELETE OLD TRANSACTION ITEMS (if safe)
-- ============================================================
-- ⚠️  WARNING: This deletes data permanently!
-- Only do this if old transaction items aren't needed

-- Step 1: Check how much data would be deleted
SELECT 
    COUNT(*) AS rows_to_delete,
    pg_size_pretty(SUM(pg_column_size(ROW(transaction_items_blaze.*)))) AS estimated_size
FROM public.transaction_items_blaze
WHERE created_at < NOW() - INTERVAL '3 months';

-- Step 2: If safe, delete old data (run separately, not in transaction)
-- DELETE FROM public.transaction_items_blaze
-- WHERE created_at < NOW() - INTERVAL '3 months';

-- Step 3: After deleting, reclaim space (run separately)
-- VACUUM ANALYZE public.transaction_items_blaze;

-- ============================================================
-- Alternative: Delete by date range (more conservative)
-- ============================================================
-- Delete items older than 6 months instead of 3
-- DELETE FROM public.transaction_items_blaze
-- WHERE created_at < NOW() - INTERVAL '6 months';

