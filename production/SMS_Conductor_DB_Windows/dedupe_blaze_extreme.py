#!/usr/bin/env python3
"""
Deduplicate Blaze tables using EXTREME batches (1-2 rows)
For databases that timeout on EVERYTHING
LAST RESORT - use only when nothing else works
"""
import time
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_SIZE = 1  # EXTREME: 1 row at a time
WAIT_BETWEEN_BATCHES = 180  # 3 minutes between batches
WAIT_ON_TIMEOUT = 300  # 5 minutes on timeout

def dedupe_table_items():
    """Delete duplicates from transaction_items_blaze - EXTREME mode"""
    print("\n" + "="*70)
    print("DEDUPLICATING: transaction_items_blaze - EXTREME MODE")
    print(f"Using EXTREME batches: {BATCH_SIZE} row, {WAIT_BETWEEN_BATCHES}s wait")
    print("="*70)
    print("\n⚠️  EXTREME MODE:")
    print("   - 1 row at a time")
    print("   - 3 minutes wait between batches")
    print("   - 5 minutes wait on timeout")
    print("   - Expected: ~500 hours for 1 million duplicates (20+ days)")
    print("   - This is the ABSOLUTE LAST RESORT")
    print("\n" + "="*70)
    
    total_deleted = 0
    iteration = 0
    consecutive_timeouts = 0
    start_time = time.time()
    
    while iteration < 100000:  # Safety limit
        iteration += 1
        
        try:
            # Call RPC function with EXTREME batch (1 row)
            response = client.rpc('dedupe_transaction_items_batch', {'batch_size': BATCH_SIZE}).execute()
            
            deleted_count = response.data if isinstance(response.data, int) else 0
            
            if deleted_count == 0:
                elapsed = time.time() - start_time
                print(f"\n✅ Iteration {iteration}: No more duplicates found!")
                print(f"   Total deleted: {total_deleted:,}")
                print(f"   Time elapsed: {elapsed/3600:.1f} hours")
                break
            
            total_deleted += deleted_count
            consecutive_timeouts = 0
            
            elapsed = time.time() - start_time
            if iteration % 10 == 0:
                rate = total_deleted / elapsed if elapsed > 0 else 0
                print(f"\n[{iteration}] Deleted {deleted_count} (Total: {total_deleted:,})")
                print(f"   Rate: {rate:.2f} rows/hour | Elapsed: {elapsed/3600:.1f} hours")
            else:
                print(f"  [{iteration}] +{deleted_count} (Total: {total_deleted:,})")
            
            # Wait 3 minutes between batches
            print(f"   Waiting {WAIT_BETWEEN_BATCHES}s...")
            time.sleep(WAIT_BETWEEN_BATCHES)
            
        except Exception as e:
            error_msg = str(e).lower()
            if "does not exist" in error_msg or "function" in error_msg.lower():
                print("\n[ERROR] RPC function not found!")
                return 0
            elif "timeout" in error_msg.lower():
                consecutive_timeouts += 1
                print(f"\n⏱️  Iteration {iteration}: TIMEOUT #{consecutive_timeouts}")
                
                if consecutive_timeouts >= 2:
                    print("\n⚠️  WARNING: Even EXTREME mode is timing out!")
                    print("\nRECOMMENDATION: Database is too overloaded for ANY operation.")
                    print("\nYou MUST:")
                    print("  1. Wait for database to be 'Healthy' in Supabase dashboard")
                    print("  2. OR delete entire archive tables first (instant space)")
                    print("  3. OR contact Supabase support about database overload")
                    print("\nContinuing anyway, but expect frequent timeouts...")
                    consecutive_timeouts = 0
                
                print(f"   Waiting {WAIT_ON_TIMEOUT} seconds (5 minutes)...")
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
    print("BLAZE TABLES DEDUPLICATION - EXTREME MODE")
    print("="*70)
    print("LAST RESORT - Use only when everything else times out")
    print(f"\nSettings:")
    print(f"  Batch size: {BATCH_SIZE} row (EXTREME)")
    print(f"  Wait between batches: {WAIT_BETWEEN_BATCHES} seconds (3 minutes)")
    print(f"  Wait on timeout: {WAIT_ON_TIMEOUT} seconds (5 minutes)")
    print(f"\n⚠️  WARNING: This will take WEEKS")
    print("   1 million duplicates = ~500 hours (20+ days)")
    print("\n" + "="*70)
    
    print("\n⚠️  BEFORE USING EXTREME MODE:")
    print("   1. ✅ Check Supabase dashboard - is database 'Healthy'?")
    print("   2. ✅ Try deleting archive tables first (instant space)")
    print("   3. ✅ Wait for database to recover if it's 'Unhealthy'")
    print("   4. ✅ Consider contacting Supabase support")
    print("\n   EXTREME MODE should be LAST RESORT!")
    
    response = input("\nReally use EXTREME mode? (type 'EXTREME' to confirm): ")
    if response != 'EXTREME':
        print("Cancelled. Good choice - try other options first.")
        return
    
    # Test connection
    try:
        print("\nTesting connection...")
        test = client.table('transactions_blaze').select('id').limit(1).execute()
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nDatabase is too overloaded. You MUST:")
        print("  1. Wait for database to be 'Healthy'")
        print("  2. Delete archive tables first")
        return
    
    print("\nStarting EXTREME deduplication in 5 seconds...")
    print("(Press Ctrl+C to stop safely)")
    time.sleep(5)
    
    total_deleted = 0
    
    try:
        total_deleted = dedupe_table_items()
        
        print("\n" + "="*70)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted:,}")
        print("="*70)
        
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted")
        print(f"Deleted {total_deleted:,} duplicates before stopping")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()

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

