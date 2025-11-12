# Why Database is "Unhealthy" Despite Only 10GB

## The Problem

Your database is **10GB total**, which is fine. But `transaction_items_blaze` is **9.7GB** and has **MASSIVE DUPLICATES**.

## Why It's Timing Out

It's not about total size - it's about **query performance**:

1. **Duplicate rows** make queries slow
2. When deduplication runs, it scans the **entire 9.7GB table**
3. Even with indexes, scanning 9.7GB takes time
4. If there are millions of duplicates, the deduplication query itself is huge
5. Database times out because queries take too long

## Why Supabase Says "Unhealthy"

Supabase marks databases as "Unhealthy" when:
- Queries timeout frequently
- Database is slow to respond
- Too many concurrent operations
- Not enough resources for the workload

**It's not about size - it's about performance.**

## Solutions

### Option 1: Delete Old Data (If Safe)

If old transaction items aren't needed:

```sql
-- Check how much would be deleted
SELECT COUNT(*) FROM transaction_items_blaze 
WHERE created_at < NOW() - INTERVAL '3 months';

-- If safe, delete old data
DELETE FROM transaction_items_blaze 
WHERE created_at < NOW() - INTERVAL '3 months';
```

**Pros:**
- Instant space recovery
- Smaller table = faster queries
- Faster deduplication

**Cons:**
- Lose historical data
- Can't undo

### Option 2: Deduplicate with Tiny Batches

Use 10-row batches (very slow but works):

```powershell
python dedupe_blaze_tiny.py
```

**Pros:**
- Keeps all data
- Eventually works

**Cons:**
- Takes days/weeks
- Database stays slow during process

### Option 3: Both (Recommended)

1. Delete old data (if safe) → Instant relief
2. Deduplicate remaining data → Clean up

## Check: Are Duplicates in Old Data?

Run this to see if duplicates are concentrated in old data:

```sql
SELECT 
    CASE 
        WHEN created_at < NOW() - INTERVAL '3 months' THEN 'Older than 3 months'
        WHEN created_at < NOW() - INTERVAL '1 month' THEN '1-3 months old'
        ELSE 'Less than 1 month'
    END AS age_group,
    COUNT(*) AS row_count
FROM transaction_items_blaze
WHERE created_at IS NOT NULL
GROUP BY age_group;
```

If most duplicates are in old data → Delete old data first
If duplicates are recent → Need to deduplicate

## Database Size Limits

Supabase free tier: **500MB**
Supabase Pro: **8GB** (you're over!)
Supabase Team: **100GB+**

**You might be hitting the Pro tier limit (8GB)**, which could cause:
- Read-only mode
- Performance throttling
- "Unhealthy" status

Check your Supabase plan!

