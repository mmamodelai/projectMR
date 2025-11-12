#!/usr/bin/env python3
"""Quick phone number lookup"""

from supabase import create_client
import os

# Supabase connection
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

phone = "+12096288371"
msg_id = 875

print(f"\n{'='*60}")
print(f"PHONE NUMBER LOOKUP: {phone}")
print(f"{'='*60}\n")

# Check Budtenders
print("--- BUDTENDERS DATABASE ---")
try:
    bt_response = supabase.table('budtenders').select('*').or_(
        f'phone.eq.{phone},phone.eq.{phone[2:]},phone.eq.2096288371,phone.eq.(209) 628-8371,phone.eq.209-628-8371'
    ).execute()
    
    if bt_response.data:
        print(f"FOUND {len(bt_response.data)} budtender(s)!")
        for bt in bt_response.data:
            print(f"\nName: {bt.get('name', 'N/A')}")
            print(f"Phone: {bt.get('phone', 'N/A')}")
            print(f"Dispensary: {bt.get('dispensary', 'N/A')}")
            print(f"Email: {bt.get('email', 'N/A')}")
            print(f"Points: {bt.get('points', 0)}")
    else:
        print("Not found in budtenders")
except Exception as e:
    print(f"Error: {e}")

print("\n--- CUSTOMERS (BLAZE) DATABASE ---")
try:
    cust_response = supabase.table('customers_blaze').select('*').or_(
        f'phone.eq.{phone},phone.eq.{phone[2:]},phone.eq.2096288371'
    ).execute()
    
    if cust_response.data:
        print(f"FOUND {len(cust_response.data)} customer(s)!")
        for c in cust_response.data:
            print(f"\nName: {c.get('name', 'N/A')}")
            print(f"Phone: {c.get('phone', 'N/A')}")
            print(f"Email: {c.get('email', 'N/A')}")
            print(f"Lifetime Value: ${c.get('lifetime_value', 0)}")
            print(f"Total Visits: {c.get('total_visits', 0)}")
    else:
        print("Not found in customers")
except Exception as e:
    print(f"Error: {e}")

print("\n--- MESSAGE CONTENT (ID: 875) ---")
try:
    msg_response = supabase.table('messages').select('*').eq('id', msg_id).execute()
    
    if msg_response.data:
        msg = msg_response.data[0]
        print(f"From: {msg.get('phone_number', 'N/A')}")
        print(f"Direction: {msg.get('direction', 'N/A')}")
        print(f"Status: {msg.get('status', 'N/A')}")
        print(f"Timestamp: {msg.get('timestamp', 'N/A')}")
        print(f"\nContent:\n{msg.get('content', 'N/A')}")
    else:
        print("Message not found")
except Exception as e:
    print(f"Error: {e}")

print(f"\n{'='*60}\n")

# Try alternate formats
print("--- CHECKING ALTERNATE FORMATS ---")
alternates = [
    "2096288371",
    "(209) 628-8371",
    "209-628-8371",
    "1-209-628-8371",
    "+1 209-628-8371"
]

for alt in alternates:
    print(f"\nTrying: {alt}")
    try:
        bt = supabase.table('budtenders').select('name,phone').ilike('phone', f'%{alt}%').execute()
        if bt.data:
            print(f"  FOUND in budtenders: {bt.data[0].get('name')}")
        
        cust = supabase.table('customers_blaze').select('name,phone').ilike('phone', f'%{alt}%').execute()
        if cust.data:
            print(f"  FOUND in customers: {cust.data[0].get('name')}")
    except:
        pass

