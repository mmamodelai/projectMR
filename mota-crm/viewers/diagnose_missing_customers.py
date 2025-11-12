#!/usr/bin/env python3
"""
Diagnose Missing Customers in Viewer
Find why specific customers aren't showing up
"""

from supabase import create_client, Client
from datetime import datetime, timedelta

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def diagnose():
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 80)
    print("DIAGNOSTIC: Missing Customer Investigation")
    print("=" * 80)
    
    # Search for Aaron Campos
    search_name = "Aaron Campos"
    print(f"\n1. Searching for '{search_name}'...")
    
    # Try variations
    results = []
    
    # Try first name + last name
    result1 = sb.table('customers_blaze').select('*').ilike('first_name', '%aaron%').ilike('last_name', '%campos%').execute()
    results.extend(result1.data)
    
    # Try just first name
    result2 = sb.table('customers_blaze').select('*').ilike('first_name', '%aaron%').execute()
    results.extend(result2.data)
    
    # Try just last name
    result3 = sb.table('customers_blaze').select('*').ilike('last_name', '%campos%').execute()
    results.extend(result3.data)
    
    # Deduplicate by member_id
    unique_results = {r['member_id']: r for r in results}.values()
    
    print(f"   Found {len(unique_results)} customer(s) matching 'Aaron' or 'Campos'\n")
    
    if not unique_results:
        print("NO CUSTOMERS FOUND matching 'Aaron Campos'")
        print("\nPossible reasons:")
        print("   - Name spelled differently in database")
        print("   - Customer doesn't exist in customers_blaze")
        print("   - Only in old 'customers' table (not migrated)")
        
        # Check old table
        print("\n2. Checking OLD customers table...")
        try:
            old_result = sb.table('customers').select('*').ilike('name', '%aaron%campos%').execute()
            if old_result.data:
                print(f"   Found {len(old_result.data)} in OLD 'customers' table!")
                for c in old_result.data:
                    print(f"      - {c.get('name')} | {c.get('phone')} | {c.get('email')}")
                print("\n   WARNING: This customer is in OLD database, not Blaze database!")
                print("   WARNING: Need to sync from Blaze API or wait for next sync")
        except:
            print("   (Old customers table not accessible)")
        
        return
    
    # Analyze each match
    for i, customer in enumerate(unique_results, 1):
        print(f"\n{'=' * 80}")
        print(f"CUSTOMER #{i}: {customer.get('first_name')} {customer.get('last_name')}")
        print(f"{'=' * 80}")
        
        member_id = customer.get('member_id')
        email = customer.get('email')
        phone = customer.get('phone')
        last_visited = customer.get('last_visited')
        
        print(f"\nBASIC INFO:")
        print(f"   Member ID: {member_id}")
        print(f"   Name: {customer.get('first_name')} {customer.get('middle_name', '')} {customer.get('last_name')}")
        print(f"   Email: {email or '[NO EMAIL]'}")
        print(f"   Phone: {phone or '[NO PHONE]'}")
        print(f"   Last Visited: {last_visited or '[NO VISIT DATE]'}")
        print(f"   Date Joined: {customer.get('date_joined')}")
        print(f"   Member Status: {customer.get('member_status')}")
        
        # Calculate visits
        trans_result = sb.table('transactions_blaze').select('*', count='exact').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
        visits = trans_result.count or 0
        lifetime = sum([t.get('total_amount', 0) or 0 for t in trans_result.data])
        
        print(f"\nSTATS:")
        print(f"   Total Visits: {visits}")
        print(f"   Lifetime Value: ${lifetime:.2f}")
        
        # Check filter criteria
        print(f"\nFILTER CHECK (Default Viewer Filters):")
        
        passes_email = email and email.strip() != ''
        passes_phone = phone and phone.strip() != ''
        
        print(f"   Has Email: {'PASS' if passes_email else 'FAIL'}")
        print(f"   Has Phone: {'PASS' if passes_phone else 'FAIL'}")
        
        if last_visited:
            try:
                last_visit_date = datetime.strptime(last_visited, '%Y-%m-%d')
                days_ago = (datetime.now() - last_visit_date).days
                passes_180 = days_ago <= 180
                
                print(f"   Last Visited: {last_visited} ({days_ago} days ago)")
                print(f"   Within 180 days: {'PASS' if passes_180 else 'FAIL'}")
            except:
                print(f"   Last Visited: {last_visited} (invalid format)")
                passes_180 = False
        else:
            print(f"   Last Visited: NULL - FAILS 180-day filter")
            passes_180 = False
        
        # Overall verdict
        print(f"\n{'=' * 80}")
        if passes_email and passes_phone and passes_180:
            print("VERDICT: SHOULD APPEAR IN VIEWER (all filters pass)")
            print("   If not showing, it's a pagination/loading bug")
        else:
            print("VERDICT: FILTERED OUT (doesn't meet criteria)")
            print(f"\n   Failing filters:")
            if not passes_email:
                print(f"      - No email address")
            if not passes_phone:
                print(f"      - No phone number")
            if not passes_180:
                print(f"      - Last visit > 180 days ago (or NULL)")
        print(f"{'=' * 80}")
    
    # Check pagination
    print(f"\n{'=' * 80}")
    print("3. PAGINATION CHECK")
    print(f"{'=' * 80}")
    
    cutoff_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    # Count total matching customers
    total_result = sb.table('customers_blaze').select('*', count='exact')\
        .neq('email', None).neq('email', '')\
        .neq('phone', None).neq('phone', '')\
        .gte('last_visited', cutoff_date)\
        .execute()
    
    total_count = total_result.count or 0
    
    print(f"\nTotal customers matching filters (Email + Phone + <180 days):")
    print(f"   {total_count} customers")
    
    if total_count > 1000:
        print(f"\n⚠️ WARNING: {total_count} customers > 1000")
        print("   Viewer uses pagination with 1000 records per page")
        print("   It should load ALL pages, but there might be a bug")
        
        # Test pagination
        print("\n   Testing pagination...")
        page1 = sb.table('customers_blaze').select('member_id', count='exact')\
            .neq('email', None).neq('email', '')\
            .neq('phone', None).neq('phone', '')\
            .gte('last_visited', cutoff_date)\
            .order('last_name')\
            .range(0, 999)\
            .execute()
        
        page2 = sb.table('customers_blaze').select('member_id', count='exact')\
            .neq('email', None).neq('email', '')\
            .neq('phone', None).neq('phone', '')\
            .gte('last_visited', cutoff_date)\
            .order('last_name')\
            .range(1000, 1999)\
            .execute()
        
        print(f"   Page 1 (0-999): {len(page1.data)} records")
        print(f"   Page 2 (1000-1999): {len(page2.data)} records")
        
        # Check if Aaron is in later pages
        all_member_ids = set([c['member_id'] for c in unique_results])
        page1_ids = set([c['member_id'] for c in page1.data])
        page2_ids = set([c['member_id'] for c in page2.data])
        
        for customer in unique_results:
            mid = customer['member_id']
            if mid in page1_ids:
                print(f"   ✅ Aaron Campos (or match) found in PAGE 1")
            elif mid in page2_ids:
                print(f"   ⚠️ Aaron Campos (or match) found in PAGE 2")
                print(f"      Viewer might be stopping after page 1!")
            else:
                print(f"   ❓ Aaron Campos not in first 2000 records")
                print(f"      Might be on later page")
    else:
        print(f"\n✅ Total customers ({total_count}) fits in single page")
        print("   No pagination issues expected")
    
    print(f"\n{'=' * 80}")
    print("4. RECOMMENDATIONS")
    print(f"{'=' * 80}")
    
    print("\nIf customer is MISSING but PASSES filters:")
    print("   1. Check viewer's page_size (currently 1000)")
    print("   2. Verify viewer's while loop loads ALL pages")
    print("   3. Check if viewer stops early on error")
    print("   4. Try increasing page_size to 5000 or 10000")
    
    print("\nIf customer FAILS filters:")
    print("   1. Update their contact info in Blaze")
    print("   2. Wait for next sync (or trigger manual sync)")
    print("   3. Or disable relevant filters in viewer")
    
    print("\nIf customer only in OLD database:")
    print("   1. Check if Blaze sync is running")
    print("   2. Run manual sync from blaze-api-sync/")
    print("   3. Check sync_status in blaze_sync_state table")

if __name__ == "__main__":
    diagnose()

