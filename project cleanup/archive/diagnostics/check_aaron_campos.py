#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check Aaron Campos transactions
"""
import sys
import os
from supabase import create_client

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("=" * 80)
print("AARON CAMPOS TRANSACTIONS")
print("=" * 80)

# Find Aaron Campos
customers = supabase.table('customers').select('*').ilike('name', '%Aaron Campos%').execute()

if not customers.data:
    print("Aaron Campos not found")
else:
    customer = customers.data[0]
    print(f"\nCustomer: {customer['name']} (ID: {customer['id']})")
    print(f"Phone: {customer.get('phone', 'N/A')}")
    
    # Get transactions for Aaron
    transactions = supabase.table('transactions').select('*').eq('customer_id', customer['id']).order('date', desc=True).limit(20).execute()
    
    print(f"\nRecent Transactions: {len(transactions.data)}")
    
    for trans in transactions.data[:10]:  # Show first 10
        trans_id = trans['id']
        trans_date = trans.get('date', 'N/A')
        trans_total = trans.get('total', 0)
        
        # Get items for this transaction
        items = supabase.table('transaction_items').select('*').eq('transaction_id', trans_id).execute()
        item_count = len(items.data)
        item_total = sum(float(item['unit_price']) * int(item['quantity']) for item in items.data)
        
        print(f"\n  Transaction {trans_id} - {trans_date}")
        print(f"    Total: ${trans_total:.2f}")
        print(f"    Items: {item_count} (sum: ${item_total:.2f})")
        
        if item_count > 0 and item_count <= 5:
            for item in items.data:
                subtotal = float(item['unit_price']) * int(item['quantity'])
                print(f"      - {item['product_name']}: ${item['unit_price']} x {item['quantity']} = ${subtotal:.2f}")
        
        # Flag discrepancies
        if abs(trans_total - item_total) > 0.01:
            print(f"    ** MISMATCH: ${abs(trans_total - item_total):.2f} difference")

print("\n" + "=" * 80)

