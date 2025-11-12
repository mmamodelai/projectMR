#!/usr/bin/env python3
"""
Quick check of campaign_messages status counts
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

response = supabase.table('campaign_messages').select('status').execute()

counts = {}
for msg in response.data:
    status = msg['status']
    counts[status] = counts.get(status, 0) + 1

print("=" * 60)
print("CAMPAIGN MESSAGE STATUS COUNTS")
print("=" * 60)
for status in ['SUG', 'APR', 'SCH', 'sent', 'cancelled', 'expired', 'draft']:
    count = counts.get(status, 0)
    if count > 0:
        print(f"{status:12} {count:4} messages")
print("=" * 60)
print(f"TOTAL:       {sum(counts.values()):4} messages")
print("=" * 60)
