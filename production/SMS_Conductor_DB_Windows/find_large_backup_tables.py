#!/usr/bin/env python3
"""
Find LARGE backup tables - the real space hogs
Focus on member/customer backups, not tiny API samples
"""
from supabase import create_client
import time

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def get_all_tables_with_sizes():
    """Get all tables and their sizes"""
    print("="*70)
    print("FINDING LARGE BACKUP TABLES")
    print("="*70)
    print("\n[INFO] Checking all tables for size...")
    print("(Looking for large backups, not tiny API samples)\n")
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # SQL to get table sizes - we'll try to execute this
    # Since we can't execute arbitrary SQL easily, let's check known tables
    # and look for backup patterns
    
    # Known tables to check
    all_tables = [
        'blaze_api_samples',
        'blaze_sync_state',
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
        'EXCustomers',
    ]
    
    # Look for backup patterns
    backup_patterns = [
        'backup', '_backup', 'backup_', '_old', '_archive', 
        'archive', '_bak', '_copy', 'copy_', 'old_',
        'members_backup', 'customers_backup', 'transactions_backup'
    ]
    
    print("Checking table row counts (as proxy for size)...\n")
    
    large_tables = []
    backup_tables = []
    small_tables = []
    
    for table in all_tables:
        try:
            # Get row count
            response = client.table(table).select('id', count='exact').limit(1).execute()
            count = response.count if hasattr(response, 'count') else 0
            
            # Estimate size (rough: 1KB per row average)
            if isinstance(count, int):
                size_mb = (count * 1024) / (1024 * 1024)
                
                # Check if it's a backup table
                is_backup = any(pattern in table.lower() for pattern in backup_patterns)
                
                if is_backup:
                    backup_tables.append((table, count, size_mb))
                elif size_mb > 100:  # Large table (>100MB)
                    large_tables.append((table, count, size_mb))
                else:
                    small_tables.append((table, count, size_mb))
                    
        except Exception as e:
            error_str = str(e).lower()
            if 'timeout' in error_str:
                print(f"  {table:40} {'TIMEOUT':>15}")
            elif 'not found' in error_str or 'does not exist' in error_str:
                pass  # Table doesn't exist, skip
            else:
                print(f"  {table:40} {'ERROR':>15} - {str(e)[:50]}")
    
    print("\n" + "="*70)
    print("🔴 LARGE BACKUP TABLES (Delete these!)")
    print("="*70)
    
    if backup_tables:
        backup_tables.sort(key=lambda x: x[2], reverse=True)  # Sort by size
        for table, count, size_mb in backup_tables:
            print(f"   {table:40} {count:>15,} rows  {size_mb:>8.1f} MB")
        
        print("\n" + "="*70)
        print("SQL TO DELETE LARGE BACKUP TABLES")
        print("="*70)
        print("\n⚠️  Copy/paste these ONE AT A TIME in Supabase SQL Editor:\n")
        
        for table, count, size_mb in backup_tables:
            print(f"-- Delete {table} ({size_mb:.1f} MB)")
            print(f"DROP TABLE IF EXISTS public.{table} CASCADE;")
            print()
    else:
        print("\n   No obvious backup tables found in known list.")
        print("\n   Need to check ALL tables in database...")
        print("\n   Run this SQL in Supabase SQL Editor to see ALL tables:")
        print("   SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
        print("\n   Then check sizes:")
        print("   SELECT tablename, pg_size_pretty(pg_total_relation_size('public.'||tablename))")
        print("   FROM pg_tables WHERE schemaname = 'public' ORDER BY pg_total_relation_size('public.'||tablename) DESC;")
    
    print("\n" + "="*70)
    print("🟡 LARGE PRODUCTION TABLES (Keep these - but have duplicates)")
    print("="*70)
    if large_tables:
        large_tables.sort(key=lambda x: x[2], reverse=True)
        for table, count, size_mb in large_tables:
            print(f"   {table:40} {count:>15,} rows  {size_mb:>8.1f} MB")
    
    print("\n" + "="*70)
    print("SQL TO FIND ALL BACKUP TABLES")
    print("="*70)
    print("\nRun this in Supabase SQL Editor to find ALL backup tables:\n")
    print("SELECT ")
    print("    tablename,")
    print("    pg_size_pretty(pg_total_relation_size('public.'||tablename)) AS size")
    print("FROM pg_tables")
    print("WHERE schemaname = 'public'")
    print("AND (tablename LIKE '%backup%' OR tablename LIKE '%_backup%' OR tablename LIKE '%backup_%'")
    print("     OR tablename LIKE '%_old%' OR tablename LIKE '%_archive%'")
    print("     OR tablename LIKE '%_bak%' OR tablename LIKE '%_copy%')")
    print("ORDER BY pg_total_relation_size('public.'||tablename) DESC;")

if __name__ == "__main__":
    get_all_tables_with_sizes()
    input("\nPress Enter to exit...")

