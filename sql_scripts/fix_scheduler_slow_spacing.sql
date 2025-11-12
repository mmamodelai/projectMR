-- =====================================================================
-- FIX SCHEDULER: SLOW SPACING (5-7 minutes apart, 3 at a time)
-- =====================================================================

DROP FUNCTION IF EXISTS schedule_approved_messages();

CREATE OR REPLACE FUNCTION schedule_approved_messages()
RETURNS TABLE(scheduled_count int, next_send_time timestamptz)
LANGUAGE plpgsql
AS $$
DECLARE
    last_scheduled_time timestamptz;
    next_time timestamptz;
    random_delay_minutes int;
    msg RECORD;
    scheduled int := 0;
BEGIN
    -- Get the last scheduled time (or use NOW if none exist)
    SELECT MAX(scheduled_for) INTO last_scheduled_time
    FROM campaign_messages
    WHERE status = 'SCH';
    
    IF last_scheduled_time IS NULL OR last_scheduled_time < NOW() THEN
        last_scheduled_time := NOW();
    END IF;
    
    -- Loop through APR messages and schedule them ONE BY ONE
    -- ONLY 3 AT A TIME, 5-7 MINUTES APART
    FOR msg IN 
        SELECT id, phone_number, customer_name, message_content
        FROM campaign_messages
        WHERE status = 'APR'
        ORDER BY generated_at ASC
        LIMIT 3  -- Only 3 at a time!
    LOOP
        -- Generate random delay: 5-7 minutes
        random_delay_minutes := 5 + floor(random() * 3)::int;
        
        -- Calculate next send time
        next_time := last_scheduled_time + (random_delay_minutes || ' minutes')::interval;
        
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
        last_scheduled_time := next_time;
    END LOOP;
    
    RETURN QUERY SELECT scheduled, last_scheduled_time;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION schedule_approved_messages TO authenticated, anon;

-- =====================================================================
-- NEW BEHAVIOR:
-- - Schedules ONLY 3 messages per run
-- - 5-7 minutes apart (random)
-- - No batching, no bursts
-- - Call this function repeatedly to schedule more
-- =====================================================================

