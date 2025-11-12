#!/usr/bin/env python3
"""
Deduplicate Blaze tables using Supabase Python client
Uses service role key - bypasses all connection issues
"""
import time
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)
BATCH_SIZE = 500  # Smaller batches via REST API

def delete_duplicates_table_items():
    """Delete duplicates from transaction_items_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transaction_items_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 200:
        iteration += 1
        print(f"Iteration {iteration}: Processing...")
        
        try:
            # Get a batch of items
            response = client.table('transaction_items_blaze').select('id,transaction_id,product_id,quantity,unit_price').limit(BATCH_SIZE * 2).execute()
            
            if not response.data:
                print("No more items to process")
                break
            
            # Find duplicates in this batch
            seen_keys = {}
            to_delete = []
            
            for item in response.data:
                key = (
                    str(item.get('transaction_id') or ''),
                    str(item.get('product_id') or ''),
                    str(item.get('quantity') or ''),
                    str(item.get('unit_price') or '')
                )
                
                if key in seen_keys:
                    to_delete.append(item['id'])
                else:
                    seen_keys[key] = item['id']
            
            if not to_delete:
                print("  No duplicates in this batch")
                if iteration > 10:
                    break
                time.sleep(1)
                continue
            
            # Delete duplicates (one at a time via REST API)
            deleted_this_batch = 0
            for item_id in to_delete[:100]:  # Limit to 100 per iteration
                try:
                    client.table('transaction_items_blaze').delete().eq('id', item_id).execute()
                    deleted_this_batch += 1
                except Exception as e:
                    if "timeout" not in str(e).lower():
                        print(f"  Error deleting {item_id}: {e}")
                    continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            
            if deleted_this_batch == 0:
                break
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transaction_items")
    return total_deleted

def delete_duplicates_products():
    """Delete duplicates from products_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: products_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 100:
        iteration += 1
        print(f"Iteration {iteration}: Processing...")
        
        try:
            response = client.table('products_blaze').select('id,sku').not_.is_('sku', 'null').limit(BATCH_SIZE * 2).execute()
            
            if not response.data:
                break
            
            seen_skus = {}
            to_delete = []
            
            for product in response.data:
                sku = str(product.get('sku') or '')
                if sku in seen_skus:
                    to_delete.append(product['id'])
                else:
                    seen_skus[sku] = product['id']
            
            if not to_delete:
                if iteration > 5:
                    break
                time.sleep(1)
                continue
            
            deleted_this_batch = 0
            for prod_id in to_delete[:100]:
                try:
                    client.table('products_blaze').delete().eq('id', prod_id).execute()
                    deleted_this_batch += 1
                except Exception:
                    continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate products")
    return total_deleted

def delete_duplicates_transactions():
    """Delete duplicates from transactions_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transactions_blaze")
    print("="*60)
    
    total_deleted = 0
    iteration = 0
    
    while iteration < 100:
        iteration += 1
        print(f"Iteration {iteration}: Processing...")
        
        try:
            response = client.table('transactions_blaze').select('id,transaction_id').limit(BATCH_SIZE * 2).execute()
            
            if not response.data:
                break
            
            seen_tids = {}
            to_delete = []
            
            for txn in response.data:
                tid = str(txn.get('transaction_id') or '')
                if tid in seen_tids:
                    to_delete.append(txn['id'])
                else:
                    seen_tids[tid] = txn['id']
            
            if not to_delete:
                if iteration > 5:
                    break
                time.sleep(1)
                continue
            
            deleted_this_batch = 0
            for txn_id in to_delete[:100]:
                try:
                    client.table('transactions_blaze').delete().eq('id', txn_id).execute()
                    deleted_this_batch += 1
                except Exception:
                    continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transactions")
    return total_deleted

def main():
    print("="*60)
    print("BLAZE TABLES DEDUPLICATION - SUPABASE CLIENT")
    print("="*60)
    print("Using service role key (bypasses connection issues)")
    print(f"Batch size: {BATCH_SIZE}")
    
    # Test connection first
    try:
        print("\nTesting connection...")
        test = client.table('transaction_items_blaze').select('id').limit(1).execute()
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nMake sure:")
        print("1. Database is Healthy in Supabase dashboard")
        print("2. Service role key is correct")
        input("\nPress Enter to exit...")
        return
    
    print("\nStarting deduplication in 2 seconds...")
    print("(This may take 30+ minutes for millions of duplicates)")
    time.sleep(2)
    
    total_deleted = 0
    
    try:
        # Deduplicate
        total_deleted += delete_duplicates_table_items()
        total_deleted += delete_duplicates_products()
        total_deleted += delete_duplicates_transactions()
        
        print("\n" + "="*60)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted}")
        print("="*60)
        print("\nNext steps:")
        print("1. Run VACUUM ANALYZE in Supabase SQL Editor")
        print("2. Check database size reduction")
        print("3. Add unique indexes to prevent future duplicates")
        
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted")
        print(f"Deleted {total_deleted} duplicates before stopping")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        print(f"\nDeleted {total_deleted} duplicates before error")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")

