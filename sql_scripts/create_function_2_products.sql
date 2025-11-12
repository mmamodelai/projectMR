-- Function 2: Deduplicate products_blaze
-- Run this SECOND in Supabase SQL Editor

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

-- Test it: SELECT dedupe_products_batch(1000);

