#!/usr/bin/env python3
"""Emergency check for incoming messages on modem"""

import serial
import time
import sys

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*60)
print("EMERGENCY INCOMING MESSAGE CHECK")
print("="*60 + "\n")

try:
    print(f"Connecting to {COM_PORT}...")
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("Connected!\n")
    
    # Check modem is responding
    ser.write(b'AT\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    if 'OK' not in response:
        print(f"ERROR: Modem not responding! Response: {response}")
        ser.close()
        sys.exit(1)
    print("Modem responding OK\n")
    
    # Set text mode
    print("Setting text mode...")
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Set storage to ME
    print("Setting storage to ME...")
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Check current CNMI setting
    print("Checking CNMI setting...")
    ser.write(b'AT+CNMI?\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"CNMI Setting: {response.strip()}\n")
    
    # Set CNMI to keep messages
    print("Setting CNMI to keep messages (1,1,0,0,0)...")
    ser.write(b'AT+CNMI=1,1,0,0,0\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Check storage capacity
    print("Checking storage capacity...")
    ser.write(b'AT+CPMS?\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Storage: {response.strip()}\n")
    
    # Read ALL messages
    print("Reading ALL messages from modem...")
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)  # Give it more time
    response = ser.read_all().decode('utf-8', errors='ignore')
    
    print("\n" + "="*60)
    print("MODEM RESPONSE:")
    print("="*60)
    print(response)
    print("="*60 + "\n")
    
    # Check if messages found
    if '+CMGL:' in response:
        lines = response.split('\n')
        msg_count = sum(1 for line in lines if '+CMGL:' in line)
        print(f"✅ FOUND {msg_count} MESSAGE(S) ON MODEM!\n")
        
        # Parse and show first message
        for i, line in enumerate(lines):
            if '+CMGL:' in line:
                print(f"Message {i+1}:")
                print(f"  Header: {line.strip()}")
                if i+1 < len(lines):
                    print(f"  Content: {lines[i+1].strip()}")
                print()
    else:
        print("❌ NO MESSAGES FOUND ON MODEM")
        print("\nPossible issues:")
        print("1. Messages were auto-deleted before Conductor could read them")
        print("2. Messages are stored in SIM instead of ME")
        print("3. Modem storage is full and messages were deleted")
        print("4. CNMI setting is wrong (should be 1,1,0,0,0)")
        print()
    
    ser.close()
    print("Disconnected from modem.")
    
except serial.SerialException as e:
    print(f"\n❌ ERROR: Cannot connect to modem!")
    print(f"Error: {e}")
    print("\nCheck:")
    print("1. Is modem connected to COM24?")
    print("2. Is another program using the modem?")
    print("3. Is Conductor running? (It might be holding the port)")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
