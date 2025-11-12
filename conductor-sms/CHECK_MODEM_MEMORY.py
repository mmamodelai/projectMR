#!/usr/bin/env python3
"""
Check Modem Memory - Direct check of onboard memory
"""

import serial
import time

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("CHECKING MODEM ONBOARD MEMORY")
print("="*70 + "\n")

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected to modem\n")
    
    # Set text mode
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Check CNMI setting
    print("CNMI Setting:")
    ser.write(b'AT+CNMI?\r\n')
    time.sleep(0.5)
    cnmi = ser.read_all().decode('utf-8', errors='ignore')
    print(cnmi.strip())
    print()
    
    # Check ME (Phone Memory) storage
    print("ME (Phone Memory) Storage:")
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    cpms_me = ser.read_all().decode('utf-8', errors='ignore')
    print(cpms_me.strip())
    
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(1)
    msgs_me = ser.read_all().decode('utf-8', errors='ignore')
    
    if '+CMGL:' in msgs_me:
        print("\n[MESSAGES FOUND IN ME STORAGE]")
        print(msgs_me[:800])
    else:
        print("[NO MESSAGES IN ME STORAGE]")
    print()
    
    # Check SIM storage
    print("SIM (SM) Storage:")
    ser.write(b'AT+CPMS="SM","SM","SM"\r\n')
    time.sleep(0.5)
    cpms_sm = ser.read_all().decode('utf-8', errors='ignore')
    print(cpms_sm.strip())
    
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(1)
    msgs_sm = ser.read_all().decode('utf-8', errors='ignore')
    
    if '+CMGL:' in msgs_sm:
        print("\n[MESSAGES FOUND IN SIM STORAGE]")
        print(msgs_sm[:800])
    else:
        print("[NO MESSAGES IN SIM STORAGE]")
    print()
    
    ser.close()
    print("[OK] Check complete")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect: {e}")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

