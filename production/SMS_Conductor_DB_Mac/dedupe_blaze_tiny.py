#!/usr/bin/env python3
"""
Deduplicate Blaze tables using TINY batches (10-50 rows)
For overloaded databases that timeout on larger operations
"""
import time
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_SIZE = 10  # TINY batches for overloaded DB
WAIT_BETWEEN_BATCHES = 30  # 30 seconds between batches
WAIT_ON_TIMEOUT = 60  # 60 seconds on timeout

def dedupe_table_items():
    """Delete duplicates from transaction_items_blaze using TINY batches"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transaction_items_blaze")
    print(f"Using TINY batches: {BATCH_SIZE} rows, {WAIT_BETWEEN_BATCHES}s wait")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    consecutive_timeouts = 0
    
    while iteration < 10000:  # Safety limit (but will stop on no duplicates)
        iteration += 1
        
        try:
            # Call RPC function with TINY batch
            response = client.rpc('dedupe_transaction_items_batch', {'batch_size': BATCH_SIZE}).execute()
            
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"\nIteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            consecutive_timeouts = 0  # Reset timeout counter
            
            if iteration % 10 == 0:
                # Progress update every 10 iterations
                print(f"Iteration {iteration}: Deleted {deleted_count} (Total: {total_deleted:,})")
            else:
                print(f"  [{iteration}] +{deleted_count} (Total: {total_deleted:,})")
            
            # Wait longer between batches to let DB recover
            time.sleep(WAIT_BETWEEN_BATCHES)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "does not exist" in error_msg or "function" in error_msg.lower():
                print("\n[ERROR] RPC function not found!")
                print("You need to create the functions first.")
                return 0
            elif "timeout" in error_msg.lower():
                consecutive_timeouts += 1
                print(f"\nIteration {iteration}: TIMEOUT #{consecutive_timeouts} (DB overloaded)")
                
                if consecutive_timeouts >= 5:
                    print("\n[WARNING] 5 consecutive timeouts!")
                    print("Database is severely overloaded.")
                    print("Consider:")
                    print("  1. Waiting for database to be 'Healthy'")
                    print("  2. Deleting entire archive tables first")
                    print("  3. Running this script during off-peak hours")
                    response = input("\nContinue anyway? (y/n): ")
                    if response.lower() != 'y':
                        break
                    consecutive_timeouts = 0
                
                print(f"  Waiting {WAIT_ON_TIMEOUT} seconds before retry...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
            else:
                print(f"\nIteration {iteration}: Error - {e}")
                print(f"  Waiting {WAIT_ON_TIMEOUT} seconds...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate transaction_items")
    return total_deleted

def dedupe_products():
    """Delete duplicates from products_blaze using TINY batches"""
    print("\n" + "="*60)
    print("DEDUPLICATING: products_blaze")
    print(f"Using TINY batches: {BATCH_SIZE} rows, {WAIT_BETWEEN_BATCHES}s wait")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 5000:
        iteration += 1
        
        try:
            response = client.rpc('dedupe_products_batch', {'batch_size': BATCH_SIZE}).execute()
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"\nIteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Deleted {deleted_count} (Total: {total_deleted:,})")
            else:
                print(f"  [{iteration}] +{deleted_count} (Total: {total_deleted:,})")
            
            time.sleep(WAIT_BETWEEN_BATCHES)
            
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"\nIteration {iteration}: TIMEOUT - waiting {WAIT_ON_TIMEOUT}s...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
            else:
                print(f"Error: {e}")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate products")
    return total_deleted

def dedupe_transactions():
    """Delete duplicates from transactions_blaze using TINY batches"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transactions_blaze")
    print(f"Using TINY batches: {BATCH_SIZE} rows, {WAIT_BETWEEN_BATCHES}s wait")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 5000:
        iteration += 1
        
        try:
            response = client.rpc('dedupe_transactions_batch', {'batch_size': BATCH_SIZE}).execute()
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                print(f"\nIteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            if iteration % 10 == 0:
                print(f"Iteration {iteration}: Deleted {deleted_count} (Total: {total_deleted:,})")
            else:
                print(f"  [{iteration}] +{deleted_count} (Total: {total_deleted:,})")
            
            time.sleep(WAIT_BETWEEN_BATCHES)
            
        except Exception as e:
            if "timeout" in str(e).lower():
                print(f"\nIteration {iteration}: TIMEOUT - waiting {WAIT_ON_TIMEOUT}s...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
            else:
                print(f"Error: {e}")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted:,} duplicate transactions")
    return total_deleted

def main():
    print("="*70)
    print("BLAZE TABLES DEDUPLICATION - TINY BATCH MODE")
    print("="*70)
    print("For overloaded databases that timeout on normal operations")
    print(f"\nSettings:")
    print(f"  Batch size: {BATCH_SIZE} rows (TINY)")
    print(f"  Wait between batches: {WAIT_BETWEEN_BATCHES} seconds")
    print(f"  Wait on timeout: {WAIT_ON_TIMEOUT} seconds")
    print(f"\n⚠️  WARNING: This will be VERY SLOW (hours/days)")
    print("   But it's the only way when DB is overloaded.")
    print("\n" + "="*70)
    
    response = input("\nStart deduplication? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
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
        test_response = client.rpc('dedupe_transaction_items_batch', {'batch_size': 1}).execute()
        print("[OK] RPC functions found!")
    except Exception as e:
        if "does not exist" in str(e) or "function" in str(e).lower():
            print("\n[ERROR] RPC functions not found!")
            print("Create them first using:")
            print("  sql_scripts/create_function_1_transaction_items.sql")
            print("  sql_scripts/create_function_2_products.sql")
            print("  sql_scripts/create_function_3_transactions.sql")
            return
        else:
            print(f"[WARNING] Function test failed: {e}")
            print("Continuing anyway...")
    
    print("\nStarting deduplication in 5 seconds...")
    print("(Press Ctrl+C to stop safely)")
    time.sleep(5)
    
    total_deleted = 0
    
    try:
        total_deleted += dedupe_table_items()
        total_deleted += dedupe_products()
        total_deleted += dedupe_transactions()
        
        print("\n" + "="*70)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted:,}")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted")
        print(f"Deleted {total_deleted:,} duplicates before stopping")
        print("\nYou can resume by running this script again.")
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
        print("\n" + "="*70)
        input("Press Enter to exit...")

