-- Check what SUG messages exist for Stephen
SELECT 
    id,
    phone_number,
    customer_name,
    status,
    LEFT(message_content, 50) as message_preview,
    generated_at
FROM campaign_messages
WHERE phone_number LIKE '%619977%'
OR customer_name LIKE '%Stephen%'
ORDER BY generated_at DESC
LIMIT 10;

-- Also check the exact phone format Stephen has in messages table:
SELECT DISTINCT phone_number
FROM messages
WHERE phone_number LIKE '%619977%'
LIMIT 5;

