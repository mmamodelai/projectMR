-- View Recent Customer Check-Ins
-- Shows last 20 transactions with check-in and check-out times

SELECT 
    transaction_id AS "Transaction",
    customer_id AS "Customer ID",
    start_time AT TIME ZONE 'America/Los_Angeles' AS "Check-In Time",
    end_time AT TIME ZONE 'America/Los_Angeles' AS "Check-Out Time",
    ROUND(EXTRACT(EPOCH FROM (end_time - start_time)) / 60.0::numeric, 2) AS "Wait (min)",
    total_amount AS "Total $",
    payment_type AS "Payment",
    blaze_status AS "Status"
FROM transactions_blaze
WHERE start_time IS NOT NULL 
AND end_time IS NOT NULL
ORDER BY date DESC
LIMIT 20;

-- Quick Stats
-- SELECT * FROM wait_time_stats_today;



