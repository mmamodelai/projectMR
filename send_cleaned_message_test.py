#!/usr/bin/env python3
"""
Send a cleaned message (no bubbles) to Stephen for testing
"""
from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("SEND CLEANED MESSAGE (NO BUBBLES) TO STEPHEN")
print("="*70)

# Get a random APR message (should be clean now)
response = supabase.table('campaign_messages').select('*').eq('status', 'APR').limit(1).execute()

if not response.data:
    print("\nNo APR messages found!")
    exit(1)

msg = response.data[0]
name = msg.get('customer_name', '').encode('ascii', 'ignore').decode()
content = msg.get('message_content', '')

print(f"\nUsing message for: {name}")
print(f"Message length: {len(content)} characters")
print(f"Has [BUBBLE] markers: {'Yes' if '[BUBBLE]' in content else 'No'}")

print(f"\nPreview:")
print("-" * 70)
print(content[:200])
if len(content) > 200:
    print(f"... ({len(content)} total characters)")
print("-" * 70)

# Queue the message
supabase.table('messages').insert({
    'phone_number': '+16199773020',
    'content': content,
    'status': 'queued',
    'direction': 'outbound',
    'timestamp': datetime.now(timezone.utc).isoformat()
}).execute()

print(f"\n[SUCCESS] Message queued!")
print(f"To: 619-977-3020")
print(f"Conductor will send within 5-10 seconds")
print("="*70)

