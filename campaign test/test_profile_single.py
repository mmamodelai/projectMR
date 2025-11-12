#!/usr/bin/env python3
"""Quick test to see what data we can pull"""

import pandas as pd
from supabase import create_client, Client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Test with one customer ID
test_customer = '5e1cc479a3b04d084c46ca87'  # Robert Platzer

print(f"Testing profile for customer: {test_customer}")

# Get transactions
print("\n1. Getting transactions...")
transactions = supabase.table('transactions').select('transaction_id').eq('customer_id', test_customer).execute()
print(f"Found {len(transactions.data)} transactions")

if transactions.data:
    transaction_ids = [t['transaction_id'] for t in transactions.data[:5]]  # Just first 5 for test
    print(f"Sample transaction IDs: {transaction_ids}")
    
    # Get transaction items
    print("\n2. Getting transaction items...")
    items = supabase.table('transaction_items').select('*').in_('transaction_id', transaction_ids).execute()
    print(f"Found {len(items.data)} items")
    
    if items.data:
        df = pd.DataFrame(items.data)
        print(f"\nColumns available: {df.columns.tolist()}")
        print(f"\nFirst item:")
        print(df.iloc[0])
        
        # Group by category
        print("\n3. Grouping by category...")
        grouped = df.groupby(['category', 'brand'], dropna=False).agg({
            'product_name': 'count',
            'quantity': 'sum',
            'total_price': 'sum'
        }).reset_index()
        grouped.columns = ['category', 'brand', 'times_purchased', 'total_quantity', 'total_spent']
        grouped = grouped.sort_values('total_spent', ascending=False)
        
        print("\nTop purchases:")
        print(grouped.head(10))








