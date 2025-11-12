#!/usr/bin/env python3
"""Check actual phone number matches"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Checking phone number situation...")
print()

# Get message phone numbers
print("1. Phone numbers FROM MESSAGES:")
messages = sb.table('messages').select('phone_number').execute()
message_phones = set(str(m['phone_number']) for m in messages.data if m.get('phone_number'))
print(f"   Found {len(message_phones)} unique phone numbers in messages")
for phone in list(message_phones)[:5]:
    print(f"      Example: {phone}")
print()

# Get customer phone numbers (NON-NULL)
print("2. Phone numbers FROM CUSTOMERS (non-null):")
customers = sb.table('customers_blaze').select('phone, first_name, last_name').not_.is_('phone', 'null').execute()
print(f"   Found {len(customers.data)} customers with phone numbers")
for cust in customers.data[:5]:
    print(f"      {cust.get('phone')} - {cust.get('first_name')} {cust.get('last_name')}")
print()

# Try to match
print("3. TRYING TO MATCH:")
test_phones = list(message_phones)[:3]
for msg_phone in test_phones:
    print(f"   Looking for: {msg_phone}")
    
    # Try exact match
    match = sb.table('customers_blaze').select('first_name, last_name, phone').eq('phone', msg_phone).execute()
    if match.data:
        print(f"      ✅ FOUND: {match.data[0]['first_name']} {match.data[0]['last_name']}")
    else:
        # Try without +
        no_plus = msg_phone.replace('+', '')
        match2 = sb.table('customers_blaze').select('first_name, last_name, phone').eq('phone', no_plus).execute()
        if match2.data:
            print(f"      ✅ FOUND (without +): {match2.data[0]['first_name']} {match2.data[0]['last_name']}")
        else:
            print(f"      ❌ NOT FOUND")
print()

print("4. TOTAL STATS:")
total_customers = sb.table('customers_blaze').select('id', count='exact').execute()
customers_with_phone = sb.table('customers_blaze').select('id', count='exact').not_.is_('phone', 'null').execute()
print(f"   Total customers: {total_customers.count}")
print(f"   Customers with phone: {customers_with_phone.count}")
print(f"   Customers WITHOUT phone: {total_customers.count - customers_with_phone.count}")
print()

input("Press Enter to close...")

