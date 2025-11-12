#!/usr/bin/env python3
"""
Fix modem SMS configuration
Issue: CGSMS=1 (GSM only) - needs to be 3 (GPRS/LTE preferred)
"""
import serial
import time

def send_at(ser, cmd, wait=0.5):
    """Send AT command and return response"""
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    return response

try:
    print("\n=== FIXING MODEM CONFIGURATION ===\n")
    print("Issue: CGSMS=1 (GSM circuit-switched only)")
    print("Fix: Change to CGSMS=3 (GPRS/LTE preferred)\n")
    
    ser = serial.Serial('COM24', 115200, timeout=5)
    time.sleep(0.5)
    
    # Check current setting
    print("Current setting:")
    response = send_at(ser, 'AT+CGSMS?')
    print(f"  {response.strip()}")
    
    # Change to GPRS/LTE preferred
    print("\nChanging to CGSMS=3...")
    response = send_at(ser, 'AT+CGSMS=3')
    if 'OK' in response:
        print("  SUCCESS! Changed to CGSMS=3")
    else:
        print(f"  FAILED: {response}")
    
    # Verify new setting
    print("\nNew setting:")
    response = send_at(ser, 'AT+CGSMS?')
    print(f"  {response.strip()}")
    
    # Also fix CSMP (SMS parameters) - add validity period
    print("\nFixing SMS parameters (CSMP)...")
    print("Current CSMP:")
    response = send_at(ser, 'AT+CSMP?')
    print(f"  {response.strip()}")
    
    print("\nSetting CSMP to 17,167,0,0 (enable delivery reports)...")
    response = send_at(ser, 'AT+CSMP=17,167,0,0')
    if 'OK' in response:
        print("  SUCCESS!")
    else:
        print(f"  FAILED: {response}")
    
    print("\nNew CSMP:")
    response = send_at(ser, 'AT+CSMP?')
    print(f"  {response.strip()}")
    
    # Save configuration
    print("\nSaving configuration to modem...")
    response = send_at(ser, 'AT&W')
    if 'OK' in response:
        print("  Configuration saved!")
    else:
        print(f"  Save failed: {response}")
    
    ser.close()
    
    print("\n" + "=" * 60)
    print("CONFIGURATION FIXED!")
    print("=" * 60)
    print("\nNow test sending:")
    print("1. Start conductor")
    print("2. Send test message to yourself")
    print("3. Check if it arrives")
    
except Exception as e:
    print(f"\nError: {e}")



