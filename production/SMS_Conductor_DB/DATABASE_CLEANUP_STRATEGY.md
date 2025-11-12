# Database Cleanup Strategy - Overloaded Database

## Problem
Database is **18GB+** and **unhealthy**, causing timeouts on all operations.

## Root Causes
1. **Duplicates** in `transaction_items_blaze`, `products_blaze`, `transactions_blaze`
2. **Large archive tables** that might not be needed
3. **Database overloaded** - even small operations timeout

## Strategy: 3-Phase Approach

### Phase 1: Identify What's Taking Space ⏱️ 5 minutes

**Run:**
```powershell
cd C:\Dev\conductor\conductor-sms
python check_table_sizes.py
```

**Or double-click:** `check_sizes.bat`

**This will show:**
- Which tables have the most rows
- Estimated sizes
- Candidates for deletion

**Look for:**
- `blaze_api_samples` - Old API samples? Can we delete?
- Tables with `_old`, `_backup`, `_archive` in name
- Test/development tables

---

### Phase 2: Delete Entire Tables (If Safe) ⏱️ 10 minutes

**⚠️ WARNING: This is PERMANENT!**

**Before deleting ANY table:**
1. ✅ Verify it's not needed
2. ✅ Check if data exists elsewhere
3. ✅ Consider exporting first (if critical)

**To delete a table:**

**Option A: Supabase SQL Editor**
```sql
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;
```

**Option B: Direct Postgres (if SQL Editor times out)**
```python
# Use psycopg2 for direct connection
# (See delete_table_safely.py for template)
```

**Common candidates:**
- `blaze_api_samples` - If it's just old API test data
- Any `_old`, `_backup`, `_archive` tables
- Test tables

**After deleting:**
- Database should be smaller
- May become "Healthy" again
- Deduplication will work better

---

### Phase 3: Deduplicate with TINY Batches ⏱️ Hours/Days

**If database is still overloaded after Phase 2:**

**Run:**
```powershell
cd C:\Dev\conductor\conductor-sms
python dedupe_blaze_tiny.py
```

**Or double-click:** `dedupe_tiny.bat`

**What it does:**
- Uses **10-row batches** (instead of 1000)
- Waits **30 seconds** between batches
- Waits **60 seconds** on timeout
- **VERY SLOW** but works on overloaded DB

**Settings:**
- Batch size: 10 rows
- Wait between batches: 30 seconds
- Wait on timeout: 60 seconds

**Expected time:**
- If you have 1 million duplicates: ~83 hours (3.5 days)
- But it WILL work, even on overloaded DB

**You can:**
- ✅ Stop anytime (Ctrl+C) - safe to interrupt
- ✅ Resume later - run script again
- ✅ Check progress - shows running total

---

## Recommended Order

### Step 1: Check Table Sizes
```powershell
python check_table_sizes.py
```

### Step 2: Delete Archive Tables (If Safe)
```sql
-- In Supabase SQL Editor
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;
-- (Verify first!)
```

### Step 3: Wait for Database to be "Healthy"
- Check Supabase Dashboard
- Wait until status is "Healthy" (not "Unhealthy")

### Step 4: Try Normal Deduplication
```powershell
python dedupe_blaze_rpc.py
```

### Step 5: If Still Timing Out, Use TINY Batches
```powershell
python dedupe_blaze_tiny.py
```

---

## Why This Works

1. **Deleting entire tables** = Instant space recovery (no timeouts)
2. **TINY batches** = Small enough to not timeout
3. **Long waits** = Gives DB time to recover between operations
4. **Resumable** = Can stop/start anytime

---

## Monitoring Progress

**While deduplication runs:**
- Watch for timeout messages
- Check total deleted count
- If 5+ consecutive timeouts, consider:
  - Waiting longer between batches
  - Deleting more tables first
  - Running during off-peak hours

---

## Success Criteria

✅ Database status = "Healthy"
✅ No more timeouts
✅ Table sizes reduced
✅ Normal operations work again

---

## Files Created

- `check_table_sizes.py` - Identify large tables
- `dedupe_blaze_tiny.py` - Deduplicate with tiny batches
- `delete_table_safely.py` - Template for safe deletion
- `check_sizes.bat` - Quick launcher
- `dedupe_tiny.bat` - Quick launcher

---

## Next Steps After Cleanup

1. **Add unique indexes** to prevent future duplicates:
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS idx_transaction_items_unique 
   ON transaction_items_blaze (transaction_id, product_id, quantity, unit_price) 
   NULLS NOT DISTINCT;
   ```

2. **Run VACUUM ANALYZE** to reclaim space:
   ```sql
   VACUUM ANALYZE;
   ```

3. **Monitor database size** - Set up alerts if it grows too large

---

**Last Updated:** 2025-01-20
**Status:** Ready to use

