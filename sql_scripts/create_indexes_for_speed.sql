-- ============================================
-- CREATE INDEXES FOR FASTER QUERIES
-- ============================================
-- 
-- PURPOSE: Speed up customer lookups and transaction counts
--
-- These are probably already created, but run this to be sure
--
-- ============================================

-- Customer lookups
CREATE INDEX IF NOT EXISTS idx_customers_blaze_email ON customers_blaze(email) WHERE email IS NOT NULL AND email != '';
CREATE INDEX IF NOT EXISTS idx_customers_blaze_phone ON customers_blaze(phone) WHERE phone IS NOT NULL AND phone != '';
CREATE INDEX IF NOT EXISTS idx_customers_blaze_last_visited ON customers_blaze(last_visited) WHERE last_visited IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_customers_blaze_name ON customers_blaze(first_name, last_name);

-- Transaction lookups (for counting)
CREATE INDEX IF NOT EXISTS idx_transactions_blaze_customer_status ON transactions_blaze(customer_id, blaze_status) WHERE blaze_status = 'Completed';
CREATE INDEX IF NOT EXISTS idx_transactions_blaze_customer_amount ON transactions_blaze(customer_id, total_amount) WHERE blaze_status = 'Completed';

-- Composite index for common queries
CREATE INDEX IF NOT EXISTS idx_customers_blaze_filters ON customers_blaze(last_visited, email, phone) 
WHERE last_visited IS NOT NULL;

-- Analyze tables to update query planner statistics
ANALYZE customers_blaze;
ANALYZE transactions_blaze;

-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as index_scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
AND tablename IN ('customers_blaze', 'transactions_blaze')
ORDER BY idx_scan DESC;

