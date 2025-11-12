-- ===================================================================
-- RESTORE CUSTOMERS_BLAZE FROM BACKUP
-- Run this ONLY if FULL_MERGE_DUPLICATES.sql went wrong!
-- ===================================================================
-- Created: 2025-11-06
-- Purpose: Emergency restore from backup
-- ===================================================================

-- Step 1: Drop the current (messed up) table
DROP TABLE IF EXISTS customers_blaze;

-- Step 2: Restore from backup
CREATE TABLE customers_blaze AS 
SELECT * FROM customers_blaze_backup_20251106;

-- Step 3: Recreate all indexes (critical for performance!)
CREATE INDEX idx_customers_member_id ON customers_blaze(member_id);
CREATE INDEX idx_customers_phone ON customers_blaze(phone);
CREATE INDEX idx_customers_email ON customers_blaze(email);
CREATE INDEX idx_customers_first_name ON customers_blaze(first_name);
CREATE INDEX idx_customers_last_name ON customers_blaze(last_name);
CREATE INDEX idx_customers_vip_status ON customers_blaze(vip_status);
CREATE INDEX idx_customers_last_purchase ON customers_blaze(last_purchase_date);
CREATE INDEX idx_customers_dob ON customers_blaze(date_of_birth);

-- Step 4: Verify restoration
SELECT 
    'RESTORATION COMPLETE!' as status,
    COUNT(*) as total_customers,
    COUNT(DISTINCT member_id) as unique_members,
    COUNT(DISTINCT phone) as unique_phones,
    SUM(total_visits) as total_visits,
    SUM(lifetime_value) as total_lifetime_value,
    pg_size_pretty(pg_total_relation_size('customers_blaze')) as table_size
FROM customers_blaze;

-- Step 5: Check a few sample records
SELECT 
    id,
    first_name,
    last_name,
    phone,
    email,
    total_visits,
    lifetime_value,
    vip_status
FROM customers_blaze
ORDER BY lifetime_value DESC
LIMIT 10;

