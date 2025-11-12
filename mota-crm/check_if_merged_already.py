#!/usr/bin/env python3
"""
CRITICAL: Check if transactions_blaze was already manually updated
to point to merged customer accounts
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CRITICAL CHECK: Were transactions_blaze manually cleaned?")
print("=" * 80)
print()

# Get unique customer_ids from transactions
print("1. CHECKING TRANSACTIONS")
print("-" * 80)
sample_tx = supabase.table('transactions_blaze').select('customer_id').limit(100).execute()
unique_customer_ids = set([tx.get('customer_id') for tx in sample_tx.data if tx.get('customer_id')])
print(f"Sample of 100 transactions uses {len(unique_customer_ids)} unique customer_ids")
print()

# Check how many of those customer_ids exist in customers_blaze
print("2. CHECKING IF THOSE CUSTOMER_IDS EXIST IN CUSTOMERS_BLAZE")
print("-" * 80)
found = 0
not_found = []

for customer_id in list(unique_customer_ids)[:20]:  # Check first 20
    result = supabase.table('customers_blaze').select('id').eq('member_id', customer_id).execute()
    if result.data:
        found += 1
    else:
        not_found.append(customer_id)

print(f"   Found in customers_blaze: {found}/20")
print(f"   NOT found: {len(not_found)}/20")

if not_found:
    print(f"\n   Example missing customer_ids:")
    for cid in not_found[:5]:
        print(f"      - {cid}")

print()
print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()

if len(not_found) == 0:
    print("GOOD: All transaction customer_ids exist in customers_blaze")
    print("   -> Transactions NOT manually cleaned")
    print("   -> Backfill is SAFE to continue")
elif len(not_found) > 15:
    print("BAD: Most transaction customer_ids DON'T exist in customers_blaze")
    print("   -> Transactions WERE manually cleaned to point to merged accounts")
    print("   -> Backfill is RE-INTRODUCING duplicate linkages")
    print("   -> STOP BACKFILL IMMEDIATELY")
else:
    print("UNCLEAR: Some customer_ids missing")
    print("   -> Need deeper investigation")

print()
print("=" * 80)

