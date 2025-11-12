#!/usr/bin/env python3
"""Quick check of CNMI setting"""
import serial
import time

try:
    ser = serial.Serial("COM24", 115200, timeout=5)
    time.sleep(1)
    ser.write(b"AT+CNMI?\r\n")
    time.sleep(1)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(response)
    ser.close()
    
    if "+CNMI: 2,0" in response:
        print("\n[BAD] CNMI=2,0 - Modem is AUTO-DELETING messages!")
        print("This is the bug! Messages arrive but get deleted immediately.")
    elif "+CNMI: 1,1" in response:
        print("\n[GOOD] CNMI=1,1 - Correct setting")
    else:
        print("\n[UNKNOWN] Check the response above")
except Exception as e:
    print(f"Error: {e}")

