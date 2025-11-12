#!/usr/bin/env python3
"""
Full Transaction Import - Handles duplicates and processes all data
"""

import pandas as pd
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def import_all_transactions():
    """Import all transactions from CSV, skipping duplicates"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("MoTa Transaction Data Import - Full Database Population".center(70))
    print("=" * 70)
    
    # First, get existing transaction IDs to skip duplicates
    print("\nChecking existing transactions...")
    try:
        existing = supabase.table('transactions').select('transaction_id').execute()
        existing_ids = set(row['transaction_id'] for row in existing.data)
        print(f"Found {len(existing_ids)} existing transactions in database")
    except Exception as e:
        print(f"Error checking existing: {e}")
        existing_ids = set()
    
    # Read CSV with pandas for robust parsing
    print("\nLoading CSV file...")
    df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
    print(f"Loaded {len(df):,} transaction line items from CSV")
    
    # Group by transaction ID to get unique transactions
    print("\nProcessing transactions...")
    transaction_groups = {}
    
    for idx, row in df.iterrows():
        if (idx + 1) % 5000 == 0:
            print(f"  Processed {idx + 1:,} rows...")
        
        trans_id = row.iloc[4]  # Trans No column
        if pd.isna(trans_id):
            continue
            
        trans_id_str = str(int(trans_id))
        
        # Skip if already in database
        if trans_id_str in existing_ids:
            continue
        
        # Only process each transaction once (first occurrence)
        if trans_id_str not in transaction_groups:
            transaction_groups[trans_id_str] = {
                'transaction_id': trans_id_str,
                'customer_id': str(row.iloc[19]) if pd.notna(row.iloc[19]) else None,
                'date': pd.to_datetime(row.iloc[0]).isoformat() if pd.notna(row.iloc[0]) else None,
                'shop_location': str(row.iloc[2]) if pd.notna(row.iloc[2]) else None,
                'total_amount': float(row.iloc[29]) if pd.notna(row.iloc[29]) else 0.0,
                'staff_name': str(row.iloc[67]) if pd.notna(row.iloc[67]) else None,
                'terminal': str(row.iloc[69]) if pd.notna(row.iloc[69]) else None,
                'payment_type': str(row.iloc[70]) if pd.notna(row.iloc[70]) else None,
            }
    
    print(f"\nFound {len(transaction_groups):,} unique new transactions to import")
    
    if len(transaction_groups) == 0:
        print("No new transactions to import!")
        return
    
    # Convert to list for batch import
    transactions = list(transaction_groups.values())
    
    # Import in batches
    batch_size = 500
    total_imported = 0
    errors = []
    
    print(f"\nImporting in batches of {batch_size}...")
    for i in range(0, len(transactions), batch_size):
        batch = transactions[i:i+batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(transactions) - 1) // batch_size + 1
        
        try:
            response = supabase.table('transactions').insert(batch).execute()
            total_imported += len(batch)
            print(f"  Batch {batch_num}/{total_batches}: Imported {len(batch)} transactions (Total: {total_imported:,})")
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"  Batch {batch_num}/{total_batches}: ERROR - {error_msg}")
            errors.append(f"Batch {batch_num}: {error_msg}")
            
            # Try individual inserts for failed batch
            print(f"  Retrying batch {batch_num} individually...")
            for trans in batch:
                try:
                    supabase.table('transactions').insert(trans).execute()
                    total_imported += 1
                except Exception as e2:
                    # Skip duplicates silently
                    if 'duplicate key' not in str(e2).lower():
                        errors.append(f"Transaction {trans['transaction_id']}: {str(e2)[:100]}")
    
    print("\n" + "=" * 70)
    print(f"Import Complete!")
    print(f"  Total transactions imported: {total_imported:,}")
    if errors:
        print(f"  Errors encountered: {len(errors)}")
        print(f"\nFirst few errors:")
        for err in errors[:5]:
            print(f"  - {err}")
    
    # Verify final count
    print("\nVerifying database...")
    try:
        final_count = supabase.table('transactions').select('transaction_id', count='exact').execute()
        print(f"  Total transactions in database: {final_count.count:,}")
    except Exception as e:
        print(f"  Error verifying: {e}")
    
    print("=" * 70)

if __name__ == "__main__":
    import_all_transactions()

