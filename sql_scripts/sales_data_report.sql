-- Sales Data Report for Specific Dates
-- Request: Sept 25, Oct 25, Nov 1-5, Dec 24
-- Run this in Supabase SQL Editor

-- ==========================================
-- PART 1: BLAZE API DATA (Most Complete)
-- ==========================================

SELECT 
    'BLAZE DATA' as data_source,
    DATE(date) as sale_date,
    COUNT(*) as total_transactions,
    SUM(total_amount) as gross_sales,
    SUM(total_tax) as total_tax,
    SUM(discounts) as total_discounts,
    SUM(total_amount - COALESCE(discounts, 0)) as net_sales,
    AVG(total_amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions_blaze
WHERE 
    DATE(date) IN (
        '2024-12-24',  -- Dec 24, 2024
        '2025-09-25',  -- Sept 25, 2025
        '2025-10-25',  -- Oct 25, 2025
        '2025-11-01',  -- Nov 1, 2025
        '2025-11-02',  -- Nov 2, 2025
        '2025-11-03',  -- Nov 3, 2025
        '2025-11-04',  -- Nov 4, 2025
        '2025-11-05'   -- Nov 5, 2025
    )
    AND blaze_status = 'Completed'  -- Only completed transactions
    AND total_amount > 0  -- Exclude refunds/negatives
GROUP BY DATE(date)
ORDER BY DATE(date);

-- ==========================================
-- PART 2: CSV/ORIGINAL DATA (Historical)
-- ==========================================

SELECT 
    'CSV DATA' as data_source,
    DATE(date) as sale_date,
    COUNT(*) as total_transactions,
    SUM(total_amount) as gross_sales,
    SUM(total_tax) as total_tax,
    SUM(discounts) as total_discounts,
    SUM(total_amount - COALESCE(discounts, 0)) as net_sales,
    AVG(total_amount) as avg_transaction_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM transactions
WHERE 
    DATE(date) IN (
        '2024-12-24',  -- Dec 24, 2024
        '2025-09-25',  -- Sept 25, 2025
        '2025-10-25',  -- Oct 25, 2025
        '2025-11-01',  -- Nov 1, 2025
        '2025-11-02',  -- Nov 2, 2025
        '2025-11-03',  -- Nov 3, 2025
        '2025-11-04',  -- Nov 4, 2025
        '2025-11-05'   -- Nov 5, 2025
    )
    AND total_amount > 0  -- Exclude refunds/negatives
GROUP BY DATE(date)
ORDER BY DATE(date);

-- ==========================================
-- PART 3: COMBINED SUMMARY (All Dates)
-- ==========================================

WITH combined_data AS (
    -- Blaze data
    SELECT 
        'BLAZE' as source,
        DATE(date) as sale_date,
        COUNT(*) as transactions,
        SUM(total_amount) as gross_sales
    FROM transactions_blaze
    WHERE 
        DATE(date) IN (
            '2024-12-24', '2025-09-25', '2025-10-25',
            '2025-11-01', '2025-11-02', '2025-11-03', 
            '2025-11-04', '2025-11-05'
        )
        AND blaze_status = 'Completed'
        AND total_amount > 0
    GROUP BY DATE(date)
    
    UNION ALL
    
    -- CSV data
    SELECT 
        'CSV' as source,
        DATE(date) as sale_date,
        COUNT(*) as transactions,
        SUM(total_amount) as gross_sales
    FROM transactions
    WHERE 
        DATE(date) IN (
            '2024-12-24', '2025-09-25', '2025-10-25',
            '2025-11-01', '2025-11-02', '2025-11-03', 
            '2025-11-04', '2025-11-05'
        )
        AND total_amount > 0
    GROUP BY DATE(date)
)
SELECT 
    sale_date,
    MAX(CASE WHEN source = 'BLAZE' THEN transactions END) as blaze_transactions,
    MAX(CASE WHEN source = 'CSV' THEN transactions END) as csv_transactions,
    MAX(CASE WHEN source = 'BLAZE' THEN gross_sales END) as blaze_gross_sales,
    MAX(CASE WHEN source = 'CSV' THEN gross_sales END) as csv_gross_sales,
    -- Use Blaze if available, otherwise CSV
    COALESCE(MAX(CASE WHEN source = 'BLAZE' THEN transactions END), 
             MAX(CASE WHEN source = 'CSV' THEN transactions END)) as best_transaction_count,
    COALESCE(MAX(CASE WHEN source = 'BLAZE' THEN gross_sales END), 
             MAX(CASE WHEN source = 'CSV' THEN gross_sales END)) as best_gross_sales
FROM combined_data
GROUP BY sale_date
ORDER BY sale_date;

-- ==========================================
-- PART 4: HOURLY BREAKDOWN (if needed)
-- ==========================================

SELECT 
    DATE(date) as sale_date,
    EXTRACT(HOUR FROM date) as hour_of_day,
    COUNT(*) as transactions,
    SUM(total_amount) as gross_sales,
    AVG(total_amount) as avg_transaction
FROM transactions_blaze
WHERE 
    DATE(date) IN (
        '2024-12-24', '2025-09-25', '2025-10-25',
        '2025-11-01', '2025-11-02', '2025-11-03', 
        '2025-11-04', '2025-11-05'
    )
    AND blaze_status = 'Completed'
    AND total_amount > 0
GROUP BY DATE(date), EXTRACT(HOUR FROM date)
ORDER BY DATE(date), EXTRACT(HOUR FROM date);

-- ==========================================
-- PART 5: TOP PRODUCTS FOR THESE DATES (Bonus)
-- ==========================================

SELECT 
    DATE(t.date) as sale_date,
    ti.product_name,
    ti.brand,
    COUNT(*) as times_sold,
    SUM(ti.quantity) as total_quantity,
    SUM(ti.total_price) as total_revenue
FROM transactions_blaze t
JOIN transaction_items_blaze ti ON t.transaction_id = ti.transaction_id
WHERE 
    DATE(t.date) IN (
        '2024-12-24', '2025-09-25', '2025-10-25',
        '2025-11-01', '2025-11-02', '2025-11-03', 
        '2025-11-04', '2025-11-05'
    )
    AND t.blaze_status = 'Completed'
    AND t.total_amount > 0
GROUP BY DATE(t.date), ti.product_name, ti.brand
ORDER BY DATE(t.date), total_revenue DESC;

-- ==========================================
-- PART 6: PAYMENT METHOD BREAKDOWN
-- ==========================================

SELECT 
    DATE(date) as sale_date,
    payment_type,
    COUNT(*) as transactions,
    SUM(total_amount) as gross_sales,
    ROUND(COUNT(*)::numeric / SUM(COUNT(*)) OVER (PARTITION BY DATE(date)) * 100, 2) as pct_of_day_transactions
FROM transactions_blaze
WHERE 
    DATE(date) IN (
        '2024-12-24', '2025-09-25', '2025-10-25',
        '2025-11-01', '2025-11-02', '2025-11-03', 
        '2025-11-04', '2025-11-05'
    )
    AND blaze_status = 'Completed'
    AND total_amount > 0
GROUP BY DATE(date), payment_type
ORDER BY DATE(date), gross_sales DESC;



