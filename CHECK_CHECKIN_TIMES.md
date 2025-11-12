# ✅ YES - We Track Customer Check-In Times!

## 📊 What We Track

In the `transactions_blaze` table, we store:
- **`start_time`** - When customer checked in / transaction started
- **`end_time`** - When customer checked out / transaction completed  
- **`completed_time`** - Final completion timestamp
- **Wait time** - Calculated as `end_time - start_time`

## 🔍 Quick Queries

### 1. See Recent Check-Ins (Last 20 transactions)

```sql
SELECT 
    transaction_id,
    customer_id,
    start_time AT TIME ZONE 'America/Los_Angeles' AS check_in,
    end_time AT TIME ZONE 'America/Los_Angeles' AS check_out,
    ROUND(EXTRACT(EPOCH FROM (end_time - start_time)) / 60.0::numeric, 2) AS wait_minutes,
    total_amount
FROM transactions_blaze
WHERE start_time IS NOT NULL 
AND end_time IS NOT NULL
ORDER BY date DESC
LIMIT 20;
```

### 2. Today's Wait Time Stats

```sql
SELECT * FROM wait_time_stats_today;
```

This view shows:
- Total transactions today
- Fastest wait time
- Slowest wait time
- Average wait time
- Median wait time
- 75th and 95th percentiles

### 3. Wait Times By Hour of Day (Last 7 Days)

```sql
SELECT 
    hour_pacific || ':00' AS "Hour",
    transactions AS "Txns",
    avg_minutes || ' min' AS "Avg Wait",
    median_minutes || ' min' AS "Median Wait"
FROM wait_time_by_hour
ORDER BY hour_pacific;
```

This shows you which hours are busiest and have longest waits.

### 4. Slowest Transactions (Last 7 Days)

```sql
SELECT 
    transaction_id,
    start_time AT TIME ZONE 'America/Los_Angeles' AS check_in,
    end_time AT TIME ZONE 'America/Los_Angeles' AS check_out,
    ROUND(EXTRACT(EPOCH FROM (end_time - start_time)) / 60.0::numeric, 2) AS wait_minutes,
    total_amount,
    customer_id
FROM transactions_blaze
WHERE start_time IS NOT NULL 
AND end_time IS NOT NULL
AND (date AT TIME ZONE 'America/Los_Angeles')::date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY EXTRACT(EPOCH FROM (end_time - start_time)) DESC
LIMIT 10;
```

### 5. Custom Date Range Stats

```sql
-- Change the dates as needed
SELECT * FROM get_wait_time_stats('2025-11-01'::date, '2025-11-03'::date);
```

## 📈 Recent Stats (From Documentation)

Based on last 7 days of data:

**Wait Time Statistics:**
- **Fastest**: 0.05 minutes (3 seconds!)
- **Slowest**: 16.12 minutes
- **Average**: 1.28 minutes (~77 seconds)
- **Median**: 0.90 minutes (~54 seconds)

**Percentiles:**
- **25th Percentile**: 0.52 minutes (~31 seconds)
- **75th Percentile**: 1.51 minutes (~91 seconds)
- **90th Percentile**: ~2.5 minutes
- **95th Percentile**: ~4 minutes

**Key Insights:**
- 95% of customers wait less than 4 minutes
- 75% of customers wait less than 1.5 minutes
- Half of customers wait less than 1 minute (median)
- Peak wait times occur around 4-5 AM and 10 AM

## 🔍 Find Specific Customer Check-Ins

```sql
-- Replace with actual customer_id
SELECT 
    transaction_id,
    date AT TIME ZONE 'America/Los_Angeles' AS transaction_date,
    start_time AT TIME ZONE 'America/Los_Angeles' AS check_in,
    end_time AT TIME ZONE 'America/Los_Angeles' AS check_out,
    ROUND(EXTRACT(EPOCH FROM (end_time - start_time)) / 60.0::numeric, 2) AS wait_minutes,
    total_amount,
    payment_type,
    blaze_status
FROM transactions_blaze
WHERE customer_id = 'MEMBER_ID_HERE'
AND start_time IS NOT NULL
ORDER BY date DESC
LIMIT 10;
```

## 🎯 Use Cases

### 1. **Identify Slow Service Times**
Use the "Wait Times By Hour" query to see when your shop is slowest and needs more staff.

### 2. **Track Customer Experience**
Monitor individual customer wait times to ensure VIP customers aren't waiting too long.

### 3. **Staff Performance**
Cross-reference `seller_id` with wait times to see which budtenders are fastest/slowest.

### 4. **Operational Efficiency**
Set alerts for transactions > 5 minutes to investigate what's causing delays.

## 📍 Where to Run These Queries

1. Go to [Supabase Dashboard](https://supabase.com/dashboard)
2. Select your project: **kiwmwoqrguyrcpjytgte**
3. Click "SQL Editor" in the left sidebar
4. Paste any query above and click "Run"

## 📚 More Information

- **Full Documentation**: `blaze-api-sync/WAIT_TIME_STATS.md`
- **Database Schema**: `blaze-api-sync/sql/01_create_tables.sql`
- **Views & Functions**: `blaze-api-sync/sql/03_create_views.sql`

## 🛠️ Available Database Functions

- **`get_wait_time_stats(start_date, end_date)`** - Stats for any date range
- **`wait_time_stats_today`** - View for today's stats (auto-updates)
- **`wait_time_by_hour`** - View showing wait times by hour (last 7 days)

---

**Summary**: Yes, we absolutely track when people check in! The data is in `transactions_blaze.start_time` and `end_time` fields, with pre-built views and functions to analyze wait times.



