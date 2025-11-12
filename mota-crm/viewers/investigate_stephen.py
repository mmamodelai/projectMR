#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("INVESTIGATING: Stephen Clare")
print("=" * 80)

# 1. Check how many Stephen Clare records exist
print("\n1. Looking for ALL 'Stephen Clare' records...")
stephens = sb.table('customers_blaze')\
    .select('member_id, first_name, last_name, phone, email, total_visits, lifetime_value, date_of_birth')\
    .ilike('first_name', 'stephen')\
    .ilike('last_name', 'clare')\
    .execute()

print(f"   Found {len(stephens.data)} Stephen Clare record(s):")
for s in stephens.data:
    print(f"\n   - ID: {s['member_id']}")
    print(f"     Name: {s['first_name']} {s['last_name']}")
    print(f"     Phone: {s.get('phone', 'N/A')}")
    print(f"     Email: {s.get('email', 'N/A')}")
    print(f"     DOB: {s.get('date_of_birth', 'N/A')}")
    print(f"     Visits (cached): {s.get('total_visits', 0)}")
    print(f"     Lifetime (cached): ${s.get('lifetime_value', 0):.2f}")

# 2. Check ACTUAL transactions for each Stephen Clare
print("\n" + "=" * 80)
print("2. Checking ACTUAL transactions in database...")
print("=" * 80)

for s in stephens.data:
    member_id = s['member_id']
    print(f"\n   Checking transactions for {s['first_name']} {s['last_name']} ({member_id}):")
    
    transactions = sb.table('transactions_blaze')\
        .select('transaction_id, date, total_amount, blaze_status')\
        .eq('customer_id', member_id)\
        .eq('blaze_status', 'Completed')\
        .execute()
    
    if transactions.data:
        print(f"   >>> FOUND {len(transactions.data)} transactions!")
        print(f"       Total amount: ${sum(t.get('total_amount', 0) for t in transactions.data):.2f}")
        print(f"\n       Sample transactions:")
        for t in transactions.data[:5]:
            print(f"       - {t.get('date', 'N/A')}: ${t.get('total_amount', 0):.2f}")
    else:
        print(f"   >>> NO transactions found")

# 3. Check the backup to see what was there before merge
print("\n" + "=" * 80)
print("SUMMARY:")
print("=" * 80)
print(f"Total Stephen Clare records now: {len(stephens.data)}")

