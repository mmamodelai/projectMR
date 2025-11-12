-- Create functions to COUNT duplicates (fast, server-side)
-- Run this in Supabase SQL Editor first

CREATE OR REPLACE FUNCTION count_duplicate_transaction_items()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    dup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dup_count
    FROM (
        SELECT transaction_id, product_id, quantity, unit_price, COUNT(*) as cnt
        FROM public.transaction_items_blaze
        GROUP BY transaction_id, product_id, quantity, unit_price
        HAVING COUNT(*) > 1
    ) g;
    
    RETURN dup_count;
END;
$$;

CREATE OR REPLACE FUNCTION count_duplicate_products()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    dup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dup_count
    FROM (
        SELECT sku, COUNT(*) as cnt
        FROM public.products_blaze
        WHERE sku IS NOT NULL
        GROUP BY sku
        HAVING COUNT(*) > 1
    ) g;
    
    RETURN dup_count;
END;
$$;

CREATE OR REPLACE FUNCTION count_duplicate_transactions()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    dup_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO dup_count
    FROM (
        SELECT transaction_id, COUNT(*) as cnt
        FROM public.transactions_blaze
        GROUP BY transaction_id
        HAVING COUNT(*) > 1
    ) g;
    
    RETURN dup_count;
END;
$$;

-- Usage:
-- SELECT count_duplicate_transaction_items();  -- Returns number of duplicate groups
-- SELECT count_duplicate_products();
-- SELECT count_duplicate_transactions();

