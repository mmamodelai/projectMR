#!/usr/bin/env python3
"""
Clean Duplicate Report Generator
Part of Conductor SMS System

Creates CSV without emoji characters for Windows compatibility
"""

import csv
import re
from datetime import datetime
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def normalize_phone(phone):
    """Normalize phone number"""
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, str(phone)))

def is_fake_number(phone):
    """Detect fake/test phone numbers"""
    if not phone:
        return False
    
    digits = normalize_phone(phone)
    
    # Common fake number patterns
    fake_patterns = [
        r'^1?(\d)\1{9}$',  # All same digit (1111111111)
        r'^1?1234567890$',  # Sequential
        r'^1?0987654321$',  # Reverse sequential
        r'^1?(\d{3})\1{2}$',  # Repeated 3-digit groups
        r'^1?0000000000$',  # All zeros
        r'^1?1111111111$',  # All ones
        r'^1?2222222222$',  # All twos
        r'^1?3333333333$',  # All threes
        r'^1?4444444444$',  # All fours
        r'^1?5555555555$',  # All fives
        r'^1?6666666666$',  # All sixes
        r'^1?7777777777$',  # All sevens
        r'^1?8888888888$',  # All eights
        r'^1?9999999999$',  # All nines
    ]
    
    for pattern in fake_patterns:
        if re.match(pattern, digits):
            return True
    
    # Check for obvious test numbers
    test_numbers = [
        '13230000000',  # The one you found
        '1234567890',
        '0987654321',
        '1111111111',
        '2222222222',
        '3333333333',
        '4444444444',
        '5555555555',
        '6666666666',
        '7777777777',
        '8888888888',
        '9999999999',
        '0000000000',
    ]
    
    return digits in test_numbers

def analyze_and_export():
    """Analyze duplicates and export to CSV"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Analyzing customer database for duplicates and fake numbers...")
    
    phone_groups = {}
    batch_size = 500
    offset = 0
    
    while True:
        print(f"Processing batch {offset//batch_size + 1}...")
        
        try:
            result = sb.table('customers').select('member_id,name,phone,email,lifetime_value,total_visits').range(offset, offset + batch_size - 1).execute()
            
            if not result.data:
                break
            
            for customer in result.data:
                phone = normalize_phone(customer.get('phone', ''))
                if phone and len(phone) >= 10:
                    if phone not in phone_groups:
                        phone_groups[phone] = []
                    phone_groups[phone].append(customer)
            
            offset += batch_size
            
            if len(result.data) < batch_size:
                break
                
        except Exception as e:
            print(f"Error processing batch: {e}")
            break
    
    # Create CSV filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"duplicate_analysis_{timestamp}.csv"
    
    print(f"Creating CSV report: {filename}")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Category',
            'Phone_Number',
            'Customer_Count',
            'Total_Lifetime_Value',
            'Max_Lifetime_Value',
            'Recommendation',
            'Customer_1_ID',
            'Customer_1_Name',
            'Customer_1_Phone',
            'Customer_1_Email',
            'Customer_1_Lifetime_Value',
            'Customer_1_Visits',
            'Customer_2_ID',
            'Customer_2_Name',
            'Customer_2_Phone',
            'Customer_2_Email',
            'Customer_2_Lifetime_Value',
            'Customer_2_Visits',
            'Customer_3_ID',
            'Customer_3_Name',
            'Customer_3_Phone',
            'Customer_3_Email',
            'Customer_3_Lifetime_Value',
            'Customer_3_Visits',
            'Notes'
        ])
        
        # Process groups
        real_duplicates = 0
        fake_duplicates = 0
        single_fake_numbers = 0
        
        for phone, customers in phone_groups.items():
            if len(customers) > 1:  # Duplicates
                total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
                max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
                
                if is_fake_number(phone):
                    # Fake number duplicates
                    fake_duplicates += 1
                    category = 'FAKE_DUPLICATE'
                    recommendation = 'DELETE_ALL'
                    notes = 'DELETE ALL - Fake phone number'
                else:
                    # Real duplicates
                    real_duplicates += 1
                    category = 'REAL_DUPLICATE'
                    
                    if total_value < 100:
                        recommendation = 'MERGE_LOW_VALUE'
                        notes = 'Safe to merge - low value customers'
                    elif max_value > 1000:
                        recommendation = 'REVIEW_HIGH_VALUE'
                        notes = 'Review carefully - high value customers'
                    else:
                        recommendation = 'MERGE_MEDIUM_VALUE'
                        notes = 'Medium value - review before merging'
                
                # Create row
                row = [
                    category,
                    phone,
                    len(customers),
                    total_value,
                    max_value,
                    recommendation
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
                            customer.get('lifetime_value', 0),
                            customer.get('total_visits', 0)
                        ])
                    else:
                        row.extend(['', '', '', '', '', ''])
                
                row.append(notes)
                writer.writerow(row)
            
            elif len(customers) == 1 and is_fake_number(phone):
                # Single fake numbers
                single_fake_numbers += 1
                customer = customers[0]
                
                row = [
                    'FAKE_SINGLE',
                    phone,
                    1,
                    float(customer.get('lifetime_value', 0)),
                    '',
                    'DELETE',
                    customer.get('member_id', ''),
                    customer.get('name', ''),
                    customer.get('phone', ''),
                    customer.get('email', ''),
                    customer.get('lifetime_value', 0),
                    customer.get('total_visits', 0)
                ]
                
                # Fill remaining columns
                row.extend(['', '', '', '', '', '', '', '', '', '', ''])
                row.append('DELETE - Fake phone number')
                writer.writerow(row)
    
    print(f"\nAnalysis complete!")
    print(f"Real duplicates: {real_duplicates} groups")
    print(f"Fake duplicates: {fake_duplicates} groups")
    print(f"Single fake numbers: {single_fake_numbers} customers")
    print(f"Report saved to: {filename}")
    
    return filename

def main():
    """Main function"""
    print("Clean Duplicate Report Generator")
    print("="*40)
    
    try:
        filename = analyze_and_export()
        print(f"\nSUCCESS: Report created at {filename}")
        print(f"\nNext steps:")
        print(f"1. Open {filename} in Excel/Google Sheets")
        print(f"2. Sort by 'Recommendation' column")
        print(f"3. DELETE all fake number accounts first")
        print(f"4. MERGE low-value real duplicates")
        print(f"5. REVIEW high-value duplicates carefully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
