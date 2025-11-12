#!/usr/bin/env python3
"""
Reset modem and verify functionality
"""
import serial
import time

COM_PORT = "COM24"

def send_at(ser, cmd, timeout=2):
    """Send AT command and return response"""
    print(f"  > {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(timeout)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"  < {response.strip()}\n")
    return response

def main():
    print("\n=== Modem Reset & Verification ===\n")
    ser = serial.Serial(COM_PORT, 115200, timeout=5)
    time.sleep(1)
    
    print("1. Soft reset modem...")
    send_at(ser, "AT+CFUN=1,1", timeout=5)
    print("   Waiting 10 seconds for modem to restart...")
    time.sleep(10)
    
    print("2. Reconnecting...")
    ser.close()
    time.sleep(2)
    ser = serial.Serial(COM_PORT, 115200, timeout=5)
    time.sleep(2)
    
    print("3. Testing modem...")
    send_at(ser, "AT")
    
    print("4. Checking registration...")
    send_at(ser, "AT+CREG?")
    
    print("5. Checking network...")
    send_at(ser, "AT+COPS?")
    
    print("6. Checking signal...")
    send_at(ser, "AT+CSQ")
    
    print("7. Setting SMS mode...")
    send_at(ser, "AT+CMGF=1")
    send_at(ser, 'AT+CPMS="SM","SM","SM"')
    send_at(ser, "AT+CNMI=2,0,0,0,0")
    send_at(ser, "AT&W")
    
    print("8. Checking for messages...")
    response = send_at(ser, 'AT+CMGL="ALL"', timeout=3)
    
    if "+CMGL:" in response:
        print("\n[+] MESSAGES FOUND!")
    else:
        print("\n[-] No messages on SIM")
    
    ser.close()
    print("\n=== Reset Complete ===")
    print("\nNow try:")
    print("1. Send a text to 619-558-7489")
    print("2. Wait 30 seconds")
    print("3. Run this script again to check")

if __name__ == "__main__":
    main()

