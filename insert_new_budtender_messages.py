#!/usr/bin/env python3
"""
INSERT NEW Budtender Campaign Messages (Sept 18+)
Adds t-shirt welcome messages in 3-bubble format

TARGET: Budtenders who signed up on/after Sept 18, 2025
"""
from supabase import create_client
import csv
from datetime import datetime
import json
import hashlib

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# CSV path
CSV_PATH = r'C:\Dev\conductor\SMSSUG\MOTA Merchandise BT Info SHEET 2 (Responses) - Form Responses 1 (1).csv'

# Cutoff date for NEW budtenders (Sept 18, 2025 or later)
CUTOFF_DATE = datetime(2025, 9, 18, 0, 0, 0)

# NEW 3-bubble message template (without "I'm excited for you")
NEW_MESSAGE_TEMPLATE = """Hi {first_name},

Its Mota-Luis

Welcome to MOTA's Budtender Program!

Please reply to confirm your welcome gift details:

[BUBBLE]

We have you down for a {size} t-shirt with a {logo} logo on the front and {dispensary} on the sleeve.

[BUBBLE]

Let me know if you want any changes."""

def normalize_phone(phone):
    """Normalize phone to E.164 format (+1XXXXXXXXXX)"""
    digits = ''.join(c for c in str(phone) if c.isdigit())
    if len(digits) == 10:
        return f"+1{digits}"
    elif len(digits) == 11 and digits[0] == '1':
        return f"+{digits}"
    return f"+1{digits[-10:]}" if len(digits) >= 10 else None

print("="*70)
print("INSERT NEW BUDTENDER MESSAGES (SEPT 18+)")
print("="*70)
print("Target: T-shirt welcome messages")
print("Format: 3 bubbles (removed 'I'm excited for you')")
print()

# Read CSV and process NEW budtenders
new_budtenders = []
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        timestamp_str = row.get('Timestamp', '').strip()
        if not timestamp_str:
            continue
        
        try:
            timestamp = datetime.strptime(timestamp_str, '%m/%d/%Y %H:%M')
        except ValueError:
            continue
        
        # Only NEW budtenders (Sept 18+)
        if timestamp >= CUTOFF_DATE:
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            full_name = f"{first_name} {last_name}".strip()
            phone = row.get('Phone Number', '').strip()
            
            if not phone or not first_name:
                continue
            
            new_budtenders.append({
                'timestamp': timestamp,
                'dispensary': row.get('Affiliation (Store Name)', 'Unknown'),
                'name': full_name,
                'first_name': first_name,
                'phone': phone,
                'size': row.get('T-Shirt Size', 'Large'),
                'logo': row.get('Front Logo Design', 'MOTA')
            })

print(f"Found {len(new_budtenders)} NEW budtenders (Sept 18+)")
print()

# Insert each budtender into campaign_messages
inserted_count = 0
skipped_count = 0

for bt in new_budtenders:
    phone_normalized = normalize_phone(bt['phone'])
    if not phone_normalized:
        print(f"[SKIP] {bt['first_name']} - Invalid phone: {bt['phone']}")
        skipped_count += 1
        continue
    
    # Format the 3-bubble message
    new_message = NEW_MESSAGE_TEMPLATE.format(
        first_name=bt['first_name'],
        size=bt['size'],
        logo=bt['logo'],
        dispensary=bt['dispensary']
    )
    
    # Create reasoning JSON
    reasoning_json = json.dumps({
        'campaign_type': 'budtender_welcome',
        'signup_date': bt['timestamp'].isoformat(),
        'dispensary_name': bt['dispensary'],
        'tshirt_size': bt['size'],
        'front_logo': bt['logo']
    })
    
    # Create message hash
    hash_content = f"{phone_normalized}_{new_message}_{bt['timestamp'].isoformat()}"
    message_hash = hashlib.sha256(hash_content.encode()).hexdigest()[:16]
    
    try:
        # Check if already exists
        response = supabase.table('campaign_messages').select('*').eq('phone_number', phone_normalized).execute()
        
        if response.data and len(response.data) > 0:
            print(f"[EXISTS] {bt['first_name']} ({phone_normalized[:12]}...)")
            skipped_count += 1
            continue
        
        # Insert new campaign message
        supabase.table('campaign_messages').insert({
            'phone_number': phone_normalized,
            'customer_name': bt['name'],
            'message_content': new_message,
            'status': 'SUG',
            'strategy_type': 'budtender_welcome',
            'reasoning': reasoning_json,
            'generated_by': 'update_script',
            'generated_at': datetime.utcnow().isoformat()
        }).execute()
        
        inserted_count += 1
        print(f"[OK] {bt['first_name']} ({phone_normalized[:12]}...) - Inserted")
            
    except Exception as e:
        print(f"[ERROR] {bt['first_name']} ({bt['phone'][:8]}...): {e}")
        skipped_count += 1

print()
print("="*70)
print(f"COMPLETE: {inserted_count} inserted, {skipped_count} skipped")
print("="*70)
print()
print("Next steps:")
print("1. Refresh 'First Texts' tab in SMS Viewer")
print("2. Review and approve NEW budtender messages")
print("3. All messages use 3-bubble format (< 150 chars each)")

