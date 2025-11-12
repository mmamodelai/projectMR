#!/usr/bin/env python3
"""
Check Specific Transaction from Screenshot
Date: 2025-08-26, Amount around $22
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("CHECKING TRANSACTION FROM SCREENSHOT")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Find transactions around $22 on 2025-08-26
print("Searching for transaction: 2025-08-26, ~$22")
print()

trans = supabase.table('transactions_blaze') \
    .select('transaction_id, customer_id, date, total_amount, blaze_status') \
    .gte('date', '2025-08-26') \
    .lte('date', '2025-08-27') \
    .gte('total_amount', 21.5) \
    .lte('total_amount', 22.5) \
    .execute()

if trans.data:
    print(f"Found {len(trans.data)} matching transactions:\n")
    
    for t in trans.data:
        print(f"Transaction: {t['transaction_id']}")
        print(f"  Date: {t['date'][:10]}")
        print(f"  Amount: ${t['total_amount']:.2f}")
        print(f"  Status: {t['blaze_status']}")
        
        # Get customer name
        cust = supabase.table('customers_blaze') \
            .select('name, first_name, last_name') \
            .eq('member_id', t['customer_id']) \
            .execute()
        
        if cust.data:
            c = cust.data[0]
            name = c.get('name') or f"{c.get('first_name', '')} {c.get('last_name', '')}".strip()
            print(f"  Customer: {name}")
        
        # CHECK ITEMS
        items = supabase.table('transaction_items_blaze') \
            .select('id, product_name, brand, quantity, total_price, product_id') \
            .eq('transaction_id', t['transaction_id']) \
            .execute()
        
        print(f"\n  ITEMS: {len(items.data)} found")
        
        if items.data:
            print("  Items list:")
            for item in items.data:
                name = item.get('product_name') or 'NULL/MISSING'
                brand = item.get('brand') or 'NULL/MISSING'
                price = item.get('total_price') or 0
                print(f"    - {name[:50]:<50} | {brand:<15} | ${price:.2f}")
        else:
            print("  *** NO ITEMS IN DATABASE FOR THIS TRANSACTION! ***")
            print("  This is why Items panel is empty!")
        
        print()
else:
    print("No transactions found matching that criteria!")
    print("\nLet me check what transactions DO exist on 2025-08-26:")
    
    all_aug26 = supabase.table('transactions_blaze') \
        .select('transaction_id, total_amount, date') \
        .gte('date', '2025-08-26') \
        .lte('date', '2025-08-27') \
        .limit(20) \
        .execute()
    
    if all_aug26.data:
        print(f"\nAll transactions on 2025-08-26: ({len(all_aug26.data)} found)")
        for t in all_aug26.data[:10]:
            print(f"  ${t['total_amount']:.2f} at {t['date'][:16]}")

print()
print("=" * 80)
print("DIAGNOSIS")
print("=" * 80)
print()
print("If 'NO ITEMS IN DATABASE' appears above:")
print("  -> That transaction has no items in transaction_items_blaze")
print("  -> This is a DATA issue, not a viewer issue")
print("  -> The sync didn't capture items for that transaction")
print()
print("If items ARE found:")
print("  -> It's a viewer bug - items exist but not displaying")
print("  -> Check viewer console for error messages")
print()
print("=" * 80)

