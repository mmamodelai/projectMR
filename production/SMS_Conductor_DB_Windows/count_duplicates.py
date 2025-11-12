#!/usr/bin/env python3
"""
Count duplicates in Blaze tables
Shows how much work needs to be done
"""
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSI6ImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

client = create_client(SUPABASE_URL, SUPABASE_KEY)

def count_duplicates_table_items():
    """Count duplicates in transaction_items_blaze"""
    print("\n" + "="*60)
    print("COUNTING DUPLICATES: transaction_items_blaze")
    print("="*60)
    
    try:
        # Try RPC function first (fast!)
        try:
            print("Using SQL function (fast)...")
            response = client.rpc('count_duplicate_transaction_items').execute()
            count = response.data if isinstance(response.data, int) else 0
            print(f"\n[EXACT COUNT] Duplicate groups: {count:,}")
            print("(Each group may have multiple duplicate rows)")
            return count
        except Exception as e:
            if "does not exist" in str(e) or "function" in str(e).lower():
                print("SQL function not found - using client-side counting (slower)...")
                print("(Run sql_scripts/count_duplicates_function.sql to create functions)")
            else:
                print(f"RPC failed: {e}, falling back to client-side...")
            
            # Fallback: client-side counting
            print("\nCounting duplicates (this may take a moment)...")
            seen_keys = {}
            duplicates = 0
            total_checked = 0
            batch_size = 10000
            
            while total_checked < 100000:  # Check first 100k rows
                response = client.table('transaction_items_blaze').select('id,transaction_id,product_id,quantity,unit_price').range(total_checked, total_checked + batch_size - 1).execute()
                
                if not response.data:
                    break
                
                for item in response.data:
                    key = (
                        str(item.get('transaction_id') or ''),
                        str(item.get('product_id') or ''),
                        str(item.get('quantity') or ''),
                        str(item.get('unit_price') or '')
                    )
                    
                    if key in seen_keys:
                        duplicates += 1
                    else:
                        seen_keys[key] = item['id']
                    
                    total_checked += 1
                
                if len(response.data) < batch_size:
                    break
                
                print(f"  Checked {total_checked:,} rows, found {duplicates:,} duplicates...")
            
            if total_checked >= 100000:
                print(f"\n[ESTIMATE] Based on first {total_checked:,} rows:")
                print(f"  Duplicates found: {duplicates:,}")
                print(f"  Duplicate rate: {duplicates/total_checked*100:.1f}%")
                print(f"\n[NOTE] This is an estimate. Create SQL function for exact count.")
            else:
                print(f"\n[EXACT] Checked all {total_checked:,} rows")
                print(f"  Total duplicates: {duplicates:,}")
            
            return duplicates
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 0

def count_duplicates_products():
    """Count duplicates in products_blaze"""
    print("\n" + "="*60)
    print("COUNTING DUPLICATES: products_blaze")
    print("="*60)
    
    try:
        # Try RPC function first
        try:
            print("Using SQL function (fast)...")
            response = client.rpc('count_duplicate_products').execute()
            count = response.data if isinstance(response.data, int) else 0
            print(f"\n[EXACT COUNT] Duplicate groups: {count:,}")
            return count
        except Exception:
            print("SQL function not found - using client-side counting...")
            
            seen_skus = {}
            duplicates = 0
            total_checked = 0
            batch_size = 10000
            
            while total_checked < 50000:
                response = client.table('products_blaze').select('id,sku').not_.is_('sku', 'null').range(total_checked, total_checked + batch_size - 1).execute()
                
                if not response.data:
                    break
                
                for product in response.data:
                    sku = str(product.get('sku') or '')
                    if sku in seen_skus:
                        duplicates += 1
                    else:
                        seen_skus[sku] = product['id']
                    total_checked += 1
                
                if len(response.data) < batch_size:
                    break
                
                print(f"  Checked {total_checked:,} rows, found {duplicates:,} duplicates...")
            
            if total_checked >= 50000:
                print(f"\n[ESTIMATE] Based on first {total_checked:,} rows:")
                print(f"  Duplicates: {duplicates:,}")
            else:
                print(f"\n[EXACT] Checked all {total_checked:,} rows")
                print(f"  Total duplicates: {duplicates:,}")
            
            return duplicates
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def count_duplicates_transactions():
    """Count duplicates in transactions_blaze"""
    print("\n" + "="*60)
    print("COUNTING DUPLICATES: transactions_blaze")
    print("="*60)
    
    try:
        # Try RPC function first
        try:
            print("Using SQL function (fast)...")
            response = client.rpc('count_duplicate_transactions').execute()
            count = response.data if isinstance(response.data, int) else 0
            print(f"\n[EXACT COUNT] Duplicate groups: {count:,}")
            return count
        except Exception:
            print("SQL function not found - using client-side counting...")
            
            seen_tids = {}
            duplicates = 0
            total_checked = 0
            batch_size = 10000
            
            while total_checked < 50000:
                response = client.table('transactions_blaze').select('id,transaction_id').range(total_checked, total_checked + batch_size - 1).execute()
                
                if not response.data:
                    break
                
                for txn in response.data:
                    tid = str(txn.get('transaction_id') or '')
                    if tid in seen_tids:
                        duplicates += 1
                    else:
                        seen_tids[tid] = txn['id']
                    total_checked += 1
                
                if len(response.data) < batch_size:
                    break
                
                print(f"  Checked {total_checked:,} rows, found {duplicates:,} duplicates...")
            
            if total_checked >= 50000:
                print(f"\n[ESTIMATE] Based on first {total_checked:,} rows:")
                print(f"  Duplicates: {duplicates:,}")
            else:
                print(f"\n[EXACT] Checked all {total_checked:,} rows")
                print(f"  Total duplicates: {duplicates:,}")
            
            return duplicates
        
    except Exception as e:
        print(f"Error: {e}")
        return 0

def main():
    print("="*60)
    print("DUPLICATE COUNT - BLAZE TABLES")
    print("="*60)
    print("\nThis will count duplicates in each table.")
    print("(May take a few minutes for large tables)")
    
    try:
        print("\nTesting connection...")
        test = client.table('transaction_items_blaze').select('id').limit(1).execute()
        print("[OK] Connected!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return
    
    total_duplicates = 0
    
    total_duplicates += count_duplicates_table_items()
    total_duplicates += count_duplicates_products()
    total_duplicates += count_duplicates_transactions()
    
    print("\n" + "="*60)
    print(f"TOTAL DUPLICATES FOUND: {total_duplicates:,}")
    print("="*60)
    
    if total_duplicates > 0:
        print(f"\nEstimated cleanup time:")
        batches = (total_duplicates // 1000) + 1
        minutes = batches * 0.5  # ~0.5 seconds per batch
        print(f"  ~{batches:,} batches")
        print(f"  ~{minutes/60:.1f} hours")
        print(f"\nRun dedupe_blaze_rpc.py to delete them")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[STOPPED] User interrupted")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n" + "="*60)
        input("Press Enter to exit...")

