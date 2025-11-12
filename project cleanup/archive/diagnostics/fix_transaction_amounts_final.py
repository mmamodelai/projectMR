#!/usr/bin/env python3
"""
Fix transaction amounts using correct CSV column
"""

import pandas as pd
from supabase import create_client, Client
from collections import defaultdict

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main():
    """Fix transaction amounts using correct CSV column"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("FIXING TRANSACTION AMOUNTS - FINAL".center(70))
    print("=" * 70)
    
    # Read CSV
    print("\nLoading CSV...")
    df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
    print(f"Loaded {len(df):,} transaction line items")
    
    # Calculate transaction totals using correct column (index 27 = Total Price)
    print("\nCalculating transaction totals...")
    trans_totals = defaultdict(float)
    
    for idx, row in df.iterrows():
        if (idx + 1) % 10000 == 0:
            print(f"  Processing row {idx + 1:,}...")
        
        trans_id = str(row.iloc[4])  # Transaction ID
        total_price = row.iloc[27]    # Total Price (correct column)
        
        if pd.notna(trans_id) and pd.notna(total_price):
            try:
                trans_totals[trans_id] += float(total_price)
            except:
                pass
    
    print(f"Calculated totals for {len(trans_totals):,} transactions")
    
    # Show sample totals
    sample_trans = list(trans_totals.items())[:5]
    print("\nSample transaction totals:")
    for trans_id, amount in sample_trans:
        print(f"  Trans {trans_id}: ${amount:.2f}")
    
    # Update transactions in batches
    print(f"\nUpdating {len(trans_totals):,} transactions...")
    batch_size = 100
    total_updated = 0
    trans_list = list(trans_totals.items())
    
    for i in range(0, len(trans_list), batch_size):
        batch = trans_list[i:i+batch_size]
        
        # Update each transaction
        for trans_id, amount in batch:
            try:
                supabase.table('transactions').update({'total_amount': amount}).eq('transaction_id', trans_id).execute()
                total_updated += 1
            except Exception as e:
                print(f"  Error updating {trans_id}: {str(e)[:50]}...")
        
        if (i + batch_size) % 1000 == 0:
            print(f"  Updated {total_updated:,} transactions...")
    
    print(f"\nTransaction amounts updated: {total_updated:,}")
    
    # Verify results
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    try:
        # Check transaction amounts
        result = supabase.table('transactions').select('transaction_id, total_amount').order('total_amount', desc=True).limit(10).execute()
        
        print("Top 10 transactions by amount:")
        for t in result.data:
            print(f"  {t['transaction_id']}: ${float(t['total_amount']):,.2f}")
        
        # Check zero amounts
        zero_count = supabase.table('transactions').select('transaction_id', count='exact').eq('total_amount', 0).execute()
        print(f"\nTransactions still at $0.00: {zero_count.count:,}")
        
        # Check non-zero amounts
        non_zero_count = supabase.table('transactions').select('transaction_id', count='exact').gt('total_amount', 0).execute()
        print(f"Transactions with amounts > $0: {non_zero_count.count:,}")
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("DONE! Transaction amounts should now be correct")
    print("=" * 70)

if __name__ == "__main__":
    main()
