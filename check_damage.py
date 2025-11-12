#!/usr/bin/env python3
"""
Check damage from mass send
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("DAMAGE ASSESSMENT")
print("="*70)

# Check for failed/queued messages
response = supabase.table('messages').select('status').order('id', desc=True).limit(300).execute()

status_counts = {}
for msg in response.data:
    status = msg.get('status')
    status_counts[status] = status_counts.get(status, 0) + 1

print("\nMessage Status (last 300):")
for status, count in sorted(status_counts.items()):
    print(f"  {status:10} : {count:3}")

# Check for blocking errors
response = supabase.table('messages').select('*').eq('direction', 'inbound').order('id', desc=True).limit(20).execute()

blocking_msgs = [m for m in response.data if 'blocking' in m.get('content', '').lower() or 'unable' in m.get('content', '').lower()]

print(f"\nBlocking error messages: {len(blocking_msgs)}")
for msg in blocking_msgs:
    phone = msg.get('phone_number')
    content = msg.get('content', '')[:60]
    print(f"  {phone}: {content}...")

print("\n" + "="*70)

