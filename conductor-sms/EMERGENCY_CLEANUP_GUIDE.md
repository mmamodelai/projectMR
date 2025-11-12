# Emergency Database Cleanup Guide

## 🚨 Current Situation
Database is **severely overloaded** - even 10-row batches timeout.

## ⚠️ Problem
- `transaction_items_blaze` times out on COUNT queries
- Even tiny batch deduplication (10 rows) times out
- Database is likely "Unhealthy" in Supabase dashboard

## ✅ Solutions (In Order of Preference)

### Option 1: Wait for Database to be Healthy ⏱️ 30 min - 2 hours

**Best option if you can wait**

1. Go to Supabase Dashboard → Database → Status
2. Wait until status shows **"Healthy"** (not "Unhealthy")
3. Then try normal deduplication: `python dedupe_blaze_rpc.py`

**Why this works:**
- Database might be processing other queries
- Once healthy, operations will work normally
- Much faster than extreme mode

---

### Option 2: Delete Archive Tables First ⏱️ 5 minutes

**Instant space recovery - no timeouts!**

**Check what tables exist:**
```sql
-- In Supabase SQL Editor
SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;
```

**Common candidates to delete:**
- `blaze_api_samples` - Old API test data?
- Any tables with `_old`, `_backup`, `_archive` in name
- Test/development tables

**Delete a table:**
```sql
-- ⚠️ WARNING: PERMANENT! Verify first!
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;
```

**Why this works:**
- DROP TABLE is instant (no scanning needed)
- Frees space immediately
- Database becomes less overloaded
- Then deduplication might work

---

### Option 3: Use EXTREME Mode ⏱️ Weeks

**LAST RESORT - only if Options 1 & 2 don't work**

```powershell
cd C:\Dev\conductor\conductor-sms
python dedupe_blaze_extreme.py
```

**Settings:**
- 1 row at a time
- 3 minutes wait between batches
- 5 minutes wait on timeout
- **Expected: 20+ days for 1 million duplicates**

**When to use:**
- Database is "Unhealthy" and won't recover
- Can't delete archive tables (they're needed)
- No other option works

---

## 📊 Recommended Action Plan

### Step 1: Check Database Status (1 min)
1. Open Supabase Dashboard
2. Go to Database → Status
3. Note if it says "Healthy" or "Unhealthy"

### Step 2A: If "Healthy" → Try Normal Deduplication
```powershell
python dedupe_blaze_rpc.py
```

### Step 2B: If "Unhealthy" → Try These in Order:

**A. Wait 30-60 minutes** (database might recover)
- Check status again
- If healthy → proceed with normal deduplication

**B. Delete Archive Tables** (instant space)
```sql
-- Verify first, then delete
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;
```
- Check database status again
- If healthy → proceed with normal deduplication

**C. Use Extreme Mode** (last resort)
```powershell
python dedupe_blaze_extreme.py
```
- Type "EXTREME" to confirm
- Leave running for days/weeks
- Can stop/resume anytime

---

## 🎯 Quick Decision Tree

```
Is database "Healthy"?
├─ YES → Try normal deduplication (dedupe_blaze_rpc.py)
└─ NO
   ├─ Can you wait 30-60 min? → Wait, then retry
   ├─ Can you delete archive tables? → Delete them, then retry
   └─ Nothing else works? → Use EXTREME mode (dedupe_blaze_extreme.py)
```

---

## 📝 Files Available

1. **`dedupe_blaze_rpc.py`** - Normal (1000 rows, fast) - Use when healthy
2. **`dedupe_blaze_tiny.py`** - Tiny (10 rows, slow) - Use when slightly overloaded
3. **`dedupe_blaze_ultra_tiny.py`** - Ultra-tiny (5 rows, very slow) - Use when overloaded
4. **`dedupe_blaze_extreme.py`** - Extreme (1 row, extremely slow) - LAST RESORT

5. **`check_db_health.py`** - Check if database can handle operations
6. **`check_table_sizes.py`** - See what tables are taking space

---

## ⚠️ Important Notes

- **EXTREME mode is VERY slow** - only use as last resort
- **Deleting tables is PERMANENT** - verify first!
- **Waiting for "Healthy" is usually fastest** - if you can wait
- **You can stop/resume anytime** - Ctrl+C is safe

---

## 🆘 If Nothing Works

1. **Contact Supabase Support** - Database might need manual intervention
2. **Check for long-running queries** - Something might be blocking
3. **Consider upgrading plan** - Database might be under-resourced

---

**Last Updated:** 2025-01-20
**Status:** Emergency cleanup guide

