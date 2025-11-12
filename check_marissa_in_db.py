#!/usr/bin/env python3
"""Check if Marissa is in campaign_messages"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

phone = "2096288371"

print("\n" + "="*60)
print("CHECKING MARISSA IN CAMPAIGN_MESSAGES")
print("="*60 + "\n")

try:
    # Check campaign_messages
    result = supabase.table('campaign_messages').select('*').like('phone_number', f'%{phone}%').execute()
    
    if result.data:
        print(f"FOUND {len(result.data)} record(s) in campaign_messages!")
        for record in result.data:
            print(f"\nID: {record.get('id')}")
            print(f"Customer Name: {record.get('customer_name', 'N/A')}")
            print(f"Phone Number: {record.get('phone_number', 'N/A')}")
            print(f"Status: {record.get('status', 'N/A')}")
            print(f"Campaign: {record.get('campaign_name', 'N/A')}")
            print(f"Message Preview: {record.get('message_content', 'N/A')[:100]}...")
    else:
        print("NOT FOUND in campaign_messages")
        
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60 + "\n")


