#!/usr/bin/env python3
"""
Check if transaction_items_blaze → transactions_blaze → customers_blaze
linkage is correct, or if we're pointing to dead duplicate accounts
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CUSTOMER LINKAGE CHECK - Are We Pointing to Dead Accounts?")
print("=" * 80)
print()

# 1. Check Luis Bobadilla - how many accounts?
print("1. CHECKING LUIS BOBADILLA ACCOUNTS")
print("-" * 80)
luis_accounts = supabase.table('customers_blaze').select('*').ilike('name', '%Luis%Bobadilla%').execute()
print(f"Found {len(luis_accounts.data)} accounts for Luis Bobadilla:")
for acc in luis_accounts.data:
    print(f"   - ID: {acc.get('id')} | Name: {acc.get('name')} | Phone: {acc.get('phone')}")
print()

# 2. Check transactions for Luis - which customer_id do they use?
if luis_accounts.data:
    luis_ids = [acc.get('id') for acc in luis_accounts.data]
    print("2. CHECKING TRANSACTIONS FOR LUIS")
    print("-" * 80)
    
    for customer_id in luis_ids:
        txns = supabase.table('transactions_blaze').select('transaction_id, date').eq('customer_id', customer_id).order('date', desc=True).limit(3).execute()
        print(f"   Customer ID {customer_id}: {len(txns.data)} transactions (showing last 3)")
        for tx in txns.data[:3]:
            print(f"      - {tx.get('date')} (txn: {tx.get('transaction_id')})")
    print()

# 3. Check if transaction_items point to these transactions
print("3. CHECKING TRANSACTION_ITEMS LINKAGE")
print("-" * 80)
if luis_accounts.data and len(luis_accounts.data) > 0:
    # Get a recent transaction from ANY Luis account
    sample_tx = supabase.table('transactions_blaze').select('transaction_id, customer_id, date').in_('customer_id', luis_ids).order('date', desc=True).limit(1).execute()
    
    if sample_tx.data:
        tx_id = sample_tx.data[0].get('transaction_id')
        cust_id = sample_tx.data[0].get('customer_id')
        print(f"Sample transaction: {tx_id}")
        print(f"   Linked to customer_id: {cust_id}")
        
        # Check if transaction_items exist for this transaction
        items = supabase.table('transaction_items_blaze').select('*').eq('transaction_id', tx_id).execute()
        print(f"   Transaction items found: {len(items.data)}")
        if items.data:
            for item in items.data[:3]:
                print(f"      - {item.get('product_name')}: ${item.get('unit_price')} x {item.get('quantity')}")
print()

# 4. Check Stephen Clare (user mentioned duplicate accounts)
print("4. CHECKING STEPHEN CLARE ACCOUNTS")
print("-" * 80)
stephen_accounts = supabase.table('customers_blaze').select('*').ilike('name', '%Stephen%Clare%').execute()
print(f"Found {len(stephen_accounts.data)} accounts for Stephen Clare:")
for acc in stephen_accounts.data:
    print(f"   - ID: {acc.get('id')} | Name: {acc.get('name')} | Phone: {acc.get('phone')}")
    
    # Check transaction count for each account
    txns = supabase.table('transactions_blaze').select('transaction_id', count='exact').eq('customer_id', acc.get('id')).limit(1).execute()
    print(f"     Transactions: {txns.count}")
print()

# 5. Overall health check
print("5. OVERALL LINKAGE HEALTH")
print("-" * 80)

# Get total transactions
tx_count = supabase.table('transactions_blaze').select('transaction_id', count='exact').limit(1).execute()
print(f"Total transactions_blaze: {tx_count.count:,}")

# Get total transaction items
items_count = supabase.table('transaction_items_blaze').select('id', count='exact').limit(1).execute()
print(f"Total transaction_items_blaze: {items_count.count:,}")

# Check how many transactions have items
print("\nSampling: Do transactions have items?")
sample_txns = supabase.table('transactions_blaze').select('transaction_id').order('date', desc=True).limit(10).execute()
for tx in sample_txns.data:
    tx_id = tx.get('transaction_id')
    items = supabase.table('transaction_items_blaze').select('id', count='exact').eq('transaction_id', tx_id).limit(1).execute()
    status = "HAS ITEMS" if items.count > 0 else "NO ITEMS"
    print(f"   Transaction {tx_id}: {items.count} items ({status})")

print()
print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()
print("If Luis/Stephen have MULTIPLE accounts with transactions spread across them:")
print("  -> BAD: Duplicate accounts not consolidated")
print()
print("If Luis/Stephen have ONE main account with ALL transactions:")
print("  -> GOOD: Accounts properly consolidated")
print()
print("If transaction_items_blaze can't find items for recent transactions:")
print("  -> BAD: Linkage broken or backfill incomplete")
print()
print("=" * 80)

