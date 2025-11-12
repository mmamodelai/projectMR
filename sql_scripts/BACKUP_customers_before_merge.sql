-- ===================================================================
-- BACKUP CUSTOMERS_BLAZE TABLE
-- Before running FULL_MERGE_DUPLICATES.sql
-- ===================================================================
-- Created: 2025-11-06
-- Purpose: Create complete backup of customers_blaze before merge
-- ===================================================================

-- Step 1: Create backup table with today's date
-- (Drop if already exists - you can run this multiple times)
DROP TABLE IF EXISTS customers_blaze_backup_20251106;

CREATE TABLE customers_blaze_backup_20251106 AS 
SELECT * FROM customers_blaze;

-- Step 2: Add indexes to backup (makes restore faster if needed)
CREATE INDEX idx_backup_member_id ON customers_blaze_backup_20251106(member_id);
CREATE INDEX idx_backup_phone ON customers_blaze_backup_20251106(phone);
CREATE INDEX idx_backup_email ON customers_blaze_backup_20251106(email);

-- Step 3: Report backup statistics
SELECT 
    'BACKUP COMPLETE!' as status,
    (SELECT COUNT(*) FROM customers_blaze) as original_count,
    (SELECT COUNT(*) FROM customers_blaze_backup_20251106) as backup_count,
    (SELECT COUNT(DISTINCT member_id) FROM customers_blaze) as original_unique_members,
    (SELECT COUNT(DISTINCT member_id) FROM customers_blaze_backup_20251106) as backup_unique_members,
    pg_size_pretty(pg_total_relation_size('customers_blaze')) as original_size,
    pg_size_pretty(pg_total_relation_size('customers_blaze_backup_20251106')) as backup_size;

-- Step 4: Verify critical data is backed up
SELECT 
    'VERIFICATION' as check_type,
    COUNT(*) as total_records,
    COUNT(DISTINCT phone) as unique_phones,
    COUNT(DISTINCT email) as unique_emails,
    SUM(total_visits) as total_visits_sum,
    SUM(lifetime_value) as total_lifetime_value
FROM customers_blaze_backup_20251106;

-- ===================================================================
-- TO RESTORE FROM BACKUP (IF SOMETHING GOES WRONG):
-- ===================================================================
-- Run these commands:
--
-- -- 1. Delete the messed up table
-- DROP TABLE customers_blaze;
--
-- -- 2. Restore from backup
-- CREATE TABLE customers_blaze AS 
-- SELECT * FROM customers_blaze_backup_20251106;
--
-- -- 3. Recreate indexes
-- CREATE INDEX idx_customers_member_id ON customers_blaze(member_id);
-- CREATE INDEX idx_customers_phone ON customers_blaze(phone);
-- CREATE INDEX idx_customers_email ON customers_blaze(email);
-- CREATE INDEX idx_customers_first_name ON customers_blaze(first_name);
-- CREATE INDEX idx_customers_last_name ON customers_blaze(last_name);
-- CREATE INDEX idx_customers_vip_status ON customers_blaze(vip_status);
-- CREATE INDEX idx_customers_last_purchase ON customers_blaze(last_purchase_date);
--
-- -- 4. Verify restoration
-- SELECT COUNT(*) FROM customers_blaze;
-- ===================================================================

