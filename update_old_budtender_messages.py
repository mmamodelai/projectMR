#!/usr/bin/env python3
"""
Update campaign messages for OLD budtenders (9/14/2025 and earlier)
Replace t-shirt welcome message with joints/product feedback message
"""
import csv
from datetime import datetime
from supabase import create_client

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Cutoff date: September 14, 2025 or older = OLD (get new message)
CUTOFF_DATE = datetime(2025, 9, 14, 23, 59, 59)

# New message template for OLD budtenders (UPDATED 2025-11-08 - iPhone optimized)
# ALL bubbles < 150 chars (iPhone limit, NOT 160!)
# Stored as single message with [BUBBLE] markers for splitting when sending
NEW_MESSAGE_TEMPLATE = """Hi {first_name}: Its Mota Luis, reaching out to see if you had a chance to try out the Fatty Joints we dropped at {dispensary}.

[BUBBLE]

My intention is for you to try a broad selection of our flower; hoping you tried each strain.

[BUBBLE]

If you didn't get all the samples, text me back; we'll pack some specifically for you.

[BUBBLE]

To help you better know our products, click this link to Mota Education Materials; organized by Flower, Vapes & Concentrates:

[BUBBLE]

https://www.motarewards.com/educational

[BUBBLE]

Hope you enjoy the Fatty Joints & feel more confident recommending MOTA Flower.

[BUBBLE]

I'd appreciate feedback on the joint samples; let me know what you think.

[BUBBLE]

Text back if you'd like to try other products; we'll bring them through the right channels."""

def parse_csv_date(date_str):
    """Parse dates from CSV (format: M/D/YYYY H:MM or MM/DD/YYYY H:MM)"""
    try:
        # Try parsing with various formats
        for fmt in ['%m/%d/%Y %H:%M', '%m/%d/%Y %H:%M:%S', '%-m/%-d/%Y %H:%M']:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        # Manual parsing as fallback
        parts = date_str.split(' ')[0].split('/')
        month, day, year = int(parts[0]), int(parts[1]), int(parts[2])
        return datetime(year, month, day)
    except Exception as e:
        print(f"  WARNING: Could not parse date '{date_str}': {e}")
        return None

def main():
    print("="*70)
    print("UPDATING OLD BUDTENDER CAMPAIGN MESSAGES")
    print("="*70)
    print(f"Cutoff Date: {CUTOFF_DATE.strftime('%m/%d/%Y')}")
    print(f"  - ON OR BEFORE {CUTOFF_DATE.strftime('%m/%d/%Y')}: Get NEW joints/feedback message")
    print(f"  - AFTER {CUTOFF_DATE.strftime('%m/%d/%Y')}: Keep ORIGINAL t-shirt welcome message")
    print()
    
    # Step 1: Read CSV and identify OLD budtenders
    csv_path = r'C:\Dev\conductor\SMSSUG\MOTA Merchandise BT Info SHEET 2 (Responses) - Form Responses 1 (1).csv'
    
    old_budtenders = []
    new_budtenders = []
    
    print("Reading CSV to identify budtenders by date...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            timestamp_str = row.get('Timestamp', '').strip()
            if not timestamp_str:
                continue
            
            timestamp = parse_csv_date(timestamp_str)
            if not timestamp:
                continue
            
            first_name = row.get('First Name', '').strip()
            last_name = row.get('Last Name', '').strip()
            phone = row.get('Phone Number', '').strip()
            dispensary = row.get('Affiliation (Store Name)', '').strip()
            
            if not first_name or not phone:
                continue
            
            # Normalize phone to E.164
            phone_clean = ''.join(filter(str.isdigit, phone))[-10:]
            phone_e164 = f"+1{phone_clean}"
            
            entry = {
                'first_name': first_name,
                'last_name': last_name,
                'phone': phone_e164,
                'dispensary': dispensary,
                'timestamp': timestamp
            }
            
            if timestamp <= CUTOFF_DATE:
                old_budtenders.append(entry)
            else:
                new_budtenders.append(entry)
    
    print(f"\nOLD Budtenders (need NEW message): {len(old_budtenders)}")
    print(f"NEW Budtenders (keep original): {len(new_budtenders)}")
    print()
    
    if not old_budtenders:
        print("No OLD budtenders found. Exiting.")
        return
    
    # Step 2: Update campaign_messages for OLD budtenders
    print(f"Updating {len(old_budtenders)} OLD budtenders with new message...")
    print()
    
    updated_count = 0
    not_found_count = 0
    
    for bt in old_budtenders:
        phone = bt['phone']
        first_name = bt['first_name']
        dispensary = bt['dispensary']
        timestamp_str = bt['timestamp'].strftime('%m/%d/%Y')
        
        # Generate new message
        new_message = NEW_MESSAGE_TEMPLATE.format(
            first_name=first_name,
            dispensary=dispensary
        )
        
        # Find message in database by phone
        try:
            response = supabase.table('campaign_messages').select('id, customer_name').eq('phone_number', phone).eq('status', 'SUG').execute()
            
            if response.data and len(response.data) > 0:
                msg_id = response.data[0]['id']
                db_name = response.data[0]['customer_name']
                
                # Update message content and strategy
                update_response = supabase.table('campaign_messages').update({
                    'message_content': new_message,
                    'strategy_type': 'product_feedback',
                    'campaign_name': 'BT_Product_Feedback_v1',
                    'reasoning': supabase.table('campaign_messages').select('reasoning').eq('id', msg_id).execute().data[0]['reasoning']  # Keep existing reasoning
                }).eq('id', msg_id).execute()
                
                print(f"  [OK] Updated: {db_name} ({dispensary}) - {timestamp_str}")
                updated_count += 1
            else:
                print(f"  [SKIP] Not found: {first_name} {bt['last_name']} ({phone}) - {timestamp_str}")
                not_found_count += 1
        
        except Exception as e:
            print(f"  ERROR: {first_name} - {str(e)}")
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total OLD budtenders in CSV: {len(old_budtenders)}")
    print(f"Successfully updated: {updated_count}")
    print(f"Not found in database: {not_found_count}")
    print()
    print("OLD budtenders now have the joints/product feedback message!")
    print("NEW budtenders (9/18/2025+) keep their original t-shirt welcome message.")

if __name__ == "__main__":
    main()

