#!/usr/bin/env python3
"""
Deduplicate Blaze tables using Supabase RPC functions
Much faster than REST API - runs SQL server-side
"""
import time
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_SIZE = 1000

def dedupe_table_items():
    """Delete duplicates from transaction_items_blaze using RPC"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transaction_items_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 500:  # Safety limit
        iteration += 1
        
        try:
            # Call RPC function
            response = client.rpc('dedupe_transaction_items_batch', {'batch_size': BATCH_SIZE}).execute()
            
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count:,} duplicates (Total: {total_deleted:,})")
            
            if deleted_count < BATCH_SIZE:
                print("  (Small batch - finishing up)")
            
            time.sleep(0.3)  # Small delay
            
        except Exception as e:
            error_msg = str(e)
            if "does not exist" in error_msg or "function" in error_msg.lower():
                print("\n[ERROR] RPC function not found!")
                print("You need to run sql_scripts/dedupe_blaze_function.sql first")
                print("in Supabase SQL Editor to create the functions.")
                return 0
            elif "timeout" in error_msg.lower():
                print(f"Iteration {iteration}: Timeout (DB overloaded) - waiting 10s...")
                time.sleep(10)
                continue
            else:
                print(f"Iteration {iteration}: Error - {e}")
                time.sleep(5)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate transaction_items")
    return total_deleted

def dedupe_products():
    """Delete duplicates from products_blaze using RPC"""
    print("\n" + "="*60)
    print("DEDUPLICATING: products_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 200:
        iteration += 1
        
        try:
            response = client.rpc('dedupe_products_batch', {'batch_size': BATCH_SIZE}).execute()
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count:,} duplicates (Total: {total_deleted:,})")
            time.sleep(0.3)
            
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"Iteration {iteration}: Timeout - waiting 10s...")
                time.sleep(10)
                continue
            else:
                print(f"Error: {e}")
                time.sleep(5)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate products")
    return total_deleted

def dedupe_transactions():
    """Delete duplicates from transactions_blaze using RPC"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transactions_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 200:
        iteration += 1
        
        try:
            response = client.rpc('dedupe_transactions_batch', {'batch_size': BATCH_SIZE}).execute()
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count:,} duplicates (Total: {total_deleted:,})")
            time.sleep(0.3)
            
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"Iteration {iteration}: Timeout - waiting 10s...")
                time.sleep(10)
                continue
            else:
                print(f"Error: {e}")
                time.sleep(5)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate transactions")
    return total_deleted

def main():
    print("="*60)
    print("BLAZE TABLES DEDUPLICATION - RPC FUNCTIONS")
    print("="*60)
    print("Using server-side SQL functions (much faster!)")
    print(f"Batch size: {BATCH_SIZE}")
    
    # Test connection
    try:
        print("\nTesting connection...")
        test = client.table('transaction_items_blaze').select('id').limit(1).execute()
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return
    
    # Check if functions exist
    print("\nChecking if RPC functions exist...")
    try:
        # Try calling with tiny batch to test
        test_response = client.rpc('dedupe_transaction_items_batch', {'batch_size': 1}).execute()
        print("[OK] RPC functions found!")
    except Exception as e:
        if "does not exist" in str(e) or "function" in str(e).lower():
            print("\n[ERROR] RPC functions not found!")
            print("\nYou MUST run this SQL first in Supabase SQL Editor:")
            print("  sql_scripts/dedupe_blaze_function.sql")
            print("\nThis creates the server-side functions that do the deduplication.")
            print("Once created, run this script again.")
            return
        else:
            print(f"[WARNING] Function test failed: {e}")
            print("Continuing anyway...")
    
    print("\nStarting deduplication in 2 seconds...")
    print("(This may take 30+ minutes for millions of duplicates)")
    time.sleep(2)
    
    total_deleted = 0
    
    try:
        # Deduplicate
        total_deleted += dedupe_table_items()
        total_deleted += dedupe_products()
        total_deleted += dedupe_transactions()
        
        print("\n" + "="*60)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted:,}")
        print("="*60)
        print("\nNext steps:")
        print("1. Run VACUUM ANALYZE in Supabase SQL Editor")
        print("2. Check database size reduction")
        print("3. Add unique indexes to prevent future duplicates")
        
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted")
        print(f"Deleted {total_deleted:,} duplicates before stopping")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nDeleted {total_deleted:,} duplicates before error")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        input("Press Enter to exit...")

