#!/usr/bin/env python3
"""
Complete Duplicate Finder - ALL Types
Part of Conductor SMS System

Finds ALL duplicates:
- Phone duplicates
- Name duplicates (fuzzy matching)
- Email duplicates
- Fake numbers
"""

import csv
import re
from datetime import datetime
from difflib import SequenceMatcher
from supabase import create_client, Client

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def normalize_phone(phone):
    """Normalize phone number"""
    if not phone:
        return ""
    return ''.join(filter(str.isdigit, str(phone)))

def normalize_name(name):
    """Normalize name for comparison"""
    if not name:
        return ""
    
    # Convert to lowercase, remove extra spaces
    normalized = ' '.join(str(name).lower().split())
    
    # Remove common suffixes/prefixes
    suffixes = ['jr', 'sr', 'ii', 'iii', 'iv', 'v']
    for suffix in suffixes:
        if normalized.endswith(f' {suffix}'):
            normalized = normalized[:-len(f' {suffix}')]
    
    return normalized

def name_similarity(name1, name2):
    """Calculate similarity between two names"""
    if not name1 or not name2:
        return 0
    
    norm1 = normalize_name(name1)
    norm2 = normalize_name(name2)
    
    return SequenceMatcher(None, norm1, norm2).ratio()

def is_fake_number(phone):
    """Detect fake/test phone numbers"""
    if not phone:
        return False
    
    digits = normalize_phone(phone)
    
    # Common fake number patterns
    fake_patterns = [
        r'^1?(\d)\1{9}$',  # All same digit
        r'^1?1234567890$',  # Sequential
        r'^1?0987654321$',  # Reverse sequential
        r'^1?(\d{3})\1{2}$',  # Repeated 3-digit groups
    ]
    
    for pattern in fake_patterns:
        if re.match(pattern, digits):
            return True
    
    # Check for obvious test numbers
    test_numbers = [
        '13230000000', '1234567890', '0987654321',
        '1111111111', '2222222222', '3333333333',
        '4444444444', '5555555555', '6666666666',
        '7777777777', '8888888888', '9999999999',
        '0000000000', '17777777777', '13333333333',
        '16666666666', '15551555255', '13234561212'
    ]
    
    return digits in test_numbers

def find_all_duplicates():
    """Find all types of duplicates"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Loading ALL customers for complete analysis...")
    
    # Load all customers
    all_customers = []
    batch_size = 500
    offset = 0
    
    while True:
        print(f"Loading batch {offset//batch_size + 1}...")
        
        try:
            result = sb.table('customers').select('member_id,name,phone,email,lifetime_value,total_visits').range(offset, offset + batch_size - 1).execute()
            
            if not result.data:
                break
            
            all_customers.extend(result.data)
            offset += batch_size
            
            if len(result.data) < batch_size:
                break
                
        except Exception as e:
            print(f"Error loading batch: {e}")
            break
    
    print(f"Loaded {len(all_customers)} customers")
    
    # Find phone duplicates
    print("Finding phone duplicates...")
    phone_groups = {}
    for customer in all_customers:
        phone = normalize_phone(customer.get('phone', ''))
        if phone and len(phone) >= 10:
            if phone not in phone_groups:
                phone_groups[phone] = []
            phone_groups[phone].append(customer)
    
    phone_duplicates = []
    for phone, customers in phone_groups.items():
        if len(customers) > 1:
            phone_duplicates.append({
                'type': 'phone',
                'match_value': phone,
                'count': len(customers),
                'customers': customers,
                'is_fake': is_fake_number(phone)
            })
    
    print(f"Found {len(phone_duplicates)} phone duplicate groups")
    
    # Find name duplicates
    print("Finding name duplicates...")
    name_duplicates = []
    processed = set()
    
    for i, customer1 in enumerate(all_customers):
        if customer1.get('member_id') in processed:
            continue
            
        name1 = customer1.get('name', '')
        if not name1:
            continue
        
        similar_customers = [customer1]
        
        for j, customer2 in enumerate(all_customers[i+1:], i+1):
            if customer2.get('member_id') in processed:
                continue
                
            name2 = customer2.get('name', '')
            if not name2:
                continue
            
            similarity = name_similarity(name1, name2)
            
            # Threshold for name similarity
            if similarity > 0.85:
                similar_customers.append(customer2)
                processed.add(customer2.get('member_id'))
        
        if len(similar_customers) > 1:
            name_duplicates.append({
                'type': 'name',
                'match_value': name1,
                'count': len(similar_customers),
                'customers': similar_customers,
                'similarity': similarity
            })
            processed.add(customer1.get('member_id'))
        
        if i % 1000 == 0:
            print(f"  Processed {i}/{len(all_customers)} customers...")
    
    print(f"Found {len(name_duplicates)} name duplicate groups")
    
    # Find email duplicates
    print("Finding email duplicates...")
    email_groups = {}
    for customer in all_customers:
        email = customer.get('email', '')
        if email and isinstance(email, str) and '@' in email:
            email = email.lower().strip()
            if email not in email_groups:
                email_groups[email] = []
            email_groups[email].append(customer)
    
    email_duplicates = []
    for email, customers in email_groups.items():
        if len(customers) > 1:
            email_duplicates.append({
                'type': 'email',
                'match_value': email,
                'count': len(customers),
                'customers': customers
            })
    
    print(f"Found {len(email_duplicates)} email duplicate groups")
    
    return phone_duplicates, name_duplicates, email_duplicates

def export_complete_report(phone_dups, name_dups, email_dups, filename=None):
    """Export complete duplicate report"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"complete_duplicate_report_{timestamp}.csv"
    
    print(f"Creating complete report: {filename}")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Type',
            'Match_Value',
            'Count',
            'Total_Lifetime_Value',
            'Max_Lifetime_Value',
            'Is_Fake',
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
        
        all_duplicates = []
        
        # Process phone duplicates
        for dup in phone_dups:
            customers = dup['customers']
            total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
            max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
            
            if dup['is_fake']:
                recommendation = 'DELETE_ALL'
                notes = 'DELETE ALL - Fake phone number'
            elif total_value < 100:
                recommendation = 'MERGE_LOW_VALUE'
                notes = 'Safe to merge - low value customers'
            elif max_value > 1000:
                recommendation = 'REVIEW_HIGH_VALUE'
                notes = 'Review carefully - high value customers'
            else:
                recommendation = 'MERGE_MEDIUM_VALUE'
                notes = 'Medium value - review before merging'
            
            all_duplicates.append({
                'type': dup['type'],
                'match_value': dup['match_value'],
                'count': dup['count'],
                'total_value': total_value,
                'max_value': max_value,
                'is_fake': dup['is_fake'],
                'recommendation': recommendation,
                'customers': customers,
                'notes': notes
            })
        
        # Process name duplicates
        for dup in name_dups:
            customers = dup['customers']
            total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
            max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
            
            if total_value < 100:
                recommendation = 'MERGE_LOW_VALUE'
                notes = 'Safe to merge - low value customers'
            elif max_value > 1000:
                recommendation = 'REVIEW_HIGH_VALUE'
                notes = 'Review carefully - high value customers'
            else:
                recommendation = 'MERGE_MEDIUM_VALUE'
                notes = 'Medium value - review before merging'
            
            all_duplicates.append({
                'type': dup['type'],
                'match_value': dup['match_value'],
                'count': dup['count'],
                'total_value': total_value,
                'max_value': max_value,
                'is_fake': False,
                'recommendation': recommendation,
                'customers': customers,
                'notes': notes
            })
        
        # Process email duplicates
        for dup in email_dups:
            customers = dup['customers']
            total_value = sum(float(c.get('lifetime_value', 0)) for c in customers)
            max_value = max(float(c.get('lifetime_value', 0)) for c in customers)
            
            recommendation = 'MERGE_HIGH_CONFIDENCE'
            notes = 'High confidence - same email address'
            
            all_duplicates.append({
                'type': dup['type'],
                'match_value': dup['match_value'],
                'count': dup['count'],
                'total_value': total_value,
                'max_value': max_value,
                'is_fake': False,
                'recommendation': recommendation,
                'customers': customers,
                'notes': notes
            })
        
        # Sort by type and count
        all_duplicates.sort(key=lambda x: (x['type'], -x['count']))
        
        # Write rows
        for dup in all_duplicates:
            customers = dup['customers']
            
            row = [
                dup['type'],
                dup['match_value'],
                dup['count'],
                dup['total_value'],
                dup['max_value'],
                dup['is_fake'],
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
            
            row.append(dup['notes'])
            writer.writerow(row)
    
    print(f"Complete report saved to: {filename}")
    return filename, len(all_duplicates)

def main():
    """Main function"""
    print("Complete Duplicate Finder - ALL Types")
    print("="*50)
    
    try:
        # Find all duplicates
        phone_dups, name_dups, email_dups = find_all_duplicates()
        
        # Export complete report
        filename, total_count = export_complete_report(phone_dups, name_dups, email_dups)
        
        print(f"\nANALYSIS COMPLETE!")
        print(f"Phone duplicates: {len(phone_dups)} groups")
        print(f"Name duplicates: {len(name_dups)} groups")
        print(f"Email duplicates: {len(email_dups)} groups")
        print(f"TOTAL DUPLICATE GROUPS: {total_count}")
        print(f"Report saved to: {filename}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
