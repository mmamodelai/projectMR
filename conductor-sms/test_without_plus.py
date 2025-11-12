#!/usr/bin/env python3
"""
Test sending SMS WITHOUT the + prefix
"""
import serial
import time

COM_PORT = "COM24"

ser = serial.Serial(COM_PORT, 115200, timeout=5)

# Set text mode
ser.write(b'AT+CMGF=1\r\n')
time.sleep(1)
ser.read_all()

# Send WITHOUT + prefix
ser.write(b'AT+CMGS="16199773020"\r\n')
time.sleep(0.5)
ser.write(b'TEST WITHOUT PLUS SIGN - Did this work?\x1A')
time.sleep(3)
response = ser.read_all().decode('utf-8', errors='ignore')
print('Modem Response:')
print(response)

ser.close()
print('\nSent to 16199773020 WITHOUT + prefix')
print('Check your phone!')


