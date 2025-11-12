#!/usr/bin/env python3
"""
Check phone number formats in both databases
"""
from supabase import create_client

SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def normalize_to_10_digits(phone):
    """Strip everything, get last 10 digits"""
    if not phone:
        return None
    digits = ''.join(filter(str.isdigit, str(phone)))
    if len(digits) >= 10:
        return digits[-10:]  # Last 10 digits
    return None

# Check budtenders
print("=" * 80)
print("BUDTENDERS DATABASE")
print("=" * 80)
bt = supabase.table('budtenders').select('first_name,last_name,phone').limit(20).execute()
for b in bt.data:
    name = f"{b.get('first_name', '')} {b.get('last_name', '')}".strip() or 'Unknown'
    phone = b.get('phone', 'N/A')
    normalized = normalize_to_10_digits(phone)
    print(f"{name:30s} | RAW: {phone:20s} | 10-DIGIT: {normalized}")

print("\n" + "=" * 80)
print("CUSTOMERS_BLAZE DATABASE")
print("=" * 80)
customers = supabase.table('customers_blaze').select('name,phone').limit(20).execute()
for c in customers.data:
    name = c.get('name', 'Unknown')
    phone = c.get('phone') or 'N/A'
    normalized = normalize_to_10_digits(phone)
    print(f"{name:30s} | RAW: {str(phone):20s} | 10-DIGIT: {normalized}")

print("\n" + "=" * 80)
print("SMS MESSAGES - INCOMING")
print("=" * 80)
sms = supabase.table('messages').select('phone_number').eq('direction', 'inbound').limit(20).execute()
phone_set = set()
for msg in sms.data:
    phone = msg.get('phone_number')
    if phone:
        phone_set.add(phone)

for phone in sorted(phone_set):
    normalized = normalize_to_10_digits(phone)
    print(f"SMS: {phone:20s} | 10-DIGIT: {normalized}")

