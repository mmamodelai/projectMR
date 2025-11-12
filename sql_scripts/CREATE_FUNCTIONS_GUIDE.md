# Create Deduplication Functions - Quick Guide

## Problem
SQL Editor times out when running all 3 functions at once.

## Solution
Run each function **separately** (one at a time) - each CREATE FUNCTION statement is fast.

## Steps (5 minutes)

### Step 1: Open Supabase SQL Editor
- Go to Supabase Dashboard → SQL Editor
- Click "New Query"

### Step 2: Create Function 1 (transaction_items)
1. Open: `sql_scripts/create_function_1_transaction_items.sql`
2. Copy ALL contents (Ctrl+A, Ctrl+C)
3. Paste into SQL Editor
4. Click **Run** (or Ctrl+Enter)
5. Wait for "Success" message

### Step 3: Create Function 2 (products)
1. **Clear the SQL Editor** (or open new query)
2. Open: `sql_scripts/create_function_2_products.sql`
3. Copy ALL contents
4. Paste into SQL Editor
5. Click **Run**
6. Wait for "Success"

### Step 4: Create Function 3 (transactions)
1. **Clear the SQL Editor** (or open new query)
2. Open: `sql_scripts/create_function_3_transactions.sql`
3. Copy ALL contents
4. Paste into SQL Editor
5. Click **Run**
6. Wait for "Success"

### Step 5: Verify Functions Created
Run this query in SQL Editor:
```sql
SELECT routine_name 
FROM information_schema.routines 
WHERE routine_schema = 'public' 
AND routine_name LIKE 'dedupe_%';
```

Should return 3 rows:
- dedupe_transaction_items_batch
- dedupe_products_batch
- dedupe_transactions_batch

## Then Run Deduplication

Once all 3 functions are created:
```powershell
cd C:\Dev\conductor\conductor-sms
python dedupe_blaze_rpc.py
```

Or double-click: `dedupe_blaze.bat`

## Why This Works

- Each CREATE FUNCTION is a small, fast statement (~1 second)
- Running them separately avoids timeout
- Once created, the Python script calls them repeatedly (fast!)

## Troubleshooting

**"Function already exists"** - That's OK! It means it was already created.

**"Syntax error"** - Make sure you copied the ENTIRE function (including `$$;` at the end)

**Still times out** - Database might be overloaded. Wait for it to be Healthy, then try again.

