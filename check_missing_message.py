#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from supabase import create_client
from datetime import datetime, timedelta

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
phone = "+16199773020"

print("="*80)
print("CHECKING FOR MISSING MESSAGE: 'Hey how many points do I have'")
print("="*80)

# Get all messages from the last hour
one_hour_ago = (datetime.utcnow() - timedelta(hours=1)).isoformat()
messages = supabase.table('messages').select('*').eq('phone_number', phone).gte('timestamp', one_hour_ago).order('timestamp', desc=True).execute()

print(f"\nMessages from {phone} in last hour: {len(messages.data)}")
print()

for i, msg in enumerate(messages.data, 1):
    print(f"[{i}] {msg.get('timestamp')}")
    print(f"    Direction: {msg.get('direction')}")
    print(f"    Status: {msg.get('status')}")
    print(f"    Content: {msg.get('content')}")
    print()

# Check for the specific message
found = any("points" in msg.get('content', '').lower() and msg.get('direction') == 'inbound' for msg in messages.data)

if found:
    print("✅ Message FOUND in database!")
else:
    print("❌ Message NOT FOUND in database!")
    print("\nPossible reasons:")
    print("1. Conductor didn't read it from modem")
    print("2. Message stuck on modem (not deleted)")
    print("3. Modem didn't receive it")
    print("4. Time zone issue")

# Check total count
total = supabase.table('messages').select('id').execute()
print(f"\nTotal messages in database: {len(total.data)}")

