#!/usr/bin/env python3
"""
Safely delete entire tables (for archive/old tables)
USE WITH EXTREME CAUTION - DELETES DATA PERMANENTLY
"""
from supabase import create_client

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def delete_table(table_name):
    """
    Delete an entire table using SQL DROP TABLE
    WARNING: This is PERMANENT and cannot be undone!
    """
    print("="*70)
    print(f"DELETE TABLE: {table_name}")
    print("="*70)
    print("\n⚠️  WARNING: This will PERMANENTLY DELETE all data in this table!")
    print("   This action CANNOT be undone!")
    
    # Double confirmation
    confirm1 = input(f"\nType '{table_name}' to confirm: ")
    if confirm1 != table_name:
        print("Confirmation failed. Aborted.")
        return False
    
    confirm2 = input("Type 'DELETE' to confirm again: ")
    if confirm2 != 'DELETE':
        print("Second confirmation failed. Aborted.")
        return False
    
    print("\n[INFO] Attempting to delete table...")
    print("(Note: Supabase Python client doesn't support DROP TABLE directly)")
    print("You need to run this SQL in Supabase SQL Editor:")
    print(f"\n  DROP TABLE IF EXISTS public.{table_name} CASCADE;")
    print("\nOr use psycopg2 for direct connection.")
    
    # For now, we'll just provide instructions
    # Direct DROP TABLE via Supabase REST API is not straightforward
    print("\n[ACTION REQUIRED] Run the SQL command above in Supabase SQL Editor")
    
    return True

def list_candidate_tables():
    """List tables that might be safe to delete"""
    print("="*70)
    print("CANDIDATE TABLES FOR DELETION")
    print("="*70)
    print("\nThese tables might be safe to delete (verify first!):")
    print("\n1. blaze_api_samples - Old API sample data")
    print("2. Any tables with '_old', '_backup', '_archive' in name")
    print("3. Test/development tables")
    print("\n⚠️  ALWAYS verify table contents before deleting!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        delete_table(table_name)
    else:
        list_candidate_tables()
        print("\nUsage: python delete_table_safely.py <table_name>")
    
    input("\nPress Enter to exit...")

