-- Create function to get customer purchase history
-- This will be called by MotaBot v5.100 to retrieve full purchase details

CREATE OR REPLACE FUNCTION get_customer_purchase_history(customer_phone TEXT)
RETURNS TABLE (
    transaction_date DATE,
    transaction_id INTEGER,
    total_amount NUMERIC,
    shop_location TEXT,
    staff_name TEXT,
    product_name TEXT,
    product_brand TEXT,
    product_category TEXT,
    quantity INTEGER,
    unit_price NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.date AS transaction_date,
        t.transaction_id,
        t.total_amount,
        t.shop_location,
        t.staff_name,
        ti.product_name,
        ti.brand AS product_brand,
        ti.category AS product_category,
        ti.quantity,
        ti.unit_price
    FROM transactions t
    INNER JOIN customers c ON t.customer_id = c.member_id
    LEFT JOIN transaction_items ti ON t.transaction_id = ti.transaction_id
    WHERE c.phone = customer_phone
    ORDER BY t.date DESC, t.transaction_id DESC
    LIMIT 50;  -- Last 50 purchases
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission to anon role (for n8n)
GRANT EXECUTE ON FUNCTION get_customer_purchase_history TO anon;
GRANT EXECUTE ON FUNCTION get_customer_purchase_history TO authenticated;

COMMENT ON FUNCTION get_customer_purchase_history IS 'Returns purchase history for a customer by phone number. Used by MotaBot AI to answer customer queries about their past purchases.';

