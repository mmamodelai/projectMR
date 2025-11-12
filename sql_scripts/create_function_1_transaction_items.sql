-- Function 1: Deduplicate transaction_items_blaze
-- Run this FIRST in Supabase SQL Editor

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

-- Test it: SELECT dedupe_transaction_items_batch(1000);

