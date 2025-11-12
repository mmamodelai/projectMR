#!/usr/bin/env python3
"""
Investigate Oct 31 Duplicate Transactions
Check why Daniel Fox and others have multiple transactions on same day
"""

import os
from supabase import create_client, Client
from datetime import datetime
from collections import Counter

# Supabase connection
url = "https://kiwmwoqrguyrcpjytgte.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODkyNzY4NCwiZXhwIjoyMDQ0NTAzNjg0fQ.O2prfiL0qB8tpqmLa1Qyo4LZWR0j4BW4U7oOV9Y1VFI"
supabase: Client = create_client(url, key)

print("=" * 80)
print("OCT 31 DUPLICATE TRANSACTIONS INVESTIGATION")
print("=" * 80)
print()

# 1. Check Daniel Fox specifically
print("1. DANIEL FOX TRANSACTIONS ON OCT 31")
print("-" * 80)

# Search for customer by phone (from screenshot: 12084078123)
phone_search = supabase.table('customers_blaze') \
    .select('member_id, name, phone') \
    .ilike('phone', '%2084078123%') \
    .execute()

if phone_search.data:
    daniel = phone_search.data[0]
    member_id = daniel['member_id']
    print(f"Found: {daniel['name']} (ID: {member_id})")
    print()
    
    # Get all Oct 31 transactions
    oct31_txns = supabase.table('transactions_blaze') \
        .select('transaction_id, date, start_time, end_time, total_amount, seller_id, blaze_status') \
        .eq('customer_id', member_id) \
        .gte('date', '2025-10-31T00:00:00') \
        .lte('date', '2025-10-31T23:59:59') \
        .order('date') \
        .execute()
    
    print(f"Oct 31 Transactions: {len(oct31_txns.data)}")
    print()
    
    for txn in oct31_txns.data:
        start = txn['start_time'][:19] if txn['start_time'] else "N/A"
        print(f"  {txn['transaction_id'][:12]}... | {start} | ${txn['total_amount']:.2f} | {txn['blaze_status']}")
    print()

print()
print("2. CHECKING FOR DUPLICATE TRANSACTION PATTERNS")
print("-" * 80)

# Check all Oct 31 transactions
all_oct31 = supabase.table('transactions_blaze') \
    .select('transaction_id, customer_id, date, total_amount, blaze_status') \
    .gte('date', '2025-10-31T00:00:00') \
    .lte('date', '2025-10-31T23:59:59') \
    .execute()

print(f"Total Oct 31 transactions: {len(all_oct31.data)}")
print()

# Group by customer to find those with multiple transactions
customer_counts = Counter([t['customer_id'] for t in all_oct31.data])
multiple_txns = {k: v for k, v in customer_counts.items() if v > 3}

print(f"Customers with 4+ transactions on Oct 31: {len(multiple_txns)}")
print()

if multiple_txns:
    print("Top 10 customers with most Oct 31 transactions:")
    for customer_id, count in sorted(multiple_txns.items(), key=lambda x: x[1], reverse=True)[:10]:
        # Get customer name
        cust = supabase.table('customers_blaze') \
            .select('name') \
            .eq('member_id', customer_id) \
            .limit(1) \
            .execute()
        name = cust.data[0]['name'] if cust.data else 'Unknown'
        print(f"  {name[:30]:<30} | {count} transactions")

print()
print("3. CHECKING TRANSACTION STATUS")
print("-" * 80)

status_counts = Counter([t['blaze_status'] for t in all_oct31.data])
print("Transaction statuses on Oct 31:")
for status, count in status_counts.most_common():
    print(f"  {status:<20} | {count:>5} transactions")

print()
print("4. CHECKING FOR DUPLICATE ITEMS")
print("-" * 80)

# Get all transaction items for Oct 31
oct31_txn_ids = [t['transaction_id'] for t in all_oct31.data]

# Sample first 20 transaction IDs to check items
sample_ids = oct31_txn_ids[:20]

print(f"Checking items for first 20 Oct 31 transactions...")
print()

items_response = supabase.table('transaction_items_blaze') \
    .select('transaction_id, product_name, quantity, brand') \
    .in_('transaction_id', sample_ids) \
    .execute()

print(f"Total items found: {len(items_response.data)}")
print()

# Count item duplicates
item_counts = Counter([
    (item['transaction_id'], item['product_name'], item['brand']) 
    for item in items_response.data
])

duplicates = {k: v for k, v in item_counts.items() if v > 1}
if duplicates:
    print(f"Found {len(duplicates)} duplicate item entries!")
    print("\nExample duplicates:")
    for (txn_id, product, brand), count in list(duplicates.items())[:5]:
        print(f"  {product[:40]:<40} | {brand:<15} | {count}x in txn {txn_id[:12]}")
else:
    print("No duplicate items found in sampled transactions")

print()
print("5. POSSIBLE CAUSES")
print("-" * 80)
print("- Data backfill ran multiple times on Oct 31")
print("- Blaze API returned same transactions multiple times")
print("- Multiple sync processes running simultaneously")
print("- Transaction items inserted multiple times per transaction")
print()
print("RECOMMENDATION:")
print("- Check sync logs for Oct 31")
print("- Look for duplicate transaction_id values in transactions_blaze")
print("- Check if transaction_items have unique constraints")
print("=" * 80)



