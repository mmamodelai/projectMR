#!/usr/bin/env python3
"""
Fix transaction amounts by calculating from CSV data
"""

import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def fix_transaction_amounts():
    """Calculate and update transaction amounts from CSV data"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 60)
    print("Fixing Transaction Amounts from CSV Data".center(60))
    print("=" * 60)
    
    try:
        # Read CSV
        print("Loading transaction CSV...")
        df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
        print(f"Loaded {len(df)} transaction line items")
        
        # Group by transaction ID and calculate totals
        print("\nCalculating transaction totals...")
        transaction_totals = {}
        
        for idx, row in df.iterrows():
            if (idx + 1) % 10000 == 0:
                print(f"  Processed {idx + 1:,} rows...")
            
            trans_id = str(row.iloc[4])  # Transaction ID
            total_price = row.iloc[29]   # Total price column
            
            if pd.notna(trans_id) and pd.notna(total_price):
                try:
                    amount = float(total_price)
                    if trans_id not in transaction_totals:
                        transaction_totals[trans_id] = 0
                    transaction_totals[trans_id] += amount
                except:
                    continue
        
        print(f"\nCalculated totals for {len(transaction_totals)} transactions")
        
        # Update transactions in batches
        batch_size = 100
        total_updated = 0
        
        # Convert to list of updates
        updates = []
        for trans_id, total_amount in transaction_totals.items():
            updates.append({
                'transaction_id': trans_id,
                'total_amount': total_amount
            })
        
        print(f"\nUpdating transactions in batches of {batch_size}...")
        for i in range(0, len(updates), batch_size):
            batch = updates[i:i+batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(updates) - 1) // batch_size + 1
            
            try:
                for update in batch:
                    supabase.table('transactions').update({
                        'total_amount': update['total_amount']
                    }).eq('transaction_id', update['transaction_id']).execute()
                
                total_updated += len(batch)
                print(f"  Batch {batch_num}/{total_batches}: Updated {len(batch)} transactions (Total: {total_updated:,})")
                
            except Exception as e:
                print(f"  Batch {batch_num}/{total_batches}: ERROR - {str(e)[:100]}...")
        
        print("\n" + "=" * 60)
        print(f"Transaction Amount Fix Complete!")
        print(f"  Total transactions updated: {total_updated:,}")
        
        # Verify some examples
        print("\nSample updated transactions:")
        sample_response = supabase.table('transactions').select('transaction_id, total_amount').order('total_amount', desc=True).limit(5).execute()
        for trans in sample_response.data:
            print(f"  {trans['transaction_id']}: ${float(trans['total_amount']):,.2f}")
        
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    fix_transaction_amounts()

