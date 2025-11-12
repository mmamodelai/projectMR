#!/usr/bin/env python3
"""
Check if self-test message was sent and received
"""
from supabase import create_client

supabase = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

# Check message 489 (self-test)
msg489 = supabase.table('messages').select('*').eq('id', 489).execute()

print('\n=== Self-Test Message (ID 489) ===\n')
if msg489.data:
    msg = msg489.data[0]
    print(f"Status: {msg['status']}")
    print(f"Phone: {msg['phone_number']}")
    print(f"Direction: {msg['direction']}")
    print(f"Content: {msg['content']}")
    print(f"Timestamp: {msg['timestamp']}")
else:
    print("Message 489 not found")

# Check last 5 incoming messages
incoming = supabase.table('messages').select('*').eq('direction', 'inbound').order('timestamp', desc=True).limit(5).execute()

print('\n=== Last 5 Incoming Messages ===\n')
if incoming.data:
    for msg in incoming.data:
        print(f"{msg['timestamp'][:19]} | {msg['content'][:60]}")
else:
    print("No incoming messages")

# Check if SELF TEST was received
self_test_received = [m for m in incoming.data if 'SELF TEST' in m['content']]
if self_test_received:
    print('\n*** SELF TEST MESSAGE WAS RECEIVED! ***')
else:
    print('\n*** SELF TEST MESSAGE NOT RECEIVED YET ***')



