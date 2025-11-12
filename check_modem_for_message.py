#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check if message is stuck on modem"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import serial
import time

COM_PORT = "COM24"
BAUDRATE = 115200

print("="*80)
print("CHECKING MODEM FOR STUCK MESSAGES")
print("="*80)

try:
    ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
    print(f"✅ Connected to {COM_PORT}")
    
    # Set text mode
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(1)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"\nText mode: {response.strip()}")
    
    # List all messages
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)
    response = ser.read_all().decode('utf-8', errors='ignore')
    
    print(f"\nMessages on modem:")
    print("="*80)
    print(response)
    print("="*80)
    
    # Count messages
    msg_count = response.count('+CMGL:')
    print(f"\nTotal messages on modem: {msg_count}")
    
    if "points" in response.lower():
        print("✅ FOUND MESSAGE WITH 'POINTS' ON MODEM!")
        print("⚠️ This message was NOT read by Conductor!")
    else:
        print("❌ Message with 'points' not found on modem")
    
    ser.close()
except Exception as e:
    print(f"❌ Error: {e}")

