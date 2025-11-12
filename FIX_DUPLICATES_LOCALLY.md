# Fix Duplicates Locally - NO TIMEOUT!

## Why Local is Better

Supabase's web SQL editor has a **30-second timeout**. With 2.2M rows, everything times out.

Connecting **directly to the database** has:
- ✅ **No timeout** - can run for hours if needed
- ✅ **Faster** - no web interface overhead  
- ✅ **More control** - can see progress in real-time

## Option 1: Python Script (EASIEST - Recommended)

I created a Python script that handles everything automatically.

### Step 1: Get Your Database Password

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: `kiwmwoqrguyrcpjytgte`
3. Go to **Settings** → **Database**
4. Find your **Database Password** (or reset it if you forgot)

### Step 2: Install psycopg2 (if you don't have it)

```bash
pip install psycopg2-binary
```

### Step 3: Run the Script

**Option A: Double-click the batch file**
```
fix_duplicate_items_LOCAL.bat
```

**Option B: Run Python directly**
```bash
python fix_duplicate_items_LOCAL.py
```

### What It Does

1. ✅ Connects to Supabase (you enter password)
2. ✅ Shows current state (2.2M items, 1.2M duplicates)
3. ✅ Creates clean table with DISTINCT ON (2-5 minutes)
4. ✅ Verifies count matches (1.04M unique items)
5. ✅ Swaps tables (backs up old one)
6. ✅ Recreates indexes
7. ✅ Final verification (0 duplicates!)

**Time**: 5-10 minutes total  
**Risk**: Low (backs up old table first)

---

## Option 2: psql Command Line

If you have PostgreSQL installed locally:

### Step 1: Get Connection String

Go to Supabase Dashboard → Settings → Database → Connection String (URI)

It looks like:
```
postgresql://postgres.kiwmwoqrguyrcpjytgte:[YOUR-PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres
```

Replace `[YOUR-PASSWORD]` with your actual password.

### Step 2: Connect

```bash
psql "postgresql://postgres.kiwmwoqrguyrcpjytgte:[PASSWORD]@aws-0-us-west-1.pooler.supabase.com:6543/postgres"
```

### Step 3: Run SQL (No Timeout!)

```sql
-- Create clean table
CREATE TABLE transaction_items_blaze_clean AS
SELECT DISTINCT ON (transaction_id, product_id, product_name, quantity, unit_price)
    *
FROM transaction_items_blaze
ORDER BY transaction_id, product_id, product_name, quantity, unit_price, id ASC;

-- Verify count
SELECT COUNT(*) FROM transaction_items_blaze_clean;
-- Should be ~1,042,141

-- Swap tables
BEGIN;
ALTER TABLE transaction_items_blaze RENAME TO transaction_items_blaze_old_with_dupes;
ALTER TABLE transaction_items_blaze_clean RENAME TO transaction_items_blaze;
COMMIT;

-- Recreate indexes
CREATE INDEX idx_items_blaze_transaction_id ON transaction_items_blaze(transaction_id);
CREATE INDEX idx_items_blaze_product_id ON transaction_items_blaze(product_id);
CREATE INDEX idx_transaction_items_dedup ON transaction_items_blaze(transaction_id, product_id, product_name, quantity, unit_price);
```

---

## Option 3: DBeaver / pgAdmin (GUI Tools)

If you prefer a GUI:

### DBeaver (Free)
1. Download: https://dbeaver.io/download/
2. Create new PostgreSQL connection
3. Host: `db.kiwmwoqrguyrcpjytgte.supabase.co`
4. Port: `5432`
5. Database: `postgres`
6. User: `postgres`
7. Password: [Your Supabase password]
8. Run the SQL from Option 2

### pgAdmin (Free)
Similar to DBeaver - add new server with same connection details.

---

## After Fixing Duplicates

### Step 1: Verify in Viewer

Check your CRM viewer - items should now show correctly without duplicates.

### Step 2: Drop Old Table (Once Confident)

```sql
-- After you verify everything looks good
DROP TABLE transaction_items_blaze_old_with_dupes;
```

### Step 3: Fix the Python Code

**File**: `blaze-api-sync/src/supabase_client.py`  
**Line**: 133

Change:
```python
self.client.table('transaction_items_blaze').insert(item).execute()
```

To:
```python
self.client.table('transaction_items_blaze').upsert(
    item,
    on_conflict='transaction_id,product_id,quantity,unit_price'
).execute()
```

Or just:
```bash
cp blaze-api-sync/src/supabase_client.py blaze-api-sync/src/supabase_client_OLD.py
cp blaze-api-sync/src/supabase_client_FIXED.py blaze-api-sync/src/supabase_client.py
```

### Step 4: Add Unique Constraint (Prevent Future Duplicates)

```sql
ALTER TABLE transaction_items_blaze
ADD CONSTRAINT unique_transaction_item
UNIQUE (transaction_id, product_id, quantity, unit_price);
```

---

## Troubleshooting

### "Connection refused"
- Check your Supabase password
- Make sure you're using the correct connection string
- Check if your IP needs to be whitelisted (usually not required)

### "psycopg2 not found"
```bash
pip install psycopg2-binary
```

### "Still timing out"
- The Python script sets `statement_timeout=0` (no limit)
- If it still times out, your internet connection might be slow
- Try the DBeaver/pgAdmin GUI option

---

## Quick Start (TL;DR)

1. Get your Supabase database password
2. Run: `pip install psycopg2-binary`
3. Run: `python fix_duplicate_items_LOCAL.py`
4. Enter password when prompted
5. Type 'yes' at each confirmation
6. Wait 5-10 minutes
7. Done! ✅

**Files Created:**
- `fix_duplicate_items_LOCAL.py` - Python script
- `fix_duplicate_items_LOCAL.bat` - Windows launcher
- `FIX_DUPLICATES_LOCALLY.md` - This guide

**I recommend Option 1 (Python script) - it's the easiest!**



