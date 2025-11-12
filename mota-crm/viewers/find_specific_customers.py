#!/usr/bin/env python3
"""Find specific customers by phone"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Search for Stephen Clare
print("1. Searching for STEPHEN CLARE:")
result = sb.table('customers_blaze').select('*').ilike('first_name', '%stephen%').ilike('last_name', '%clare%').execute()
for r in result.data:
    print(f"   Name: {r.get('first_name')} {r.get('last_name')}")
    print(f"   Phone: {r.get('phone')}")
    print(f"   Member ID: {r.get('member_id')}")
    print()

# Search for Luis Bobadilla
print("2. Searching for LUIS BOBADILLA:")
result = sb.table('customers_blaze').select('*').ilike('first_name', '%luis%').ilike('last_name', '%bobadilla%').execute()
for r in result.data:
    print(f"   Name: {r.get('first_name')} {r.get('last_name')}")
    print(f"   Phone: {r.get('phone')}")
    print(f"   Member ID: {r.get('member_id')}")
    print()

# Search by partial phone
print("3. Searching by phone containing '6199773020':")
result = sb.table('customers_blaze').select('first_name, last_name, phone').like('phone', '%6199773020%').execute()
for r in result.data:
    print(f"   {r.get('phone')} → {r.get('first_name')} {r.get('last_name')}")

print()
print("4. Searching by phone containing '3683370':")
result = sb.table('customers_blaze').select('first_name, last_name, phone').like('phone', '%3683370%').execute()
for r in result.data:
    print(f"   {r.get('phone')} → {r.get('first_name')} {r.get('last_name')}")

print()
print("5. What phone formats exist:")
result = sb.table('customers_blaze').select('phone').not_.is_('phone', 'null').limit(20).execute()
for r in result.data:
    phone = r.get('phone')
    print(f"   {phone} (len={len(str(phone))}, type={type(phone)})")

input("\nPress Enter...")

