-- ============================================================
-- CHECK FOR BLOCKING QUERIES
-- ============================================================
-- See what's locking transaction_items_blaze

-- Find active queries
SELECT 
    pid,
    usename,
    state,
    query_start,
    now() - query_start AS duration,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE state != 'idle'
AND query NOT LIKE '%pg_stat_activity%'
ORDER BY query_start;

-- ============================================================
-- Check for locks on transaction_items_blaze
-- ============================================================
SELECT 
    l.pid,
    l.locktype,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.query_start,
    now() - a.query_start AS duration
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.relation = 'transaction_items_blaze'::regclass
OR l.relation::text LIKE '%transaction_items_blaze%';

-- ============================================================
-- Kill blocking queries (if needed)
-- ============================================================
-- SELECT pg_terminate_backend(pid) FROM pg_stat_activity 
-- WHERE pid IN (SELECT blocking_pid FROM pg_locks WHERE ...);
-- USE WITH CAUTION!

