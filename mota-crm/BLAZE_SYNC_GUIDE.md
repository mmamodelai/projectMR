# Blaze API → Supabase Sync Guide

## What This Does

Syncs transactions from Blaze POS to Supabase using **UPSERT** logic (no duplicates).

## Setup

### Step 1: Recreate Tables (one-time)

Run these SQL files in Supabase SQL Editor:

1. `sql_scripts/recreate_transactions_schema.sql`
2. `sql_scripts/recreate_transaction_items_schema.sql`

This creates tables with **UNIQUE constraints** to prevent duplicates.

### Step 2: Run Initial Sync

```powershell
cd C:\Dev\conductor\mota-crm
python blaze_sync_transactions.py 30
```

This syncs last 30 days of transactions.

## How It Works

### UPSERT Logic

**For `transactions_blaze`:**
- Uses `transaction_id` as unique key
- If transaction exists → UPDATE
- If transaction is new → INSERT
- Never creates duplicates

**For `transaction_items_blaze`:**
- Uses `(transaction_id, product_id, quantity, unit_price)` as unique key
- Same item in same transaction → UPDATE
- New item → INSERT
- Never creates duplicates

### Blaze API

- **Endpoint**: `/api/v1/partner/transactions`
- **Auth**: PARTNER_KEY + DISPENSARY_KEY
- **Rate limit**: 10,000 calls per 5 minutes
- **Format**: Dates in MM/dd/yyyy
- **Response**: `{values: [transactions...]}`

### Data Mapping

**Blaze → Supabase:**
- `id` → `transaction_id` (unique key)
- `customerId` → `customer_id`
- `date` → `date`
- `totalAmount` → `total_amount`
- `items[]` → `transaction_items_blaze` table

## Running Sync

### Manual Sync

```powershell
# Sync last 7 days (default)
python blaze_sync_transactions.py

# Sync last 30 days
python blaze_sync_transactions.py 30

# Or use batch file
sync_blaze.bat
```

### Automated Sync (Recommended)

Set up Windows Task Scheduler to run hourly:

```powershell
# Task: Blaze API Sync
# Trigger: Every 1 hour
# Action: Run python blaze_sync_transactions.py 7
```

## Monitoring

Check sync status:

```sql
-- Check latest synced transactions
SELECT * FROM transactions_blaze 
ORDER BY last_synced_at DESC 
LIMIT 10;

-- Check total transactions
SELECT COUNT(*) FROM transactions_blaze;

-- Check transaction items
SELECT COUNT(*) FROM transaction_items_blaze;

-- Check for sync errors
SELECT * FROM transactions_blaze 
WHERE sync_status = 'error';
```

## Troubleshooting

### "UNIQUE constraint violation"

Good! This means UPSERT is working - it's preventing duplicates.

### API timeout

Reduce days_back parameter:

```powershell
python blaze_sync_transactions.py 1  # Just today
```

### Missing data

Check Blaze API response:
- Verify PARTNER_KEY and DISPENSARY_KEY
- Check date range format (MM/dd/yyyy)
- Ensure BASE_URL is correct (stage vs production)

## Next Steps

1. Run initial sync (30 days)
2. Verify data in Supabase
3. Set up hourly cron job
4. Monitor for 24 hours
5. Increase to daily sync if needed

## Files

- `blaze_sync_transactions.py` - Main sync script
- `sync_blaze.bat` - Quick launcher
- `sql_scripts/recreate_*_schema.sql` - Table creation

