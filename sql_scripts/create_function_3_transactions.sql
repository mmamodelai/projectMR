-- Function 3: Deduplicate transactions_blaze
-- Run this THIRD in Supabase SQL Editor

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

-- Test it: SELECT dedupe_transactions_batch(1000);

