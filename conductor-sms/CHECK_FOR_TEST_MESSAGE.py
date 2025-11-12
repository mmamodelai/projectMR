#!/usr/bin/env python3
import serial
import time

print("\nChecking modem for REAL TEST 1624...")
try:
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            break
        except:
            time.sleep(0.5)
    
    time.sleep(1)
    ser.write(b"AT+CMGF=1\r\n")
    time.sleep(0.5)
    ser.read_all()
    
    # Check ME storage
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    resp = ser.read_all().decode('utf-8', errors='ignore')
    print("\nME Storage:", resp)
    
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)
    resp = ser.read_all().decode('utf-8', errors='ignore')
    print("\nME Messages:", resp)
    
    if "REAL TEST" in resp:
        print("\n✓ MESSAGE FOUND IN ME!")
    else:
        print("\n✗ Not in ME, checking SM...")
        ser.write(b'AT+CPMS="SM","SM","SM"\r\n')
        time.sleep(0.5)
        ser.read_all()
        
        ser.write(b'AT+CMGL="ALL"\r\n')
        time.sleep(2)
        resp = ser.read_all().decode('utf-8', errors='ignore')
        print("\nSM Messages:", resp)
        
        if "REAL TEST" in resp:
            print("\n✓ MESSAGE FOUND IN SM!")
        else:
            print("\n✗ MESSAGE NOT ON MODEM AT ALL")
    
    ser.close()
except Exception as e:
    print(f"Error: {e}")

