#!/usr/bin/env python3
"""
Test SMS send with delivery report enabled
"""
import serial
import time

COM_PORT = "COM24"

ser = serial.Serial(COM_PORT, 115200, timeout=5)

# Enable delivery reports
print("Enabling delivery reports...")
ser.write(b'AT+CNMI=2,1,2,1,0\r\n')
time.sleep(1)
response = ser.read_all().decode('utf-8', errors='ignore')
print(response)

# Set text mode
ser.write(b'AT+CMGF=1\r\n')
time.sleep(1)
ser.read_all()

# Send message
print("\nSending test message with delivery report...")
ser.write(b'AT+CMGS="+16199773020"\r\n')
time.sleep(0.5)
ser.write(b'DELIVERY REPORT TEST - Did this arrive?\x1A')

# Wait longer for response and delivery report
print("\nWaiting for send confirmation...")
time.sleep(5)
response = ser.read_all().decode('utf-8', errors='ignore')
print("Response:")
print(response)

# Wait for delivery report (can take 30+ seconds)
print("\nWaiting for delivery report (30 seconds)...")
time.sleep(30)
response = ser.read_all().decode('utf-8', errors='ignore')
if response.strip():
    print("Delivery Report:")
    print(response)
else:
    print("No delivery report received")

ser.close()


