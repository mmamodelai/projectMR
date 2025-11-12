-- ================================================================
-- CAMPAIGN SCHEDULING SYSTEM - SUPABASE NATIVE
-- ================================================================
-- Handles scheduling with Pacific Time business hours
-- Status Flow: SUG → APR → SCH → messages(queued) → messages(sent)
-- ================================================================

-- ================================================================
-- 1. CREATE scheduled_messages TABLE
-- ================================================================
CREATE TABLE IF NOT EXISTS public.scheduled_messages (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    phone_number text NOT NULL,
    customer_name text,
    message_content text NOT NULL,
    scheduled_for timestamptz NOT NULL,  -- UTC timestamp
    status text NOT NULL DEFAULT 'SCH',  -- SCH, sent, cancelled, failed
    campaign_message_id bigint,
    campaign_name text,
    sent_at timestamptz,
    error_message text,
    created_at timestamptz DEFAULT timezone('utc'::text, now()),
    updated_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_scheduled_messages_status_time 
    ON public.scheduled_messages(status, scheduled_for);

CREATE INDEX IF NOT EXISTS idx_scheduled_messages_phone 
    ON public.scheduled_messages(phone_number);

-- Enable RLS
ALTER TABLE public.scheduled_messages ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Allow all for authenticated" 
    ON public.scheduled_messages FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" 
    ON public.scheduled_messages FOR ALL TO anon USING (true) WITH CHECK (true);

-- ================================================================
-- 2. CREATE FUNCTION: Process Scheduled Messages
-- ================================================================
-- This function:
-- 1. Finds messages where scheduled_for <= now (in Pacific Time)
-- 2. Splits message by [BUBBLE] markers
-- 3. Inserts each bubble into messages table as 'queued'
-- 4. Updates scheduled_messages status to 'sent'
-- ================================================================

CREATE OR REPLACE FUNCTION process_scheduled_messages()
RETURNS TABLE(processed_count int, error_message text) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    sched_msg RECORD;
    bubble_text text;
    bubbles text[];
    processed int := 0;
    errors text := '';
BEGIN
    -- Find scheduled messages where time has arrived (Pacific Time)
    -- Convert both scheduled_for and now() to Pacific Time for comparison
    FOR sched_msg IN 
        SELECT * 
        FROM scheduled_messages 
        WHERE status = 'SCH'
        AND scheduled_for AT TIME ZONE 'America/Los_Angeles' <= now() AT TIME ZONE 'America/Los_Angeles'
        ORDER BY scheduled_for
        LIMIT 50  -- Process 50 at a time to avoid timeouts
    LOOP
        BEGIN
            -- Split message by [BUBBLE] markers
            bubbles := string_to_array(sched_msg.message_content, '[BUBBLE]');
            
            -- Clean up bubbles (trim whitespace, remove empty)
            bubbles := array_remove(bubbles, '');
            bubbles := array_remove(bubbles, null);
            
            -- If no bubbles after split, use original message
            IF array_length(bubbles, 1) IS NULL OR array_length(bubbles, 1) = 0 THEN
                bubbles := ARRAY[sched_msg.message_content];
            END IF;
            
            -- Insert each bubble as separate queued message
            FOREACH bubble_text IN ARRAY bubbles
            LOOP
                -- Trim whitespace from bubble
                bubble_text := trim(bubble_text);
                
                -- Skip empty bubbles
                IF length(bubble_text) > 0 THEN
                    INSERT INTO messages (
                        phone_number,
                        content,
                        status,
                        direction,
                        timestamp
                    ) VALUES (
                        sched_msg.phone_number,
                        bubble_text,
                        'queued',
                        'outbound',
                        now()
                    );
                END IF;
            END LOOP;
            
            -- Update scheduled_messages to 'sent'
            UPDATE scheduled_messages
            SET 
                status = 'sent',
                sent_at = now(),
                updated_at = now()
            WHERE id = sched_msg.id;
            
            processed := processed + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Log error and mark as failed
            errors := errors || format('Message %s: %s; ', sched_msg.id, SQLERRM);
            
            UPDATE scheduled_messages
            SET 
                status = 'failed',
                error_message = SQLERRM,
                updated_at = now()
            WHERE id = sched_msg.id;
        END;
    END LOOP;
    
    RETURN QUERY SELECT processed, errors;
END;
$$;

-- ================================================================
-- 3. CREATE FUNCTION: Check Business Hours (Pacific Time)
-- ================================================================
-- Returns true if current time is within business hours (9 AM - 8 PM PST)
-- ================================================================

CREATE OR REPLACE FUNCTION is_business_hours()
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT 
        EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int >= 9
        AND EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int < 20
        AND EXTRACT(DOW FROM now() AT TIME ZONE 'America/Los_Angeles')::int BETWEEN 1 AND 5;  -- Mon-Fri
$$;

-- ================================================================
-- 4. CREATE FUNCTION: Safe Process (Only During Business Hours)
-- ================================================================

CREATE OR REPLACE FUNCTION process_scheduled_messages_safe()
RETURNS TABLE(processed_count int, error_message text, skipped_reason text) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result RECORD;
BEGIN
    -- Check if we're in business hours
    IF NOT is_business_hours() THEN
        RETURN QUERY SELECT 0, ''::text, 'Outside business hours (9 AM - 8 PM PST, Mon-Fri)'::text;
        RETURN;
    END IF;
    
    -- Process messages
    FOR result IN 
        SELECT * FROM process_scheduled_messages()
    LOOP
        RETURN QUERY SELECT result.processed_count, result.error_message, NULL::text;
    END LOOP;
END;
$$;

-- ================================================================
-- 5. ENABLE pg_cron EXTENSION (if not already enabled)
-- ================================================================
-- NOTE: This requires Supabase Pro plan or database admin access
-- If you can't enable pg_cron, we'll fall back to Conductor checking

-- Uncomment if you have pg_cron access:
-- CREATE EXTENSION IF NOT EXISTS pg_cron;

-- ================================================================
-- 6. CREATE CRON JOB (runs every minute)
-- ================================================================
-- NOTE: Only run this if pg_cron is available
-- Otherwise, Conductor will check scheduled_messages

-- Uncomment if you have pg_cron:
-- SELECT cron.schedule(
--     'process-scheduled-messages',  -- Job name
--     '* * * * *',                    -- Every minute
--     $$SELECT * FROM process_scheduled_messages_safe()$$
-- );

-- ================================================================
-- 7. HELPER VIEWS
-- ================================================================

-- View: Scheduled messages in Pacific Time (easier to read)
CREATE OR REPLACE VIEW scheduled_messages_pst AS
SELECT 
    id,
    customer_name,
    phone_number,
    scheduled_for AT TIME ZONE 'America/Los_Angeles' as scheduled_for_pst,
    scheduled_for as scheduled_for_utc,
    status,
    campaign_name,
    CASE 
        WHEN status = 'SCH' AND scheduled_for > now() THEN 
            EXTRACT(EPOCH FROM (scheduled_for - now())) / 60
        ELSE NULL 
    END as minutes_until_send,
    created_at AT TIME ZONE 'America/Los_Angeles' as created_at_pst
FROM scheduled_messages
WHERE status = 'SCH'
ORDER BY scheduled_for;

-- View: Business hours status
CREATE OR REPLACE VIEW business_hours_status AS
SELECT 
    is_business_hours() as is_business_hours,
    (now() AT TIME ZONE 'America/Los_Angeles')::timestamp as current_pacific_time,
    EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int as current_hour_pst,
    EXTRACT(DOW FROM now() AT TIME ZONE 'America/Los_Angeles')::int as day_of_week_pst,
    CASE EXTRACT(DOW FROM now() AT TIME ZONE 'America/Los_Angeles')::int
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END as day_name;

-- ================================================================
-- 8. GRANT PERMISSIONS
-- ================================================================

GRANT SELECT, INSERT, UPDATE, DELETE ON scheduled_messages TO authenticated, anon;
GRANT EXECUTE ON FUNCTION process_scheduled_messages() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION process_scheduled_messages_safe() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION is_business_hours() TO authenticated, anon;
GRANT SELECT ON scheduled_messages_pst TO authenticated, anon;
GRANT SELECT ON business_hours_status TO authenticated, anon;

-- ================================================================
-- DONE! 
-- ================================================================
-- 
-- To test:
-- 1. Check current time: SELECT * FROM business_hours_status;
-- 2. Manually process: SELECT * FROM process_scheduled_messages_safe();
-- 3. View schedule in PST: SELECT * FROM scheduled_messages_pst;
--
-- ================================================================

