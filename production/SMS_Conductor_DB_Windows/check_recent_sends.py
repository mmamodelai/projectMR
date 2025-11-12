#!/usr/bin/env python3
"""
Check recent sent messages
"""
from supabase import create_client
from datetime import datetime

supabase = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Get last 15 sent messages
result = supabase.table('messages').select('*').eq('status', 'sent').eq('direction', 'outbound').order('timestamp', desc=True).limit(15).execute()

print('\n=== Last 15 SENT Outbound Messages ===\n')
print(f"{'ID':<6} | {'Timestamp':<19} | {'Phone':<15} | {'Content Preview'}")
print('-' * 80)

for msg in result.data:
    msg_id = msg['id']
    timestamp = msg['timestamp'][:19].replace('T', ' ')
    phone = msg['phone_number']
    content = msg['content'][:40] + '...' if len(msg['content']) > 40 else msg['content']
    print(f"{msg_id:<6} | {timestamp} | {phone:<15} | {content}")

print(f"\n{len(result.data)} messages found")
print("\nNOTE: These messages show as 'sent' in database.")
print("Did you receive ANY of these on your phone?")



