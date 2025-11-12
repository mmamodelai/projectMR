#!/usr/bin/env python3
"""Check phone number formats from modem and database"""

import sqlite3
import serial
import time

COM_PORT = "COM24"
DB_PATH = "database/olive_sms.db"

print("\n" + "="*70)
print("CHECKING PHONE NUMBER FORMATS")
print("="*70 + "\n")

# Check database formats
print("[1] Checking phone number formats in database...")
try:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute("""
        SELECT DISTINCT phone_number 
        FROM messages 
        WHERE phone_number LIKE '%619%' 
           OR phone_number LIKE '%977%'
           OR phone_number LIKE '%3020%'
        LIMIT 20
    """)
    db_numbers = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if db_numbers:
        print(f"Found {len(db_numbers)} phone numbers in DB:")
        for num in db_numbers:
            print(f"  {num}")
    else:
        print("No matching numbers found in DB")
except Exception as e:
    print(f"Error checking DB: {e}")

print("\n[2] Checking what modem sends...")
try:
    ser = serial.Serial(COM_PORT, 115200, timeout=5)
    time.sleep(1)
    
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)
    response = ser.read_all().decode('utf-8', errors='ignore')
    ser.close()
    
    # Extract phone numbers from +CMGL response
    import re
    pattern = r'\+CMGL:\s*\d+,"[^"]+","([^"]+)"'
    matches = re.findall(pattern, response)
    
    if matches:
        print(f"Found {len(matches)} phone numbers in modem response:")
        for phone in set(matches):
            print(f"  {phone}")
    else:
        print("No messages found on modem")
        print("\nRaw response (first 500 chars):")
        print(response[:500])
        
except Exception as e:
    print(f"Error checking modem: {e}")

print("\n[3] Testing normalization...")
def normalize_phone_number(phone):
    if not phone or not isinstance(phone, str):
        return phone
    digits = ''.join(filter(str.isdigit, phone))
    if len(digits) == 11 and digits[0] == '1':
        return '+' + digits
    if len(digits) == 10:
        return '+1' + digits
    if phone.startswith('+'):
        return phone
    return phone

test_formats = ['+16199773020', '16199773020', '6199773020', '(619) 977-3020', '619-977-3020']
print("\nNormalization test:")
for fmt in test_formats:
    norm = normalize_phone_number(fmt)
    print(f"  {fmt:20} -> {norm}")

print("\n" + "="*70)
print("DIAGNOSIS:")
print("="*70)

# Check if there's a mismatch
if db_numbers:
    db_formats = set([normalize_phone_number(n) for n in db_numbers])
    print(f"Database formats normalize to: {db_formats}")
    
    if len(db_formats) > 1:
        print("WARNING: Multiple formats in database!")
    else:
        print("OK: All database numbers normalize to same format")

print("\nDone!")

