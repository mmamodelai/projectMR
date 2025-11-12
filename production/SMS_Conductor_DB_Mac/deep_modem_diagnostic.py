#!/usr/bin/env python3
"""
Deep modem diagnostic - check ALL SMS settings
Since SIM works in phone but not modem, this is a modem config issue
"""
import serial
import time
import sys

def send_at(ser, cmd, wait=0.5):
    """Send AT command and return response"""
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    return response

try:
    print("\n=== DEEP MODEM DIAGNOSTIC ===\n")
    print("SIM works in phone but NOT in modem = MODEM CONFIG ISSUE\n")
    
    ser = serial.Serial('COM24', 115200, timeout=5)
    time.sleep(0.5)
    
    # Basic info
    print("1. BASIC INFO")
    print("-" * 60)
    print("Manufacturer:", send_at(ser, 'AT+CGMI').strip())
    print("Model:", send_at(ser, 'AT+CGMM').strip())
    print("Firmware:", send_at(ser, 'AT+CGMR').strip())
    
    # Network status
    print("\n2. NETWORK STATUS")
    print("-" * 60)
    print("Signal Strength:", send_at(ser, 'AT+CSQ').strip())
    print("Network Registration:", send_at(ser, 'AT+CREG?').strip())
    print("Operator:", send_at(ser, 'AT+COPS?').strip())
    
    # SMS Configuration
    print("\n3. SMS CONFIGURATION")
    print("-" * 60)
    print("SMS Format:", send_at(ser, 'AT+CMGF?').strip())
    print("SMS Service:", send_at(ser, 'AT+CSMS?').strip())
    print("SMS Center (SMSC):", send_at(ser, 'AT+CSCA?').strip())
    print("Service for MO SMS:", send_at(ser, 'AT+CGSMS?').strip())
    print("SMS Status Report:", send_at(ser, 'AT+CSMP?').strip())
    print("More Messages to Send:", send_at(ser, 'AT+CMMS?').strip())
    
    # Message storage
    print("\n4. MESSAGE STORAGE")
    print("-" * 60)
    print("Current Storage:", send_at(ser, 'AT+CPMS?').strip())
    
    # Check stored messages
    send_at(ser, 'AT+CMGF=1')  # Text mode
    print("\nChecking stored messages...")
    messages = send_at(ser, 'AT+CMGL="ALL"', wait=2)
    if '+CMGL:' in messages:
        print("FOUND STORED MESSAGES:")
        print(messages[:500])  # First 500 chars
    else:
        print("No stored messages")
    
    # Check if there are any pending sends
    print("\n5. CHECKING FOR ISSUES")
    print("-" * 60)
    
    # Try to get error codes
    print("Extended Error Codes:", send_at(ser, 'AT+CMEE=2').strip())
    
    # Check SMS parameters
    print("SMS Parameters (CSMP):", send_at(ser, 'AT+CSMP?').strip())
    
    # Check if modem is in test mode or restricted
    print("Phone Functionality:", send_at(ser, 'AT+CFUN?').strip())
    
    print("\n6. RECOMMENDED FIXES")
    print("-" * 60)
    
    # Check CGSMS setting
    cgsms_response = send_at(ser, 'AT+CGSMS?')
    if '+CGSMS: 1' in cgsms_response:
        print("⚠️  FOUND ISSUE: CGSMS=1 (GSM only)")
        print("   Fix: Change to CGSMS=3 (GPRS/LTE preferred)")
        print("   Command: AT+CGSMS=3")
    
    # Check if SMS delivery reports are enabled
    csmp_response = send_at(ser, 'AT+CSMP?')
    print(f"\n   Current CSMP: {csmp_response.strip()}")
    if '17,167' not in csmp_response and '49,167' not in csmp_response:
        print("   ⚠️  Delivery reports may not be requested")
        print("   Fix: AT+CSMP=17,167,0,0 (request delivery report)")
    
    ser.close()
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC COMPLETE")
    print("=" * 60)
    
except serial.SerialException as e:
    print(f"\n❌ Cannot access COM24: {e}")
    print("\nIs conductor running? If so, stop it first:")
    print("  Get-Process python | Stop-Process")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)



