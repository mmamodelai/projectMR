#!/usr/bin/env python3
"""
Check if phone numbers still exist after merge
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 60)
print("Checking Phone Number Data After Merge")
print("=" * 60)

# Check specific phone from screenshot: +16193683370
test_phone = "+16193683370"
print(f"\nLooking for: {test_phone}")

# Try different formats
formats_to_try = [
    test_phone,
    test_phone.replace("+", ""),
    "16193683370",
    "6193683370",
    "(619) 368-3370",
    "619-368-3370"
]

for fmt in formats_to_try:
    result = sb.table('customers_blaze')\
        .select('member_id, first_name, last_name, phone, email, total_visits')\
        .eq('phone', fmt)\
        .execute()
    
    if result.data:
        print(f"\n>>> FOUND with format: '{fmt}'")
        for customer in result.data:
            print(f"    Name: {customer['first_name']} {customer['last_name']}")
            print(f"    Phone: {customer['phone']}")
            print(f"    Email: {customer.get('email', 'N/A')}")
            print(f"    Visits: {customer.get('total_visits', 0)}")
        break
else:
    print(f"\n❌ NOT FOUND in customers_blaze!")
    print("   Trying partial match...")
    
    # Try LIKE search
    result = sb.table('customers_blaze')\
        .select('member_id, first_name, last_name, phone, email')\
        .like('phone', '%6193683370%')\
        .execute()
    
    if result.data:
        print(f"\n>>> FOUND with partial match:")
        for customer in result.data[:5]:
            print(f"    {customer['first_name']} {customer['last_name']}")
            print(f"    Phone: '{customer['phone']}'")
    else:
        print("   Still not found!")

# Check overall phone number stats
print(f"\n" + "=" * 60)
print("Overall Phone Number Stats:")
print("=" * 60)

total = sb.table('customers_blaze').select('phone', count='exact').execute()
with_phone = sb.table('customers_blaze')\
    .select('phone', count='exact')\
    .not_.is_('phone', 'null')\
    .neq('phone', '')\
    .execute()

print(f"Total customers: {total.count:,}")
print(f"With phone numbers: {with_phone.count:,}")
print(f"Without phone: {total.count - with_phone.count:,}")

if with_phone.count < 30000:
    print(f"\n⚠️  WARNING: Only {with_phone.count:,} customers have phones!")
    print("   This seems low - phone numbers might have been lost in merge!")
else:
    print(f"\n✓ Phone numbers look OK ({with_phone.count:,} customers)")

input("\nPress Enter to close...")

