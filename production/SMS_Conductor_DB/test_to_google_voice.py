#!/usr/bin/env python3
"""
Test SMS send to Google Voice number
"""
import serial
import time

COM_PORT = "COM24"
GOOGLE_VOICE = "+16198004766"

ser = serial.Serial(COM_PORT, 115200, timeout=5)

# Set text mode
ser.write(b'AT+CMGF=1\r\n')
time.sleep(1)
ser.read_all()

# Send message
print(f"Sending test message to Google Voice {GOOGLE_VOICE}...")
ser.write(f'AT+CMGS="{GOOGLE_VOICE}"\r\n'.encode())
time.sleep(0.5)
ser.write(b'GOOGLE VOICE TEST - Check if this arrives at your Google Voice number!\x1A')

# Wait for response
print("\nWaiting for modem response...")
time.sleep(3)
response = ser.read_all().decode('utf-8', errors='ignore')
print("Modem Response:")
print(response)

if '+CMGS:' in response and 'OK' in response:
    print("\n SUCCESS - Modem confirmed send")
    print(f"Check your Google Voice app/inbox for: {GOOGLE_VOICE}")
else:
    print("\n ERROR - Modem did not confirm send")

ser.close()


