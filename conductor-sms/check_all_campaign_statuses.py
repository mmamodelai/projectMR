#!/usr/bin/env python3
"""Check all campaign_messages and their statuses"""
from supabase import create_client

client = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

try:
    # Get ALL campaign_messages
    result = client.table('campaign_messages').select('id,customer_name,phone_number,status,strategy_type').limit(20).execute()
    
    print(f"Total campaign_messages found: {len(result.data)}")
    print()
    
    if len(result.data) == 0:
        print("NO MESSAGES IN TABLE - Table is empty!")
    else:
        # Group by status
        from collections import Counter
        statuses = Counter([r.get('status') for r in result.data])
        
        print("Status breakdown:")
        for status, count in statuses.items():
            print(f"  {status}: {count} messages")
        
        print()
        print("Sample messages:")
        for r in result.data[:10]:
            print(f"  - [{r.get('status')}] {r.get('customer_name')} ({r.get('phone_number')[:10]}...)")
        
except Exception as e:
    print(f"ERROR: {e}")

