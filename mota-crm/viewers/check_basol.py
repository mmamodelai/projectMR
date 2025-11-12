#!/usr/bin/env python3
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("HOW DID BASOL GUNGOR GET IN THE SYSTEM WITH 0 VISITS?")
print("=" * 80)

basol = sb.table('customers_blaze')\
    .select('*')\
    .eq('member_id', '685d86cde2dd4760bd13c14d')\
    .execute()

if basol.data:
    b = basol.data[0]
    print(f"\nBasol Gungor's record:")
    print(f"  Member ID: {b['member_id']}")
    print(f"  Name: {b['first_name']} {b['last_name']}")
    print(f"  Phone: {b.get('phone')}")
    print(f"  Email: {b.get('email')}")
    print(f"  DOB: {b.get('date_of_birth')}")
    print(f"  Created: {b.get('created_at')}")
    print(f"  Date Joined: {b.get('date_joined')}")
    print(f"  Total Visits: {b.get('total_visits')}")
    print(f"  Lifetime Value: ${b.get('lifetime_value', 0):.2f}")

# Check ALL transactions (not just Completed)
all_tx = sb.table('transactions_blaze')\
    .select('transaction_id, date, blaze_status, total_amount')\
    .eq('customer_id', '685d86cde2dd4760bd13c14d')\
    .execute()

print(f"\n  ALL Transactions (any status): {len(all_tx.data)}")
if all_tx.data:
    for tx in all_tx.data:
        print(f"    - {tx['date'][:10]}: ${tx['total_amount']:.2f} ({tx['blaze_status']})")
else:
    print("    NONE! Literally 0 transactions")

print("\n" + "=" * 80)
print("THEORY:")
print("=" * 80)
print("Blaze creates customer records in two ways:")
print("  1. At checkout (has transactions)")
print("  2. Pre-registration / Profile creation WITHOUT checkout")
print("     - Someone signed up for loyalty/rewards")
print("     - Budtender created profile but customer left")
print("     - Online registration never followed by purchase")
print("\nBasol Gungor probably got created but never actually bought anything.")
print("These 0-transaction customers are NOISE and should probably be deleted.")

