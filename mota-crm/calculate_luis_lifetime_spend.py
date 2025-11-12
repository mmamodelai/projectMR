#!/usr/bin/env python3
"""
Calculate Luis's TOTAL lifetime spend across all accounts
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("LUIS BOBADILLA - LIFETIME SPEND CALCULATION")
print("=" * 80)
print()

# Get Luis accounts
luis_accounts = supabase.table('customers_blaze').select('*').ilike('name', '%Luis%Bobadilla%').execute()

total_spend = 0.0
account_spends = []

for acc in luis_accounts.data:
    member_id = acc.get('member_id')
    name = acc.get('name')
    
    print(f"ACCOUNT: {name}")
    print(f"   member_id: {member_id}")
    print()
    
    # Get ALL transactions for this account
    all_transactions = []
    offset = 0
    limit = 1000
    
    while True:
        txns = supabase.table('transactions_blaze').select('*').eq('customer_id', member_id).range(offset, offset + limit - 1).execute()
        
        if not txns.data:
            break
        
        all_transactions.extend(txns.data)
        offset += limit
        
        if len(txns.data) < limit:
            break
    
    print(f"   Total transactions: {len(all_transactions)}")
    
    # Calculate spend from transaction items
    account_spend = 0.0
    items_found = 0
    
    for tx in all_transactions:
        tx_id = tx.get('transaction_id')
        
        # Get items for this transaction
        items = supabase.table('transaction_items_blaze').select('*').eq('transaction_id', tx_id).execute()
        
        for item in items.data:
            final_price = item.get('final_price')
            if final_price:
                account_spend += float(final_price)
                items_found += 1
    
    print(f"   Items found: {items_found}")
    print(f"   Total spend: ${account_spend:,.2f}")
    print()
    
    account_spends.append({
        'name': name,
        'transactions': len(all_transactions),
        'items': items_found,
        'spend': account_spend
    })
    
    total_spend += account_spend

print("=" * 80)
print("SUMMARY")
print("=" * 80)
print()

for acc_data in account_spends:
    percent = (acc_data['spend'] / total_spend * 100) if total_spend > 0 else 0
    print(f"{acc_data['name']}:")
    print(f"   Transactions: {acc_data['transactions']}")
    print(f"   Items: {acc_data['items']}")
    print(f"   Spend: ${acc_data['spend']:,.2f} ({percent:.1f}%)")
    print()

print(f"TOTAL LIFETIME SPEND: ${total_spend:,.2f}")
print()

print("=" * 80)
print("NOTE:")
print("=" * 80)
print()
print("This is calculated from transaction_items_blaze (currently backfilling)")
print(f"Current backfill progress: ~243K items (26% complete)")
print()
print("Once backfill completes (~900K items), this number will be higher")
print("as we'll have ALL items from Jan 1, 2024 to now.")
print()
print("=" * 80)

