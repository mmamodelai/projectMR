#!/usr/bin/env python3
"""
Quick script to check queued messages in Supabase
"""
from supabase import create_client

# Initialize Supabase
supabase = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Get queued messages
result = supabase.table('messages').select('*').eq('status', 'queued').execute()

print(f'\n=== Queued Messages: {len(result.data)} ===\n')

if result.data:
    for msg in result.data:
        print(f"ID: {msg['id']}")
        print(f"Phone: {msg['phone_number']}")
        print(f"Content: {msg['content'][:60]}...")
        print(f"Timestamp: {msg['timestamp']}")
        print(f"Direction: {msg['direction']}")
        print(f"Retry Count: {msg.get('retry_count', 0)}")
        print("-" * 60)
else:
    print("No queued messages found")

# Get recent sent messages
result = supabase.table('messages').select('*').eq('status', 'sent').order('timestamp', desc=True).limit(5).execute()

print(f'\n=== Recent Sent Messages: {len(result.data)} ===\n')

for msg in result.data:
    print(f"ID: {msg['id']} | {msg['timestamp']} | {msg['phone_number']} | {msg['content'][:40]}...")
