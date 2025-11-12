#!/usr/bin/env python3
"""
Quick check: Why are customer stats zero?
"""
import os
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== CHECKING DATABASE STATE ===\n")

# 1. Check customer stats
print("1. CUSTOMER STATS (first 5):")
customers = sb.table('customers_blaze').select('member_id, name, total_visits, lifetime_value, last_visited').order('created_at', desc=True).limit(5).execute()
for c in customers.data:
    print(f"   {c.get('name', 'N/A')[:30]:<30} | Visits: {c.get('total_visits')} | LTV: ${c.get('lifetime_value')} | Last: {c.get('last_visited')}")

# 2. Check if ANY customers have stats
print("\n2. CUSTOMERS WITH NON-ZERO STATS:")
with_stats = sb.table('customers_blaze').select('member_id, name, total_visits, lifetime_value').gt('total_visits', 0).limit(5).execute()
print(f"   Found {len(with_stats.data)} customers with visits > 0")
if with_stats.data:
    for c in with_stats.data:
        print(f"   {c.get('name', 'N/A')[:30]:<30} | Visits: {c.get('total_visits')} | LTV: ${c.get('lifetime_value')}")

# 3. Check total transactions
print("\n3. TRANSACTIONS COUNT:")
trans_count = sb.table('transactions_blaze').select('transaction_id', count='exact').limit(1).execute()
print(f"   Total transactions: {trans_count.count}")

# 4. Check specific customer (NASERA ANN ALAYON from screenshot)
print("\n4. CHECKING SPECIFIC CUSTOMER:")
# Try to find by name
nasera = sb.table('customers_blaze').select('member_id, name, total_visits, lifetime_value').ilike('name', '%NASERA%').execute()
if nasera.data:
    customer = nasera.data[0]
    member_id = customer['member_id']
    print(f"   Customer: {customer['name']}")
    print(f"   Member ID: {member_id}")
    print(f"   Total Visits (in DB): {customer.get('total_visits')}")
    print(f"   Lifetime Value (in DB): ${customer.get('lifetime_value')}")
    
    # Check if they have transactions
    print(f"\n   Checking transactions for {member_id}:")
    trans = sb.table('transactions_blaze').select('transaction_id, date, total_amount').eq('customer_id', member_id).order('date', desc=True).limit(5).execute()
    print(f"   Found {len(trans.data)} transactions")
    for t in trans.data:
        print(f"      {t.get('date')[:10]} | ${t.get('total_amount')} | ID: {t.get('transaction_id')}")
else:
    print("   Customer not found")

# 5. Sample transaction to customer link
print("\n5. RANDOM TRANSACTION CHECK:")
sample_trans = sb.table('transactions_blaze').select('transaction_id, customer_id, date, total_amount, blaze_status').order('date', desc=True).limit(1).execute()
if sample_trans.data:
    t = sample_trans.data[0]
    print(f"   Latest Transaction: {t.get('transaction_id')}")
    print(f"   Customer ID: {t.get('customer_id')}")
    print(f"   Date: {t.get('date')}")
    print(f"   Amount: ${t.get('total_amount')}")
    print(f"   Status: {t.get('blaze_status')}")

print("\n=== DIAGNOSIS ===")
print("If customers have 0 visits but transactions exist:")
print("  -> Customer stats need to be calculated/backfilled")
print("\nIf transactions exist for customer but don't show in viewer:")
print("  -> Check viewer query logic")

