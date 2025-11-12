# Oct 31 Duplicate Transactions & Items Issue

## 🔴 Problem Observed

Looking at the viewer screenshot, we see:

### Issue 1: Duplicate Transactions
**Daniel Fox** has 4 transactions on Oct 31, 2025 within 8 minutes:
- 05:44 PM - $54.00 - Leo Salguero
- 05:50 PM - $60.48 - Jimmy Silks  
- 05:52 PM - $82.08 - Jacob Vangel
- 05:58 PM - $48.60 - Devon Calone

**Red flags:**
- All within 8-minute window
- Different budtenders (unusual)
- Different transaction amounts
- Same customer

### Issue 2: Duplicate Items
The Items panel shows many repeated entries:
- Multiple "Recycling: 7g for $50" (MOTA, $25 each)
- Multiple "Mota Flwr 7g Blue Dream" (MOTA, $19.92 each)
- Multiple "Nasha Submerge 1g Hash" entries

## 🔍 Investigation Steps

Run these SQL queries in Supabase SQL Editor:

### 1. Check for Duplicate `transaction_id` Values

```sql
SELECT 
    transaction_id,
    COUNT(*) as count,
    STRING_AGG(DISTINCT id::text, ', ') as row_ids
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
GROUP BY transaction_id
HAVING COUNT(*) > 1
LIMIT 20;
```

**Expected**: Empty result (transaction_id should be UNIQUE)  
**If not empty**: We have duplicate transaction records in database

### 2. Check Transaction Items

```sql
SELECT 
    transaction_id,
    product_name,
    COUNT(*) as times_inserted
FROM transaction_items_blaze
WHERE transaction_id IN (
    SELECT transaction_id 
    FROM transactions_blaze 
    WHERE customer_id = 'DANIEL_FOX_MEMBER_ID'
    AND date >= '2025-10-31T00:00:00'
)
GROUP BY transaction_id, product_name
HAVING COUNT(*) > 1;
```

**Expected**: Empty result (no duplicate items per transaction)  
**If not empty**: Items are being inserted multiple times

### 3. Check Sync History

```sql
SELECT 
    (last_synced_at AT TIME ZONE 'America/Los_Angeles')::timestamp as sync_time,
    COUNT(*) as transactions_synced
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
GROUP BY last_synced_at
ORDER BY sync_time;
```

This shows if multiple sync runs happened for Oct 31 data.

## 🎯 Likely Causes

### Cause A: Backfill Script Ran Multiple Times
- **Symptom**: Multiple transactions with same transaction_id
- **Root cause**: No UNIQUE constraint on `transaction_id` column
- **Fix**: Add UNIQUE constraint, then deduplicate data

### Cause B: Transaction Items Inserted Multiple Times  
- **Symptom**: Duplicate items in `transaction_items_blaze`
- **Root cause**: Upsert logic not checking for existing items
- **Fix**: Add unique constraint on (transaction_id, product_id, quantity)

### Cause C: Legitimate Multiple Transactions
- **Symptom**: Different transaction_ids, same customer, same time
- **Root cause**: Customer actually made multiple purchases
- **Likelihood**: Low (4 transactions in 8 minutes is unusual)

## ✅ Solutions

### Solution 1: Add UNIQUE Constraints

```sql
-- Ensure transaction_id is unique
ALTER TABLE transactions_blaze 
ADD CONSTRAINT unique_transaction_id UNIQUE (transaction_id);

-- Ensure transaction items aren't duplicated
ALTER TABLE transaction_items_blaze
ADD CONSTRAINT unique_transaction_item 
UNIQUE (transaction_id, product_id, quantity, unit_price);
```

**NOTE**: This will FAIL if duplicates already exist. Must deduplicate first.

### Solution 2: Deduplicate Transactions

```sql
-- Find duplicate transactions (keep oldest record)
WITH ranked_transactions AS (
    SELECT 
        id,
        transaction_id,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id 
            ORDER BY id
        ) as rn
    FROM transactions_blaze
)
DELETE FROM transactions_blaze
WHERE id IN (
    SELECT id 
    FROM ranked_transactions 
    WHERE rn > 1
);
```

### Solution 3: Deduplicate Transaction Items

```sql
-- Find duplicate items (keep oldest record)
WITH ranked_items AS (
    SELECT 
        id,
        transaction_id,
        product_id,
        product_name,
        quantity,
        ROW_NUMBER() OVER (
            PARTITION BY transaction_id, product_id, product_name, quantity
            ORDER BY id
        ) as rn
    FROM transaction_items_blaze
)
DELETE FROM transaction_items_blaze
WHERE id IN (
    SELECT id 
    FROM ranked_items 
    WHERE rn > 1
);
```

### Solution 4: Fix Sync Scripts

Update `blaze-api-sync/src/supabase_client.py`:

```python
# Line 62 - Already using upsert with on_conflict
self.client.table('customers_blaze').upsert(customer, on_conflict='member_id').execute()

# Line 103 - Already using upsert  
self.client.table('transactions_blaze').upsert(transaction, on_conflict='transaction_id').execute()

# Line 133 - PROBLEM: Using insert() instead of upsert()
self.client.table('transaction_items_blaze').insert(item).execute()  # ❌ BAD

# SHOULD BE:
self.client.table('transaction_items_blaze').upsert(
    item, 
    on_conflict='transaction_id,product_id,quantity'  # Need composite unique key
).execute()  # ✅ GOOD
```

## 🚨 Immediate Actions

1. **Run investigation SQL** (`sql_scripts/investigate_oct31_duplicates.sql`)
2. **Check for duplicates** in both transactions and items tables
3. **Review sync logs** from Oct 31 to see if multiple runs occurred
4. **Backup data** before running any DELETE queries
5. **Deduplicate** if duplicates found
6. **Add UNIQUE constraints** to prevent future duplicates
7. **Fix sync scripts** to use upsert for transaction items

## 📊 Verification

After fixes, verify with:

```sql
-- Should return 0
SELECT COUNT(*) 
FROM (
    SELECT transaction_id
    FROM transactions_blaze
    GROUP BY transaction_id
    HAVING COUNT(*) > 1
) as dupes;

-- Should return 0
SELECT COUNT(*)
FROM (
    SELECT transaction_id, product_id, product_name, quantity
    FROM transaction_items_blaze
    GROUP BY transaction_id, product_id, product_name, quantity
    HAVING COUNT(*) > 1
) as dupes;
```

## 📁 Files Created

- `sql_scripts/investigate_oct31_duplicates.sql` - Investigation queries
- `docs/OCT31_DUPLICATE_ISSUE.md` - This document
- `investigate_oct31_duplicates.py` - Python investigation script (needs API key fix)

---

**Status**: 🔴 NEEDS INVESTIGATION  
**Priority**: HIGH (affects data integrity and customer experience)  
**Next Step**: Run investigation SQL to determine root cause



