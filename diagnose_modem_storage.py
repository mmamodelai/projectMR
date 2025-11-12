#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Diagnose modem message storage settings"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import serial
import time

COM_PORT = "COM24"
BAUDRATE = 115200

def send_at(ser, cmd, timeout=2):
    """Send AT command and get response"""
    print(f"\n→ {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(timeout)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"← {response}")
    return response

print("="*80)
print("MODEM STORAGE DIAGNOSTIC")
print("="*80)

# Wait for Conductor to release port
print("\nWaiting 10 seconds for Conductor to release port...")
time.sleep(10)

try:
    ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
    print(f"✅ Connected to {COM_PORT}")
    
    # 1. Check current storage settings
    print("\n1. CHECKING CURRENT STORAGE SETTINGS")
    print("-" * 40)
    send_at(ser, "AT+CPMS?")
    
    # 2. Check if we can list messages from different storages
    print("\n2. LISTING MESSAGES FROM PHONE MEMORY (ME)")
    print("-" * 40)
    send_at(ser, 'AT+CPMS="ME","ME","ME"')  # Set to phone memory
    send_at(ser, 'AT+CMGL="ALL"', timeout=3)
    
    print("\n3. LISTING MESSAGES FROM SIM CARD (SM)")
    print("-" * 40)
    send_at(ser, 'AT+CPMS="SM","SM","SM"')  # Set to SIM
    send_at(ser, 'AT+CMGL="ALL"', timeout=3)
    
    # 3. Check message format settings
    print("\n4. CHECKING MESSAGE FORMAT")
    print("-" * 40)
    send_at(ser, "AT+CMGF?")  # Should be 1 for text mode
    
    # 4. Check new message indication settings
    print("\n5. CHECKING NEW MESSAGE NOTIFICATIONS")
    print("-" * 40)
    send_at(ser, "AT+CNMI?")
    
    # 5. Check if messages are being deleted automatically
    print("\n6. CHECKING AUTO-DELETE SETTINGS")
    print("-" * 40)
    send_at(ser, "AT+CSMS?")
    
    # 6. Set back to default storage
    print("\n7. RESTORING DEFAULT STORAGE")
    print("-" * 40)
    send_at(ser, 'AT+CPMS="ME","ME","ME"')
    
    ser.close()
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80)
    
except serial.SerialException as e:
    print(f"❌ Error: {e}")
    print("\n⚠️ Conductor is holding the port. Stop Conductor first!")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

