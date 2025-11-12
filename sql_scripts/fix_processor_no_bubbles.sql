-- =====================================================================
-- UPDATE PROCESSOR: NO BUBBLE SPLITTING
-- Send messages as single SMS (no splitting)
-- =====================================================================

DROP FUNCTION IF EXISTS process_scheduled_messages();

CREATE OR REPLACE FUNCTION process_scheduled_messages()
RETURNS TABLE(processed_count int, messages_queued int, expired_count int)
LANGUAGE plpgsql
AS $$
DECLARE
    msg RECORD;
    processed int := 0;
    queued int := 0;
    expired int := 0;
    current_time_pst timestamptz;
    scheduled_time_pst timestamptz;
    minutes_late numeric;
BEGIN
    -- Get current time in PST
    current_time_pst := NOW() AT TIME ZONE 'America/Los_Angeles';
    
    -- Find SCH messages where scheduled_for <= NOW()
    FOR msg IN 
        SELECT id, phone_number, message_content, scheduled_for
        FROM campaign_messages
        WHERE status = 'SCH' 
          AND scheduled_for <= NOW()
        ORDER BY scheduled_for ASC
        LIMIT 50  -- Process 50 at a time
    LOOP
        -- Convert scheduled time to PST
        scheduled_time_pst := msg.scheduled_for AT TIME ZONE 'America/Los_Angeles';
        
        -- Calculate how many minutes late
        minutes_late := EXTRACT(EPOCH FROM (current_time_pst - scheduled_time_pst)) / 60;
        
        -- If more than 5 minutes late, mark as expired (don't send)
        IF minutes_late > 5 THEN
            UPDATE campaign_messages
            SET 
                status = 'expired',
                updated_at = NOW(),
                feedback_notes = CONCAT(
                    COALESCE(feedback_notes, ''), 
                    ' [EXPIRED: ', 
                    ROUND(minutes_late::numeric, 1), 
                    ' minutes late - requires manual review]'
                )
            WHERE id = msg.id;
            
            expired := expired + 1;
            
        ELSE
            -- Within 5-minute window, send as SINGLE message
            -- NO bubble splitting - send message_content as-is
            INSERT INTO messages (phone_number, content, status, direction, timestamp)
            VALUES (
                msg.phone_number,
                msg.message_content,  -- Send complete message
                'queued',
                'outbound',
                NOW()
            );
            queued := queued + 1;
            
            -- Update campaign_messages: SCH → sent
            UPDATE campaign_messages
            SET 
                status = 'sent',
                updated_at = NOW()
            WHERE id = msg.id;
            
            processed := processed + 1;
        END IF;
    END LOOP;
    
    RETURN QUERY SELECT processed, queued, expired;
END;
$$;

-- Grant permissions
GRANT EXECUTE ON FUNCTION process_scheduled_messages TO authenticated, anon;

-- =====================================================================
-- USAGE:
-- When this runs, it will:
--   1. Send messages as SINGLE SMS (no bubble splitting)
--   2. Mark messages >5 minutes late as 'expired'
--   3. Return counts: (sent, queued_messages, expired)
-- =====================================================================

