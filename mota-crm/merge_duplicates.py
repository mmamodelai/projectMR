#!/usr/bin/env python3
"""
Duplicate Customer Merger
Merges duplicate customer records in customers_blaze table
Part of Conductor SMS System
"""

from supabase import create_client, Client
import time
import random

# Initialize Supabase
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def find_next_duplicate_group():
    """Find the next duplicate group to merge - searches specific names for duplicates"""
    print("\n🔍 Finding next duplicate group...")
    
    # New strategy: Get ALL first names, then check each one for duplicates
    # This ensures we find ALL duplicates across the entire database
    
    try:
        # Get 1000 customers randomly to find names to check
        result = sb.table('customers_blaze')\
            .select('first_name, last_name')\
            .not_.is_('first_name', 'null')\
            .not_.is_('last_name', 'null')\
            .limit(1000)\
            .execute()
        
        if not result.data:
            return None
        
        # Shuffle to check different people each time
        names = list(result.data)
        random.shuffle(names)
        
        print(f"   Checking {len(names)} names for duplicates...")
        
        # Check each name to see if there are duplicates
        for person in names:
            first = person['first_name']
            last = person['last_name']
            
            # Get ALL records with this exact name
            matches = sb.table('customers_blaze')\
                .select('member_id, first_name, last_name, date_of_birth, phone, email, total_visits')\
                .ilike('first_name', first)\
                .ilike('last_name', last)\
                .execute()
            
            # Group by exact match (case-insensitive) + DOB
            groups = {}
            for customer in matches.data:
                key = (
                    customer['first_name'].lower().strip(),
                    customer['last_name'].lower().strip(),
                    customer.get('date_of_birth', 'null')
                )
                
                if key not in groups:
                    groups[key] = []
                groups[key].append(customer)
            
            # Check if any group has duplicates
            for key, customers in groups.items():
                if len(customers) > 1:
                    print(f"✓ Found duplicate group: {key[0]} {key[1]} ({len(customers)} records)")
                    return customers
        
        # Checked 1000 random names, no duplicates found
        print("   No duplicates in this sample - database might be clean!")
        return None
        
    except Exception as e:
        print(f"   ⚠️  Error searching: {e}")
        return None

def score_customer(customer):
    """Score a customer record - higher is better"""
    score = 0
    
    # Phone is most valuable
    if customer.get('phone') and customer['phone'] != '':
        score += 1000
    
    # Email is next
    if customer.get('email') and customer['email'] != '':
        score += 500
    
    # Total visits
    score += (customer.get('total_visits') or 0) * 10
    
    return score

def merge_duplicate_group(customers):
    """Merge a group of duplicate customers"""
    
    # Sort by score - best first
    customers_sorted = sorted(customers, key=score_customer, reverse=True)
    
    keeper = customers_sorted[0]
    duplicates = customers_sorted[1:]
    
    print(f"\n📝 Merging Group:")
    print(f"   Keeper: {keeper['member_id']} (score: {score_customer(keeper)})")
    print(f"   Phone: {keeper.get('phone', 'N/A')}")
    print(f"   Email: {keeper.get('email', 'N/A')}")
    print(f"   Visits: {keeper.get('total_visits', 0)}")
    print(f"\n   Duplicates to merge: {len(duplicates)}")
    
    # Copy any missing data from duplicates to keeper
    update_data = {}
    
    for dupe in duplicates:
        print(f"   - Processing: {dupe['member_id']}")
        
        # Copy phone if keeper doesn't have one
        if (not keeper.get('phone') or keeper['phone'] == '') and dupe.get('phone'):
            update_data['phone'] = dupe['phone']
            print(f"     → Copying phone: {dupe['phone']}")
        
        # Copy email if keeper doesn't have one
        if (not keeper.get('email') or keeper['email'] == '') and dupe.get('email'):
            update_data['email'] = dupe['email']
            print(f"     → Copying email: {dupe['email']}")
        
        # Move transactions from duplicate to keeper
        print(f"     → Moving transactions...")
        tx_result = sb.table('transactions_blaze')\
            .update({'customer_id': keeper['member_id']})\
            .eq('customer_id', dupe['member_id'])\
            .execute()
        
        print(f"     → Moved {len(tx_result.data) if tx_result.data else 0} transactions")
        
        # Delete the duplicate
        print(f"     → Deleting duplicate...")
        sb.table('customers_blaze')\
            .delete()\
            .eq('member_id', dupe['member_id'])\
            .execute()
        
        print(f"     ✓ Deleted")
    
    # Update keeper with any missing data
    if update_data:
        print(f"\n   → Updating keeper with missing data...")
        sb.table('customers_blaze')\
            .update(update_data)\
            .eq('member_id', keeper['member_id'])\
            .execute()
    
    # Recalculate stats for keeper
    print(f"\n   → Recalculating stats for keeper...")
    
    # Get all completed transactions for this customer
    tx_result = sb.table('transactions_blaze')\
        .select('total_amount')\
        .eq('customer_id', keeper['member_id'])\
        .eq('blaze_status', 'Completed')\
        .execute()
    
    total_visits = len(tx_result.data)
    lifetime_value = sum(tx.get('total_amount', 0) for tx in tx_result.data)
    
    # Calculate VIP status
    if total_visits >= 16:
        vip_status = 'VIP'
    elif total_visits >= 11:
        vip_status = 'Regular2'
    elif total_visits >= 5:
        vip_status = 'Regular1'
    elif total_visits >= 2:
        vip_status = 'Casual'
    elif total_visits == 1:
        vip_status = 'First'
    else:
        vip_status = 'New'
    
    # Update keeper
    sb.table('customers_blaze')\
        .update({
            'total_visits': total_visits,
            'lifetime_value': lifetime_value,
            'vip_status': vip_status
        })\
        .eq('member_id', keeper['member_id'])\
        .execute()
    
    print(f"   ✓ Stats updated: {total_visits} visits, ${lifetime_value:.2f} lifetime, {vip_status}")
    print(f"\n✅ Merge complete! Deleted {len(duplicates)} duplicates")
    
    return len(duplicates)

def main():
    """Main merger loop"""
    print("=" * 60)
    print("🔧 Duplicate Customer Merger")
    print("=" * 60)
    
    total_deleted = 0
    groups_processed = 0
    
    while True:
        # Find next duplicate group
        duplicate_group = find_next_duplicate_group()
        
        if not duplicate_group:
            print("\n" + "=" * 60)
            print("🎉 NO MORE DUPLICATES FOUND!")
            print(f"✓ Processed {groups_processed} groups")
            print(f"✓ Deleted {total_deleted} duplicate records")
            print("=" * 60)
            break
        
        # Merge the group
        deleted = merge_duplicate_group(duplicate_group)
        total_deleted += deleted
        groups_processed += 1
        
        print(f"\n📊 Progress: {groups_processed} groups processed, {total_deleted} duplicates deleted")
        
        # Small delay to avoid rate limits
        time.sleep(0.5)
        
        # Progress update every 100 groups
        if groups_processed % 100 == 0:
            print(f"\n⏸️  Processed {groups_processed} groups so far...")
            print("   Press Ctrl+C to stop, or wait to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPress Enter to close...")

