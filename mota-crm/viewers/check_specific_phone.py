#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

phone_to_check = "6199773020"
print(f"Looking for: {phone_to_check}")
print("=" * 60)

formats = [
    '6199773020',
    '+16199773020',
    '(619) 977-3020',
    '619-977-3020',
    '+1 (619) 977-3020',
    '619.977.3020'
]

found = False
for fmt in formats:
    result = sb.table('customers_blaze')\
        .select('first_name, last_name, phone, email, total_visits, lifetime_value, member_id')\
        .eq('phone', fmt)\
        .execute()
    
    if result.data:
        found = True
        print(f"\n>>> FOUND with format: '{fmt}'")
        for c in result.data:
            print(f"\n  Name: {c.get('first_name')} {c.get('last_name')}")
            print(f"  Phone: {c.get('phone')}")
            print(f"  Email: {c.get('email', 'N/A')}")
            print(f"  Visits: {c.get('total_visits', 0)}")
            print(f"  Lifetime: ${c.get('lifetime_value', 0):.2f}")
            print(f"  ID: {c.get('member_id')}")

if not found:
    print("\nNOT FOUND with exact match. Trying partial search...")
    result = sb.table('customers_blaze')\
        .select('first_name, last_name, phone, email, total_visits')\
        .like('phone', '%9773020%')\
        .execute()
    
    if result.data:
        print(f"\nFound {len(result.data)} records with partial match:")
        for c in result.data[:10]:
            print(f"  {c.get('first_name')} {c.get('last_name')} - Phone: '{c.get('phone')}' - Visits: {c.get('total_visits', 0)}")
    else:
        print("\nNO RECORDS FOUND with this phone number!")

