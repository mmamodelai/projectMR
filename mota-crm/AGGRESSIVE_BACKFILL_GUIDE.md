# AGGRESSIVE Backfill Guide

## What Makes This AGGRESSIVE?

### Speed Improvements vs Old Script

| Feature | Old Script | AGGRESSIVE Script | Speedup |
|---------|-----------|------------------|---------|
| API Rate | 2,000 calls/5min | **7,500 calls/5min** | 3.75x faster |
| UPSERT | 1 item at a time | **500 items per batch** | 500x faster |
| Delays | 100ms between calls | No delays (rate limit only) | 10x faster |
| Progress | Every transaction | Every 1000 transactions | Less overhead |

**Expected Time:**
- **Old script**: 15-30 hours
- **AGGRESSIVE script**: 2-4 hours ⚡

## How It Works

### 7-Day Windows (Blaze Requirement)
The Blaze API requires date ranges. We use 7-day windows:
- Jan 1-7, 2024
- Jan 8-14, 2024
- Jan 15-21, 2024
- etc.

### API Pagination (100 records per call)
Blaze has an unpublished limit: **max 100 transactions per API call**

For a 7-day window with 2,000 transactions:
- Call 1: skip=0, returns 100 transactions
- Call 2: skip=100, returns 100 transactions
- Call 3: skip=200, returns 100 transactions
- ...
- Call 20: skip=1900, returns 100 transactions

**Total: 20 API calls for that window**

### Batch UPSERT (500 items at once)
Instead of:
```python
# OLD - SLOW
for item in items:
    supabase.insert(item)  # 1000 items = 1000 database calls
```

We do:
```python
# NEW - FAST
supabase.upsert(items)  # 1000 items = 2 database calls (batches of 500)
```

### Rate Limiting
- **Max**: 7,500 calls per 5 minutes (25% safety margin below 10K Blaze limit)
- **Auto-pause**: Script waits when limit reached
- **Safe**: Never exceeds rate limit

## Run the Backfill

```powershell
cd C:\Dev\conductor\mota-crm
python backfill_aggressive.py
```

Or: `backfill_aggressive.bat`

## What You'll See

```
======================================================================
AGGRESSIVE BACKFILL - JAN 1, 2024 → NOW
======================================================================
Max Rate: 7,500 calls per 5 min (safe margin below 10K max)
Batch Size: 500 items per UPSERT
Window Size: 7 days (Blaze requirement)
======================================================================

======================================================================
Window 1: 2024-01-01 to 2024-01-08
======================================================================
  Fetching 01/01/2024 to 01/08/2024...
    Fetched 1,000 transactions...
    Fetched 2,000 transactions...
  Processing 2,458 transactions...
  Upserting 12,340 items in batches...
    Upserted 5,000/12,340 items...
    Upserted 10,000/12,340 items...

  Window: 2,458 transactions, 12,340 items in 45.2s
  Total: 1 windows, 2,458 transactions, 12,340 items
  Time: 0.8min | Rate: 3247 trans/min, 16300 items/min
  Est. remaining: ~51 windows (~38 minutes)
```

## Safety Features

1. **UPSERT (no duplicates)**
   - Unique index prevents duplicate items
   - Safe to run multiple times
   - Safe to stop and resume (Ctrl+C)

2. **Rate Limiting**
   - Never exceeds 10,000 calls per 5 min
   - Respects Blaze 429 rate limit responses
   - Auto-waits when needed

3. **Error Handling**
   - Batch UPSERT fails → tries one at a time
   - API errors → continues to next window
   - Database errors → logged and continues

## Expected Results

### For ~$19M in Transactions
- **Transactions**: ~180,000-200,000
- **Items**: ~900,000-1,000,000
- **Windows**: ~52 (365 days ÷ 7)
- **Time**: 2-4 hours
- **API Calls**: ~50,000-100,000

### Database After Backfill
```sql
SELECT COUNT(*) FROM transaction_items_blaze;
-- Should show ~900K-1M items

SELECT COUNT(DISTINCT transaction_id) FROM transaction_items_blaze;
-- Should match transactions_blaze count
```

## Troubleshooting

### "Rate limit hit: 7500/7500"
- **Normal**: Script is running at max speed
- **Wait**: Script auto-waits ~5 minutes
- **Continue**: Resumes automatically

### "Batch UPSERT error"
- **Fallback**: Script tries one at a time
- **Continue**: Won't stop the backfill

### Stop and Resume
- **Press Ctrl+C** to stop
- **Run again**: UPSERT handles duplicates
- **Picks up**: Continues from where it left off

## Why This is Fast

1. **High API rate**: 7,500 calls/5min (75% of max, safe margin)
2. **Batch UPSERTs**: 500 items at once
3. **No unnecessary delays**: Only rate limiting
4. **Efficient processing**: Extract all items, then batch upload

## Comparison with Old Script

### Old Script Issues:
- 2K API calls/5min → wasted 80% of allowed rate
- 1 item per UPSERT → 1000x slower database operations
- 100ms delays → wasted time
- Called edge function → extra overhead

### AGGRESSIVE Script:
- 7.5K API calls/5min → 3.75x faster with safety margin ✅
- 500 items per UPSERT → 500x faster ✅
- No delays → faster ✅
- Direct Supabase → no overhead ✅

---

**Ready?** Run `backfill_aggressive.bat` and watch it fly! 🚀

