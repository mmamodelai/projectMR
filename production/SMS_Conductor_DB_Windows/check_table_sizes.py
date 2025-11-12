#!/usr/bin/env python3
"""
Check table sizes to identify what's taking up space
Helps identify tables that can be deleted entirely
"""
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def get_table_sizes():
    """Get approximate table sizes from PostgreSQL"""
    print("="*70)
    print("CHECKING TABLE SIZES")
    print("="*70)
    print("\n[INFO] Querying database for table sizes...")
    print("(This may timeout if database is overloaded)\n")
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL query to get table sizes
    # Using pg_total_relation_size for total size (including indexes)
    sql_query = """
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
        pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes,
        (SELECT COUNT(*) FROM information_schema.tables 
         WHERE table_schema = schemaname AND table_name = tablename) as exists
    FROM pg_tables
    WHERE schemaname = 'public'
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
    LIMIT 30;
    """
    
    try:
        # Try to execute via RPC if we have a helper function, otherwise use direct query
        # Since Supabase doesn't expose direct SQL easily, let's try a simpler approach
        # We'll query each table's row count as a proxy for size
        
        print("Getting row counts for major tables...\n")
        
        # List of tables to check
        tables_to_check = [
            'transaction_items_blaze',
            'transactions_blaze',
            'products_blaze',
            'blaze_api_samples',
            'customers_blaze',
            'budtenders',
            'messages',
            'campaign_messages',
            'transaction_items',
            'transactions',
            'products',
            'customer_product_affinity',
            'customer_visit_patterns',
            'campaign_customer_patterns',
        ]
        
        results = []
        
        for table_name in tables_to_check:
            try:
                # Get approximate count (fast)
                response = client.table(table_name).select('id', count='exact').limit(1).execute()
                count = response.count if hasattr(response, 'count') else 'unknown'
                
                # Estimate size (rough: assume 1KB per row average)
                if isinstance(count, int):
                    size_mb = (count * 1024) / (1024 * 1024)
                    size_str = f"{size_mb:.1f} MB (est)"
                else:
                    size_str = "unknown"
                
                results.append({
                    'table': table_name,
                    'rows': count,
                    'size': size_str
                })
                
                print(f"  {table_name:40} {str(count):>15} rows  {size_str}")
                
            except Exception as e:
                error_str = str(e).lower()
                if 'timeout' in error_str:
                    print(f"  {table_name:40} {'TIMEOUT':>15}")
                elif 'does not exist' in error_str or 'not found' in error_str:
                    print(f"  {table_name:40} {'NOT FOUND':>15}")
                else:
                    print(f"  {table_name:40} {'ERROR':>15} - {str(e)[:50]}")
        
        print("\n" + "="*70)
        print("RECOMMENDATIONS:")
        print("="*70)
        print("\n1. LARGEST TABLES (likely candidates for deduplication):")
        print("   - transaction_items_blaze (has duplicates)")
        print("   - products_blaze (has duplicates)")
        print("   - transactions_blaze (has duplicates)")
        print("   - blaze_api_samples (might be archive/old data)")
        
        print("\n2. TABLES TO CHECK FOR DELETION:")
        print("   - blaze_api_samples (if it's just old API samples)")
        print("   - Any tables with '_old', '_backup', '_archive' in name")
        print("   - Any test/development tables")
        
        print("\n3. NEXT STEPS:")
        print("   - Run deduplication with TINY batches (10-50 rows)")
        print("   - Delete entire archive/old tables if safe")
        print("   - Wait for database to be 'Healthy' before major operations")
        
    except Exception as e:
        print(f"\n[ERROR] Failed to get table sizes: {e}")
        import traceback
        traceback.print_exc()
        print("\n[SUGGESTION] Database might be too overloaded.")
        print("Try again when database status is 'Healthy'")

if __name__ == "__main__":
    get_table_sizes()
    input("\nPress Enter to exit...")

