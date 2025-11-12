-- =====================================================================
-- CAMPAIGN SCHEDULER - Business Hours & Batch Auto-Scheduling
-- =====================================================================
-- This creates server-side functions to:
-- 1. Schedule APR messages in BATCHES (8-13 msgs) with 10-14 min breaks
-- 2. Within batch: 30-60 second delays (human-like burst sending)
-- 3. Move SCH messages to 'messages' table as 'queued' when time arrives
-- 4. Preserve [BUBBLE] order when queueing
-- 5. Enforce business hours (Mon-Fri 10:15 AM - 6:30 PM, Sat 11 AM - 9 PM PST)
-- =====================================================================

-- =====================================================================
-- STEP 1: Drop existing functions if they exist
-- =====================================================================
DROP FUNCTION IF EXISTS is_business_hours_pst(timestamptz);
DROP FUNCTION IF EXISTS schedule_approved_messages();
DROP FUNCTION IF EXISTS process_scheduled_messages();

-- =====================================================================
-- STEP 2: Add scheduled_for column to campaign_messages (if missing)
-- =====================================================================
ALTER TABLE campaign_messages 
ADD COLUMN IF NOT EXISTS scheduled_for timestamptz;

-- =====================================================================
-- STEP 3: Helper Function - Check if time is within business hours
-- =====================================================================
CREATE OR REPLACE FUNCTION is_business_hours_pst(check_time timestamptz)
RETURNS boolean
LANGUAGE plpgsql
AS $$
DECLARE
    pst_time timestamptz;
    day_of_week int;
    hour_of_day int;
BEGIN
    -- Convert to Pacific Time
    pst_time := check_time AT TIME ZONE 'America/Los_Angeles';
    
    -- Get day of week (0=Sunday, 1=Monday, ..., 6=Saturday)
    day_of_week := EXTRACT(DOW FROM pst_time);
    
    -- Get hour (0-23)
    hour_of_day := EXTRACT(HOUR FROM pst_time);
    
    -- Monday-Friday (1-5): 10:15 AM - 6:30 PM
    IF day_of_week BETWEEN 1 AND 5 THEN
        -- 10:15 AM = hour 10 + 15 min
        -- 6:30 PM = hour 18 + 30 min
        IF hour_of_day > 10 AND hour_of_day < 18 THEN
            RETURN TRUE;
        END IF;
        IF hour_of_day = 10 AND EXTRACT(MINUTE FROM pst_time) >= 15 THEN
            RETURN TRUE;
        END IF;
        IF hour_of_day = 18 AND EXTRACT(MINUTE FROM pst_time) <= 30 THEN
            RETURN TRUE;
        END IF;
    END IF;
    
    -- Saturday (6): 11 AM - 9 PM
    IF day_of_week = 6 THEN
        IF hour_of_day >= 11 AND hour_of_day < 21 THEN
            RETURN TRUE;
        END IF;
    END IF;
    
    -- Sunday (0): No sending
    RETURN FALSE;
END;
$$;

-- =====================================================================
-- STEP 4: Schedule Approved Messages (APR → SCH) - BATCH MODE
-- =====================================================================
CREATE OR REPLACE FUNCTION schedule_approved_messages()
RETURNS TABLE(scheduled_count int, next_send_time timestamptz)
LANGUAGE plpgsql
AS $$
DECLARE
    last_scheduled_time timestamptz;
    next_time timestamptz;
    batch_size int;
    batch_break_minutes int;
    msg RECORD;
    scheduled int := 0;
    batch_count int := 0;
    in_batch_delay_seconds int;
BEGIN
    -- Get the last scheduled time (or use NOW if none exist)
    SELECT MAX(scheduled_for) INTO last_scheduled_time
    FROM campaign_messages
    WHERE status = 'SCH';
    
    IF last_scheduled_time IS NULL OR last_scheduled_time < NOW() THEN
        last_scheduled_time := NOW();
    END IF;
    
    -- Loop through APR messages and schedule them in batches
    FOR msg IN 
        SELECT id, phone_number, customer_name, message_content
        FROM campaign_messages
        WHERE status = 'APR'
        ORDER BY generated_at ASC
        LIMIT 100  -- Process 100 at a time
    LOOP
        -- Start new batch?
        IF batch_count = 0 THEN
            -- Random batch size: 8-13 messages
            batch_size := 8 + floor(random() * 6)::int;
            
            -- If this is not the first batch, add 10-14 min break
            IF scheduled > 0 THEN
                batch_break_minutes := 10 + floor(random() * 5)::int;
                last_scheduled_time := last_scheduled_time + (batch_break_minutes || ' minutes')::interval;
            END IF;
            
            batch_count := 0;
        END IF;
        
        -- Small delay within batch (30-60 seconds between messages)
        in_batch_delay_seconds := 30 + floor(random() * 31)::int;
        next_time := last_scheduled_time + (in_batch_delay_seconds || ' seconds')::interval;
        
        -- Skip ahead to next business hours if needed
        WHILE NOT is_business_hours_pst(next_time) LOOP
            -- If outside business hours, jump to next business day start
            IF EXTRACT(DOW FROM (next_time AT TIME ZONE 'America/Los_Angeles')) = 0 THEN
                -- Sunday → Monday 10:15 AM
                next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                           + interval '1 day' 
                           + interval '10 hours 15 minutes';
                next_time := next_time AT TIME ZONE 'America/Los_Angeles';
            ELSIF EXTRACT(DOW FROM (next_time AT TIME ZONE 'America/Los_Angeles')) = 6 THEN
                -- Saturday after 9 PM → Monday 10:15 AM
                IF EXTRACT(HOUR FROM (next_time AT TIME ZONE 'America/Los_Angeles')) >= 21 THEN
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '2 days' 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                ELSE
                    -- Saturday before 11 AM → 11 AM
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '11 hours';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                END IF;
            ELSE
                -- Weekday outside hours
                IF EXTRACT(HOUR FROM (next_time AT TIME ZONE 'America/Los_Angeles')) < 10 THEN
                    -- Before 10:15 AM → 10:15 AM same day
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                ELSE
                    -- After 6:30 PM → Next day 10:15 AM
                    next_time := date_trunc('day', next_time AT TIME ZONE 'America/Los_Angeles') 
                               + interval '1 day' 
                               + interval '10 hours 15 minutes';
                    next_time := next_time AT TIME ZONE 'America/Los_Angeles';
                END IF;
            END IF;
        END LOOP;
        
        -- Update message: APR → SCH
        UPDATE campaign_messages
        SET 
            status = 'SCH',
            scheduled_for = next_time,
            updated_at = NOW()
        WHERE id = msg.id;
        
        scheduled := scheduled + 1;
        batch_count := batch_count + 1;
        last_scheduled_time := next_time;
        
        -- Reset batch_count when batch is full
        IF batch_count >= batch_size THEN
            batch_count := 0;
        END IF;
    END LOOP;
    
    RETURN QUERY SELECT scheduled, last_scheduled_time;
END;
$$;

-- =====================================================================
-- STEP 5: Process Scheduled Messages (SCH → messages table as queued)
-- =====================================================================
CREATE OR REPLACE FUNCTION process_scheduled_messages()
RETURNS TABLE(processed_count int, messages_queued int)
LANGUAGE plpgsql
AS $$
DECLARE
    msg RECORD;
    bubble TEXT;
    bubbles TEXT[];
    processed int := 0;
    queued int := 0;
BEGIN
    -- Find SCH messages where scheduled_for <= NOW()
    FOR msg IN 
        SELECT id, phone_number, message_content
        FROM campaign_messages
        WHERE status = 'SCH' 
          AND scheduled_for <= NOW()
        ORDER BY scheduled_for ASC
        LIMIT 50  -- Process 50 at a time
    LOOP
        -- Split message by [BUBBLE] markers
        bubbles := string_to_array(msg.message_content, '[BUBBLE]');
        
        -- Insert each bubble as separate queued message
        FOREACH bubble IN ARRAY bubbles
        LOOP
            bubble := trim(bubble);
            IF length(bubble) > 0 THEN
                INSERT INTO messages (phone_number, content, status, direction, timestamp)
                VALUES (
                    msg.phone_number,
                    bubble,
                    'queued',
                    'outbound',
                    NOW()
                );
                queued := queued + 1;
            END IF;
        END LOOP;
        
        -- Update campaign_messages: SCH → sent
        UPDATE campaign_messages
        SET 
            status = 'sent',
            updated_at = NOW()
        WHERE id = msg.id;
        
        processed := processed + 1;
    END LOOP;
    
    RETURN QUERY SELECT processed, queued;
END;
$$;

-- =====================================================================
-- STEP 6: Create views for monitoring
-- =====================================================================

-- Drop existing views first
DROP VIEW IF EXISTS scheduled_messages_view;
DROP VIEW IF EXISTS business_hours_status;

-- View: Scheduled messages in PST
CREATE OR REPLACE VIEW scheduled_messages_view AS
SELECT 
    id,
    customer_name,
    phone_number,
    LEFT(message_content, 50) as message_preview,
    status,
    scheduled_for AT TIME ZONE 'America/Los_Angeles' as scheduled_pst,
    generated_at
FROM campaign_messages
WHERE status = 'SCH'
ORDER BY scheduled_for ASC;

-- View: Current business hours status
CREATE OR REPLACE VIEW business_hours_status AS
SELECT 
    NOW() AT TIME ZONE 'America/Los_Angeles' as current_time_pst,
    is_business_hours_pst(NOW()) as is_open,
    CASE 
        WHEN is_business_hours_pst(NOW()) THEN 'OPEN - Messages will send'
        ELSE 'CLOSED - Messages will wait'
    END as status;

-- =====================================================================
-- STEP 7: Grant permissions
-- =====================================================================
GRANT EXECUTE ON FUNCTION is_business_hours_pst TO authenticated, anon;
GRANT EXECUTE ON FUNCTION schedule_approved_messages TO authenticated, anon;
GRANT EXECUTE ON FUNCTION process_scheduled_messages TO authenticated, anon;
GRANT SELECT ON scheduled_messages_view TO authenticated, anon;
GRANT SELECT ON business_hours_status TO authenticated, anon;

-- =====================================================================
-- DONE! Usage:
-- =====================================================================
-- Manual trigger:
--   SELECT * FROM schedule_approved_messages();   -- Schedule APR messages
--   SELECT * FROM process_scheduled_messages();   -- Queue SCH messages
--
-- Check status:
--   SELECT * FROM business_hours_status;          -- Are we open?
--   SELECT * FROM scheduled_messages_view;        -- What's scheduled?
--
-- Automation:
--   - Call from Conductor's polling loop
--   - Use pg_cron (if enabled on Supabase Pro)
--   - Call from Python script every minute
-- =====================================================================

