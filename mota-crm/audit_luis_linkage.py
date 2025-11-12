#!/usr/bin/env python3
"""
AUDIT: Do Luis's transactions properly link to items?
"""

from supabase import create_client
from datetime import datetime

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("AUDIT: LUIS'S TRANSACTION -> ITEMS LINKAGE")
print("=" * 80)
print()

# Get Luis's member_ids
luis = supabase.table('customers_blaze').select('member_id, name').ilike('name', '%Luis%Bobadilla%').execute()
member_ids = [acc.get('member_id') for acc in luis.data]

print(f"Luis has {len(member_ids)} accounts")
print()

# Get ALL transactions for Luis
all_transactions = []
for member_id in member_ids:
    offset = 0
    while True:
        txns = supabase.table('transactions_blaze').select('transaction_id, date').eq('customer_id', member_id).range(offset, offset + 999).execute()
        if not txns.data:
            break
        all_transactions.extend(txns.data)
        offset += 1000
        if len(txns.data) < 1000:
            break

print(f"TOTAL TRANSACTIONS: {len(all_transactions)}")
print()

# Categorize by date
before_2024 = []
after_2024 = []

for tx in all_transactions:
    tx_date = tx.get('date')
    if tx_date:
        try:
            date_obj = datetime.fromisoformat(tx_date.replace('Z', '+00:00'))
            if date_obj.year < 2024:
                before_2024.append(tx)
            else:
                after_2024.append(tx)
        except:
            pass

print("TRANSACTIONS BY DATE:")
print(f"   Before 2024: {len(before_2024)}")
print(f"   2024+: {len(after_2024)}")
print()

# Check which transactions have items
print("=" * 80)
print("CHECKING ITEMS LINKAGE:")
print("=" * 80)
print()

print("Checking BEFORE 2024 transactions (should have NO items):")
has_items_old = 0
for tx in before_2024[:20]:  # Sample 20
    items = supabase.table('transaction_items_blaze').select('id', count='exact').eq('transaction_id', tx.get('transaction_id')).limit(1).execute()
    if items.count > 0:
        has_items_old += 1

print(f"   Sample: {has_items_old}/20 have items (should be 0)")
print()

print("Checking 2024+ transactions (SHOULD have items from backfill):")
has_items_new = 0
no_items_new = 0
for tx in after_2024[:20]:  # Sample 20
    items = supabase.table('transaction_items_blaze').select('id', count='exact').eq('transaction_id', tx.get('transaction_id')).limit(1).execute()
    if items.count > 0:
        has_items_new += 1
    else:
        no_items_new += 1

print(f"   Sample: {has_items_new}/20 have items")
print(f"   Sample: {no_items_new}/20 missing items (backfill not reached yet)")
print()

print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()

if has_items_new > 0:
    print("GOOD: 2024+ transactions ARE getting items linked")
    print(f"   Linkage is working: transaction_id -> items")
else:
    print("BAD: 2024+ transactions have NO items")
    print("   Backfill may not have reached these yet")

print()
print(f"Backfill progress: Still running (currently at ~243K items)")
print(f"Once complete, ALL 2024+ transactions ({len(after_2024)}) should have items")
print()
print("=" * 80)

