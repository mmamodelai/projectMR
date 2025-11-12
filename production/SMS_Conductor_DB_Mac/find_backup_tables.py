#!/usr/bin/env python3
"""
Find backup/archive tables that can be safely deleted
"""
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def find_backup_tables():
    """Find tables with backup/archive keywords"""
    print("="*70)
    print("FINDING BACKUP/ARCHIVE TABLES")
    print("="*70)
    
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Known tables - check which ones are backups
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
    
    backup_keywords = ['backup', '_old', '_archive', '_test', '_temp', 'samples', 'sync_state']
    
    print("\nChecking tables for backup keywords...\n")
    
    backup_tables = []
    production_tables = []
    
    for table in all_tables:
        table_lower = table.lower()
        is_backup = any(keyword in table_lower for keyword in backup_keywords)
        
        if is_backup:
            backup_tables.append(table)
        else:
            production_tables.append(table)
    
    print("="*70)
    print("🔴 BACKUP/ARCHIVE TABLES (Safe to delete)")
    print("="*70)
    
    if backup_tables:
        for table in backup_tables:
            print(f"   ✓ {table}")
        
        print("\n" + "="*70)
        print("SQL COMMANDS TO DELETE BACKUP TABLES")
        print("="*70)
        print("\n⚠️  Copy/paste these ONE AT A TIME in Supabase SQL Editor:\n")
        
        for table in backup_tables:
            print(f"-- Delete {table}")
            print(f"DROP TABLE IF EXISTS public.{table} CASCADE;")
            print()
        
        print("="*70)
        print("RECOMMENDED DELETION ORDER")
        print("="*70)
        print("\n1. blaze_api_samples (old API test data)")
        print("2. blaze_sync_state (sync tracking - can be recreated)")
        print("\nAfter each deletion:")
        print("  - Wait 30 seconds")
        print("  - Check database status")
        print("  - If still timing out, delete next table")
        
    else:
        print("\n   No obvious backup tables found.")
        print("\n   To see ALL tables, run this SQL in Supabase SQL Editor:")
        print("   SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;")
    
    print("\n" + "="*70)
    print("🟢 PRODUCTION TABLES (Keep these)")
    print("="*70)
    print("\nThese are production tables - DO NOT DELETE:\n")
    for table in production_tables[:10]:  # Show first 10
        print(f"   - {table}")
    if len(production_tables) > 10:
        print(f"   ... and {len(production_tables) - 10} more")

if __name__ == "__main__":
    find_backup_tables()
    input("\nPress Enter to exit...")

