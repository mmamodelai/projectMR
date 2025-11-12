#!/usr/bin/env python3
"""
Test actual SMS sending and capture full modem response
"""
import serial
import time

# Test sending an SMS and capture the full response
COM_PORT = "COM24"
PHONE = "+16199773020"  # Your phone
MESSAGE = "TEST from manual script - checking if SMS actually sends"

try:
    print(f"\n=== Manual SMS Send Test ===\n")
    print(f"Opening {COM_PORT}...")
    ser = serial.Serial(COM_PORT, 115200, timeout=5)
    time.sleep(0.5)
    
    # Set text mode
    print("Setting text mode (AT+CMGF=1)...")
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {repr(response)}")
    
    # Send message
    print(f"\nSending SMS to {PHONE}...")
    print(f"Message: {MESSAGE}")
    ser.write(f'AT+CMGS="{PHONE}"\r\n'.encode())
    time.sleep(0.5)
    prompt_response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"After CMGS command: {repr(prompt_response)}")
    
    # Send message body + Ctrl+Z
    print("\nSending message content...")
    ser.write((MESSAGE + '\x1A').encode())
    
    # Wait for response (up to 30 seconds)
    print("\nWaiting for modem response...")
    response = ""
    start_time = time.time()
    while time.time() - start_time < 30:
        if ser.in_waiting:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            response += data
            print(f"[{time.time() - start_time:.1f}s] Received: {repr(data)}")
            
            if 'OK' in response:
                print("\n✅ SUCCESS! Modem returned OK")
                break
            elif 'ERROR' in response:
                print("\n❌ FAILED! Modem returned ERROR")
                break
        time.sleep(0.1)
    
    if 'OK' not in response and 'ERROR' not in response:
        print("\n⚠️ TIMEOUT! No OK or ERROR received from modem")
    
    print(f"\n=== Full Response ===")
    print(response)
    print(f"\n=== Response Length: {len(response)} bytes ===")
    
    ser.close()
    print("\nPort closed.")
    
except Exception as e:
    print(f"\n❌ Exception: {e}")



