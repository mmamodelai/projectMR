#!/usr/bin/env python3
"""
Debug Why Items Panel is Empty
Check specific transaction that user clicked
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

print("=" * 80)
print("DEBUG: Why Items Panel is Empty")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# From screenshot: Carlos Aguztingonez, 2025-08-26, $22.00
print("Looking for transaction matching screenshot:")
print("  Customer: Carlos Aguztingonez")
print("  Date: 2025-08-26")
print("  Amount: $22.00")
print()

# Find this customer
cust = supabase.table('customers_blaze') \
    .select('member_id, name') \
    .ilike('name', '%Carlos%Aguzt%') \
    .execute()

if not cust.data:
    print("Customer not found - trying broader search...")
    cust = supabase.table('customers_blaze') \
        .select('member_id, name') \
        .ilike('name', '%Carlos%') \
        .limit(5) \
        .execute()

if cust.data:
    print(f"Found {len(cust.data)} matching customers:")
    for c in cust.data:
        print(f"  {c['name']} - ID: {c['member_id'][:20]}...")
    
    # Use first match
    member_id = cust.data[0]['member_id']
    print(f"\nChecking transactions for: {cust.data[0]['name']}")
    print()
    
    # Get transactions around that date
    trans = supabase.table('transactions_blaze') \
        .select('transaction_id, date, total_amount, blaze_status') \
        .eq('customer_id', member_id) \
        .gte('date', '2025-08-20') \
        .lte('date', '2025-08-30') \
        .execute()
    
    if trans.data:
        print(f"Found {len(trans.data)} transactions in Aug 2025:")
        for t in trans.data:
            print(f"  {t['date'][:10]} | ${t['total_amount']:.2f} | {t['blaze_status']}")
            
            # Check items for each
            items = supabase.table('transaction_items_blaze') \
                .select('*', count='exact') \
                .eq('transaction_id', t['transaction_id']) \
                .limit(0) \
                .execute()
            
            print(f"    -> Has {items.count} items")
            
            # If this is the $22 transaction, show details
            if abs(t['total_amount'] - 22.00) < 0.01:
                print(f"\n    THIS IS THE ONE! Transaction ID: {t['transaction_id']}")
                
                # Get items
                items_detail = supabase.table('transaction_items_blaze') \
                    .select('id, product_name, brand, quantity, total_price') \
                    .eq('transaction_id', t['transaction_id']) \
                    .execute()
                
                if items_detail.data:
                    print(f"    Items found: {len(items_detail.data)}")
                    for item in items_detail.data:
                        name = item.get('product_name') or 'NULL'
                        brand = item.get('brand') or 'NULL'
                        print(f"      - {name[:40]:<40} | {brand:<15} | ${item['total_price']:.2f}")
                else:
                    print("    NO ITEMS FOUND!")
                    print("    This is why the Items panel is empty!")
    else:
        print("  No transactions found in late August")
else:
    print("Customer not found!")
    print("\nLet me check a recent transaction instead...")
    
    # Just get any recent transaction with items
    recent = supabase.table('transactions_blaze') \
        .select('transaction_id, customer_id, date, total_amount') \
        .order('date', desc=True) \
        .limit(5) \
        .execute()
    
    print("\nRecent transactions:")
    for t in recent.data:
        items = supabase.table('transaction_items_blaze') \
            .select('*', count='exact') \
            .eq('transaction_id', t['transaction_id']) \
            .limit(0) \
            .execute()
        
        print(f"  {t['date'][:10]} | ${t['total_amount']:.2f} | {items.count} items")

print()
print("=" * 80)
print("CHECKING VIEWER CODE")
print("=" * 80)
print()
print("The viewer calls:")
print("  self.sb.table('transaction_items_blaze').select(...)")
print("  .eq('transaction_id', transaction_id)")
print()
print("Possible issues:")
print("  1. Transaction has no items in transaction_items_blaze")
print("  2. transaction_id format doesn't match")
print("  3. Items query is failing silently")
print()
print("=" * 80)

