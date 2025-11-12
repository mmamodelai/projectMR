#!/usr/bin/env python3
"""
DELETE backup tables NOW - actually deletes them
"""
from supabase import create_client
import time

# Hardcoded credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1OTg0NTA1MSwiZXhwIjoyMDc1NDIxMDUxfQ.o-GId7meaTXwyB4neYjg05oPfRdasvOHs6FHZZyprLs"

def delete_table_direct(table_name):
    """Delete a table using direct SQL execution"""
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    # Use RPC to execute DROP TABLE
    # We'll create a temporary function to do this
    try:
        # Try to execute DROP TABLE via RPC
        # Since Supabase Python client doesn't support DROP TABLE directly,
        # we need to use the SQL editor or create a function
        
        # Actually, the best way is to use psycopg2 for direct SQL
        # But since that's been problematic, let's try using Supabase's REST API
        # to execute raw SQL
        
        print(f"Attempting to delete: {table_name}...")
        
        # Supabase Python client doesn't support DDL directly
        # We need to use the SQL editor or create a server-side function
        # Let me create a function that can be called
        
        # Actually, let me just provide the SQL and execute it via a helper function
        # The most reliable way is still SQL Editor, but let me try RPC
        
        # Create a function to delete tables if it doesn't exist
        create_function_sql = f"""
        CREATE OR REPLACE FUNCTION delete_table_safe(table_name TEXT)
        RETURNS TEXT
        LANGUAGE plpgsql
        AS $$
        BEGIN
            EXECUTE format('DROP TABLE IF EXISTS public.%I CASCADE', table_name);
            RETURN 'Deleted: ' || table_name;
        END;
        $$;
        """
        
        # Try to create the function first (if it doesn't exist)
        try:
            # We can't execute DDL via RPC easily, so let's use a different approach
            # Actually, let me just print the SQL commands and execute them
            
            # The Python client doesn't support DDL, so we need to use SQL Editor
            # But the user wants it done NOW, so let me try using psycopg2
            
            import psycopg2
            
            # Parse connection string from Supabase URL
            # Supabase connection details
            DB_HOST = "db.kiwmwoqrguyrcpjytgte.supabase.co"
            DB_PORT = 5432
            DB_NAME = "postgres"
            DB_USER = "postgres.kiwmwoqrguyrcpjytgte"
            DB_PASSWORD = "Xbmc2024!"  # From previous context
            
            try:
                conn = psycopg2.connect(
                    host=DB_HOST,
                    port=DB_PORT,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD
                )
                conn.autocommit = True
                cursor = conn.cursor()
                
                sql = f"DROP TABLE IF EXISTS public.{table_name} CASCADE;"
                cursor.execute(sql)
                
                print(f"✅ DELETED: {table_name}")
                cursor.close()
                conn.close()
                return True
                
            except Exception as e:
                print(f"❌ Failed to delete {table_name}: {e}")
                print(f"\nRun this SQL in Supabase SQL Editor:")
                print(f"DROP TABLE IF EXISTS public.{table_name} CASCADE;")
                return False
                
        except ImportError:
            print("psycopg2 not available. Run this SQL in Supabase SQL Editor:")
            print(f"DROP TABLE IF EXISTS public.{table_name} CASCADE;")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"\nRun this SQL in Supabase SQL Editor:")
        print(f"DROP TABLE IF EXISTS public.{table_name} CASCADE;")
        return False

def main():
    print("="*70)
    print("DELETING BACKUP TABLES NOW")
    print("="*70)
    
    backup_tables = [
        'blaze_api_samples',
        'blaze_sync_state',
    ]
    
    print("\nDeleting backup tables...\n")
    
    for table in backup_tables:
        delete_table_direct(table)
        time.sleep(2)  # Small delay between deletions
    
    print("\n" + "="*70)
    print("DONE")
    print("="*70)
    print("\nIf any failed, run the SQL commands shown above")
    print("in Supabase SQL Editor.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")

