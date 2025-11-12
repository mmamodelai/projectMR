#!/usr/bin/env python3
"""
Check why messages are failing
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("CHECKING FAILED MESSAGES")
print("="*70)

# Get recent failed messages
response = supabase.table('messages').select('*').eq('status', 'failed').eq('direction', 'outbound').order('id', desc=True).limit(20).execute()

print(f"\nTotal failed: {len(response.data)}")

for msg in response.data:
    print(f"\nID {msg.get('id')}:")
    print(f"  Phone: {msg.get('phone_number')}")
    print(f"  Content: {msg.get('content', '')[:50]}...")
    print(f"  Timestamp: {msg.get('timestamp')}")
    print(f"  Retry Count: {msg.get('retry_count', 0)}")
    print(f"  Error: {msg.get('error_message', 'No error message')}")

# Check queued count
response = supabase.table('messages').select('id', count='exact').eq('status', 'queued').execute()
print(f"\n{'='*70}")
print(f"Currently queued: {len(response.data)} messages")
print("="*70)

