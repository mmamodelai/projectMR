#!/usr/bin/env python3
"""Check if Windows is intercepting messages from specific numbers"""

import serial
import time
import sys

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("CHECKING FOR WINDOWS MESSAGE INTERCEPTION")
print("="*70 + "\n")

print("This script will:")
print("1. Set CNMI to prevent Windows interception")
print("2. Monitor modem for 30 seconds")
print("3. Check if messages arrive but disappear")
print("\nSend a test message NOW from 619-977-3020...\n")

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected to modem\n")
    
    # Set text mode
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Set storage to ME
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Set CNMI to store messages (prevent Windows interception)
    print("Setting CNMI to 1,1,0,0,0 (store messages, prevent Windows)...")
    ser.write(b'AT+CNMI=1,1,0,0,0\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Save configuration
    ser.write(b'AT&W\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Monitor for 30 seconds
    print("Monitoring modem for 30 seconds...")
    print("Send a test message from 619-977-3020 NOW!\n")
    
    for i in range(30):
        time.sleep(1)
        
        # Check for messages every 5 seconds
        if i % 5 == 0:
            ser.write(b'AT+CMGL="ALL"\r\n')
            time.sleep(1)
            response = ser.read_all().decode('utf-8', errors='ignore')
            
            if '+CMGL:' in response:
                print(f"[{i}s] MESSAGE FOUND ON MODEM!")
                print(response[:500])
                print("\n")
            else:
                print(f"[{i}s] No messages on modem...")
    
    # Final check
    print("\nFinal check...")
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(1)
    response = ser.read_all().decode('utf-8', errors='ignore')
    
    if '+CMGL:' in response:
        print("[FOUND] Message is on modem!")
        print(response)
    else:
        print("[NOT FOUND] Message never arrived on modem")
        print("\nPossible causes:")
        print("1. Message routed to Windows instead")
        print("2. Message blocked by carrier")
        print("3. Modem not receiving from that number")
        print("4. Windows Messaging app intercepting")
    
    ser.close()
    print("\n[OK] Done")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect: {e}")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

