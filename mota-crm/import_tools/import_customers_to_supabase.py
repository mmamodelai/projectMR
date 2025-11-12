#!/usr/bin/env python3
"""
Import Customer Data to Supabase
Reads MEMBER_PERFORMANCE.csv and imports to Supabase customers table

Usage:
    python import_customers_to_supabase.py [--dry-run] [--batch-size 100]
    
Features:
- Phone number validation and formatting
- Batch imports for performance
- Duplicate detection
- Progress tracking
- Dry-run mode for testing
"""

import csv
import sys
import json
import re
from datetime import datetime
from supabase import create_client, Client
import argparse
from typing import Dict, List, Optional

# Supabase configuration
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def parse_currency(value: str) -> float:
    """Convert currency string like '$52.00' to float"""
    if not value or value == 'N/A':
        return 0.0
    # Remove $ and commas
    clean = value.replace('$', '').replace(',', '')
    try:
        return float(clean)
    except:
        return 0.0

def parse_decimal(value: str) -> float:
    """Convert string to float, handle N/A"""
    if not value or value == 'N/A':
        return 0.0
    try:
        return float(value)
    except:
        return 0.0

def parse_int(value: str) -> int:
    """Convert string to int, handle N/A"""
    if not value or value == 'N/A':
        return 0
    try:
        return int(value)
    except:
        return 0

def parse_date(value: str) -> Optional[str]:
    """Convert MM/DD/YYYY to YYYY-MM-DD format"""
    if not value or value == 'N/A':
        return None
    try:
        # Parse MM/DD/YYYY
        dt = datetime.strptime(value, '%m/%d/%Y')
        # Return in YYYY-MM-DD format for PostgreSQL
        return dt.strftime('%Y-%m-%d')
    except:
        return None

def format_phone(phone: str) -> Optional[str]:
    """Format phone number to E.164 format (+1234567890)"""
    if not phone or phone == 'N/A' or phone.strip() == '':
        return None
    
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    # If 10 digits, assume US number
    if len(digits) == 10:
        return f'+1{digits}'
    # If 11 digits and starts with 1, format
    elif len(digits) == 11 and digits[0] == '1':
        return f'+{digits}'
    # If already has +, clean and return
    elif phone.startswith('+'):
        return f'+{digits}'
    else:
        # Unknown format, return None
        return None

def clean_text(value: str) -> Optional[str]:
    """Clean text fields, return None if empty/N/A"""
    if not value or value == 'N/A' or value.strip() == '':
        return None
    return value.strip()

def row_to_customer(row: Dict) -> Dict:
    """Convert CSV row to customer database record"""
    
    # Parse financial values
    gross_sales = parse_currency(row.get('Gross Sales Receipts', '0'))
    gross_refunds = parse_currency(row.get('Gross Refund Receipts', '0'))
    
    customer = {
        # Identity
        'member_id': row.get('MemberId', '').strip(),
        'name': clean_text(row.get('Member Name')),
        'phone': format_phone(row.get('Member Phone', '')),
        'email': None,  # Not in CSV, but field exists
        
        # Loyalty Metrics
        'loyalty_points': parse_decimal(row.get('Loyalty Points', '0')),
        'total_visits': parse_int(row.get('# of Visits', '0')),
        'total_sales': parse_int(row.get('# of Sales', '0')),
        'total_refunds': parse_int(row.get('# of Refunds', '0')),
        
        # Financial Metrics
        'gross_sales': gross_sales,
        'gross_refunds': gross_refunds,
        'avg_sale_value': parse_decimal(row.get('Avg Sales Receipts', '0')),
        'lifetime_value': gross_sales - gross_refunds,  # Calculated
        
        # Customer Profile
        'customer_type': clean_text(row.get('Consumer Type')),
        'member_group': clean_text(row.get('Member Group')),
        'marketing_source': clean_text(row.get('Marketing Src')),
        'state': clean_text(row.get('State')),
        'zip_code': clean_text(row.get('Zip Code')),
        
        # Dates
        'date_joined': parse_date(row.get('Date Joined')),
        'last_visited': parse_date(row.get('Last Visited')),
    }
    
    # Database triggers will calculate:
    # - vip_status (based on total_visits)
    # - churn_risk (based on last_visited)
    # - days_since_last_visit (based on last_visited)
    
    return customer

def import_customers(csv_path: str, dry_run: bool = False, batch_size: int = 100):
    """Import customers from CSV to Supabase"""
    
    print(f"Starting customer import from {csv_path}")
    print(f"   Dry run: {dry_run}")
    print(f"   Batch size: {batch_size}")
    print()
    
    # Initialize Supabase client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("Connected to Supabase")
    
    # Read CSV file
    customers = []
    skipped = []
    total_rows = 0
    
    print(f"Reading CSV file...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        # Skip first line (title row)
        first_line = f.readline()
        
        reader = csv.DictReader(f)
        
        for row in reader:
            total_rows += 1
            
            # Skip header row if it appears in data
            if row.get('MemberId', '').startswith('Member'):
                continue
            
            try:
                customer = row_to_customer(row)
                
                # Validate required fields
                if not customer['member_id']:
                    skipped.append(f"Row {total_rows}: Missing member_id")
                    continue
                
                customers.append(customer)
                
                # Show progress every 1000 rows
                if len(customers) % 1000 == 0:
                    print(f"   Processed {len(customers)} customers...")
                    
            except Exception as e:
                skipped.append(f"Row {total_rows}: {str(e)}")
    
    print(f"Read {len(customers)} valid customers")
    print(f"   Skipped {len(skipped)} invalid rows")
    print()
    
    if skipped and len(skipped) <= 10:
        print("Skipped rows:")
        for skip in skipped:
            print(f"   {skip}")
        print()
    
    if dry_run:
        print("DRY RUN MODE - No data will be inserted")
        print()
        if customers:
            print("Sample customer data:")
            print(json.dumps(customers[0], indent=2, default=str))
            print()
        print(f"Summary:")
        print(f"   Total customers to import: {len(customers)}")
        print(f"   Customers with phone numbers: {sum(1 for c in customers if c['phone'])}")
        print(f"   VIP customers (16+ visits): {sum(1 for c in customers if c['total_visits'] >= 16)}")
        print(f"   Regular customers (6-15 visits): {sum(1 for c in customers if 6 <= c['total_visits'] < 16)}")
        print(f"   Casual customers (2-5 visits): {sum(1 for c in customers if 2 <= c['total_visits'] < 6)}")
        print(f"   New customers (1 visit): {sum(1 for c in customers if c['total_visits'] == 1)}")
        return
    
    # Import in batches
    print(f"Importing {len(customers)} customers to Supabase...")
    imported = 0
    errors = []
    
    for i in range(0, len(customers), batch_size):
        batch = customers[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (len(customers) + batch_size - 1) // batch_size
        
        try:
            # Upsert batch (insert or update if member_id exists)
            response = supabase.table('customers').upsert(
                batch,
                on_conflict='member_id'
            ).execute()
            
            imported += len(batch)
            print(f"   Batch {batch_num}/{total_batches}: Imported {len(batch)} customers (Total: {imported})")
            
        except Exception as e:
            error_msg = f"Batch {batch_num} failed: {str(e)}"
            errors.append(error_msg)
            print(f"   ERROR: {error_msg}")
    
    print()
    print("Import complete!")
    print(f"   Successfully imported: {imported} customers")
    if errors:
        print(f"   Errors: {len(errors)}")
        for error in errors[:5]:  # Show first 5 errors
            print(f"   - {error}")
    print()
    
    # Summary statistics
    print("Database Summary:")
    try:
        # Get total count
        total = supabase.table('customers').select('id', count='exact').execute()
        print(f"   Total customers in database: {total.count}")
        
        # Get VIP count
        vips = supabase.table('customers').select('id', count='exact').eq('vip_status', 'VIP').execute()
        print(f"   VIP customers: {vips.count}")
        
        # Get customers with phone numbers
        with_phone = supabase.table('customers').select('id', count='exact').not_.is_('phone', 'null').execute()
        print(f"   Customers with phone numbers: {with_phone.count}")
        
    except Exception as e:
        print(f"   Could not fetch summary: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description='Import MoTa customer data to Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Test import without writing to database')
    parser.add_argument('--batch-size', type=int, default=100, help='Number of records per batch (default: 100)')
    parser.add_argument('--csv', type=str, default='MEMBER_PERFORMANCE.csv', help='Path to CSV file')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MoTa CRM Customer Data Import Tool")
    print("=" * 60)
    print()
    
    try:
        import_customers(args.csv, dry_run=args.dry_run, batch_size=args.batch_size)
        print("Import completed successfully!")
        
    except FileNotFoundError:
        print(f"ERROR: Could not find file '{args.csv}'")
        print(f"   Make sure you're in the 'mota finance' directory")
        sys.exit(1)
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()

