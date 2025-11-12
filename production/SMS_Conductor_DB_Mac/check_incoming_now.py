#!/usr/bin/env python3
"""
Check incoming messages NOW
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

result = supabase.table('messages').select('*').eq('direction', 'inbound').order('timestamp', desc=True).limit(10).execute()

print("INCOMING MESSAGES (Last 10):")
print("=" * 80)
for i, msg in enumerate(result.data, 1):
    print(f"{i}. FROM: {msg['phone_number']}")
    print(f"   TIME: {msg['timestamp']}")
    print(f"   CONTENT: {msg['content']}")
    print(f"   STATUS: {msg['status']}")
    print()


