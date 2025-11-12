# Delete Archive Tables - Quick Guide

## Goal
Delete archive/old tables to free up space and get database "Healthy"

## ⚠️ WARNING
- **PERMANENT** - Cannot be undone!
- **Verify first** - Check table contents before deleting
- **Run one at a time** - Check database status after each

---

## Step 1: List Tables (30 seconds)

**Run:**
```powershell
cd C:\Dev\conductor\conductor-sms
python list_all_tables.py
```

**Or double-click:** `delete_archive.bat`

**This shows:**
- Archive table candidates
- SQL commands to delete them
- Recommended deletion order

---

## Step 2: Verify Tables (2 minutes)

**Before deleting, check what's in each table:**

```sql
-- In Supabase SQL Editor
-- Check blaze_api_samples
SELECT COUNT(*) FROM public.blaze_api_samples;
SELECT * FROM public.blaze_api_samples LIMIT 10;

-- Check blaze_sync_state
SELECT * FROM public.blaze_sync_state;
```

**Questions to ask:**
- Is this old/test data? → Safe to delete
- Is this needed for production? → Keep it
- Can this be recreated? → Safe to delete

---

## Step 3: Delete Tables (5 minutes)

**Run SQL commands ONE AT A TIME:**

```sql
-- Delete blaze_api_samples (if verified safe)
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;

-- Wait 30 seconds, check database status
-- If still "Unhealthy", continue...

-- Delete blaze_sync_state (if verified safe)
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;

-- Wait 30 seconds, check database status
```

**After each deletion:**
1. Wait 30 seconds
2. Check Supabase Dashboard → Database → Status
3. If "Healthy" → Stop! You're done.
4. If still "Unhealthy" → Continue with next table

---

## Step 4: Check Database Status

**Go to Supabase Dashboard:**
- Database → Status
- Should show "Healthy" after deletions

**If still "Unhealthy":**
- Wait 5-10 minutes (database might be processing)
- Check again
- If still unhealthy, might need deduplication

---

## Common Archive Tables

### 🔴 High Priority (likely safe to delete):

1. **`blaze_api_samples`**
   - Old API test/sample data?
   - Check: `SELECT COUNT(*) FROM blaze_api_samples;`
   - If just test data → Delete

2. **`blaze_sync_state`**
   - Sync tracking/metadata?
   - Check: `SELECT * FROM blaze_sync_state;`
   - If can be recreated → Delete

3. **Tables with `_old`, `_backup`, `_archive`**
   - Obviously archive tables
   - Usually safe to delete

### 🟡 Medium Priority (verify first):

- Any table you don't recognize
- Tables with "test" or "temp" in name
- Old migration/backup tables

### 🟢 Keep These (production data):

- `transaction_items_blaze` (has duplicates, but needed)
- `transactions_blaze` (has duplicates, but needed)
- `products_blaze` (has duplicates, but needed)
- `customers_blaze`
- `budtenders`
- `messages`
- `campaign_messages`

---

## SQL Commands (Copy/Paste)

**See:** `sql_scripts/delete_archive_tables.sql`

**Or run these one at a time:**

```sql
-- 1. Delete blaze_api_samples
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;

-- 2. Delete blaze_sync_state
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;

-- 3. After deleting, reclaim space
VACUUM ANALYZE;
```

---

## After Deletion

1. ✅ Check database status → Should be "Healthy"
2. ✅ Try normal deduplication: `python dedupe_blaze_rpc.py`
3. ✅ If still times out → Use tiny batches: `python dedupe_blaze_tiny.py`

---

## Troubleshooting

**"Table does not exist"**
- That's OK! `DROP TABLE IF EXISTS` won't error
- Just means it was already deleted

**"Cannot delete - foreign key constraint"**
- Use `CASCADE` to delete dependencies too
- Or delete dependent tables first

**Database still "Unhealthy" after deletion**
- Wait 5-10 minutes
- Database might be processing
- Check again
- Might need deduplication still

---

**Last Updated:** 2025-01-20
**Status:** Ready to use

