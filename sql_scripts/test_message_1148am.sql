-- ================================================================
-- TEST MESSAGE: Schedule for 11:48 AM PST
-- ================================================================
-- Run AFTER clean_install_scheduling.sql
-- ================================================================

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
    'Test bubble 1: Scheduled for 11:48 AM PST.

[BUBBLE]

Test bubble 2: If you get this, Pacific Time scheduling works!

[BUBBLE]

Test bubble 3: Database-native scheduler is operational.',
    '2025-11-08 11:48:00-08'::timestamptz,
    'SCH',
    'test_11_48_am'
);

-- Verify it was inserted:
SELECT 
    id,
    customer_name,
    scheduled_for AT TIME ZONE 'America/Los_Angeles' as scheduled_pst,
    status
FROM scheduled_messages
WHERE phone_number = '+16199773020';

