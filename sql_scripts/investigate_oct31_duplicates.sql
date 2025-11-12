-- Investigation: Oct 31 Duplicate Transactions & Items
-- Run these queries in Supabase SQL Editor to diagnose the issue

-- ============================================================================
-- 1. FIND DANIEL FOX'S OCT 31 TRANSACTIONS
-- ============================================================================
SELECT 
    t.transaction_id,
    t.date AT TIME ZONE 'America/Los_Angeles' AS transaction_time,
    t.start_time AT TIME ZONE 'America/Los_Angeles' AS check_in,
    t.end_time AT TIME ZONE 'America/Los_Angeles' AS check_out,
    t.total_amount,
    t.blaze_status,
    t.seller_id,
    c.name AS customer_name,
    c.phone
FROM transactions_blaze t
JOIN customers_blaze c ON c.member_id = t.customer_id
WHERE c.phone LIKE '%2084078123%'
AND t.date >= '2025-10-31T00:00:00'
AND t.date <= '2025-10-31T23:59:59'
ORDER BY t.date;

-- ============================================================================
-- 2. CHECK FOR DUPLICATE TRANSACTION IDs
-- ============================================================================
-- This will show if the same transaction_id appears multiple times
SELECT 
    transaction_id,
    COUNT(*) as count,
    STRING_AGG(DISTINCT id::text, ', ') as row_ids,
    MAX(total_amount) as amount
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'
GROUP BY transaction_id
HAVING COUNT(*) > 1
ORDER BY count DESC
LIMIT 20;

-- ============================================================================
-- 3. CUSTOMERS WITH MOST OCT 31 TRANSACTIONS
-- ============================================================================
SELECT 
    c.name,
    c.phone,
    COUNT(t.transaction_id) as transaction_count,
    SUM(t.total_amount) as total_spent,
    STRING_AGG(t.transaction_id, ', ' ORDER BY t.date) as txn_ids
FROM transactions_blaze t
JOIN customers_blaze c ON c.member_id = t.customer_id
WHERE t.date >= '2025-10-31T00:00:00'
AND t.date <= '2025-10-31T23:59:59'
GROUP BY c.member_id, c.name, c.phone
HAVING COUNT(t.transaction_id) >= 4
ORDER BY transaction_count DESC
LIMIT 20;

-- ============================================================================
-- 4. CHECK TRANSACTION STATUS DISTRIBUTION ON OCT 31
-- ============================================================================
SELECT 
    blaze_status,
    COUNT(*) as count,
    SUM(total_amount) as total_revenue
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'
GROUP BY blaze_status
ORDER BY count DESC;

-- ============================================================================
-- 5. CHECK FOR DUPLICATE TRANSACTION ITEMS
-- ============================================================================
-- This shows if items are inserted multiple times for same transaction
SELECT 
    transaction_id,
    product_name,
    brand,
    quantity,
    COUNT(*) as times_inserted,
    STRING_AGG(DISTINCT id::text, ', ') as row_ids
FROM transaction_items_blaze
WHERE transaction_id IN (
    SELECT transaction_id 
    FROM transactions_blaze 
    WHERE date >= '2025-10-31T00:00:00'
    AND date <= '2025-10-31T23:59:59'
    LIMIT 50  -- Check first 50 transactions
)
GROUP BY transaction_id, product_name, brand, quantity
HAVING COUNT(*) > 1
ORDER BY times_inserted DESC
LIMIT 20;

-- ============================================================================
-- 6. TOTAL OCT 31 STATISTICS
-- ============================================================================
SELECT 
    'Total Transactions' as metric,
    COUNT(DISTINCT transaction_id)::text as value
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'

UNION ALL

SELECT 
    'Unique Customers',
    COUNT(DISTINCT customer_id)::text
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'

UNION ALL

SELECT 
    'Total Revenue',
    '$' || ROUND(SUM(total_amount)::numeric, 2)::text
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'

UNION ALL

SELECT 
    'Avg Transactions per Customer',
    ROUND(
        COUNT(*)::numeric / 
        NULLIF(COUNT(DISTINCT customer_id), 0)::numeric, 
        2
    )::text
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59';

-- ============================================================================
-- 7. CHECK IF THIS IS JUST AN OCT 31 PROBLEM
-- ============================================================================
-- Compare Oct 31 to other days in October
SELECT 
    (date AT TIME ZONE 'America/Los_Angeles')::date as transaction_date,
    COUNT(*) as total_transactions,
    COUNT(DISTINCT customer_id) as unique_customers,
    ROUND(COUNT(*)::numeric / NULLIF(COUNT(DISTINCT customer_id), 0)::numeric, 2) as avg_txns_per_customer
FROM transactions_blaze
WHERE date >= '2025-10-01T00:00:00'
AND date <= '2025-10-31T23:59:59'
GROUP BY (date AT TIME ZONE 'America/Los_Angeles')::date
ORDER BY transaction_date DESC;

-- ============================================================================
-- 8. FIND WHEN DATA WAS SYNCED (Check for multiple sync runs)
-- ============================================================================
SELECT 
    (last_synced_at AT TIME ZONE 'America/Los_Angeles')::date as sync_date,
    COUNT(*) as transactions_synced,
    MIN(last_synced_at AT TIME ZONE 'America/Los_Angeles') as first_sync,
    MAX(last_synced_at AT TIME ZONE 'America/Los_Angeles') as last_sync
FROM transactions_blaze
WHERE date >= '2025-10-31T00:00:00'
AND date <= '2025-10-31T23:59:59'
GROUP BY (last_synced_at AT TIME ZONE 'America/Los_Angeles')::date
ORDER BY sync_date DESC;

-- ============================================================================
-- DIAGNOSIS CHECKLIST
-- ============================================================================
-- [ ] Query 2: Are there duplicate transaction_ids? (Should be UNIQUE)
-- [ ] Query 3: Do many customers have 4+ transactions on Oct 31?
-- [ ] Query 5: Are items duplicated within transactions?
-- [ ] Query 7: Is Oct 31 anomalous compared to other October days?
-- [ ] Query 8: Were there multiple sync runs on Oct 31?

-- LIKELY CAUSES:
-- 1. Backfill script ran multiple times on Oct 31 data
-- 2. transaction_id not properly set as UNIQUE constraint
-- 3. Transaction items inserted multiple times
-- 4. Blaze API pagination issue causing duplicate fetches



