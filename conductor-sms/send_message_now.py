#!/usr/bin/env python3
"""Quick script to send a single SMS message via Supabase queue"""

import sys
from datetime import datetime, timezone
from supabase import create_client, Client
import json

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

# Initialize Supabase
supabase_url = config['database']['supabase_url']
supabase_key = config['database']['supabase_key']
supabase: Client = create_client(supabase_url, supabase_key)

def normalize_phone(phone):
    """Normalize phone number to E.164 format"""
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits[0] == '1':
        return '+' + digits
    if len(digits) == 10:
        return '+1' + digits
    if phone.startswith('+'):
        return phone
    return phone

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python send_message_now.py <phone> <message>")
        print("Example: python send_message_now.py \"(209) 900-3562\" \"Hello test\"")
        sys.exit(1)
    
    phone = normalize_phone(sys.argv[1])
    message = ' '.join(sys.argv[2:])
    
    print(f"Sending message to {phone}...")
    print(f"Message: {message[:50]}...")
    
    try:
        result = supabase.table('messages').insert({
            'phone_number': phone,
            'content': message,
            'status': 'queued',
            'direction': 'outbound',
            'timestamp': datetime.now(timezone.utc).isoformat()
        }).execute()
        
        print(f"✅ Message queued successfully!")
        print(f"   ID: {result.data[0]['id']}")
        print(f"   Status: queued")
        print(f"   Conductor will send it on next cycle (every 5 seconds)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

