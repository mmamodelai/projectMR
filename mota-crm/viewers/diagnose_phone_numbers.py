#!/usr/bin/env python3
"""
Diagnostic script to check phone number formats in database
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("PHONE NUMBER DIAGNOSTIC")
print("=" * 80)
print()

# Check messages table
print("1. MESSAGES TABLE - Sample phone numbers:")
print("-" * 80)
messages = sb.table('messages').select('phone_number').limit(10).execute()
for msg in messages.data:
    phone = msg.get('phone_number')
    print(f"   Phone: {phone} | Type: {type(phone)} | Repr: {repr(phone)}")
print()

# Check customers_blaze table
print("2. CUSTOMERS_BLAZE TABLE - Sample phone numbers:")
print("-" * 80)
customers = sb.table('customers_blaze').select('phone, first_name, last_name').limit(10).execute()
for cust in customers.data:
    phone = cust.get('phone')
    name = f"{cust.get('first_name')} {cust.get('last_name')}"
    print(f"   Phone: {phone} | Type: {type(phone)} | Name: {name}")
print()

# Check budtenders table
print("3. BUDTENDERS TABLE - Sample phone numbers:")
print("-" * 80)
try:
    budtenders = sb.table('budtenders').select('phone_number, first_name, last_name, dispensary_name').limit(10).execute()
    for bud in budtenders.data:
        phone = bud.get('phone_number')
        name = f"{bud.get('first_name')} {bud.get('last_name')}"
        disp = bud.get('dispensary_name')
        print(f"   Phone: {phone} | Type: {type(phone)} | Name: {name} @ {disp}")
except Exception as e:
    print(f"   Error: {e}")
print()

# Try to match a specific phone number
print("4. TESTING PHONE NUMBER MATCHING:")
print("-" * 80)
test_phone = "16193683370"  # From your screenshot
print(f"Testing phone: {test_phone}")
print()

# Try messages
msg_result = sb.table('messages').select('*').eq('phone_number', test_phone).execute()
print(f"   Messages found (as string): {len(msg_result.data)}")

# Try as integer
msg_result_int = sb.table('messages').select('*').eq('phone_number', int(test_phone)).execute()
print(f"   Messages found (as int): {len(msg_result_int.data)}")

# Try customers
cust_result = sb.table('customers_blaze').select('*').eq('phone', test_phone).execute()
print(f"   Customer found (as string): {len(cust_result.data)}")

cust_result_int = sb.table('customers_blaze').select('*').eq('phone', int(test_phone)).execute()
print(f"   Customer found (as int): {len(cust_result_int.data)}")

print()
print("=" * 80)
print("DIAGNOSIS COMPLETE")
print("=" * 80)

input("\nPress Enter to close...")

