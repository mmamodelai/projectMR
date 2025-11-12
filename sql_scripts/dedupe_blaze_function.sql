-- Create a function to delete duplicates in batches
-- Run this ONCE in Supabase SQL Editor, then call it repeatedly

CREATE OR REPLACE FUNCTION dedupe_transaction_items_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY transaction_id, product_id, quantity, unit_price
                   ORDER BY id DESC
               ) AS rn
        FROM public.transaction_items_blaze
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.transaction_items_blaze t
    USING to_del d
    WHERE t.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

CREATE OR REPLACE FUNCTION dedupe_products_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY id DESC) rn
        FROM public.products_blaze
        WHERE sku IS NOT NULL
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.products_blaze p
    USING to_del d
    WHERE p.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

CREATE OR REPLACE FUNCTION dedupe_transactions_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY id DESC) rn
        FROM public.transactions_blaze
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.transactions_blaze t
    USING to_del d
    WHERE t.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Usage examples:
-- SELECT dedupe_transaction_items_batch(1000);  -- Returns number deleted
-- SELECT dedupe_products_batch(1000);
-- SELECT dedupe_transactions_batch(1000);
-- 
-- Keep calling until it returns 0 (no more duplicates)

