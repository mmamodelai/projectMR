-- Schedule test message for 11:47 AM PST on November 8, 2025
-- Run this in Supabase SQL Editor

INSERT INTO scheduled_messages (
    phone_number,
    customer_name,
    message_content,
    scheduled_for,
    status,
    campaign_name
) VALUES (
    '+16199773020',
    'Stephen Clare (Test)',
    'Test bubble 1: This is a test of the scheduling system at 11:47 AM PST.

[BUBBLE]

Test bubble 2: If you receive this, the Pacific Time scheduling is working correctly!

[BUBBLE]

Test bubble 3: This message was scheduled via the database-native scheduler.',
    '2025-11-08 11:47:00-08'::timestamptz,  -- 11:47 AM PST
    'SCH',
    'test_11_47_am'
);

-- Check it was inserted:
SELECT 
    id,
    customer_name,
    phone_number,
    scheduled_for AT TIME ZONE 'America/Los_Angeles' as scheduled_for_pst,
    status
FROM scheduled_messages
WHERE phone_number = '+16199773020'
ORDER BY scheduled_for DESC
LIMIT 1;

