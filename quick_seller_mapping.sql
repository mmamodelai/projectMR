-- Quick Seller ID Mapping
-- Map the top seller_ids to staff names

-- First, see what seller_ids exist and their transaction counts
SELECT
    seller_id,
    COUNT(*) as transaction_count,
    ROUND(SUM(total_amount), 2) as total_sales
FROM transactions_blaze
WHERE seller_id IS NOT NULL
GROUP BY seller_id
ORDER BY transaction_count DESC
LIMIT 20;

-- Then manually map them (replace with actual staff names):
/*
UPDATE sellers_blaze SET seller_name = 'Jimmy Silks' WHERE seller_id = '6096c37abebf144f90cb0a5a';
UPDATE sellers_blaze SET seller_name = 'Devon Calonzo' WHERE seller_id = '60ccd68ef8b2482f5c6cec14';
UPDATE sellers_blaze SET seller_name = 'Bob McGinn' WHERE seller_id = '62099b715a533c534697daa7';
-- etc...
*/

-- After mapping, restart the viewer to see the names!

