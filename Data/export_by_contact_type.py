#!/usr/bin/env python3
"""
Export member data segmented by contact information type
Creates three files:
- memberdata_phones.csv: Phone only (no email)
- memberdata_emails.csv: Email only (no phone)
- memberdata_both.csv: Both phone and email
"""

import csv

csv_path = r'C:\Dev\conductor\Data\MemberDataExport_Mota_10_16_2025 - EXPORT_MEMBERS_Mota).csv'

# Open output files
phones_file = open('memberdata_phones.csv', 'w', newline='', encoding='utf-8')
emails_file = open('memberdata_emails.csv', 'w', newline='', encoding='utf-8')
both_file = open('memberdata_both.csv', 'w', newline='', encoding='utf-8')

# CSV writers
phones_writer = csv.writer(phones_file)
emails_writer = csv.writer(emails_file)
both_writer = csv.writer(both_file)

# Write headers
header = ['Member Id', 'First Name', 'Last Name', 'Street Address', 'City', 'State', 'Zip Code', 'Primary Phone', 'Email Address']
phones_writer.writerow(header)
emails_writer.writerow(header)
both_writer.writerow(header)

# Counters
phones_count = 0
emails_count = 0
both_count = 0

print("Creating segmented exports...")

with open(csv_path, 'r', encoding='utf-8') as f:
    next(f)  # Skip timestamp header
    reader = csv.DictReader(f)
    
    for idx, row in enumerate(reader):
        member_id = row.get('Member Id', '').strip()
        first_name = row.get('First Name', '').strip()
        last_name = row.get('Last Name', '').strip()
        street = row.get('Street Address', '').strip()
        city = row.get('City', '').strip()
        state = row.get('State', '').strip()
        zip_code = row.get('Zip Code', '').strip()
        phone = row.get('Primary Phone', '').strip()
        email = row.get('Email Address', '').strip()
        
        # Create output row
        out_row = [member_id, first_name, last_name, street, city, state, zip_code, phone, email]
        
        # Categorize
        has_phone = bool(phone and phone != '')
        has_email = bool(email and email != '')
        
        if has_phone and has_email:
            both_writer.writerow(out_row)
            both_count += 1
        elif has_phone:
            phones_writer.writerow(out_row)
            phones_count += 1
        elif has_email:
            emails_writer.writerow(out_row)
            emails_count += 1
        
        if (idx + 1) % 20000 == 0:
            print(f"  Processed {idx + 1} records...")

phones_file.close()
emails_file.close()
both_file.close()

print(f"\n{'='*60}")
print(f"EXPORT COMPLETE")
print(f"{'='*60}")
print(f"memberdata_phones.csv: {phones_count:,} records (PHONE ONLY)")
print(f"memberdata_emails.csv: {emails_count:,} records (EMAIL ONLY)")
print(f"memberdata_both.csv:   {both_count:,} records (PHONE + EMAIL)")
print(f"\nTotal with contact: {phones_count + emails_count + both_count:,}")
print(f"{'='*60}")

