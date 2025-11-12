#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("VERIFYING KEY ACCOUNTS AFTER MERGE")
print("=" * 80)

# 1. Check Luis Bobadilla
print("\n1. LUIS BOBADILLA")
print("-" * 80)

luis = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, phone, email, total_visits, lifetime_value, date_of_birth')\
    .ilike('first_name', 'luis')\
    .ilike('last_name', 'bobadilla')\
    .execute()

print(f"Found {len(luis.data)} Luis Bobadilla record(s):")
for l in luis.data:
    print(f"\n  ID: {l['member_id']}")
    print(f"  Name: {l['first_name']} {l['last_name']}")
    print(f"  Phone: {l.get('phone', 'N/A')}")
    print(f"  Email: {l.get('email', 'N/A')}")
    print(f"  DOB: {l.get('date_of_birth', 'N/A')}")
    print(f"  Visits (cached): {l.get('total_visits', 0)}")
    print(f"  Lifetime (cached): ${l.get('lifetime_value', 0):.2f}")
    
    # Check ACTUAL transactions
    transactions = sb.table('transactions_blaze')\
        .select('transaction_id, date, total_amount', count='exact')\
        .eq('customer_id', l['member_id'])\
        .eq('blaze_status', 'Completed')\
        .execute()
    
    print(f"  ACTUAL Transactions: {transactions.count}")
    if transactions.count > 0:
        total = sum(t.get('total_amount', 0) for t in transactions.data)
        print(f"  ACTUAL Lifetime: ${total:.2f}")

# 2. Check Stephen Clare
print("\n" + "=" * 80)
print("2. STEPHEN CLARE")
print("-" * 80)

stephen = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, phone, email, total_visits, lifetime_value, date_of_birth')\
    .ilike('first_name', 'stephen')\
    .ilike('last_name', 'clare')\
    .execute()

print(f"Found {len(stephen.data)} Stephen Clare record(s):")
for s in stephen.data:
    print(f"\n  ID: {s['member_id']}")
    print(f"  Name: {s['first_name']} {s['last_name']}")
    print(f"  Phone: {s.get('phone', 'N/A')}")
    print(f"  Email: {s.get('email', 'N/A')}")
    print(f"  DOB: {s.get('date_of_birth', 'N/A')}")
    print(f"  Visits (cached): {s.get('total_visits', 0)}")
    print(f"  Lifetime (cached): ${s.get('lifetime_value', 0):.2f}")
    
    # Check ACTUAL transactions
    transactions = sb.table('transactions_blaze')\
        .select('transaction_id, date, total_amount', count='exact')\
        .eq('customer_id', s['member_id'])\
        .eq('blaze_status', 'Completed')\
        .execute()
    
    print(f"  ACTUAL Transactions: {transactions.count}")
    if transactions.count > 0:
        total = sum(t.get('total_amount', 0) for t in transactions.data)
        print(f"  ACTUAL Lifetime: ${total:.2f}")

# 3. Check phone (619) 368-3370 for Luis
print("\n" + "=" * 80)
print("3. ALL RECORDS WITH PHONE (619) 368-3370")
print("-" * 80)

phone_records = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, phone, total_visits')\
    .eq('phone', '(619) 368-3370')\
    .execute()

print(f"Found {len(phone_records.data)} records sharing this phone:")
for p in phone_records.data:
    print(f"  - {p['first_name']} {p['last_name']}: {p.get('total_visits', 0)} visits")

if len(phone_records.data) > 1:
    print(f"\n  WARNING: Multiple people still share this phone!")
    print(f"  The merge only handled same first+last+DOB, not same phone numbers")

# Summary
print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)

issues = []

if len(stephen.data) > 1:
    issues.append(f"Stephen Clare has {len(stephen.data)} records (needs fuzzy merge for +/-1 day DOB)")

if len(luis.data) > 1:
    issues.append(f"Luis Bobadilla has {len(luis.data)} records")

if len(phone_records.data) > 1:
    issues.append(f"{len(phone_records.data)} people share phone (619) 368-3370")

if issues:
    print("\nISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    print("\nNEXT STEPS:")
    print("  1. Run MERGE_FUZZY_KEEP_LATER_DATE.sql for +/-1 day DOB issues")
    print("  2. Manually handle shared phone numbers if needed")
else:
    print("\nNo major issues found!")
    print("Accounts look clean!")

