#!/usr/bin/env python3
"""
Check what date range we have in the database
Quick diagnostic to see if we need to backfill
"""

from supabase import create_client, Client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

print("=" * 80)
print("DATABASE DATE RANGE CHECK")
print("=" * 80)
print()

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Check customers
print("CUSTOMERS:")
result = supabase.table('customers_blaze').select('date_joined').order('date_joined').limit(1).execute()
if result.data:
    print(f"  First customer joined: {result.data[0]['date_joined']}")
result = supabase.table('customers_blaze').select('date_joined').order('date_joined', desc=True).limit(1).execute()
if result.data:
    print(f"  Last customer joined:  {result.data[0]['date_joined']}")
print()

# Check transactions
print("TRANSACTIONS:")
result = supabase.table('transactions_blaze').select('date').order('date').limit(1).execute()
if result.data:
    first_date = result.data[0]['date'][:10]
    print(f"  First transaction: {first_date}")
    
result = supabase.table('transactions_blaze').select('date').order('date', desc=True).limit(1).execute()
if result.data:
    last_date = result.data[0]['date'][:10]
    print(f"  Last transaction:  {last_date}")

# Count by year
print("\n  Transactions by year:")
result = supabase.rpc('get_transactions_by_year', {}).execute() if False else None

# Manual count for key years
for year in [2021, 2022, 2023, 2024, 2025]:
    try:
        result = supabase.table('transactions_blaze') \
            .select('*', count='exact') \
            .gte('date', f'{year}-01-01') \
            .lt('date', f'{year+1}-01-01') \
            .limit(0) \
            .execute()
        print(f"    {year}: {result.count:,} transactions")
    except:
        print(f"    {year}: (timeout)")

print()

# Check products
print("PRODUCTS:")
result = supabase.table('products_blaze').select('blaze_created').order('blaze_created').limit(1).execute()
if result.data and result.data[0]['blaze_created']:
    print(f"  First product created: {result.data[0]['blaze_created'][:10]}")
result = supabase.table('products_blaze').select('blaze_modified').order('blaze_modified', desc=True).limit(1).execute()
if result.data and result.data[0]['blaze_modified']:
    print(f"  Last product modified: {result.data[0]['blaze_modified'][:10]}")

print()
print("=" * 80)
print("SUMMARY")
print("=" * 80)
print("If first transaction is after 2024, you need to backfill.")
print("If you have 2021-2024 data, you're already backfilled.")
print("=" * 80)

