#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

phone = "+16199773020"
print("=== CHECKING LINKAGE ===\n")

# Get customer
customers = supabase.table('customers').select('*').eq('phone', phone).execute()
c = customers.data[0]
print(f"Customer record for {phone}:")
print(f"  id: {c.get('id')}")
print(f"  member_id: {c.get('member_id')}")
print(f"  name: {c.get('name')}")

# Try transaction by ID
print(f"\nTrying transactions WHERE customer_id={c.get('id')}:")
tx_by_id = supabase.table('transactions').select('*').eq('customer_id', c.get('id')).limit(3).execute()
print(f"  Found: {len(tx_by_id.data)} transactions")

# Try transaction by member_id
print(f"\nTrying transactions WHERE customer_id={c.get('member_id')}:")
tx_by_member = supabase.table('transactions').select('*').eq('customer_id', c.get('member_id')).limit(3).execute()
print(f"  Found: {len(tx_by_member.data)} transactions")

# Check first transaction structure
if tx_by_member.data:
    t = tx_by_member.data[0]
    print(f"\nFirst transaction keys: {list(t.keys())}")
    print(f"  transaction_id: {t.get('transaction_id') or t.get('id')}")
    print(f"  customer_id: {t.get('customer_id') or t.get('member_id')}")

# Check customer_purchase_history view
print(f"\nTrying customer_purchase_history WHERE phone={phone}:")
view = supabase.table('customer_purchase_history').select('*').eq('phone', phone).limit(3).execute()
print(f"  Found: {len(view.data)} records")
if view.data:
    print(f"  View columns: {list(view.data[0].keys())}")

print(f"\n✅ CORRECT LINKAGE:")
print(f"customers.member_id ({c.get('member_id')}) → transactions.customer_id")

