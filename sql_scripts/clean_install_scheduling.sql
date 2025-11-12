-- ================================================================
-- CLEAN INSTALL: Drop Everything and Recreate
-- ================================================================
-- Run this to start fresh if you had errors
-- ================================================================

-- Drop views first (they depend on table)
DROP VIEW IF EXISTS scheduled_messages_pst CASCADE;
DROP VIEW IF EXISTS business_hours_status CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS process_scheduled_messages() CASCADE;
DROP FUNCTION IF EXISTS process_scheduled_messages_safe() CASCADE;
DROP FUNCTION IF EXISTS is_business_hours() CASCADE;

-- Drop table
DROP TABLE IF EXISTS public.scheduled_messages CASCADE;

-- ================================================================
-- NOW CREATE EVERYTHING FRESH
-- ================================================================

-- 1. CREATE TABLE
CREATE TABLE public.scheduled_messages (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    phone_number text NOT NULL,
    customer_name text,
    message_content text NOT NULL,
    scheduled_for timestamptz NOT NULL,
    status text NOT NULL DEFAULT 'SCH',
    campaign_message_id bigint,
    campaign_name text,
    sent_at timestamptz,
    error_message text,
    created_at timestamptz DEFAULT timezone('utc'::text, now()),
    updated_at timestamptz DEFAULT timezone('utc'::text, now())
);

-- 2. INDEXES
CREATE INDEX idx_scheduled_messages_status_time ON public.scheduled_messages(status, scheduled_for);
CREATE INDEX idx_scheduled_messages_phone ON public.scheduled_messages(phone_number);

-- 3. RLS
ALTER TABLE public.scheduled_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow all for authenticated" 
    ON public.scheduled_messages FOR ALL TO authenticated USING (true) WITH CHECK (true);

CREATE POLICY "Allow all for anon" 
    ON public.scheduled_messages FOR ALL TO anon USING (true) WITH CHECK (true);

-- 4. FUNCTION: Business Hours Check
CREATE OR REPLACE FUNCTION is_business_hours()
RETURNS boolean
LANGUAGE sql
STABLE
AS $$
    SELECT 
        EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int >= 9
        AND EXTRACT(HOUR FROM now() AT TIME ZONE 'America/Los_Angeles')::int < 20
        AND EXTRACT(DOW FROM now() AT TIME ZONE 'America/Los_Angeles')::int BETWEEN 1 AND 5;
$$;

-- 5. FUNCTION: Process Scheduled Messages
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
    FOR sched_msg IN 
        SELECT * 
        FROM scheduled_messages 
        WHERE status = 'SCH'
        AND scheduled_for AT TIME ZONE 'America/Los_Angeles' <= now() AT TIME ZONE 'America/Los_Angeles'
        ORDER BY scheduled_for
        LIMIT 50
    LOOP
        BEGIN
            bubbles := string_to_array(sched_msg.message_content, '[BUBBLE]');
            bubbles := array_remove(bubbles, '');
            bubbles := array_remove(bubbles, null);
            
            IF array_length(bubbles, 1) IS NULL OR array_length(bubbles, 1) = 0 THEN
                bubbles := ARRAY[sched_msg.message_content];
            END IF;
            
            FOREACH bubble_text IN ARRAY bubbles
            LOOP
                bubble_text := trim(bubble_text);
                
                IF length(bubble_text) > 0 THEN
                    INSERT INTO messages (
                        phone_number, content, status, direction, timestamp
                    ) VALUES (
                        sched_msg.phone_number, bubble_text, 'queued', 'outbound', now()
                    );
                END IF;
            END LOOP;
            
            UPDATE scheduled_messages
            SET status = 'sent', sent_at = now(), updated_at = now()
            WHERE id = sched_msg.id;
            
            processed := processed + 1;
            
        EXCEPTION WHEN OTHERS THEN
            errors := errors || format('Message %s: %s; ', sched_msg.id, SQLERRM);
            
            UPDATE scheduled_messages
            SET status = 'failed', error_message = SQLERRM, updated_at = now()
            WHERE id = sched_msg.id;
        END;
    END LOOP;
    
    RETURN QUERY SELECT processed, errors;
END;
$$;

-- 6. FUNCTION: Safe Process (Business Hours Check)
CREATE OR REPLACE FUNCTION process_scheduled_messages_safe()
RETURNS TABLE(processed_count int, error_message text, skipped_reason text) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result RECORD;
BEGIN
    IF NOT is_business_hours() THEN
        RETURN QUERY SELECT 0, ''::text, 'Outside business hours (9 AM - 8 PM PST, Mon-Fri)'::text;
        RETURN;
    END IF;
    
    FOR result IN 
        SELECT * FROM process_scheduled_messages()
    LOOP
        RETURN QUERY SELECT result.processed_count, result.error_message, NULL::text;
    END LOOP;
END;
$$;

-- 7. VIEW: Scheduled Messages in PST
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

-- 8. VIEW: Business Hours Status
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

-- 9. GRANT PERMISSIONS
GRANT SELECT, INSERT, UPDATE, DELETE ON scheduled_messages TO authenticated, anon;
GRANT EXECUTE ON FUNCTION process_scheduled_messages() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION process_scheduled_messages_safe() TO authenticated, anon;
GRANT EXECUTE ON FUNCTION is_business_hours() TO authenticated, anon;
GRANT SELECT ON scheduled_messages_pst TO authenticated, anon;
GRANT SELECT ON business_hours_status TO authenticated, anon;

-- ================================================================
-- DONE! Now test:
-- SELECT * FROM business_hours_status;
-- ================================================================

