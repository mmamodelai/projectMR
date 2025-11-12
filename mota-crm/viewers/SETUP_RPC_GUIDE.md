# IC Viewer v5.5 - RPC Setup Guide

## What's Happening?

The viewer is showing this error:
```
RPC Not Available
Server-side function not found!

Run these SQL scripts first:
1. HYBRID_SOLUTION_step1_backfill.sql
2. HYBRID_SOLUTION_step2_create_fast_query.sql
```

**Why?** The viewer wants to use FAST MODE (server-side filtering), but the Supabase function doesn't exist yet.

**Solution?** Run the setup **once**, then it works forever!

---

## Option 1: Supabase SQL Editor (Easiest - 2 minutes)

### Step 1: Open Supabase
1. Go to: https://supabase.com/dashboard
2. Select project: **kiwmwoqrguyrcpjytgte**
3. Click **SQL Editor** (left sidebar)

### Step 2: Run Backfill (10-15 minutes)
1. Click **New Query**
2. Copy this SQL:

```sql
-- STEP 1: BACKFILL
UPDATE customers_blaze c
SET
    total_visits = COALESCE(trans_stats.visit_count, 0),
    lifetime_value = COALESCE(trans_stats.total_spent, 0),
    last_visited = trans_stats.most_recent_visit,
    vip_status = CASE
        WHEN COALESCE(trans_stats.visit_count, 0) >= 15 THEN 'VIP'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 6 THEN 'Regular'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 2 THEN 'Casual'
        ELSE 'New'
    END,
    days_since_last_visit = CASE
        WHEN trans_stats.most_recent_visit IS NOT NULL 
        THEN EXTRACT(DAY FROM NOW() - trans_stats.most_recent_visit)::INTEGER
        ELSE NULL
    END,
    updated_at = NOW()
FROM (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as visit_count,
        SUM(total_amount) as total_spent,
        MAX(date::DATE) as most_recent_visit
    FROM transactions_blaze
    WHERE blaze_status = 'Completed'
    GROUP BY customer_id
) AS trans_stats
WHERE c.member_id = trans_stats.customer_id;

UPDATE customers_blaze
SET
    total_visits = 0,
    lifetime_value = 0,
    vip_status = 'New',
    updated_at = NOW()
WHERE total_visits IS NULL;
```

3. Click **Run** (or Ctrl+Enter)
4. Wait 10-15 minutes (grab coffee ☕)

### Step 3: Create Function (Instant)
1. Click **New Query**
2. Copy this SQL:

```sql
-- STEP 2: CREATE FUNCTION
CREATE OR REPLACE FUNCTION get_customers_fast(
    filter_email BOOLEAN DEFAULT FALSE,
    filter_phone BOOLEAN DEFAULT FALSE,
    days_cutoff INTEGER DEFAULT 365,
    search_term TEXT DEFAULT NULL
)
RETURNS TABLE (
    member_id TEXT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    date_of_birth DATE,
    phone TEXT,
    email TEXT,
    is_medical BOOLEAN,
    text_opt_in BOOLEAN,
    email_opt_in BOOLEAN,
    loyalty_points NUMERIC,
    total_visits INTEGER,
    lifetime_value NUMERIC,
    vip_status TEXT,
    last_visited DATE,
    days_since_last_visit INTEGER,
    city TEXT,
    state TEXT,
    zip_code TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.member_id,
        c.first_name,
        c.last_name,
        c.middle_name,
        c.date_of_birth,
        c.phone,
        c.email,
        c.is_medical,
        c.text_opt_in,
        c.email_opt_in,
        c.loyalty_points,
        c.total_visits,
        c.lifetime_value,
        c.vip_status,
        c.last_visited,
        c.days_since_last_visit,
        c.city,
        c.state,
        c.zip_code
    FROM customers_blaze c
    WHERE 
        (NOT filter_email OR (c.email IS NOT NULL AND c.email != ''))
        AND (NOT filter_phone OR (c.phone IS NOT NULL AND c.phone != ''))
        AND (days_cutoff IS NULL OR c.last_visited >= CURRENT_DATE - (days_cutoff || ' days')::INTERVAL)
        AND (
            search_term IS NULL 
            OR LOWER(c.first_name) LIKE LOWER('%' || search_term || '%')
            OR LOWER(c.last_name) LIKE LOWER('%' || search_term || '%')
            OR LOWER(c.email) LIKE LOWER('%' || search_term || '%')
            OR c.phone LIKE '%' || search_term || '%'
        )
    ORDER BY c.last_visited DESC NULLS LAST, c.lifetime_value DESC;
END;
$$ LANGUAGE plpgsql STABLE;
```

3. Click **Run**
4. Done in seconds! ✅

### Step 4: Restart Viewer
1. Close IC Viewer
2. Reopen it
3. Error is GONE! 🚀
4. Title bar will say "FAST MODE"

---

## Option 2: Python Script (Automated)

Want to run it automatically? Use the script!

### Quick Start:
```bash
cd mota-crm/viewers
setup_rpc_function.bat
```

**OR**:
```bash
python setup_rpc_function.py
```

### What it does:
1. Connects to Supabase directly
2. Runs Step 1 (backfill)
3. Runs Step 2 (create function)
4. Verifies everything worked
5. Reports results

### Time: ~10-15 minutes

---

## Why Do I Need This?

### Without RPC (Fallback Mode):
- ❌ Loads ALL customers into Python
- ❌ Filters in Python (slow)
- ❌ 30-60 second load time
- ❌ High memory usage

### With RPC (FAST MODE):
- ✅ Filters on Supabase server
- ✅ Only sends filtered results
- ✅ 0.5-2 second load time
- ✅ Low memory usage
- ✅ Scales to millions of customers

**TL;DR**: FAST MODE is 30x faster! 🚀

---

## What Does It Do?

### Step 1: Backfill
**Updates customers_blaze table**:
- `total_visits` - Count of transactions
- `lifetime_value` - Sum of all purchases
- `last_visited` - Most recent transaction date
- `vip_status` - VIP/Regular/Casual/New
- `days_since_last_visit` - Days since last transaction

**Why?** Pre-calculate these once instead of calculating every time.

### Step 2: Create Function
**Creates `get_customers_fast()` function**:
- Takes filter parameters (email, phone, days, search)
- Returns filtered customer list
- Runs on Supabase server (not Python)

**Why?** Server-side filtering is MUCH faster.

---

## Troubleshooting

### Error: "Connection failed"
**Fix**: Check your database password
- File: `setup_rpc_function.py`
- Line 14: `SUPABASE_PASSWORD = "9YqTPhlCxytiXxnb"`
- Make sure it matches your actual password

### Error: "Permission denied"
**Fix**: Use service role key instead of anon key
- The script uses direct database connection
- No API key needed

### Backfill takes too long
**Normal!** With 130K+ customers, 10-15 minutes is expected.
- You only run it ONCE
- Worth the wait for 30x speed improvement

### Function already exists
**Not a problem!** `CREATE OR REPLACE` will update it.

---

## After Setup

### Verify It Worked:
1. Open IC Viewer
2. Check title bar
3. Should say "**FAST MODE**" or "**HYBRID (FAST RPC)**"
4. Load time should be ~1-2 seconds

### Future Updates:
- Run Step 1 (backfill) occasionally to refresh stats
- Run Step 2 (function) if we add new filters
- Both are safe to run multiple times

---

## Summary

**Easiest way**: Copy/paste SQL in Supabase SQL Editor (2 minutes of work, 15 minutes total)

**Automated way**: Run `setup_rpc_function.bat` (hands-off, 15 minutes)

**Result**: Viewer loads 30x faster, no more error messages!

---

**Created**: November 9, 2025  
**Status**: One-time setup, then works forever  
**Impact**: 30x faster customer loading

