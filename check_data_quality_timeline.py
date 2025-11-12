#!/usr/bin/env python3
"""
Check Data Quality Timeline
See when data is good vs when it's missing prices/names
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("DATA QUALITY TIMELINE CHECK")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check different time periods
time_periods = [
    ("Nov 2025", "2025-11-01", "2025-11-10"),
    ("Oct 2025", "2025-10-01", "2025-10-31"),
    ("Sep 2025", "2025-09-01", "2025-09-30"),
    ("Aug 2025", "2025-08-01", "2025-08-31"),
    ("Jan 2025", "2025-01-01", "2025-01-31"),
    ("Dec 2024", "2024-12-01", "2024-12-31"),
]

print("Checking data quality by month:")
print("=" * 80)
print(f"{'Period':<15} {'Transactions':<15} {'Items':<15} {'Has Name':<15} {'Has Price':<15}")
print("-" * 80)

for period_name, start_date, end_date in time_periods:
    # Get transactions in this period
    trans = supabase.table('transactions_blaze') \
        .select('transaction_id', count='exact') \
        .gte('date', start_date) \
        .lt('date', end_date) \
        .limit(0) \
        .execute()
    
    trans_count = trans.count if trans.count else 0
    
    if trans_count == 0:
        print(f"{period_name:<15} {'0':<15} {'-':<15} {'-':<15} {'-':<15}")
        continue
    
    # Get sample transactions to check items
    sample_trans = supabase.table('transactions_blaze') \
        .select('transaction_id') \
        .gte('date', start_date) \
        .lt('date', end_date) \
        .limit(10) \
        .execute()
    
    sample_ids = [t['transaction_id'] for t in sample_trans.data]
    
    if not sample_ids:
        print(f"{period_name:<15} {trans_count:<15} {'-':<15} {'-':<15} {'-':<15}")
        continue
    
    # Check items for these transactions
    items = supabase.table('transaction_items_blaze') \
        .select('product_name, total_price') \
        .in_('transaction_id', sample_ids) \
        .execute()
    
    if items.data:
        items_count = len(items.data)
        has_name = sum(1 for i in items.data if i.get('product_name'))
        has_price = sum(1 for i in items.data if i.get('total_price') is not None and i.get('total_price') != 0)
        
        name_pct = int((has_name / items_count) * 100) if items_count > 0 else 0
        price_pct = int((has_price / items_count) * 100) if items_count > 0 else 0
        
        print(f"{period_name:<15} {trans_count:<15} {items_count:<15} {name_pct}%{'':<12} {price_pct}%{'':<12}")
    else:
        print(f"{period_name:<15} {trans_count:<15} {'0 ITEMS!':<15} {'-':<15} {'-':<15}")

print()
print("=" * 80)
print("DETAILED CHECK: Recent vs Old")
print("=" * 80)
print()

# Check a recent transaction in detail
print("RECENT (Nov 2025) - Sample Transaction:")
recent = supabase.table('transactions_blaze') \
    .select('transaction_id, date, total_amount') \
    .gte('date', '2025-11-01') \
    .limit(1) \
    .execute()

if recent.data:
    t = recent.data[0]
    print(f"  Transaction: {t['date'][:10]} | ${t['total_amount']:.2f}")
    
    items = supabase.table('transaction_items_blaze') \
        .select('product_name, brand, quantity, total_price, unit_price') \
        .eq('transaction_id', t['transaction_id']) \
        .execute()
    
    print(f"  Items: {len(items.data)}")
    for item in items.data[:3]:
        name = item.get('product_name') or 'NULL'
        price = item.get('total_price')
        unit = item.get('unit_price')
        print(f"    {name[:40]:<40} | total_price: ${price if price else 'NULL'} | unit_price: ${unit if unit else 'NULL'}")

print()
print("OLD (Aug 2025) - Sample Transaction:")
old = supabase.table('transactions_blaze') \
    .select('transaction_id, date, total_amount') \
    .gte('date', '2025-08-01') \
    .lt('date', '2025-08-31') \
    .limit(1) \
    .execute()

if old.data:
    t = old.data[0]
    print(f"  Transaction: {t['date'][:10]} | ${t['total_amount']:.2f}")
    
    items = supabase.table('transaction_items_blaze') \
        .select('product_name, brand, quantity, total_price, unit_price') \
        .eq('transaction_id', t['transaction_id']) \
        .execute()
    
    print(f"  Items: {len(items.data)}")
    for item in items.data[:3]:
        name = item.get('product_name') or 'NULL'
        price = item.get('total_price')
        unit = item.get('unit_price')
        print(f"    {name[:40]:<40} | total_price: ${price if price else 'NULL'} | unit_price: ${unit if unit else 'NULL'}")

print()
print("=" * 80)
print("VERDICT")
print("=" * 80)
print()
print("If Nov 2025 has prices but Aug 2025 doesn't:")
print("  -> Your recent backfill IS working")
print("  -> Old data from before rebuild is missing prices")
print("  -> This is normal - Blaze API may not return item prices for old transactions")
print()
print("If NOTHING has prices:")
print("  -> The sync isn't capturing the price field")
print("  -> Need to check sync script")
print()
print("=" * 80)

