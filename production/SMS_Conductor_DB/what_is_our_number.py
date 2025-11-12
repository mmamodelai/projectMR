#!/usr/bin/env python3
"""
Query modem to find out OUR phone number
"""
import serial
import time
import re

COM_PORT = "COM24"
BAUDRATE = 115200

def send_at(ser, command, wait=1.0):
    """Send AT command and return response"""
    print(f">> {command}")
    ser.write(f"{command}\r\n".encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"<< {response.strip()}")
    return response

print("\n" + "="*60)
print("WHAT IS OUR PHONE NUMBER?")
print("="*60)

try:
    # Try to connect (might be busy if Conductor is polling)
    print("\nAttempting to connect to modem...")
    print("(May need to wait if Conductor is polling...)")
    
    for attempt in range(5):
        try:
            ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
            print("\n[OK] Connected to modem")
            break
        except serial.SerialException:
            if attempt < 4:
                print(f"  Busy, waiting... ({attempt+1}/5)")
                time.sleep(2)
            else:
                raise
    
    time.sleep(1)
    
    # Test modem
    response = send_at(ser, "AT")
    if "OK" not in response:
        print("\n[ERROR] Modem not responding")
        ser.close()
        exit(1)
    
    # Query SIM phone number
    print("\n=== QUERYING SIM CARD ===")
    response = send_at(ser, "AT+CNUM", 2)
    
    # Parse phone number from response
    # Format: +CNUM: "","<number>",<type>
    if "+CNUM:" in response:
        match = re.search(r'\+CNUM:.*?"([+\d]+)"', response)
        if match:
            our_number = match.group(1)
            print(f"\n" + "="*60)
            print(f"OUR NUMBER: {our_number}")
            print("="*60)
        else:
            print("\n[WARNING] Phone number not found in SIM")
            print("SIM may not have number stored")
            print("\nCheck with carrier or recent inbound message 'To:' field")
    else:
        print("\n[WARNING] AT+CNUM not supported or SIM issue")
        print("\nAlternative: Check recent INBOUND messages")
        print("Customers are texting TO our number")
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    print("\nAlternative methods to find our number:")
    print("1. Check SIM card packaging")
    print("2. Look at recent inbound messages (they texted TO our number)")
    print("3. Check Mint Mobile account")
    print()

print()

