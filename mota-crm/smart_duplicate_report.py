#!/usr/bin/env python3
"""
Smart Duplicate & Fake Number Detector
Part of Conductor SMS System

Detects:
- Real phone duplicates
- Fake/test phone numbers
- Provides merge recommendations
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
        r'^1?(\d)\1{2}(\d)\2{2}(\d)\3{2}$',  # Pattern like 111222333
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

def get_phone_type(phone):
    """Determine phone number type"""
    if not phone:
        return "NO_PHONE"
    
    digits = normalize_phone(phone)
    
    if is_fake_number(phone):
        return "FAKE"
    elif len(digits) == 10:
        return "US_10_DIGIT"
    elif len(digits) == 11 and digits.startswith('1'):
        return "US_11_DIGIT"
    else:
        return "INVALID_FORMAT"

def analyze_duplicates():
    """Find and analyze duplicates"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Analyzing customer database...")
    
    phone_groups = {}
    batch_size = 500
    offset = 0
    
    while True:
        print(f"   Processing batch {offset//batch_size + 1}...")
        
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
            print(f"   Error processing batch: {e}")
            break
    
    # Analyze groups
    real_duplicates = []
    fake_numbers = []
    single_fake_numbers = []
    
    for phone, customers in phone_groups.items():
        phone_type = get_phone_type(phone)
        
        if phone_type == "FAKE":
            if len(customers) > 1:
                fake_numbers.append({
                    'phone': phone,
                    'type': 'FAKE_DUPLICATE',
                    'count': len(customers),
                    'customers': customers,
                    'total_value': sum(float(c.get('lifetime_value', 0)) for c in customers),
                    'recommendation': 'DELETE_ALL'
                })
            else:
                single_fake_numbers.append({
                    'phone': phone,
                    'type': 'FAKE_SINGLE',
                    'customer': customers[0],
                    'value': float(customers[0].get('lifetime_value', 0)),
                    'recommendation': 'DELETE'
                })
        elif len(customers) > 1:
            # Real duplicate
            total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
            max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
            
            # Determine merge recommendation
            if total_value < 100:  # Low value customers
                recommendation = 'MERGE_LOW_VALUE'
            elif max_value > 1000:  # High value customers
                recommendation = 'REVIEW_HIGH_VALUE'
            else:
                recommendation = 'MERGE_MEDIUM_VALUE'
            
            real_duplicates.append({
                'phone': phone,
                'type': 'REAL_DUPLICATE',
                'count': len(customers),
                'customers': customers,
                'total_value': total_value,
                'max_value': max_value,
                'recommendation': recommendation
            })
    
    return real_duplicates, fake_numbers, single_fake_numbers

def export_report(real_duplicates, fake_numbers, single_fake_numbers, filename=None):
    """Export comprehensive report"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"smart_duplicate_report_{timestamp}.csv"
    
    print(f"Exporting report to {filename}...")
    
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
        
        # Real duplicates
        for dup in real_duplicates:
            customers = dup['customers']
            
            row = [
                'REAL_DUPLICATE',
                dup['phone'],
                dup['count'],
                dup['total_value'],
                dup['max_value'],
                dup['recommendation']
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
            
            # Notes
            if dup['recommendation'] == 'MERGE_LOW_VALUE':
                notes = 'Safe to merge - low value customers'
            elif dup['recommendation'] == 'REVIEW_HIGH_VALUE':
                notes = 'Review carefully - high value customers'
            else:
                notes = 'Medium value - review before merging'
            
            row.append(notes)
            writer.writerow(row)
        
        # Fake number duplicates
        for fake in fake_numbers:
            customers = fake['customers']
            
            row = [
                'FAKE_DUPLICATE',
                fake['phone'],
                fake['count'],
                fake['total_value'],
                '',
                fake['recommendation']
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
            
            row.append('DELETE ALL - Fake phone number')
            writer.writerow(row)
        
        # Single fake numbers
        for fake in single_fake_numbers:
            customer = fake['customer']
            
            row = [
                'FAKE_SINGLE',
                fake['phone'],
                1,
                fake['value'],
                '',
                fake['recommendation'],
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
    
    print(f"Report exported to {filename}")
    return filename

def print_summary(real_duplicates, fake_numbers, single_fake_numbers):
    """Print summary"""
    print("\n" + "="*80)
    print("SMART DUPLICATE & FAKE NUMBER ANALYSIS")
    print("="*80)
    
    print(f"Real phone duplicates: {len(real_duplicates)} groups")
    print(f"Fake number duplicates: {len(fake_numbers)} groups")
    print(f"Single fake numbers: {len(single_fake_numbers)} customers")
    
    # Real duplicates summary
    if real_duplicates:
        print(f"\nREAL DUPLICATES ({len(real_duplicates)} groups):")
        for i, dup in enumerate(real_duplicates[:5], 1):
            print(f"\n{i}. Phone: {dup['phone']}")
            print(f"   Count: {dup['count']} customers")
            print(f"   Total Value: ${dup['total_value']:.2f}")
            print(f"   Max Value: ${dup['max_value']:.2f}")
            print(f"   Recommendation: {dup['recommendation']}")
            
            for j, customer in enumerate(dup['customers'][:3], 1):
                print(f"   Customer {j}: {customer.get('name', 'N/A')} (${customer.get('lifetime_value', 0):.2f})")
    
    # Fake numbers summary
    if fake_numbers:
        print(f"\nFAKE NUMBER DUPLICATES ({len(fake_numbers)} groups):")
        for i, fake in enumerate(fake_numbers[:5], 1):
            print(f"\n{i}. Phone: {fake['phone']} (FAKE)")
            print(f"   Count: {fake['count']} customers")
            print(f"   Total Value: ${fake['total_value']:.2f}")
            print(f"   Recommendation: DELETE ALL")
            
            for j, customer in enumerate(fake['customers'][:3], 1):
                print(f"   Customer {j}: {customer.get('name', 'N/A')} (${customer.get('lifetime_value', 0):.2f})")
    
    if single_fake_numbers:
        print(f"\nSINGLE FAKE NUMBERS ({len(single_fake_numbers)} customers):")
        for i, fake in enumerate(single_fake_numbers[:5], 1):
            customer = fake['customer']
            print(f"{i}. {customer.get('name', 'N/A')} - {fake['phone']} (${fake['value']:.2f})")

def main():
    """Main function"""
    print("Smart Duplicate & Fake Number Detector")
    print("="*50)
    
    try:
        # Analyze duplicates
        real_duplicates, fake_numbers, single_fake_numbers = analyze_duplicates()
        
        # Print summary
        print_summary(real_duplicates, fake_numbers, single_fake_numbers)
        
        # Export report
        csv_file = export_report(real_duplicates, fake_numbers, single_fake_numbers)
        
        print(f"\nAnalysis complete!")
        print(f"Report saved to: {csv_file}")
        print(f"\nNext steps:")
        print(f"1. DELETE all fake number accounts first")
        print(f"2. MERGE low-value real duplicates")
        print(f"3. REVIEW high-value duplicates carefully")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
