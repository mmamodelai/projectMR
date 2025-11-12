#!/usr/bin/env python3
"""
Customer Duplicate Detector
Part of Conductor SMS System

Analyzes customer database for potential duplicates based on:
- Phone numbers
- Names (fuzzy matching)
- Email addresses
- Address combinations

Outputs results to CSV for review
"""

import csv
import json
from datetime import datetime
from difflib import SequenceMatcher
from supabase import create_client, Client
import sys

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class DuplicateDetector:
    def __init__(self):
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.customers = []
        self.duplicates = []
        
    def load_customers(self):
        """Load all customers from database"""
        print("Loading customers from database...")
        
        try:
            # Load all customers with pagination
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = self.sb.table('customers').select('*').range(offset, offset + page_size - 1).execute()
                
                if not result.data:
                    break
                    
                all_customers.extend(result.data)
                offset += page_size
                
                if len(result.data) < page_size:
                    break
            
            self.customers = all_customers
            print(f"Loaded {len(self.customers)} customers")
            
        except Exception as e:
            print(f"Error loading customers: {e}")
            sys.exit(1)
    
    def normalize_phone(self, phone):
        """Normalize phone number for comparison"""
        if not phone:
            return ""
        
        # Remove all non-digits
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        # Handle different formats
        if len(digits) == 10:
            return digits  # US format without country code
        elif len(digits) == 11 and digits.startswith('1'):
            return digits[1:]  # Remove US country code
        else:
            return digits
    
    def normalize_name(self, name):
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
    
    def name_similarity(self, name1, name2):
        """Calculate similarity between two names"""
        if not name1 or not name2:
            return 0
        
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)
        
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def find_phone_duplicates(self):
        """Find customers with same phone numbers"""
        print("Checking for phone number duplicates...")
        
        phone_groups = {}
        
        for customer in self.customers:
            phone = self.normalize_phone(customer.get('phone'))
            if phone and len(phone) >= 10:  # Valid phone number
                if phone not in phone_groups:
                    phone_groups[phone] = []
                phone_groups[phone].append(customer)
        
        # Find groups with multiple customers
        for phone, customers in phone_groups.items():
            if len(customers) > 1:
                self.duplicates.append({
                    'type': 'phone',
                    'match_value': phone,
                    'customers': customers,
                    'confidence': 'high'
                })
        
        print(f"Found {len([d for d in self.duplicates if d['type'] == 'phone'])} phone duplicate groups")
    
    def find_name_duplicates(self):
        """Find customers with similar names"""
        print("Checking for name duplicates...")
        
        processed = set()
        name_duplicates = []
        
        for i, customer1 in enumerate(self.customers):
            if customer1.get('member_id') in processed:
                continue
                
            name1 = customer1.get('name', '')
            if not name1:
                continue
            
            similar_customers = [customer1]
            
            for j, customer2 in enumerate(self.customers[i+1:], i+1):
                if customer2.get('member_id') in processed:
                    continue
                    
                name2 = customer2.get('name', '')
                if not name2:
                    continue
                
                similarity = self.name_similarity(name1, name2)
                
                # Threshold for name similarity (adjust as needed)
                if similarity > 0.85:
                    similar_customers.append(customer2)
                    processed.add(customer2.get('member_id'))
            
            if len(similar_customers) > 1:
                name_duplicates.append({
                    'type': 'name',
                    'match_value': name1,
                    'customers': similar_customers,
                    'confidence': 'medium'
                })
                processed.add(customer1.get('member_id'))
        
        self.duplicates.extend(name_duplicates)
        print(f"Found {len(name_duplicates)} name duplicate groups")
    
    def find_email_duplicates(self):
        """Find customers with same email addresses"""
        print("Checking for email duplicates...")
        
        email_groups = {}
        
        for customer in self.customers:
            email = customer.get('email', '')
            if email and isinstance(email, str):
                email = email.lower().strip()
            else:
                email = ''
            
            if email and '@' in email:
                if email not in email_groups:
                    email_groups[email] = []
                email_groups[email].append(customer)
        
        # Find groups with multiple customers
        for email, customers in email_groups.items():
            if len(customers) > 1:
                self.duplicates.append({
                    'type': 'email',
                    'match_value': email,
                    'customers': customers,
                    'confidence': 'high'
                })
        
        print(f"Found {len([d for d in self.duplicates if d['type'] == 'email'])} email duplicate groups")
    
    def find_address_duplicates(self):
        """Find customers with same address combinations"""
        print("Checking for address duplicates...")
        
        address_groups = {}
        
        for customer in self.customers:
            street = customer.get('street_address', '').lower().strip()
            city = customer.get('city', '').lower().strip()
            zip_code = customer.get('zip_code', '').strip()
            
            if street and city and zip_code:
                address_key = f"{street}|{city}|{zip_code}"
                if address_key not in address_groups:
                    address_groups[address_key] = []
                address_groups[address_key].append(customer)
        
        # Find groups with multiple customers
        for address, customers in address_groups.items():
            if len(customers) > 1:
                self.duplicates.append({
                    'type': 'address',
                    'match_value': address,
                    'customers': customers,
                    'confidence': 'medium'
                })
        
        print(f"Found {len([d for d in self.duplicates if d['type'] == 'address'])} address duplicate groups")
    
    def export_to_csv(self, filename=None):
        """Export duplicates to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"customer_duplicates_{timestamp}.csv"
        
        print(f"Exporting duplicates to {filename}...")
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            writer.writerow([
                'Duplicate_Type',
                'Match_Value',
                'Confidence',
                'Customer_Count',
                'Member_ID_1',
                'Name_1',
                'Phone_1',
                'Email_1',
                'Lifetime_Value_1',
                'Last_Visit_1',
                'Member_ID_2',
                'Name_2',
                'Phone_2',
                'Email_2',
                'Lifetime_Value_2',
                'Last_Visit_2',
                'Member_ID_3',
                'Name_3',
                'Phone_3',
                'Email_3',
                'Lifetime_Value_3',
                'Last_Visit_3',
                'Notes'
            ])
            
            # Data rows
            for duplicate in self.duplicates:
                customers = duplicate['customers']
                
                # Create row with up to 3 customers
                row = [
                    duplicate['type'],
                    duplicate['match_value'],
                    duplicate['confidence'],
                    len(customers)
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
                            customer.get('last_visited', '')
                        ])
                    else:
                        row.extend(['', '', '', '', '', ''])
                
                # Add notes
                notes = f"Group of {len(customers)} customers"
                if len(customers) > 3:
                    notes += f" (+{len(customers)-3} more)"
                row.append(notes)
                
                writer.writerow(row)
        
        print(f"Exported {len(self.duplicates)} duplicate groups to {filename}")
        return filename
    
    def export_to_json(self, filename=None):
        """Export duplicates to JSON file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"customer_duplicates_{timestamp}.json"
        
        print(f"Exporting duplicates to {filename}...")
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'total_customers_analyzed': len(self.customers),
            'total_duplicate_groups': len(self.duplicates),
            'duplicate_types': {
                'phone': len([d for d in self.duplicates if d['type'] == 'phone']),
                'name': len([d for d in self.duplicates if d['type'] == 'name']),
                'email': len([d for d in self.duplicates if d['type'] == 'email']),
                'address': len([d for d in self.duplicates if d['type'] == 'address'])
            },
            'duplicates': self.duplicates
        }
        
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(export_data, jsonfile, indent=2, default=str)
        
        print(f"Exported detailed data to {filename}")
        return filename
    
    def print_summary(self):
        """Print summary of findings"""
        print("\n" + "="*60)
        print("DUPLICATE DETECTION SUMMARY")
        print("="*60)
        
        print(f"Total customers analyzed: {len(self.customers):,}")
        print(f"Total duplicate groups found: {len(self.duplicates)}")
        
        type_counts = {}
        for duplicate in self.duplicates:
            dup_type = duplicate['type']
            type_counts[dup_type] = type_counts.get(dup_type, 0) + 1
        
        print("\nDuplicate types:")
        for dup_type, count in type_counts.items():
            print(f"  {dup_type.capitalize()}: {count} groups")
        
        # Show some examples
        print("\nSample duplicates:")
        for i, duplicate in enumerate(self.duplicates[:5]):
            customers = duplicate['customers']
            print(f"\n{i+1}. {duplicate['type'].upper()} match: '{duplicate['match_value']}'")
            print(f"   Confidence: {duplicate['confidence']}")
            print(f"   Customers ({len(customers)}):")
            for customer in customers[:3]:
                print(f"     - {customer.get('name', 'N/A')} (ID: {customer.get('member_id', 'N/A')})")
                print(f"       Phone: {customer.get('phone', 'N/A')}")
                print(f"       Email: {customer.get('email', 'N/A')}")
                print(f"       Lifetime Value: ${customer.get('lifetime_value', 0):.2f}")
        
        if len(self.duplicates) > 5:
            print(f"\n... and {len(self.duplicates) - 5} more groups")

def main():
    """Main function"""
    print("Customer Duplicate Detector")
    print("="*40)
    
    detector = DuplicateDetector()
    
    # Load customers
    detector.load_customers()
    
    # Run all duplicate checks
    detector.find_phone_duplicates()
    detector.find_name_duplicates()
    detector.find_email_duplicates()
    detector.find_address_duplicates()
    
    # Print summary
    detector.print_summary()
    
    # Export results
    csv_file = detector.export_to_csv()
    json_file = detector.export_to_json()
    
    print(f"\n✅ Analysis complete!")
    print(f"📊 CSV file: {csv_file}")
    print(f"📋 JSON file: {json_file}")
    print(f"\nReview the files and decide which duplicates to merge/remove.")

if __name__ == "__main__":
    main()
