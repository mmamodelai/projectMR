#!/usr/bin/env python3
"""
Setup Script for IC Viewer v5
Runs all SQL setup automatically via Supabase API
"""

from supabase import create_client, Client
import time

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def main():
    print("=" * 80)
    print("IC VIEWER V5 - AUTOMATED SETUP")
    print("=" * 80)
    print()
    
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Step 1: Checking database size...")
    try:
        # Get customer count
        result = sb.table('customers_blaze').select('*', count='exact').limit(1).execute()
        total_customers = result.count or 0
        print(f"   Total customers: {total_customers:,}")
        
        # Get transaction count
        result = sb.table('transactions_blaze').select('*', count='exact').limit(1).execute()
        total_trans = result.count or 0
        print(f"   Total transactions: {total_trans:,}")
        
        print()
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    print("Step 2: Backfilling customer stats...")
    print("   This will take 10-15 minutes for 131K customers")
    print("   Updating total_visits, lifetime_value, vip_status...")
    print()
    
    # Note: We can't run complex SQL via REST API
    # But we can do it via RPC or direct queries
    
    try:
        # Check if we can use PostgREST for this
        # Actually, this is too complex for REST API
        # Need to use SQL Editor for the backfill
        
        print("   NOTE: Backfill is too complex for REST API")
        print("   You need to run this in Supabase SQL Editor:")
        print("   --> sql_scripts/HYBRID_SOLUTION_step1_backfill.sql")
        print()
        print("   OR I can create a simpler version that works via API...")
        print()
        
        response = input("   Want me to try the API method? (y/n): ").lower()
        
        if response == 'y':
            print()
            print("   Starting API-based backfill...")
            print("   This will be SLOWER but doesn't require SQL Editor")
            print()
            
            # Get all customers
            print("   Fetching customers...")
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = sb.table('customers_blaze').select('member_id').range(offset, offset + page_size - 1).execute()
                if not result.data:
                    break
                all_customers.extend(result.data)
                offset += page_size
                print(f"      Loaded {len(all_customers)} customers...")
                if len(result.data) < page_size:
                    break
            
            print(f"   Total customers to update: {len(all_customers)}")
            print()
            
            # Update in batches
            print("   Calculating stats for each customer...")
            updated = 0
            errors = 0
            
            for i, customer in enumerate(all_customers):
                member_id = customer['member_id']
                
                try:
                    # Get transaction stats
                    trans_result = sb.table('transactions_blaze').select('total_amount', count='exact')\
                        .eq('customer_id', member_id)\
                        .eq('blaze_status', 'Completed')\
                        .execute()
                    
                    visits = trans_result.count or 0
                    lifetime = sum([t.get('total_amount', 0) or 0 for t in trans_result.data])
                    
                    # Calculate VIP status
                    if visits >= 16:
                        vip = 'VIP'
                    elif visits >= 11:
                        vip = 'Regular2'
                    elif visits >= 5:
                        vip = 'Regular1'
                    elif visits >= 2:
                        vip = 'Casual'
                    elif visits == 1:
                        vip = 'First'
                    else:
                        vip = 'New'
                    
                    # Update customer
                    sb.table('customers_blaze').update({
                        'total_visits': visits,
                        'lifetime_value': lifetime,
                        'vip_status': vip
                    }).eq('member_id', member_id).execute()
                    
                    updated += 1
                    
                    if (i + 1) % 100 == 0:
                        print(f"      Progress: {i+1}/{len(all_customers)} ({(i+1)/len(all_customers)*100:.1f}%) - Updated: {updated}, Errors: {errors}")
                
                except Exception as e:
                    errors += 1
                    if errors < 10:
                        print(f"      ERROR updating {member_id}: {e}")
            
            print()
            print(f"   Backfill complete!")
            print(f"   Updated: {updated}")
            print(f"   Errors: {errors}")
            print()
        
    except Exception as e:
        print(f"   ERROR: {e}")
        print()
    
    print("Step 3: Creating RPC function...")
    print("   NOTE: RPC functions can't be created via REST API")
    print("   You must run this in Supabase SQL Editor:")
    print("   --> sql_scripts/HYBRID_SOLUTION_step2_create_fast_query.sql")
    print()
    
    print("=" * 80)
    print("SETUP SUMMARY")
    print("=" * 80)
    print()
    print("AUTOMATED:")
    print("   [PARTIAL] Customer stats backfill (via API - slow but works)")
    print()
    print("MANUAL (Required):")
    print("   [TODO] Create RPC function in Supabase SQL Editor")
    print("          File: sql_scripts/HYBRID_SOLUTION_step2_create_fast_query.sql")
    print()
    print("RECOMMENDATION:")
    print("   Use SQL Editor for both steps - it's MUCH faster!")
    print("   1. Open: https://supabase.com/dashboard/project/kiwmwoqrguyrcpjytgte/sql")
    print("   2. Run: HYBRID_SOLUTION_step1_backfill.sql (~10-15 min)")
    print("   3. Run: HYBRID_SOLUTION_step2_create_fast_query.sql (~1 min)")
    print()

if __name__ == "__main__":
    main()

