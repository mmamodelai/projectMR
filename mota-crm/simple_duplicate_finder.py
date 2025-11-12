#!/usr/bin/env python3
"""
Simple Duplicate Finder
Part of Conductor SMS System

Processes customers in small batches to avoid memory issues
"""

import csv
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

def find_phone_duplicates():
    """Find phone duplicates using batch processing"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Finding phone duplicates...")
    
    phone_groups = {}
    batch_size = 500
    offset = 0
    
    while True:
        print(f"   Processing batch {offset//batch_size + 1}...")
        
        try:
            result = sb.table('customers').select('member_id,name,phone,email,lifetime_value').range(offset, offset + batch_size - 1).execute()
            
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
    
    # Find groups with duplicates
    duplicates = []
    for phone, customers in phone_groups.items():
        if len(customers) > 1:
            duplicates.append({
                'type': 'phone',
                'match_value': phone,
                'count': len(customers),
                'customers': customers,
                'confidence': 'HIGH'
            })
    
    print(f"   Found {len(duplicates)} phone duplicate groups")
    return duplicates

def find_email_duplicates():
    """Find email duplicates using batch processing"""
    sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    
    print("Finding email duplicates...")
    
    email_groups = {}
    batch_size = 500
    offset = 0
    
    while True:
        print(f"   Processing batch {offset//batch_size + 1}...")
        
        try:
            result = sb.table('customers').select('member_id,name,phone,email,lifetime_value').range(offset, offset + batch_size - 1).execute()
            
            if not result.data:
                break
            
            for customer in result.data:
                email = customer.get('email', '')
                if email and isinstance(email, str) and '@' in email:
                    email = email.lower().strip()
                    if email not in email_groups:
                        email_groups[email] = []
                    email_groups[email].append(customer)
            
            offset += batch_size
            
            if len(result.data) < batch_size:
                break
                
        except Exception as e:
            print(f"   Error processing batch: {e}")
            break
    
    # Find groups with duplicates
    duplicates = []
    for email, customers in email_groups.items():
        if len(customers) > 1:
            duplicates.append({
                'type': 'email',
                'match_value': email,
                'count': len(customers),
                'customers': customers,
                'confidence': 'HIGH'
            })
    
    print(f"   Found {len(duplicates)} email duplicate groups")
    return duplicates

def export_to_csv(all_duplicates, filename=None):
    """Export duplicates to CSV"""
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"simple_duplicates_{timestamp}.csv"
    
    print("Exporting to {filename}...")
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # Header
        writer.writerow([
            'Type',
            'Match_Value',
            'Count',
            'Confidence',
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
            'Merge_Recommendation'
        ])
        
        # Data rows
        for dup in all_duplicates:
            customers = dup['customers']
            
            # Create row
            row = [
                dup['type'],
                dup['match_value'],
                dup['count'],
                dup['confidence']
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
            
            # Merge recommendation
            if dup['confidence'] == 'HIGH':
                recommendation = 'MERGE - High confidence'
            else:
                recommendation = 'REVIEW - Check details'
            
            row.append(recommendation)
            writer.writerow(row)
    
    print(f"Exported {len(all_duplicates)} duplicate groups to {filename}")
    return filename

def print_summary(all_duplicates):
    """Print summary"""
    print("\n" + "="*60)
    print("SIMPLE DUPLICATE FINDER - RESULTS")
    print("="*60)
    
    print(f"Total duplicate groups found: {len(all_duplicates)}")
    
    # Count by type
    type_counts = {}
    for dup in all_duplicates:
        dup_type = dup['type']
        type_counts[dup_type] = type_counts.get(dup_type, 0) + 1
    
    print("\nBy Type:")
    for dup_type, count in type_counts.items():
        print(f"  {dup_type}: {count} groups")
    
    # Show top duplicates
    print("\nTOP DUPLICATES:")
    sorted_dups = sorted(all_duplicates, key=lambda x: x['count'], reverse=True)
    
    for i, dup in enumerate(sorted_dups[:10], 1):
        print(f"\n{i}. {dup['type'].upper()} - {dup['match_value']}")
        print(f"   Count: {dup['count']} customers")
        print(f"   Confidence: {dup['confidence']}")
        
        for j, customer in enumerate(dup['customers'][:3], 1):
            print(f"   Customer {j}: {customer.get('name', 'N/A')} (ID: {customer.get('member_id', 'N/A')})")
            print(f"              Phone: {customer.get('phone', 'N/A')}")
            print(f"              Email: {customer.get('email', 'N/A')}")
            print(f"              Lifetime Value: ${customer.get('lifetime_value', 0):.2f}")

def main():
    """Main function"""
    print("Simple Duplicate Finder")
    print("="*30)
    
    try:
        all_duplicates = []
        
        # Find phone duplicates
        phone_dups = find_phone_duplicates()
        all_duplicates.extend(phone_dups)
        
        # Find email duplicates
        email_dups = find_email_duplicates()
        all_duplicates.extend(email_dups)
        
        # Print summary
        print_summary(all_duplicates)
        
        # Export to CSV
        csv_file = export_to_csv(all_duplicates)
        
        print(f"\nAnalysis complete!")
        print(f"Results saved to: {csv_file}")
        print(f"\nFocus on HIGH confidence duplicates first!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
