#!/usr/bin/env python3
"""
List all tables in the database to identify archive/old tables
"""
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def list_tables():
    """List all tables in public schema"""
    print("="*70)
    print("LISTING ALL TABLES")
    print("="*70)
    print("\n[INFO] Getting table list...")
    print("(This may timeout if database is overloaded)\n")
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Try to get table list via a simple query
    # We'll use a known table to test connection first
    try:
        # Test connection
        test = client.table('transactions_blaze').select('id').limit(1).execute()
        print("[OK] Connected successfully!\n")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nDatabase is too overloaded. Try:")
        print("  1. Wait for database to be 'Healthy'")
        print("  2. Run SQL directly in Supabase SQL Editor:")
        print("     SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
        return
    
    # List of tables we know about
    known_tables = [
        'blaze_api_samples',
        'transaction_items_blaze',
        'transactions_blaze',
        'products_blaze',
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
        'scheduled_messages',
        'staff',
        'employees_blaze',
        'regions_blaze',
        'terminals_blaze',
        'vendors_blaze',
        'blaze_sync_state',
        'EXCustomers',
    ]
    
    print("="*70)
    print("ARCHIVE TABLE CANDIDATES")
    print("="*70)
    print("\nThese tables might be safe to delete (VERIFY FIRST!):\n")
    
    archive_keywords = ['_old', '_backup', '_archive', '_test', '_temp', 'samples', 'sync_state']
    
    archive_candidates = []
    other_tables = []
    
    for table in known_tables:
        is_archive = any(keyword in table.lower() for keyword in archive_keywords)
        if is_archive:
            archive_candidates.append(table)
        else:
            other_tables.append(table)
    
    if archive_candidates:
        print("🔴 HIGH PRIORITY (likely archive/old):")
        for table in archive_candidates:
            print(f"   - {table}")
    
    print("\n" + "="*70)
    print("OTHER TABLES (probably keep these)")
    print("="*70)
    for table in other_tables:
        print(f"   - {table}")
    
    print("\n" + "="*70)
    print("SQL COMMANDS TO DELETE ARCHIVE TABLES")
    print("="*70)
    print("\n⚠️  WARNING: These commands are PERMANENT!")
    print("   Verify each table before deleting!\n")
    
    if archive_candidates:
        for table in archive_candidates:
            print(f"-- Delete {table}")
            print(f"DROP TABLE IF EXISTS public.{table} CASCADE;")
            print()
    else:
        print("No obvious archive tables found.")
        print("\nTo see ALL tables, run this SQL in Supabase SQL Editor:")
        print("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
    
    print("\n" + "="*70)
    print("RECOMMENDED DELETION ORDER")
    print("="*70)
    print("\n1. blaze_api_samples (if it's just old API test data)")
    print("2. blaze_sync_state (if it's just sync tracking, can be recreated)")
    print("3. Any tables with '_old', '_backup', '_archive' in name")
    print("\nAfter deleting, check database status - should become 'Healthy'")

if __name__ == "__main__":
    list_tables()
    input("\nPress Enter to exit...")

