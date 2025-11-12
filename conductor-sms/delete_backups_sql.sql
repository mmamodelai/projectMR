-- COPY AND PASTE THIS ENTIRE FILE INTO SUPABASE SQL EDITOR AND RUN IT
-- This will delete backup tables immediately

-- Delete blaze_api_samples
DROP TABLE IF EXISTS public.blaze_api_samples CASCADE;

-- Delete blaze_sync_state
DROP TABLE IF EXISTS public.blaze_sync_state CASCADE;

-- Reclaim space
VACUUM ANALYZE;

