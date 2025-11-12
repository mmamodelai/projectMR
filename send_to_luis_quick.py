#!/usr/bin/env python3
"""
Send single message test to Luis Bobadilla
"""
from supabase import create_client
from datetime import datetime, timezone

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("SEND SINGLE MESSAGE TO LUIS BOBADILLA")
print("="*70)

luis_phone = '+16193683370'

# Get a sample message
response = supabase.table('campaign_messages').select('*').eq('status', 'APR').limit(1).execute()
message_content = response.data[0].get('message_content', '')

# Remove [BUBBLE] markers - send as ONE message
message_single = message_content.replace('[BUBBLE]', '\n\n')

print(f"\nTo: {luis_phone}")
print(f"Message length: {len(message_single)} characters")

# Queue the message
supabase.table('messages').insert({
    'phone_number': luis_phone,
    'content': message_single,
    'status': 'queued',
    'direction': 'outbound',
    'timestamp': datetime.now(timezone.utc).isoformat()
}).execute()

print(f"\n[SUCCESS] Message queued for Luis!")
print(f"Conductor will send within 5-10 seconds")
print("="*70)

