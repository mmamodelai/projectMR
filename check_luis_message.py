#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table('messages').select('*').eq('phone_number', '+16193683370').eq('direction', 'outbound').order('id', desc=True).limit(1).execute()

if response.data:
    msg = response.data[0]
    print(f"Latest message to Luis:")
    print(f"  Status: {msg.get('status')}")
    print(f"  Content: {msg.get('content', '')[:100]}...")
    print(f"  Timestamp: {msg.get('timestamp')}")
else:
    print("No messages found")

