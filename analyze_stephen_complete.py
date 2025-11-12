#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Quick analysis of Stephen's complete data from Supabase"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from supabase import create_client
import json

# Use CRM Supabase (not SMS)
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
phone = "+16199773020"

print(f"{'='*80}")
print(f"COMPLETE DATA LINKAGE FOR: {phone}")
print(f"{'='*80}\n")

# Step 1: customers table
print("STEP 1: customers → customer_id")
customers = supabase.table('customers').select('*').eq('phone', phone).execute()
if not customers.data:
    print("❌ No customer found!")
    exit(1)

c = customers.data[0]
print(f"DEBUG: Keys in customer record: {list(c.keys())}")
cid = c.get('customer_id') or c.get('id')
print(f"✅ customer_id: {cid}")
print(f"   Name: {c.get('first_name')} {c.get('last_name')}")
print(f"   Email: {c.get('email')}")
print(f"   VIP: {c.get('vip_status')} | LTV: ${c.get('lifetime_value')} | Visits: {c.get('total_visits')}")

# Step 2: transactions table
print(f"\nSTEP 2: transactions (customer_id={cid}) → transaction_ids")
txs = supabase.table('transactions').select('*').eq('customer_id', cid).order('date', desc=True).limit(3).execute()
print(f"✅ Found {len(txs.data)} transactions\n")

for i, tx in enumerate(txs.data, 1):
    tx_id = tx['transaction_id']
    print(f"   [{i}] TX {tx_id}: ${tx['total']} on {tx['date']}")
    print(f"       Store: {tx.get('store_name')} | Staff: {tx.get('staff_name')} (ID: {tx.get('staff_id')})")
    
    # Step 3: transaction_items
    items = supabase.table('transaction_items').select('*').eq('transaction_id', tx_id).execute()
    print(f"       Items ({len(items.data)}):")
    
    for item in items.data[:3]:  # Show first 3 items
        print(f"         - {item.get('product_name')}: ${item.get('price')}")
        print(f"           SKU: {item.get('product_sku')}")
    
    if len(items.data) > 3:
        print(f"         ... and {len(items.data) - 3} more items")
    print()

# Show the linkage chain
print(f"{'='*80}")
print(f"DATA LINKAGE CHAIN")
print(f"{'='*80}\n")
print(f"phone → customers.phone = '{phone}'")
print(f"   ↓")
print(f"customers.customer_id = {cid}")
print(f"   ↓")
print(f"transactions.customer_id = {cid}")
print(f"   ↓")
print(f"transactions.transaction_id = [549196, 548915, 548869, ...]")
print(f"   ↓")
print(f"transaction_items.transaction_id = 549196")
print(f"   ↓")
print(f"transaction_items.product_sku = 'FTGM100BRD'")
print(f"   ↓")
print(f"products.sku = 'FTGM100BRD' → full product details")

print(f"\n{'='*80}")
print(f"FOR N8N / AI AGENT")
print(f"{'='*80}\n")
print(f"Query Strategy:")
print(f"1. Get phone from SMS → +16199773020")
print(f"2. Query customers by phone → get customer_id ({cid})")
print(f"3. Query transactions by customer_id → get list of transaction_ids")
print(f"4. For each transaction_id:")
print(f"   - Query transaction_items → get all items + product_skus")
print(f"   - Query products by sku → get full product details")
print(f"5. Query staff by staff_id → get budtender info")
print(f"\n✅ This gives the COMPLETE customer dataset from JUST a phone number!")

