#!/usr/bin/env python3
"""
Quick check: Do the deduplication functions exist?
"""
from supabase import create_client, Client

# Hardcoded Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTcyODUyMjE3MCwiZXhwIjoyMDQ0MDk4MTcwfQ.9YqTPhlCxytiXxnb"

def verify_functions():
    print("="*60)
    print("VERIFYING DEDUPLICATION FUNCTIONS")
    print("="*60)
    
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Check functions by attempting to call them
        print("\n[INFO] Checking functions by attempting to call them...")
        functions = []
        
        test_functions = [
            'dedupe_transaction_items_batch',
            'dedupe_products_batch',
            'dedupe_transactions_batch'
        ]
        
        for func_name in test_functions:
            try:
                # Try to call with batch_size=0 (should return 0, not error)
                if func_name == 'dedupe_transaction_items_batch':
                    result = supabase.rpc('dedupe_transaction_items_batch', {'batch_size': 0}).execute()
                elif func_name == 'dedupe_products_batch':
                    result = supabase.rpc('dedupe_products_batch', {'batch_size': 0}).execute()
                elif func_name == 'dedupe_transactions_batch':
                    result = supabase.rpc('dedupe_transactions_batch', {'batch_size': 0}).execute()
                
                functions.append(func_name)
                print(f"  [OK] {func_name} exists")
            except Exception as e2:
                error_str = str(e2).lower()
                if 'does not exist' in error_str or 'function' in error_str or 'not found' in error_str:
                    print(f"  [MISSING] {func_name} - not found")
                else:
                    # Function exists but might have returned an error (that's OK)
                    functions.append(func_name)
                    print(f"  [OK] {func_name} exists (callable)")
        
        print("\n" + "="*60)
        if len(functions) == 3:
            print("✅ SUCCESS: All 3 functions are created!")
            print("\nFunctions found:")
            for func in ['dedupe_transaction_items_batch', 'dedupe_products_batch', 'dedupe_transactions_batch']:
                if func in functions:
                    print(f"  ✓ {func}")
                else:
                    print(f"  ✗ {func} - MISSING")
            print("\nYou can now run: python dedupe_blaze_rpc.py")
            return True
        else:
            print(f"❌ INCOMPLETE: Only {len(functions)}/3 functions found")
            print("\nMissing functions:")
            all_funcs = ['dedupe_transaction_items_batch', 'dedupe_products_batch', 'dedupe_transactions_batch']
            for func in all_funcs:
                if func not in functions:
                    print(f"  ✗ {func}")
            print("\nCreate them by running:")
            print("  1. sql_scripts/create_function_1_transaction_items.sql")
            print("  2. sql_scripts/create_function_2_products.sql")
            print("  3. sql_scripts/create_function_3_transactions.sql")
            print("\nSee: sql_scripts/CREATE_FUNCTIONS_GUIDE.md")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Failed to verify: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    verify_functions()
    input("\nPress Enter to exit...")

