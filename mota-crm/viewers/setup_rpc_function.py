#!/usr/bin/env python3
"""
Setup RPC Function for IC Viewer v5.5
Runs the HYBRID_SOLUTION SQL scripts in Supabase
"""

import os
import psycopg2
from psycopg2 import sql

# Supabase connection details
SUPABASE_HOST = "aws-0-us-west-1.pooler.supabase.com"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres.kiwmwoqrguyrcpjytgte"
SUPABASE_PASSWORD = "9YqTPhlCxytiXxnb"  # From your earlier message
SUPABASE_PORT = 6543

def run_sql_file(cursor, sql_content, description):
    """Run SQL and report results"""
    print(f"\n{'='*60}")
    print(f"RUNNING: {description}")
    print(f"{'='*60}")
    
    try:
        cursor.execute(sql_content)
        print(f"✓ SUCCESS: {description}")
        
        # Try to fetch results if any
        try:
            results = cursor.fetchall()
            if results:
                print(f"\nResults ({len(results)} rows):")
                for row in results[:10]:  # Show first 10
                    print(f"  {row}")
                if len(results) > 10:
                    print(f"  ... and {len(results) - 10} more rows")
        except:
            pass
            
        return True
    except Exception as e:
        print(f"✗ ERROR: {e}")
        return False

def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║  IC VIEWER v5.5 - RPC FUNCTION SETUP                         ║
║  This script will create the get_customers_fast() function   ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    # Step 1: Backfill SQL
    step1_sql = """
-- STEP 1: BACKFILL
UPDATE customers_blaze c
SET
    total_visits = COALESCE(trans_stats.visit_count, 0),
    lifetime_value = COALESCE(trans_stats.total_spent, 0),
    last_visited = trans_stats.most_recent_visit,
    vip_status = CASE
        WHEN COALESCE(trans_stats.visit_count, 0) >= 15 THEN 'VIP'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 6 THEN 'Regular'
        WHEN COALESCE(trans_stats.visit_count, 0) >= 2 THEN 'Casual'
        ELSE 'New'
    END,
    days_since_last_visit = CASE
        WHEN trans_stats.most_recent_visit IS NOT NULL 
        THEN EXTRACT(DAY FROM NOW() - trans_stats.most_recent_visit)::INTEGER
        ELSE NULL
    END,
    updated_at = NOW()
FROM (
    SELECT 
        customer_id,
        COUNT(DISTINCT transaction_id) as visit_count,
        SUM(total_amount) as total_spent,
        MAX(date::DATE) as most_recent_visit
    FROM transactions_blaze
    WHERE blaze_status = 'Completed'
    GROUP BY customer_id
) AS trans_stats
WHERE c.member_id = trans_stats.customer_id;

-- Also update customers with NO transactions
UPDATE customers_blaze
SET
    total_visits = 0,
    lifetime_value = 0,
    vip_status = 'New',
    updated_at = NOW()
WHERE total_visits IS NULL;
"""

    # Step 2: Create RPC Function
    step2_sql = """
-- STEP 2: CREATE FAST QUERY FUNCTION
CREATE OR REPLACE FUNCTION get_customers_fast(
    filter_email BOOLEAN DEFAULT FALSE,
    filter_phone BOOLEAN DEFAULT FALSE,
    days_cutoff INTEGER DEFAULT 365,
    search_term TEXT DEFAULT NULL
)
RETURNS TABLE (
    member_id TEXT,
    first_name TEXT,
    last_name TEXT,
    middle_name TEXT,
    date_of_birth DATE,
    phone TEXT,
    email TEXT,
    is_medical BOOLEAN,
    text_opt_in BOOLEAN,
    email_opt_in BOOLEAN,
    loyalty_points NUMERIC,
    total_visits INTEGER,
    lifetime_value NUMERIC,
    vip_status TEXT,
    last_visited DATE,
    days_since_last_visit INTEGER,
    city TEXT,
    state TEXT,
    zip_code TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.member_id,
        c.first_name,
        c.last_name,
        c.middle_name,
        c.date_of_birth,
        c.phone,
        c.email,
        c.is_medical,
        c.text_opt_in,
        c.email_opt_in,
        c.loyalty_points,
        c.total_visits,
        c.lifetime_value,
        c.vip_status,
        c.last_visited,
        c.days_since_last_visit,
        c.city,
        c.state,
        c.zip_code
    FROM customers_blaze c
    WHERE 
        -- Email filter
        (NOT filter_email OR (c.email IS NOT NULL AND c.email != ''))
        -- Phone filter
        AND (NOT filter_phone OR (c.phone IS NOT NULL AND c.phone != ''))
        -- Date filter
        AND (days_cutoff IS NULL OR c.last_visited >= CURRENT_DATE - (days_cutoff || ' days')::INTERVAL)
        -- Search filter
        AND (
            search_term IS NULL 
            OR LOWER(c.first_name) LIKE LOWER('%' || search_term || '%')
            OR LOWER(c.last_name) LIKE LOWER('%' || search_term || '%')
            OR LOWER(c.email) LIKE LOWER('%' || search_term || '%')
            OR c.phone LIKE '%' || search_term || '%'
        )
    ORDER BY c.last_visited DESC NULLS LAST, c.lifetime_value DESC;
END;
$$ LANGUAGE plpgsql STABLE;
"""

    # Verification query
    verify_sql = """
SELECT 
    COUNT(*) as total_customers,
    COUNT(CASE WHEN total_visits > 0 THEN 1 END) as with_visits,
    COUNT(CASE WHEN lifetime_value > 0 THEN 1 END) as with_lifetime,
    ROUND(AVG(NULLIF(total_visits, 0)), 2) as avg_visits,
    ROUND(AVG(NULLIF(lifetime_value, 0)), 2) as avg_lifetime_value
FROM customers_blaze;
"""

    # Connect to Supabase
    print("Connecting to Supabase...")
    try:
        conn = psycopg2.connect(
            host=SUPABASE_HOST,
            database=SUPABASE_DB,
            user=SUPABASE_USER,
            password=SUPABASE_PASSWORD,
            port=SUPABASE_PORT
        )
        conn.autocommit = False
        cursor = conn.cursor()
        print("✓ Connected!")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nCheck your credentials:")
        print(f"  Host: {SUPABASE_HOST}")
        print(f"  User: {SUPABASE_USER}")
        print(f"  Port: {SUPABASE_PORT}")
        return
    
    try:
        # Step 1: Backfill (takes time)
        print("\n⏳ STEP 1: Backfilling customer stats (this will take 10-15 minutes)...")
        if run_sql_file(cursor, step1_sql, "Backfill customer data"):
            conn.commit()
            print("\n✓ Backfill committed to database")
        else:
            print("\n✗ Backfill failed, rolling back...")
            conn.rollback()
            return
        
        # Step 2: Create function (instant)
        print("\n⏳ STEP 2: Creating RPC function (instant)...")
        if run_sql_file(cursor, step2_sql, "Create get_customers_fast function"):
            conn.commit()
            print("\n✓ Function created and committed")
        else:
            print("\n✗ Function creation failed, rolling back...")
            conn.rollback()
            return
        
        # Verify
        print("\n⏳ VERIFYING: Checking results...")
        run_sql_file(cursor, verify_sql, "Verify backfill results")
        
        print(f"\n{'='*60}")
        print("✓✓✓ SETUP COMPLETE! ✓✓✓")
        print(f"{'='*60}")
        print("\nYou can now:")
        print("  1. Close the IC Viewer")
        print("  2. Reopen it")
        print("  3. RPC error will be GONE!")
        print("\n🚀 FAST MODE ENABLED!")
        
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
        print("\n✓ Database connection closed")

if __name__ == "__main__":
    main()

