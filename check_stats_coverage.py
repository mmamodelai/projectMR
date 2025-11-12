#!/usr/bin/env python3
"""
Check: How many customers have stats vs. how many should?
"""
import os
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs")

sb = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=== STATS COVERAGE ANALYSIS ===\n")

# 1. Total customers
total_customers = sb.table('customers_blaze').select('member_id', count='exact').limit(1).execute()
print(f"1. TOTAL CUSTOMERS: {total_customers.count}")

# 2. Customers with visits > 0
with_visits = sb.table('customers_blaze').select('member_id', count='exact').gt('total_visits', 0).limit(1).execute()
print(f"2. CUSTOMERS WITH VISITS > 0: {with_visits.count}")

# 3. Customers with last_visited NOT NULL
with_last_visit = sb.table('customers_blaze').select('member_id', count='exact').not_.is_('last_visited', 'null').limit(1).execute()
print(f"3. CUSTOMERS WITH LAST_VISITED: {with_last_visit.count}")

# 4. Total transactions
total_trans = sb.table('transactions_blaze').select('transaction_id', count='exact').limit(1).execute()
print(f"4. TOTAL TRANSACTIONS: {total_trans.count}")

# 5. Unique customers in transactions
print("\n5. UNIQUE CUSTOMERS IN TRANSACTIONS:")
print("   (Sampling to estimate...)")
sample_trans = sb.table('transactions_blaze').select('customer_id').eq('blaze_status', 'Completed').limit(10000).execute()
unique_customers = len(set([t['customer_id'] for t in sample_trans.data if t.get('customer_id')]))
print(f"   Sample of 10k transactions has {unique_customers} unique customers")

# 6. Check date range of transactions
print("\n6. TRANSACTION DATE RANGE:")
earliest = sb.table('transactions_blaze').select('date').order('date', desc=False).limit(1).execute()
latest = sb.table('transactions_blaze').select('date').order('date', desc=True).limit(1).execute()
if earliest.data and latest.data:
    print(f"   Earliest: {earliest.data[0]['date'][:10]}")
    print(f"   Latest: {latest.data[0]['date'][:10]}")

# 7. Recent transactions (last 30 days)
print("\n7. RECENT ACTIVITY (Last 30 days):")
from datetime import datetime, timedelta
thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
recent_trans = sb.table('transactions_blaze').select('transaction_id', count='exact').gte('date', thirty_days_ago).limit(1).execute()
print(f"   Transactions in last 30 days: {recent_trans.count}")

print("\n=== DIAGNOSIS ===")
coverage = (with_visits.count / total_customers.count * 100) if total_customers.count > 0 else 0
print(f"Stats Coverage: {coverage:.1f}% of customers have calculated stats")
print(f"\nIf coverage is low (<50%), customer stats need to be backfilled.")
print(f"If coverage is high (>90%), system is working correctly.")

