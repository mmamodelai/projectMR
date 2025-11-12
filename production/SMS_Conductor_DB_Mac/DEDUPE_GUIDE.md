# Blaze Tables Deduplication - Quick Start

## Problem
- Database is 18GB+ and crashing
- SQL Editor times out on delete queries
- Need to delete duplicates from `transaction_items_blaze`, `products_blaze`, `transactions_blaze`

## Solution
Direct Postgres connection script that bypasses SQL editor timeout.

## Setup (One Time)

### 1. Get Your Database Password
- Supabase Dashboard → Settings → Database
- Copy your database password (or reset it if needed)

### 2. Install psycopg2 (if not installed)
```powershell
pip install psycopg2-binary
```

### 3. Set Password (PowerShell)
```powershell
$env:DB_PASSWORD="your_supabase_password_here"
```

### 4. Get Connection Details

**Option A: Direct Connection (requires IPv4 add-on)**
- Supabase Dashboard → Settings → Database → Connection String
- Use "Direct connection" details:
  - Host: `db.kiwmwoqrguyrcpjytgte.supabase.co`
  - Port: `5432`

**Option B: Session Pooler (no IPv4 needed - RECOMMENDED)**
- Supabase Dashboard → Settings → Database → Connection String
- Switch to "Session" mode
- Host will be: `aws-0-us-east-2.pooler.supabase.com` (or similar)
- Port: `6543` (pooler port)

### 5. Update Script Connection (if needed)
Edit `dedupe_blaze_direct.py` and change these if using Session Pooler:
```python
DB_HOST = "aws-0-us-east-2.pooler.supabase.com"  # Session pooler host
DB_PORT = "6543"  # Pooler port
```

## Run Deduplication

### Method 1: Batch File (Easiest)
```powershell
cd C:\Dev\conductor\conductor-sms
$env:DB_PASSWORD="your_password"
.\dedupe_blaze.bat
```

### Method 2: Python Directly
```powershell
cd C:\Dev\conductor\conductor-sms
$env:DB_PASSWORD="your_password"
python dedupe_blaze_direct.py
```

## What It Does

1. **Connects directly** to Postgres (bypasses SQL editor)
2. **Deletes duplicates** in batches of 1000:
   - `transaction_items_blaze` (by transaction_id, product_id, quantity, unit_price)
   - `products_blaze` (by SKU)
   - `transactions_blaze` (by transaction_id)
3. **Shows progress** - prints how many deleted per iteration
4. **Finds archive tables** - lists old/backup tables you can delete

## Expected Output

```
============================================================
BLAZE TABLES DEDUPLICATION - DIRECT POSTGRES
============================================================

Connecting to: db.kiwmwoqrguyrcpjytgte.supabase.co:5432/postgres
Batch size: 1000
✓ Connected successfully!

============================================================
DEDUPLICATING: transaction_items_blaze
============================================================
Iteration 1: Deleted 1000 duplicates (Total: 1000)
Iteration 2: Deleted 1000 duplicates (Total: 2000)
Iteration 3: Deleted 500 duplicates (Total: 2500)
Iteration 4: No more duplicates found!

COMPLETE: Deleted 2500 duplicate transaction_items

[... continues for products and transactions ...]

============================================================
TOTAL DUPLICATES DELETED: 5000
============================================================
```

## After Deduplication

1. **Run VACUUM** in Supabase SQL Editor:
   ```sql
   VACUUM ANALYZE;
   ```

2. **Check size reduction**:
   ```sql
   SELECT pg_size_pretty(pg_database_size(current_database()));
   ```

3. **Add unique indexes** (prevents future duplicates):
   ```sql
   CREATE UNIQUE INDEX IF NOT EXISTS uq_ti_blaze
   ON public.transaction_items_blaze (transaction_id, product_id, quantity, unit_price);
   
   CREATE UNIQUE INDEX IF NOT EXISTS uq_products_blaze_sku
   ON public.products_blaze (sku) WHERE sku IS NOT NULL;
   
   CREATE UNIQUE INDEX IF NOT EXISTS uq_transactions_blaze_tid
   ON public.transactions_blaze (transaction_id);
   ```

## Troubleshooting

### "Connection timeout"
- Database might be unhealthy - wait for it to become Healthy in dashboard
- Try Session Pooler instead of Direct connection

### "psycopg2 not found"
```powershell
pip install psycopg2-binary
```

### "Authentication failed"
- Check DB_PASSWORD is correct
- Reset password in Supabase Dashboard if needed

### Script runs but deletes slowly
- Normal - database is under load
- Let it run (can take 30+ minutes for millions of duplicates)
- Each iteration shows progress

## Safety

- Script only deletes DUPLICATES (keeps newest row)
- Uses transactions (rolls back on error)
- Has iteration limits (won't run forever)
- Shows progress so you can monitor

## Next: Delete Archive Tables

After deduplication, the script will list archive tables. Review and delete manually:

```sql
-- Example (check size first!)
SELECT pg_size_pretty(pg_total_relation_size('archive.customers_old_20251107'));

-- If safe to delete:
DROP TABLE IF EXISTS archive.customers_old_20251107 CASCADE;
```

