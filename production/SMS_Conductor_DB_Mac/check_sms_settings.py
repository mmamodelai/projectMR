#!/usr/bin/env python3
"""
Check modem SMS configuration settings
"""
import serial
import time

COM_PORT = "COM24"

ser = serial.Serial(COM_PORT, 115200, timeout=5)

commands = [
    ('Service Center Number', 'AT+CSCA?'),
    ('SMS Parameters', 'AT+CSMP?'),
    ('Message Format', 'AT+CMGF?'),
    ('Show Text Mode Parameters', 'AT+CSDH?'),
    ('Validity Period', 'AT+CSAS?'),
]

print("SMS MODEM CONFIGURATION")
print("=" * 60)

for name, cmd in commands:
    print(f"\n{name} ({cmd}):")
    ser.write(f'{cmd}\r\n'.encode())
    time.sleep(1)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(response)

ser.close()


