#!/usr/bin/env python3
"""
Deduplicate Blaze tables using ULTRA-TINY batches (5 rows)
For SEVERELY overloaded databases that timeout on everything
"""
import time
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_SIZE = 5  # ULTRA-TINY batches (5 rows at a time)
WAIT_BETWEEN_BATCHES = 60  # 60 seconds between batches
WAIT_ON_TIMEOUT = 120  # 2 minutes on timeout

def dedupe_table_items():
    """Delete duplicates from transaction_items_blaze using ULTRA-TINY batches"""
    print("\n" + "="*70)
    print("DEDUPLICATING: transaction_items_blaze")
    print(f"Using ULTRA-TINY batches: {BATCH_SIZE} rows, {WAIT_BETWEEN_BATCHES}s wait")
    print("="*70)
    print("\n⚠️  This will be EXTREMELY SLOW but is the only way when DB times out")
    print("   Expected: ~200 hours for 1 million duplicates")
    print("   But it WILL work eventually.\n")
    
    total_deleted = 0
    iteration = 0
    consecutive_timeouts = 0
    start_time = time.time()
    
    while iteration < 50000:  # Safety limit
        iteration += 1
        
        try:
            # Call RPC function with ULTRA-TINY batch
            response = client.rpc('dedupe_transaction_items_batch', {'batch_size': BATCH_SIZE}).execute()
            
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                elapsed = time.time() - start_time
                print(f"\n✅ Iteration {iteration}: No more duplicates found!")
                print(f"   Total deleted: {total_deleted:,}")
                print(f"   Time elapsed: {elapsed/3600:.1f} hours")
                break
            
            total_deleted += deleted_count
            consecutive_timeouts = 0  # Reset timeout counter
            
            elapsed = time.time() - start_time
            if iteration % 5 == 0:
                # Progress update every 5 iterations
                rate = total_deleted / elapsed if elapsed > 0 else 0
                remaining_est = "unknown"
                if rate > 0:
                    remaining_est = f"{(1000000 - total_deleted) / rate / 3600:.1f} hours"
                print(f"\n[{iteration}] Deleted {deleted_count} (Total: {total_deleted:,})")
                print(f"   Rate: {rate:.1f} rows/sec | Est. remaining: {remaining_est}")
            else:
                print(f"  [{iteration}] +{deleted_count} (Total: {total_deleted:,})")
            
            # Wait longer between batches to let DB recover
            print(f"   Waiting {WAIT_BETWEEN_BATCHES}s...")
            time.sleep(WAIT_BETWEEN_BATCHES)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "does not exist" in error_msg or "function" in error_msg.lower():
                print("\n[ERROR] RPC function not found!")
                print("You need to create the functions first.")
                return 0
            elif "timeout" in error_msg.lower():
                consecutive_timeouts += 1
                print(f"\n⏱️  Iteration {iteration}: TIMEOUT #{consecutive_timeouts}")
                
                if consecutive_timeouts >= 3:
                    print("\n⚠️  WARNING: 3 consecutive timeouts!")
                    print("Database is severely overloaded.")
                    print("\nOptions:")
                    print("  1. Wait longer (increase WAIT_ON_TIMEOUT)")
                    print("  2. Wait for database to be 'Healthy' in Supabase dashboard")
                    print("  3. Delete entire archive tables first to free space")
                    print("  4. Continue anyway (will be very slow)")
                    response = input("\nContinue? (y/n): ")
                    if response.lower() != 'y':
                        print(f"\nStopped. Deleted {total_deleted:,} duplicates so far.")
                        print("You can resume by running this script again.")
                        break
                    consecutive_timeouts = 0
                
                print(f"   Waiting {WAIT_ON_TIMEOUT} seconds before retry...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
            else:
                print(f"\n❌ Iteration {iteration}: Error - {e}")
                print(f"   Waiting {WAIT_ON_TIMEOUT} seconds...")
                time.sleep(WAIT_ON_TIMEOUT)
                continue
    
    elapsed = time.time() - start_time
    print(f"\n{'='*70}")
    print(f"COMPLETE: Deleted {total_deleted:,} duplicate transaction_items")
    print(f"Time elapsed: {elapsed/3600:.1f} hours")
    print(f"{'='*70}")
    return total_deleted

def main():
    print("="*70)
    print("BLAZE TABLES DEDUPLICATION - ULTRA-TINY BATCH MODE")
    print("="*70)
    print("For SEVERELY overloaded databases")
    print(f"\nSettings:")
    print(f"  Batch size: {BATCH_SIZE} rows (ULTRA-TINY)")
    print(f"  Wait between batches: {WAIT_BETWEEN_BATCHES} seconds (1 minute)")
    print(f"  Wait on timeout: {WAIT_ON_TIMEOUT} seconds (2 minutes)")
    print(f"\n⚠️  WARNING: This will be EXTREMELY SLOW")
    print("   Example: 1 million duplicates = ~200 hours (8+ days)")
    print("   But it's the ONLY way when DB times out on everything.")
    print("\n" + "="*70)
    
    print("\n⚠️  BEFORE STARTING:")
    print("   1. Check Supabase dashboard - is database 'Healthy'?")
    print("   2. Consider deleting archive tables first (instant space)")
    print("   3. This will run for DAYS - leave it running")
    print("   4. You can stop/resume anytime (Ctrl+C is safe)")
    
    response = input("\nStart deduplication? (y/n): ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    # Test connection
    try:
        print("\nTesting connection...")
        test = client.table('transactions_blaze').select('id').limit(1).execute()
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nDatabase might be too overloaded. Try:")
        print("  1. Wait for database to be 'Healthy'")
        print("  2. Delete archive tables first")
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
            return
        else:
            print(f"[WARNING] Function test failed: {e}")
            print("Continuing anyway...")
    
    print("\nStarting deduplication in 5 seconds...")
    print("(Press Ctrl+C to stop safely)")
    time.sleep(5)
    
    total_deleted = 0
    
    try:
        total_deleted = dedupe_table_items()
        
        print("\n" + "="*70)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted:,}")
        print("="*70)
        print("\nNext steps:")
        print("  1. Run VACUUM ANALYZE in Supabase SQL Editor")
        print("  2. Check database size reduction")
        print("  3. Add unique indexes to prevent future duplicates")
        
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

