#!/usr/bin/env python3
"""
Reset ALL scheduled messages back to APR so we can reschedule properly
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("="*70)
print("RESET ALL SCHEDULED MESSAGES")
print("="*70)

# Delete queued messages
response = supabase.table('messages').select('id', count='exact').eq('status', 'queued').execute()
queued_count = len(response.data)
print(f"\n1. Deleting {queued_count} queued messages...")
supabase.table('messages').delete().eq('status', 'queued').execute()
print(f"   [DONE] Cleared queue")

# Reset all SCH back to APR
response = supabase.table('campaign_messages').select('id', count='exact').eq('status', 'SCH').execute()
sch_count = len(response.data)
print(f"\n2. Resetting {sch_count} SCH messages to APR...")
supabase.table('campaign_messages').update({
    'status': 'APR',
    'scheduled_for': None
}).eq('status', 'SCH').execute()
print(f"   [DONE] All reset to APR")

print("\n" + "="*70)
print("READY TO RESCHEDULE with new 5-7 minute spacing!")
print("="*70)

