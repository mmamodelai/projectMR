#!/usr/bin/env python3
"""
Test sending SMS directly through modem to diagnose the issue
"""
import serial
import time

COM_PORT = "COM24"
PHONE = "+16199773020"
MESSAGE = "DIRECT MODEM TEST - If you get this, modem works!"

print("=" * 80)
print("TESTING MODEM SEND DIRECTLY")
print("=" * 80)

try:
    ser = serial.Serial(COM_PORT, 115200, timeout=5)
    time.sleep(1)
    
    print("\n1. Testing modem response...")
    ser.write(b"AT\r\n")
    time.sleep(0.5)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Response: {response}")
    
    if "OK" not in response:
        print("ERROR: Modem not responding to AT command")
        ser.close()
        exit(1)
    
    print("\n2. Setting text mode...")
    ser.write(b"AT+CMGF=1\r\n")
    time.sleep(0.5)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"Response: {response}")
    
    print(f"\n3. Sending SMS to {PHONE}...")
    print(f"Message: {MESSAGE}")
    
    # Send AT+CMGS command
    ser.write(f'AT+CMGS="{PHONE}"\r\n'.encode())
    time.sleep(0.5)
    response = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
    print(f"After CMGS command: {response}")
    
    if ">" not in response:
        print("ERROR: Modem didn't show '>' prompt")
        ser.close()
        exit(1)
    
    print("Got '>' prompt, sending message...")
    
    # Send message content + Ctrl+Z
    ser.write((MESSAGE + "\x1A").encode())
    
    # Wait for confirmation
    print("Waiting for modem to send...")
    time.sleep(10)  # Give it time
    
    response = ""
    while ser.in_waiting:
        response += ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
        time.sleep(0.1)
    
    print(f"Final response: {response}")
    
    if "OK" in response:
        print("\nSUCCESS: Modem said OK!")
        print("Check your phone for: 'DIRECT MODEM TEST'")
    elif "ERROR" in response:
        print("\nERROR: Modem returned error")
    else:
        print("\nUNKNOWN: Timeout or unexpected response")
    
    ser.close()
    
except Exception as e:
    print(f"\nEXCEPTION: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)


