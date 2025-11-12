#!/usr/bin/env python3
"""
Check Modem Status - Signal, phone number, network registration
"""

import serial
import time

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("MODEM STATUS CHECK")
print("="*70 + "\n")

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected to modem\n")
    
    # Check signal strength
    print("Signal Strength:")
    ser.write(b'AT+CSQ\r\n')
    time.sleep(0.5)
    csq = ser.read_all().decode('utf-8', errors='ignore')
    print(csq.strip())
    print()
    
    # Check network registration
    print("Network Registration:")
    ser.write(b'AT+CREG?\r\n')
    time.sleep(0.5)
    creg = ser.read_all().decode('utf-8', errors='ignore')
    print(creg.strip())
    print()
    
    # Check phone number
    print("Phone Number (CNUM):")
    ser.write(b'AT+CNUM\r\n')
    time.sleep(0.5)
    cnum = ser.read_all().decode('utf-8', errors='ignore')
    print(cnum.strip())
    print()
    
    # Check SIM status
    print("SIM Status:")
    ser.write(b'AT+CPIN?\r\n')
    time.sleep(0.5)
    cpin = ser.read_all().decode('utf-8', errors='ignore')
    print(cpin.strip())
    print()
    
    ser.close()
    print("[OK] Status check complete")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect: {e}")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

