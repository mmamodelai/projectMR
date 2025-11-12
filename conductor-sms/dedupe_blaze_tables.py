#!/usr/bin/env python3
"""
Deduplicate Blaze tables - runs batch deletes until no duplicates remain
Bypasses SQL editor timeout by connecting directly
"""
import os
import time
from supabase import create_client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

# Use service_role key for direct SQL execution
client = create_client(SUPABASE_URL, SUPABASE_KEY)

BATCH_SIZE = 1000  # Smaller batches to avoid timeout
MAX_ITERATIONS = 1000  # Safety limit

def run_sql(query: str) -> dict:
    """Execute SQL via Supabase REST API"""
    try:
        # Use RPC or direct SQL execution
        response = client.rpc('exec_sql', {'query': query}).execute()
        return {'success': True, 'data': response.data}
    except Exception as e:
        # Fallback: try direct table operations
        return {'success': False, 'error': str(e)}

def delete_duplicates_table_items():
    """Delete duplicates from transaction_items_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transaction_items_blaze")
    print("="*60)
    
    iteration = 0
    total_deleted = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        
        # Check how many duplicates exist
        check_query = f"""
        SELECT COUNT(*) as dup_count
        FROM (
            SELECT transaction_id, product_id, quantity, unit_price, COUNT(*) as cnt
            FROM public.transaction_items_blaze
            GROUP BY transaction_id, product_id, quantity, unit_price
            HAVING COUNT(*) > 1
        ) g;
        """
        
        try:
            # Use PostgREST to count duplicates
            result = client.table('transaction_items_blaze').select('id,transaction_id,product_id,quantity,unit_price', count='exact').limit(1).execute()
            print(f"Iteration {iteration}: Checking duplicates...")
        except Exception as e:
            print(f"Error checking: {e}")
            break
        
        # Delete batch using Python logic (safer than SQL timeout)
        try:
            # Get all rows
            all_items = client.table('transaction_items_blaze').select('id,transaction_id,product_id,quantity,unit_price').limit(BATCH_SIZE * 10).execute()
            
            if not all_items.data:
                print("No more items to process")
                break
            
            # Group by key and find duplicates
            seen = {}
            to_delete = []
            
            for item in all_items.data:
                key = (
                    item.get('transaction_id'),
                    item.get('product_id'),
                    item.get('quantity'),
                    item.get('unit_price')
                )
                
                if key in seen:
                    # Duplicate - mark for deletion (keep first, delete this)
                    to_delete.append(item['id'])
                else:
                    seen[key] = item['id']
            
            if not to_delete:
                print("No duplicates found in this batch")
                if iteration > 10:  # Been running a while, might be done
                    break
                time.sleep(1)
                continue
            
            # Delete in smaller chunks
            deleted_this_batch = 0
            for i in range(0, len(to_delete), 100):  # Delete 100 at a time
                chunk = to_delete[i:i+100]
                try:
                    for item_id in chunk:
                        client.table('transaction_items_blaze').delete().eq('id', item_id).execute()
                        deleted_this_batch += 1
                except Exception as e:
                    print(f"Error deleting chunk: {e}")
                    continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            
            if deleted_this_batch < 100:  # Getting small, might be done
                print("Deletion rate slowing, checking if complete...")
                time.sleep(2)
            
        except Exception as e:
            print(f"Error in batch {iteration}: {e}")
            time.sleep(5)  # Back off on error
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transaction_items")
    return total_deleted

def delete_duplicates_products():
    """Delete duplicates from products_blaze (by SKU)"""
    print("\n" + "="*60)
    print("DEDUPLICATING: products_blaze")
    print("="*60)
    
    iteration = 0
    total_deleted = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"Iteration {iteration}: Processing products...")
        
        try:
            # Get products with SKUs
            products = client.table('products_blaze').select('id,sku').not_.is_('sku', 'null').limit(BATCH_SIZE * 10).execute()
            
            if not products.data:
                print("No more products to process")
                break
            
            # Find duplicates by SKU
            seen_skus = {}
            to_delete = []
            
            for product in products.data:
                sku = product.get('sku')
                if sku in seen_skus:
                    to_delete.append(product['id'])
                else:
                    seen_skus[sku] = product['id']
            
            if not to_delete:
                print("No duplicates found")
                if iteration > 5:
                    break
                time.sleep(1)
                continue
            
            # Delete in chunks
            deleted_this_batch = 0
            for i in range(0, len(to_delete), 100):
                chunk = to_delete[i:i+100]
                for prod_id in chunk:
                    try:
                        client.table('products_blaze').delete().eq('id', prod_id).execute()
                        deleted_this_batch += 1
                    except Exception as e:
                        print(f"Error deleting product {prod_id}: {e}")
                        continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate products")
    return total_deleted

def delete_duplicates_transactions():
    """Delete duplicates from transactions_blaze (by transaction_id)"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transactions_blaze")
    print("="*60)
    
    iteration = 0
    total_deleted = 0
    
    while iteration < MAX_ITERATIONS:
        iteration += 1
        print(f"Iteration {iteration}: Processing transactions...")
        
        try:
            transactions = client.table('transactions_blaze').select('id,transaction_id').limit(BATCH_SIZE * 10).execute()
            
            if not transactions.data:
                break
            
            seen_tids = {}
            to_delete = []
            
            for txn in transactions.data:
                tid = txn.get('transaction_id')
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
            for i in range(0, len(to_delete), 100):
                chunk = to_delete[i:i+100]
                for txn_id in chunk:
                    try:
                        client.table('transactions_blaze').delete().eq('id', txn_id).execute()
                        deleted_this_batch += 1
                    except Exception as e:
                        print(f"Error deleting transaction {txn_id}: {e}")
                        continue
            
            total_deleted += deleted_this_batch
            print(f"  Deleted {deleted_this_batch} duplicates (Total: {total_deleted})")
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
            continue
    
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transactions")
    return total_deleted

def main():
    print("="*60)
    print("BLAZE TABLES DEDUPLICATION SCRIPT")
    print("="*60)
    print(f"Batch size: {BATCH_SIZE}")
    print(f"Max iterations per table: {MAX_ITERATIONS}")
    print("\nStarting in 3 seconds...")
    time.sleep(3)
    
    total_deleted = 0
    
    # 1. Transaction Items (biggest bloat)
    total_deleted += delete_duplicates_table_items()
    
    # 2. Products
    total_deleted += delete_duplicates_products()
    
    # 3. Transactions
    total_deleted += delete_duplicates_transactions()
    
    print("\n" + "="*60)
    print(f"TOTAL DUPLICATES DELETED: {total_deleted}")
    print("="*60)
    print("\nNext steps:")
    print("1. Run VACUUM ANALYZE in Supabase SQL Editor")
    print("2. Check database size reduction")
    print("3. Add unique indexes to prevent future duplicates")

if __name__ == "__main__":
    main()

