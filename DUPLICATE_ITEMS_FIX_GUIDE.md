# 🔴 Duplicate Items Bug - Quick Fix Guide

## Problem Summary

You're seeing duplicate transaction items in your viewer because:

1. **The sync code uses `.insert()` instead of `.upsert()`** → Every sync run adds duplicates
2. **No unique constraint on items table** → Database allows infinite duplicates

### Example from Your Screenshot

Daniel Fox's Oct 31 transactions show:
- 4 transactions in 8 minutes (05:44 PM - 05:52 PM)
- Same items repeated multiple times:
  - "Recycling: 7g for $50" appears 5+ times
  - "Mota Flwr 7g Blue Dream" appears 6+ times
  - "Nasha Submerge 1g Hash" appears 5+ times

## How to Fix (3 Steps)

### Step 1: Investigate the Damage

Run this in Supabase SQL Editor:

```sql
-- See how many duplicates you have
SELECT 
    COUNT(*) as total_items,
    COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as unique_items,
    COUNT(*) - COUNT(DISTINCT (transaction_id, product_id, product_name, quantity)) as duplicates
FROM transaction_items_blaze;
```

### Step 2: Clean Up Duplicates

**Option A: Run the SQL File**
1. Open `sql_scripts/fix_duplicate_items.sql`
2. Follow the commented instructions (it walks you through each step)
3. Uncomment and run the DELETE query to remove duplicates

**Option B: Quick Delete (Advanced)**

```sql
-- WARNING: This permanently deletes duplicates. Backup first!
WITH ranked_items AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id, product_id, product_name, quantity, unit_price
            ORDER BY id  -- Keep oldest record
        ) as rn
    FROM transaction_items_blaze
)
DELETE FROM transaction_items_blaze
WHERE id IN (
    SELECT id 
    FROM ranked_items 
    WHERE rn > 1  -- Delete all but first occurrence
);
```

### Step 3: Add Unique Constraint

After cleaning duplicates, prevent future duplicates:

```sql
ALTER TABLE transaction_items_blaze
ADD CONSTRAINT unique_transaction_item
UNIQUE (transaction_id, product_id, quantity, unit_price);
```

### Step 4: Fix the Sync Code

Replace the buggy file:

```bash
# Backup original
cp blaze-api-sync/src/supabase_client.py blaze-api-sync/src/supabase_client_OLD.py

# Use fixed version
cp blaze-api-sync/src/supabase_client_FIXED.py blaze-api-sync/src/supabase_client.py
```

**Or manually edit line 133**:

```python
# CHANGE THIS (line 133 in supabase_client.py):
self.client.table('transaction_items_blaze').insert(item).execute()

# TO THIS:
self.client.table('transaction_items_blaze').upsert(
    item,
    on_conflict='transaction_id,product_id,quantity,unit_price'
).execute()
```

## Verification

After applying fixes, verify:

```sql
-- Should return 0 duplicates
SELECT COUNT(*)
FROM (
    SELECT transaction_id, product_id, product_name, quantity
    FROM transaction_items_blaze
    GROUP BY transaction_id, product_id, product_name, quantity, unit_price
    HAVING COUNT(*) > 1
) as dupes;
```

## Files Available

- **`sql_scripts/fix_duplicate_items.sql`** - Step-by-step cleanup SQL
- **`sql_scripts/investigate_oct31_duplicates.sql`** - Investigation queries
- **`blaze-api-sync/src/supabase_client_FIXED.py`** - Fixed Python code
- **`docs/OCT31_DUPLICATE_ISSUE.md`** - Detailed technical analysis

## Impact

**Before Fix:**
- Each sync run = more duplicates
- Viewer shows 5-6x same items
- Database bloat (wasted storage)
- Poor query performance

**After Fix:**
- No more duplicates
- Clean data
- Better performance
- Accurate reporting

## Quick Check: Is This Affecting You?

Run this to see your worst cases:

```sql
SELECT 
    transaction_id,
    product_name,
    COUNT(*) as duplicates
FROM transaction_items_blaze
GROUP BY transaction_id, product_id, product_name, quantity
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC
LIMIT 10;
```

If you see results → You have duplicates  
If empty → You're clean

---

**Status**: 🔴 Ready to Apply  
**Priority**: HIGH (Data integrity issue)  
**Time to Fix**: 10-15 minutes  
**Risk**: Low (if you backup first)



