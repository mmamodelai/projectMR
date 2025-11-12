#!/usr/bin/env python3
"""List all Supabase tables to find campaign messages"""

from supabase import create_client

CRM_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
CRM_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(CRM_URL, CRM_KEY)

# Try common table names
common_names = [
    'campaign_messages',
    'campaigns',
    'suggested_messages',
    'message_suggestions',
    'ai_messages',
    'budtender_campaigns',
    'bt_campaigns',
    'outreach_messages',
    'scheduled_messages'
]

print("Searching for campaign/message tables...\n")

for table_name in common_names:
    try:
        result = sb.table(table_name).select('*').limit(1).execute()
        print(f"[FOUND] {table_name}")
        if result.data:
            print(f"  Columns: {', '.join(result.data[0].keys())}")
            print(f"  Row count: {len(result.data)}")
    except Exception as e:
        if 'not found' not in str(e).lower():
            print(f"[ERROR] {table_name}: {e}")

