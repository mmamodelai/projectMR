#!/usr/bin/env python3
"""
Send ONE complete message (no bubble splitting) to test
"""
from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("TEST: SINGLE MESSAGE (NO BUBBLE SPLITTING)")
print("="*70)

# Get a sample Flavors message
response = supabase.table('campaign_messages').select('*').eq('status', 'APR').limit(1).execute()

if not response.data:
    print("\nNo APR messages found!")
    exit(1)

sample = response.data[0]
message_content = sample.get('message_content', '')

# Remove [BUBBLE] markers - send as ONE message
message_single = message_content.replace('[BUBBLE]', '\n\n')

print(f"\nOriginal message had {message_content.count('[BUBBLE]') + 1} bubbles")
print(f"Sending as ONE message with line breaks instead")
print(f"\nMessage preview:")
print("-" * 70)
print(message_single[:200])
if len(message_single) > 200:
    print(f"... ({len(message_single)} total characters)")
print("-" * 70)

# Queue the message
supabase.table('messages').insert({
    'phone_number': '+16199773020',
    'content': message_single,
    'status': 'queued',
    'direction': 'outbound',
    'timestamp': datetime.now(timezone.utc).isoformat()
}).execute()

print(f"\n[SUCCESS] Message queued!")
print(f"To: 619-977-3020")
print(f"Length: {len(message_single)} characters")
print(f"\nStart Conductor to send it!")
print("="*70)

