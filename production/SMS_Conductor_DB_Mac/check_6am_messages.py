#!/usr/bin/env python3
"""
Check messages sent at 6am that worked
"""
from supabase import create_client

supabase = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Check 6am-8am PST (14:00-16:00 UTC)
result = supabase.table('messages').select('*').gte('timestamp', '2025-11-07T13:00:00').lte('timestamp', '2025-11-07T15:00:00').eq('direction', 'outbound').eq('status', 'sent').execute()

print('\n=== Messages Sent 6am-8am PST (that worked) ===\n')
print(f"Total: {len(result.data)}")
print(f"{'ID':<6} | {'Timestamp':<19} | {'Phone':<15} | {'Content'}")
print('-' * 90)

for msg in result.data[:15]:
    msg_id = msg['id']
    timestamp = msg['timestamp'][:19].replace('T', ' ')
    phone = msg['phone_number']
    content = msg['content'][:50] + '...' if len(msg['content']) > 50 else msg['content']
    print(f"{msg_id:<6} | {timestamp} | {phone:<15} | {content}")



