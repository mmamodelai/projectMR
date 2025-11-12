#!/usr/bin/env python3
"""Quick test to check campaign_messages table"""
from supabase import create_client

client = create_client(
    'https://kiwmwoqrguyrcpjytgte.supabase.co',
    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0'
)

try:
    # Test query
    result = client.table('campaign_messages').select('id,customer_name,phone_number,status,strategy_type').eq('status', 'SUG').limit(10).execute()
    
    print(f"FOUND {len(result.data)} SUG messages!")
    print()
    
    for r in result.data:
        print(f"  - {r.get('customer_name')} ({r.get('phone_number')}) [{r.get('strategy_type')}]")
        
except Exception as e:
    print(f"ERROR: {e}")
    print()
    print("This might mean:")
    print("  1. The campaign_messages table doesn't exist")
    print("  2. We're pointing at the wrong database")
    print("  3. The status values are different (not 'SUG')")

