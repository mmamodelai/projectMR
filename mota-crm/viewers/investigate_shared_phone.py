#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("INVESTIGATING: HOW CAN 5 PEOPLE HAVE SAME PHONE?")
print("=" * 80)

phone = "(619) 368-3370"

# Get all 5 people with this phone
people = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, phone, email, date_of_birth, created_at, total_visits, lifetime_value')\
    .eq('phone', phone)\
    .execute()

print(f"\n{len(people.data)} people with phone {phone}:\n")

for i, p in enumerate(people.data, 1):
    print(f"{i}. {p['first_name']} {p['last_name']}")
    print(f"   Member ID: {p['member_id']}")
    print(f"   DOB: {p.get('date_of_birth', 'N/A')}")
    print(f"   Email: {p.get('email', 'N/A')}")
    print(f"   Created: {p.get('created_at', 'N/A')[:10]}")
    print(f"   Visits: {p.get('total_visits', 0)}")
    print(f"   Lifetime: ${p.get('lifetime_value', 0):.2f}")
    
    # Check when they last purchased
    last_tx = sb.table('transactions_blaze')\
        .select('date, total_amount')\
        .eq('customer_id', p['member_id'])\
        .eq('blaze_status', 'Completed')\
        .order('date', desc=True)\
        .limit(1)\
        .execute()
    
    if last_tx.data:
        print(f"   Last Purchase: {last_tx.data[0]['date'][:10]} (${last_tx.data[0]['total_amount']:.2f})")
    else:
        print(f"   Last Purchase: NEVER")
    
    print()

# Check the BACKUP to see if they were always like this
print("=" * 80)
print("CHECKING BACKUP (before merge)")
print("=" * 80)

try:
    backup = sb.table('customers_blaze_backup_20251106')\
        .select('member_id, first_name, last_name, phone')\
        .eq('phone', phone)\
        .execute()
    
    print(f"\nIn BACKUP: {len(backup.data)} people had this phone")
    if len(backup.data) > len(people.data):
        print(f"  -> Merge reduced from {len(backup.data)} to {len(people.data)}")
    elif len(backup.data) == len(people.data):
        print(f"  -> Same count before/after merge - these are NOT duplicates by our rules")
    
    print("\nBackup records:")
    for b in backup.data:
        print(f"  - {b['first_name']} {b['last_name']} ({b['member_id']})")
except Exception as e:
    print(f"Could not check backup: {e}")

# Check how many OTHER people share phones
print("\n" + "=" * 80)
print("HOW COMMON IS THIS ISSUE?")
print("=" * 80)

print("\nSearching for other shared phone numbers...")
print("(This might take a moment...)")

# Get sample of customers with phones
sample = sb.table('customers_blaze')\
    .select('phone')\
    .not_.is_('phone', 'null')\
    .neq('phone', '')\
    .limit(10000)\
    .execute()

from collections import Counter
phone_counts = Counter([p['phone'] for p in sample.data if p['phone']])

# Find phones used by multiple people
shared_phones = {phone: count for phone, count in phone_counts.items() if count > 1}

print(f"\nIn sample of 10,000 customers with phones:")
print(f"  Total unique phones: {len(phone_counts)}")
print(f"  Phones shared by multiple people: {len(shared_phones)}")

if shared_phones:
    print(f"\n  Top 10 most shared phones:")
    for phone, count in sorted(shared_phones.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"    {phone}: {count} people")

print("\n" + "=" * 80)
print("THEORY:")
print("=" * 80)
print("Blaze API does NOT enforce unique phone numbers!")
print("This could happen because:")
print("  1. Budtenders entering wrong phone numbers")
print("  2. People using store/business phones")
print("  3. Test accounts with dummy data")
print("  4. Data quality issues in Blaze")
print("  5. Someone using the STORE phone number for rewards")
print("\nThe person with MOST visits/purchases is likely the real owner.")
print(f"For (619) 368-3370: Luis Bobadilla (190 visits) is probably real,")
print(f"  others might be mistakes or using store phone.")

