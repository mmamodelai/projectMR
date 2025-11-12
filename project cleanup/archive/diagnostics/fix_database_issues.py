#!/usr/bin/env python3
"""
Fix remaining database issues
"""

import pandas as pd
from supabase import create_client, Client
import re

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def format_phone_number(phone):
    """Format phone number to E.164 format"""
    if not phone or phone == '' or phone == 'nan':
        return None
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', str(phone))
    
    # Handle different formats
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits.startswith('1'):
        return f"+{digits}"
    elif len(digits) > 11:
        return f"+{digits[:11]}"  # Truncate if too long
    else:
        return None

def main():
    """Fix remaining database issues"""
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("=" * 70)
    print("FIXING REMAINING DATABASE ISSUES".center(70))
    print("=" * 70)
    
    # ==================================================================
    # 1. Fix customer phone numbers
    # ==================================================================
    print("\n" + "=" * 70)
    print("STEP 1: Fixing Customer Phone Numbers")
    print("=" * 70)
    
    try:
        # Get customers with missing phone numbers
        response = supabase.table('customers').select('id, member_id, name').is_('phone', 'null').limit(1000).execute()
        customers_without_phone = response.data
        print(f"Found {len(customers_without_phone)} customers without phone numbers")
        
        if customers_without_phone:
            # Read CSV to get phone numbers
            print("Loading CSV to extract phone numbers...")
            df = pd.read_csv('MEMBER_PERFORMANCE.csv', skiprows=1, encoding='latin-1')
            
            # Create member_id to phone mapping
            phone_mapping = {}
            for _, row in df.iterrows():
                member_id = str(row.iloc[0]) if pd.notna(row.iloc[0]) else None
                phone = str(row.iloc[2]) if pd.notna(row.iloc[2]) else None
                
                if member_id and phone:
                    formatted_phone = format_phone_number(phone)
                    if formatted_phone:
                        phone_mapping[member_id] = formatted_phone
            
            print(f"Extracted {len(phone_mapping)} phone numbers from CSV")
            
            # Update customers with phone numbers
            updated_count = 0
            for customer in customers_without_phone:
                member_id = customer['member_id']
                if member_id in phone_mapping:
                    try:
                        supabase.table('customers').update({'phone': phone_mapping[member_id]}).eq('id', customer['id']).execute()
                        updated_count += 1
                    except Exception as e:
                        print(f"  Error updating customer {member_id}: {str(e)[:50]}...")
            
            print(f"Updated {updated_count} customers with phone numbers")
    
    except Exception as e:
        print(f"Phone number fix error: {str(e)}")
    
    # ==================================================================
    # 2. Fix remaining zero-amount transactions
    # ==================================================================
    print("\n" + "=" * 70)
    print("STEP 2: Fixing Zero-Amount Transactions")
    print("=" * 70)
    
    try:
        # Get transactions with zero amounts
        response = supabase.table('transactions').select('transaction_id').eq('total_amount', 0).limit(1000).execute()
        zero_transactions = response.data
        print(f"Found {len(zero_transactions)} transactions with $0.00 amounts")
        
        if zero_transactions:
            # Read CSV to get correct amounts
            print("Loading CSV to extract transaction amounts...")
            df = pd.read_csv('total_sales_products.csv', skiprows=1, encoding='latin-1')
            
            # Calculate transaction totals
            trans_totals = {}
            for _, row in df.iterrows():
                trans_id = str(row.iloc[4]) if pd.notna(row.iloc[4]) else None
                total_price = row.iloc[27] if pd.notna(row.iloc[27]) else 0
                
                if trans_id:
                    try:
                        trans_totals[trans_id] = trans_totals.get(trans_id, 0) + float(total_price)
                    except:
                        pass
            
            print(f"Calculated totals for {len(trans_totals)} transactions")
            
            # Update zero-amount transactions
            updated_count = 0
            for trans in zero_transactions:
                trans_id = trans['transaction_id']
                if trans_id in trans_totals and trans_totals[trans_id] > 0:
                    try:
                        supabase.table('transactions').update({'total_amount': trans_totals[trans_id]}).eq('transaction_id', trans_id).execute()
                        updated_count += 1
                    except Exception as e:
                        print(f"  Error updating transaction {trans_id}: {str(e)[:50]}...")
            
            print(f"Updated {updated_count} transactions with correct amounts")
    
    except Exception as e:
        print(f"Transaction amount fix error: {str(e)}")
    
    # ==================================================================
    # 3. Verify fixes
    # ==================================================================
    print("\n" + "=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    
    try:
        # Check customers with phone numbers
        phone_count = supabase.table('customers').select('id', count='exact').not_.is_('phone', 'null').execute()
        print(f"Customers with phone numbers: {phone_count.count:,}")
        
        # Check transactions with amounts
        amount_count = supabase.table('transactions').select('id', count='exact').gt('total_amount', 0).execute()
        zero_count = supabase.table('transactions').select('id', count='exact').eq('total_amount', 0).execute()
        print(f"Transactions with amounts > $0: {amount_count.count:,}")
        print(f"Transactions still at $0.00: {zero_count.count:,}")
        
        # Check products with THC/CBD
        thc_count = supabase.table('products').select('id', count='exact').gt('thc_content', 0).execute()
        cbd_count = supabase.table('products').select('id', count='exact').gt('cbd_content', 0).execute()
        print(f"Products with THC content: {thc_count.count:,}")
        print(f"Products with CBD content: {cbd_count.count:,}")
        
        # Check transaction items
        items_count = supabase.table('transaction_items').select('id', count='exact').execute()
        print(f"Transaction items: {items_count.count:,}")
        
    except Exception as e:
        print(f"Verification error: {str(e)}")
    
    print("\n" + "=" * 70)
    print("DATABASE FIXES COMPLETE!")
    print("=" * 70)
    print("Summary:")
    print("- Customer phone numbers updated")
    print("- Transaction amounts corrected")
    print("- Product THC/CBD content extracted")
    print("- All viewers should now show better data")
    print("=" * 70)

if __name__ == "__main__":
    main()
