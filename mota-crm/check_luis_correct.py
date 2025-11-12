#!/usr/bin/env python3
"""
Check Luis's transactions using CORRECT member_id linkage
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("LUIS BOBADILLA - CORRECT LINKAGE CHECK")
print("=" * 80)
print()

# Get Luis's accounts
luis_accounts = supabase.table('customers_blaze').select('*').ilike('name', '%Luis%Bobadilla%').execute()
print(f"LUIS ACCOUNTS: {len(luis_accounts.data)}")
print("-" * 80)

total_transactions = 0
total_items = 0

for acc in luis_accounts.data:
    print(f"\nAccount: {acc.get('name')}")
    print(f"   Supabase ID: {acc.get('id')}")
    print(f"   Blaze member_id: {acc.get('member_id')}")
    print(f"   Phone: {acc.get('phone')}")
    
    # Get transactions using member_id (CORRECT)
    if acc.get('member_id'):
        txns = supabase.table('transactions_blaze').select('transaction_id, date').eq('customer_id', acc.get('member_id')).order('date', desc=True).limit(5).execute()
        print(f"   Transactions: {len(txns.data)}")
        total_transactions += len(txns.data)
        
        for tx in txns.data[:3]:
            print(f"      - {tx.get('date')}: {tx.get('transaction_id')}")
            
            # Get items for this transaction
            items = supabase.table('transaction_items_blaze').select('id', count='exact').eq('transaction_id', tx.get('transaction_id')).limit(1).execute()
            total_items += items.count
            print(f"         Items: {items.count}")

print()
print("=" * 80)
print(f"TOTAL ACROSS ALL LUIS ACCOUNTS:")
print(f"   Transactions: {total_transactions}")
print(f"   Items: {total_items}")
print("=" * 80)
print()

# Check if there are duplicate transactions across accounts
if len(luis_accounts.data) > 1:
    print("CHECKING FOR DUPLICATE TRANSACTIONS")
    print("-" * 80)
    all_tx_ids = []
    for acc in luis_accounts.data:
        if acc.get('member_id'):
            txns = supabase.table('transactions_blaze').select('transaction_id').eq('customer_id', acc.get('member_id')).execute()
            all_tx_ids.extend([tx.get('transaction_id') for tx in txns.data])
    
    unique_tx_ids = set(all_tx_ids)
    print(f"   Total transactions: {len(all_tx_ids)}")
    print(f"   Unique transactions: {len(unique_tx_ids)}")
    
    if len(all_tx_ids) == len(unique_tx_ids):
        print("   NO DUPLICATES - Each account has separate transactions")
    else:
        print(f"   DUPLICATES FOUND - {len(all_tx_ids) - len(unique_tx_ids)} duplicate transactions")

print()
print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()
if len(luis_accounts.data) > 1:
    print("WARNING: Luis has multiple accounts!")
    print("   - This means his purchase history is SPLIT across accounts")
    print("   - The CRM/AI will NOT see his complete history")
    print("   - Accounts need to be merged in Blaze, then re-synced")
else:
    print("GOOD: Luis has one consolidated account")
print()
print("=" * 80)

