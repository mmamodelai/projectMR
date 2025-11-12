-- ============================================
-- RESTORE FROM BACKUP
-- ============================================

-- Step 1: Drop current table
DROP TABLE IF EXISTS customers_blaze;

-- Step 2: Restore from backup
CREATE TABLE customers_blaze AS 
SELECT * FROM customers_blaze_backup_20251106;

-- Step 3: Recreate indexes (for performance)
CREATE INDEX IF NOT EXISTS idx_customers_member_id ON customers_blaze(member_id);
CREATE INDEX IF NOT EXISTS idx_customers_phone ON customers_blaze(phone);
CREATE INDEX IF NOT EXISTS idx_customers_email ON customers_blaze(email);
CREATE INDEX IF NOT EXISTS idx_customers_first_name ON customers_blaze(first_name);
CREATE INDEX IF NOT EXISTS idx_customers_last_name ON customers_blaze(last_name);

-- Step 4: Verify restoration
SELECT 
    '✓ RESTORATION COMPLETE!' as status,
    COUNT(*) as total_customers,
    COUNT(DISTINCT member_id) as unique_members
FROM customers_blaze;

-- Step 5: Check medgo is back
SELECT 
    'medgo artea drots status' as check,
    COUNT(*) as medgo_records
FROM customers_blaze
WHERE LOWER(TRIM(first_name)) = 'medgo'
AND LOWER(TRIM(last_name)) = 'drots';

-- Step 6: Count duplicates
SELECT 
    'Duplicate Status' as check,
    COUNT(*) as total_records,
    COUNT(DISTINCT CONCAT(
        LOWER(TRIM(first_name)), 
        '|', 
        LOWER(TRIM(last_name)), 
        '|', 
        COALESCE(date_of_birth::TEXT, 'null')
    )) as unique_people,
    COUNT(*) - COUNT(DISTINCT CONCAT(
        LOWER(TRIM(first_name)), 
        '|', 
        LOWER(TRIM(last_name)), 
        '|', 
        COALESCE(date_of_birth::TEXT, 'null')
    )) as duplicates_remaining
FROM customers_blaze;

