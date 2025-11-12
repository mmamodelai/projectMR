#!/usr/bin/env python3
"""
Deduplicate Blaze tables using DIRECT Postgres connection
Bypasses Supabase SQL editor timeout completely
"""
import os
import time
import psycopg2
from psycopg2.extras import execute_batch

# Hardcoded credentials for immediate use
# Try Session Pooler first (no IPv4 needed)
DB_HOST = "aws-0-us-east-2.pooler.supabase.com"  # Session pooler
DB_PORT = "6543"  # Pooler port
DB_NAME = "postgres"
DB_USER = "postgres.kiwmwoqrguyrcpjytgte"  # Pooler format: postgres.project_ref
DB_PASSWORD = "9YqTPhlCxytiXxnb"  # Hardcoded for immediate deduplication

BATCH_SIZE = 1000

def get_connection():
    """Get Postgres connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require',
        connect_timeout=30
    )

def delete_duplicates_table_items(conn):
    """Delete duplicates from transaction_items_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transaction_items_blaze")
    print("="*60)
    
    cur = conn.cursor()
    total_deleted = 0
    iteration = 0
    
    while iteration < 100:  # Safety limit
        iteration += 1
        
        # Delete batch using SQL (much faster than Python loops)
        delete_query = """
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY transaction_id, product_id, quantity, unit_price
                       ORDER BY id DESC
                   ) AS rn
            FROM public.transaction_items_blaze
        ),
        to_del AS (
            SELECT id FROM ranked WHERE rn > 1 LIMIT %s
        )
        DELETE FROM public.transaction_items_blaze t
        USING to_del d
        WHERE t.id = d.id
        RETURNING t.id;
        """
        
        try:
            cur.execute(delete_query, (BATCH_SIZE,))
            deleted_ids = cur.fetchall()
            deleted_count = len(deleted_ids)
            conn.commit()
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count} duplicates (Total: {total_deleted})")
            
            if deleted_count < BATCH_SIZE:
                print("  (Small batch - might be finishing up)")
            
            time.sleep(0.5)  # Small delay to avoid overwhelming DB
            
        except Exception as e:
            print(f"Error on iteration {iteration}: {e}")
            conn.rollback()
            time.sleep(2)
            if "timeout" in str(e).lower():
                print("  Timeout - database might be overloaded. Waiting 10s...")
                time.sleep(10)
            continue
    
    cur.close()
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transaction_items")
    return total_deleted

def delete_duplicates_products(conn):
    """Delete duplicates from products_blaze (by SKU)"""
    print("\n" + "="*60)
    print("DEDUPLICATING: products_blaze")
    print("="*60)
    
    cur = conn.cursor()
    total_deleted = 0
    iteration = 0
    
    while iteration < 100:
        iteration += 1
        
        delete_query = """
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY sku ORDER BY id DESC) rn
            FROM public.products_blaze
            WHERE sku IS NOT NULL
        ),
        to_del AS (
            SELECT id FROM ranked WHERE rn > 1 LIMIT %s
        )
        DELETE FROM public.products_blaze p
        USING to_del d
        WHERE p.id = d.id
        RETURNING p.id;
        """
        
        try:
            cur.execute(delete_query, (BATCH_SIZE,))
            deleted_ids = cur.fetchall()
            deleted_count = len(deleted_ids)
            conn.commit()
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count} duplicates (Total: {total_deleted})")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            time.sleep(2)
            continue
    
    cur.close()
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate products")
    return total_deleted

def delete_duplicates_transactions(conn):
    """Delete duplicates from transactions_blaze"""
    print("\n" + "="*60)
    print("DEDUPLICATING: transactions_blaze")
    print("="*60)
    
    cur = conn.cursor()
    total_deleted = 0
    iteration = 0
    
    while iteration < 100:
        iteration += 1
        
        delete_query = """
        WITH ranked AS (
            SELECT id, ROW_NUMBER() OVER (PARTITION BY transaction_id ORDER BY id DESC) rn
            FROM public.transactions_blaze
        ),
        to_del AS (
            SELECT id FROM ranked WHERE rn > 1 LIMIT %s
        )
        DELETE FROM public.transactions_blaze t
        USING to_del d
        WHERE t.id = d.id
        RETURNING t.id;
        """
        
        try:
            cur.execute(delete_query, (BATCH_SIZE,))
            deleted_ids = cur.fetchall()
            deleted_count = len(deleted_ids)
            conn.commit()
            
            if deleted_count == 0:
                print(f"Iteration {iteration}: No more duplicates found!")
                break
            
            total_deleted += deleted_count
            print(f"Iteration {iteration}: Deleted {deleted_count} duplicates (Total: {total_deleted})")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error: {e}")
            conn.rollback()
            time.sleep(2)
            continue
    
    cur.close()
    print(f"\nCOMPLETE: Deleted {total_deleted} duplicate transactions")
    return total_deleted

def find_archive_tables(conn):
    """Find archive/old tables that can be deleted"""
    print("\n" + "="*60)
    print("FINDING ARCHIVE TABLES TO DELETE")
    print("="*60)
    
    cur = conn.cursor()
    
    query = """
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(format('%I.%I', schemaname, tablename))) AS size,
        pg_total_relation_size(format('%I.%I', schemaname, tablename)) AS size_bytes
    FROM pg_tables
    WHERE schemaname IN ('public', 'archive')
      AND (tablename ILIKE '%old%' 
           OR tablename ILIKE '%backup%' 
           OR tablename ILIKE '%_2025%'
           OR tablename ILIKE '%archive%')
    ORDER BY size_bytes DESC
    LIMIT 20;
    """
    
    cur.execute(query)
    tables = cur.fetchall()
    
    if tables:
        print("\nArchive tables found (can be deleted):")
        for schema, table, size, size_bytes in tables:
            print(f"  {schema}.{table}: {size}")
    else:
        print("No obvious archive tables found")
    
    cur.close()
    return tables

def main():
    print("="*60)
    print("BLAZE TABLES DEDUPLICATION - DIRECT POSTGRES")
    print("="*60)
    print(f"\nConnecting to: {DB_HOST}:{DB_PORT}/{DB_NAME}")
    print(f"Batch size: {BATCH_SIZE}")
    print("Credentials: Hardcoded (ready to run)")
    
    try:
        conn = get_connection()
        print("[OK] Connected successfully!")
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        print("\nMake sure:")
        print("1. Database is Healthy in Supabase dashboard")
        print("2. DB_PASSWORD is correct")
        print("3. You have IPv4 add-on OR use Session Pooler connection")
        return
    
    try:
        total_deleted = 0
        
        # Find archive tables first
        archive_tables = find_archive_tables(conn)
        
        # Deduplicate
        total_deleted += delete_duplicates_table_items(conn)
        total_deleted += delete_duplicates_products(conn)
        total_deleted += delete_duplicates_transactions(conn)
        
        print("\n" + "="*60)
        print(f"TOTAL DUPLICATES DELETED: {total_deleted}")
        print("="*60)
        
        if archive_tables:
            print("\n⚠️  ARCHIVE TABLES FOUND - Review and delete manually:")
            for schema, table, size, _ in archive_tables:
                print(f"  DROP TABLE IF EXISTS {schema}.{table} CASCADE;  -- {size}")
        
        print("\nNext steps:")
        print("1. Run VACUUM ANALYZE in Supabase SQL Editor")
        print("2. Check database size reduction")
        print("3. Add unique indexes to prevent future duplicates")
        
    finally:
        conn.close()
        print("\n[OK] Connection closed")

if __name__ == "__main__":
    main()

