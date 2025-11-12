#!/usr/bin/env python3
"""
Check what format customer_id is in transactions_blaze
"""

from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("CUSTOMER_ID FORMAT CHECK")
print("=" * 80)
print()

# Get sample transactions
print("1. SAMPLE TRANSACTIONS_BLAZE CUSTOMER_IDs")
print("-" * 80)
txns = supabase.table('transactions_blaze').select('transaction_id, customer_id, date').order('date', desc=True).limit(10).execute()
for tx in txns.data:
    print(f"   Transaction: {tx.get('transaction_id')}")
    print(f"      customer_id: {tx.get('customer_id')} (type: {type(tx.get('customer_id')).__name__})")
print()

# Get sample customers
print("2. SAMPLE CUSTOMERS_BLAZE IDs")
print("-" * 80)
custs = supabase.table('customers_blaze').select('id, name, member_id').limit(10).execute()
for cust in custs.data:
    print(f"   Name: {cust.get('name')}")
    print(f"      id: {cust.get('id')} (Supabase internal ID)")
    print(f"      member_id: {cust.get('member_id')} (Blaze member ID)")
print()

# Check if transactions use member_id instead of id
print("3. CHECKING IF TRANSACTIONS USE MEMBER_ID")
print("-" * 80)
if txns.data and custs.data:
    sample_tx_customer_id = txns.data[0].get('customer_id')
    print(f"Sample transaction customer_id: {sample_tx_customer_id}")
    
    # Try to find in customers by member_id
    match_by_member = supabase.table('customers_blaze').select('*').eq('member_id', sample_tx_customer_id).execute()
    print(f"   Match by member_id: {len(match_by_member.data)} found")
    if match_by_member.data:
        print(f"      Customer: {match_by_member.data[0].get('name')}")
    
    # Try to find in customers by id
    match_by_id = supabase.table('customers_blaze').select('*').eq('id', sample_tx_customer_id).execute()
    print(f"   Match by id: {len(match_by_id.data)} found")
    if match_by_id.data:
        print(f"      Customer: {match_by_id.data[0].get('name')}")

print()
print("=" * 80)
print("VERDICT:")
print("=" * 80)
print()
print("If transactions use member_id:")
print("  -> transactions_blaze.customer_id = customers_blaze.member_id")
print()
print("If transactions use Supabase ID:")
print("  -> transactions_blaze.customer_id = customers_blaze.id")
print()
print("=" * 80)

