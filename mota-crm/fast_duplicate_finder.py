#!/usr/bin/env python3
"""
Fast Duplicate Finder - SQL Based
Part of Conductor SMS System

Uses direct SQL queries for speed - no hanging!
"""

import csv
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def find_duplicates_fast():
    """Find duplicates using fast SQL queries"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Running fast SQL-based duplicate detection...")
    
    all_results = []
    
    # 1. Phone duplicates
    print("Finding phone duplicates...")
    try:
        result = sb.table('customers').select('member_id,name,phone,email,lifetime_value,total_visits').not_.is_('phone', 'null').execute()
        
        phone_groups = {}
        for customer in result.data:
            phone = ''.join(filter(str.isdigit, str(customer.get('phone', ''))))
            if phone and len(phone) >= 10:
                if phone not in phone_groups:
                    phone_groups[phone] = []
                phone_groups[phone].append(customer)
        
        for phone, customers in phone_groups.items():
            if len(customers) > 1:
                all_results.append({
                    'type': 'phone',
                    'match': phone,
                    'count': len(customers),
                    'customers': customers
                })
        
        print(f"Found {len([r for r in all_results if r['type'] == 'phone'])} phone duplicate groups")
        
    except Exception as e:
        print(f"Error with phone duplicates: {e}")
    
    # 2. Exact name duplicates
    print("Finding exact name duplicates...")
    try:
        result = sb.table('customers').select('member_id,name,phone,email,lifetime_value,total_visits').not_.is_('name', 'null').execute()
        
        name_groups = {}
        for customer in result.data:
            name = str(customer.get('name', '')).lower().strip()
            if name:
                if name not in name_groups:
                    name_groups[name] = []
                name_groups[name].append(customer)
        
        for name, customers in name_groups.items():
            if len(customers) > 1:
                all_results.append({
                    'type': 'name_exact',
                    'match': name,
                    'count': len(customers),
                    'customers': customers
                })
        
        print(f"Found {len([r for r in all_results if r['type'] == 'name_exact'])} exact name duplicate groups")
        
    except Exception as e:
        print(f"Error with name duplicates: {e}")
    
    # 3. Email duplicates
    print("Finding email duplicates...")
    try:
        result = sb.table('customers').select('member_id,name,phone,email,lifetime_value,total_visits').not_.is_('email', 'null').execute()
        
        email_groups = {}
        for customer in result.data:
            email = str(customer.get('email', '')).lower().strip()
            if email and '@' in email:
                if email not in email_groups:
                    email_groups[email] = []
                email_groups[email].append(customer)
        
        for email, customers in email_groups.items():
            if len(customers) > 1:
                all_results.append({
                    'type': 'email',
                    'match': email,
                    'count': len(customers),
                    'customers': customers
                })
        
        print(f"Found {len([r for r in all_results if r['type'] == 'email'])} email duplicate groups")
        
    except Exception as e:
        print(f"Error with email duplicates: {e}")
    
    return all_results

def export_fast_report(results, filename=None):
    """Export results to CSV quickly"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"fast_duplicates_{timestamp}.csv"
    
    print(f"Creating report: {filename}")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Type',
            'Match_Value',
            'Count',
            'Total_Value',
            'Max_Value',
            'Customer_1_ID',
            'Customer_1_Name',
            'Customer_1_Phone',
            'Customer_1_Email',
            'Customer_1_Lifetime_Value',
            'Customer_2_ID',
            'Customer_2_Name',
            'Customer_2_Phone',
            'Customer_2_Email',
            'Customer_2_Lifetime_Value',
            'Customer_3_ID',
            'Customer_3_Name',
            'Customer_3_Phone',
            'Customer_3_Email',
            'Customer_3_Lifetime_Value',
            'Recommendation'
        ])
        
        # Sort by count (highest first)
        results.sort(key=lambda x: x['count'], reverse=True)
        
        for result in results:
            customers = result['customers']
            total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
            max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
            
            # Determine recommendation
            if result['type'] == 'phone':
                if total_value < 100:
                    recommendation = 'MERGE_LOW_VALUE'
                elif max_value > 1000:
                    recommendation = 'REVIEW_HIGH_VALUE'
                else:
                    recommendation = 'MERGE_MEDIUM_VALUE'
            elif result['type'] == 'email':
                recommendation = 'MERGE_HIGH_CONFIDENCE'
            else:  # name_exact
                if total_value < 100:
                    recommendation = 'MERGE_LOW_VALUE'
                elif max_value > 1000:
                    recommendation = 'REVIEW_HIGH_VALUE'
                else:
                    recommendation = 'MERGE_MEDIUM_VALUE'
            
            # Create row
            row = [
                result['type'],
                result['match'],
                result['count'],
                total_value,
                max_value
            ]
            
            # Add customer data (up to 3)
            for i in range(3):
                if i < len(customers):
                    customer = customers[i]
                    row.extend([
                        customer.get('member_id', ''),
                        customer.get('name', ''),
                        customer.get('phone', ''),
                        customer.get('email', ''),
                        customer.get('lifetime_value', 0)
                    ])
                else:
                    row.extend(['', '', '', '', ''])
            
            row.append(recommendation)
            writer.writerow(row)
    
    print(f"Report saved to: {filename}")
    return filename

def main():
    """Main function"""
    print("Fast Duplicate Finder - No Hanging!")
    print("="*40)
    
    try:
        # Find duplicates quickly
        results = find_duplicates_fast()
        
        # Export report
        filename = export_fast_report(results)
        
        print(f"\nSUCCESS!")
        print(f"Total duplicate groups found: {len(results)}")
        print(f"Report saved to: {filename}")
        
        # Show summary
        type_counts = {}
        for result in results:
            dup_type = result['type']
            type_counts[dup_type] = type_counts.get(dup_type, 0) + 1
        
        print(f"\nSummary:")
        for dup_type, count in type_counts.items():
            print(f"  {dup_type}: {count} groups")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
