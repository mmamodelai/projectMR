#!/usr/bin/env python3
"""
Create deduplication SQL functions via direct Postgres connection
Bypasses SQL editor timeout
"""
import psycopg2
import sys

# Hardcoded credentials
DB_HOST = "aws-0-us-east-2.pooler.supabase.com"  # Session pooler
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.kiwmwoqrguyrcpjytgte"
DB_PASSWORD = "9YqTPhlCxytiXxnb"

# SQL to create functions (one at a time)
FUNCTION_1 = """
CREATE OR REPLACE FUNCTION dedupe_transaction_items_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY transaction_id, product_id, quantity, unit_price
                   ORDER BY id DESC
               ) AS rn
        FROM public.transaction_items_blaze
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.transaction_items_blaze t
    USING to_del d
    WHERE t.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;
"""

FUNCTION_2 = """
CREATE OR REPLACE FUNCTION dedupe_products_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY id DESC) rn
        FROM public.products_blaze
        WHERE sku IS NOT NULL
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.products_blaze p
    USING to_del d
    WHERE p.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;
"""

FUNCTION_3 = """
CREATE OR REPLACE FUNCTION dedupe_transactions_batch(batch_size INTEGER DEFAULT 1000)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    WITH ranked AS (
        SELECT id, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY id DESC) rn
        FROM public.transactions_blaze
    ),
    to_del AS (
        SELECT id FROM ranked WHERE rn > 1 LIMIT batch_size
    )
    DELETE FROM public.transactions_blaze t
    USING to_del d
    WHERE t.id = d.id;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;
"""

def create_functions():
    print("="*60)
    print("CREATING DEDUPLICATION SQL FUNCTIONS")
    print("="*60)
    print(f"\nConnecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require',
            connect_timeout=30
        )
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nTrying alternative: Direct connection...")
        
        # Try direct connection
        try:
            conn = psycopg2.connect(
                host="db.kiwmwoqrguyrcpjytgte.supabase.co",
                port="5432",
                database="postgres",
                user="postgres",
                password=DB_PASSWORD,
                sslmode='require',
                connect_timeout=30
            )
            print("[OK] Direct connection worked!")
        except Exception as e2:
            print(f"[ERROR] Direct connection also failed: {e2}")
            print("\nOptions:")
            print("1. Wait for database to be Healthy in Supabase dashboard")
            print("2. Try running SQL manually in Supabase SQL Editor (may timeout)")
            return False
    
    cur = conn.cursor()
    
    try:
        # Create function 1
        print("\nCreating function 1: dedupe_transaction_items_batch...")
        cur.execute(FUNCTION_1)
        conn.commit()
        print("[OK] Function 1 created!")
        
        # Create function 2
        print("Creating function 2: dedupe_products_batch...")
        cur.execute(FUNCTION_2)
        conn.commit()
        print("[OK] Function 2 created!")
        
        # Create function 3
        print("Creating function 3: dedupe_transactions_batch...")
        cur.execute(FUNCTION_3)
        conn.commit()
        print("[OK] Function 3 created!")
        
        # Verify functions exist
        print("\nVerifying functions...")
        cur.execute("""
            SELECT routine_name 
            FROM information_schema.routines 
            WHERE routine_schema = 'public' 
            AND routine_name IN (
                'dedupe_transaction_items_batch',
                'dedupe_products_batch',
                'dedupe_transactions_batch'
            )
        """)
        functions = cur.fetchall()
        
        if len(functions) == 3:
            print(f"[OK] All 3 functions verified!")
            for func in functions:
                print(f"  - {func[0]}")
        else:
            print(f"[WARNING] Only found {len(functions)}/3 functions")
        
        cur.close()
        conn.close()
        
        print("\n" + "="*60)
        print("SUCCESS! Functions created.")
        print("="*60)
        print("\nYou can now run: python dedupe_blaze_rpc.py")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Failed to create functions: {e}")
        conn.rollback()
        cur.close()
        conn.close()
        return False

if __name__ == "__main__":
    try:
        success = create_functions()
        if not success:
            print("\n[FALLBACK] You can try running the SQL manually:")
            print("  Open: sql_scripts/dedupe_blaze_function.sql")
            print("  Copy/paste into Supabase SQL Editor")
            print("  Run each CREATE FUNCTION statement separately")
    except Exception as e:
        print(f"\n[FATAL ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to exit...")

