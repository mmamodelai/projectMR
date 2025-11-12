-- ====================================================
-- CHECK BASOL GUNGOR TRANSACTIONS
-- ====================================================

-- 1. Show Basol's record in customers_blaze (current)
SELECT 
    member_id,
    first_name,
    last_name,
    phone,
    total_visits,
    lifetime_value
FROM customers_blaze
WHERE LOWER(first_name) = 'basol'
AND LOWER(last_name) = 'gungor';

-- 2. Check transactions table for Basol's member_id
SELECT 
    customer_id,
    COUNT(*) as tx_count,
    SUM(total_amount) as total_amount
FROM transactions_blaze
WHERE customer_id = '685d86cde2dd4760bd13c14d'
GROUP BY customer_id;

-- 3. Look for transactions that mention Basol in customer_name or notes
SELECT 
    transaction_id,
    customer_id,
    customer_name,
    total_amount,
    blaze_status,
    date
FROM transactions_blaze
WHERE LOWER(customer_name) LIKE '%basol%'
ORDER BY date DESC
LIMIT 50;

-- 4. Check other people sharing phone (619) 368-3370 to see their totals
SELECT 
    t.customer_id,
    c.first_name,
    c.last_name,
    COUNT(*) as tx_count,
    SUM(total_amount) as total_amount
FROM transactions_blaze t
JOIN customers_blaze c ON t.customer_id = c.member_id
WHERE c.phone = '(619) 368-3370'
GROUP BY t.customer_id, c.first_name, c.last_name
ORDER BY tx_count DESC;

-- 5. Check BACKUP to confirm Basol had visits before
SELECT 
    member_id,
    first_name,
    last_name,
    total_visits,
    lifetime_value
FROM customers_blaze_backup_20251106
WHERE LOWER(first_name) = 'basol'
AND LOWER(last_name) = 'gungor';
