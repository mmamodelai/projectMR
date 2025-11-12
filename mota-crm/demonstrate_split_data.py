#!/usr/bin/env python3
"""
Demonstrate: Luis's data is SPLIT across 2 accounts
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("LUIS BOBADILLA - DATA SPLIT DEMONSTRATION")
print("=" * 80)
print()

# Get Luis accounts
luis_accounts = supabase.table('customers_blaze').select('*').ilike('name', '%Luis%Bobadilla%').execute()

account_data = {}

for acc in luis_accounts.data:
    member_id = acc.get('member_id')
    name = acc.get('name')
    phone = acc.get('phone')
    
    print(f"ACCOUNT: {name}")
    print(f"   member_id: {member_id}")
    print(f"   phone: {phone}")
    print()
    
    # Get transactions
    txns = supabase.table('transactions_blaze').select('transaction_id, date', count='exact').eq('customer_id', member_id).execute()
    
    # Get transaction items for those transactions
    total_items = 0
    if txns.data:
        for tx in txns.data[:3]:  # Sample first 3
            items = supabase.table('transaction_items_blaze').select('*').eq('transaction_id', tx.get('transaction_id')).execute()
            total_items += len(items.data)
    
    account_data[name] = {
        'transactions': txns.count,
        'sample_items': total_items
    }
    
    print(f"   Transactions: {txns.count}")
    print(f"   Sample items (first 3 tx): {total_items}")
    print()
    
    # Show sample transactions
    print(f"   Recent transactions:")
    for tx in txns.data[:5]:
        print(f"      - {tx.get('date')}: {tx.get('transaction_id')}")
    print()

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

total_tx = sum([data['transactions'] for data in account_data.values()])
print(f"Total transactions across ALL Luis accounts: {total_tx}")
print()

for name, data in account_data.items():
    percent = (data['transactions'] / total_tx * 100) if total_tx > 0 else 0
    print(f"   {name}: {data['transactions']} transactions ({percent:.1f}%)")

print()
print("=" * 80)
print("THE PROBLEM:")
print("=" * 80)
print()
print("If CRM queries by phone: +16193683370")
print("   -> Finds: Luis Bobadilla (account with phone)")
print(f"   -> Gets: {account_data.get('Luis Bobadilla', {}).get('transactions', 0)} transactions")
print(f"   -> MISSES: {account_data.get('LUIS BOBADILLA', {}).get('transactions', 0)} transactions from duplicate account")
print()
print("If AI asks 'What has Luis purchased?'")
print("   -> Sees only HALF his history")
print("   -> Makes wrong recommendations")
print()
print("=" * 80)
print("SOLUTIONS:")
print("=" * 80)
print()
print("Option 1: Merge in Blaze POS")
print("   -> Merge duplicate accounts in Blaze itself")
print("   -> Re-sync customers from Blaze")
print("   -> Transactions will then point to single account")
print()
print("Option 2: SQL mapping table")
print("   -> Create 'customer_aliases' table")
print("   -> Map both member_ids to same 'true' customer")
print("   -> Query uses mapping to get ALL data")
print()
print("Option 3: SQL view with aggregation")
print("   -> Create view that groups by name/phone")
print("   -> Aggregates data from all matching accounts")
print("   -> CRM queries the view instead of raw table")
print()
print("=" * 80)

