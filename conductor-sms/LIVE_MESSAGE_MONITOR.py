#!/usr/bin/env python3
"""
LIVE MESSAGE MONITOR - Debug incoming messages in real-time
Send a test message NOW and watch what happens
"""

import serial
import time

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("LIVE MESSAGE MONITOR - DEBUGGING INCOMING MESSAGES")
print("="*70)
print("\n>>> SEND A TEST MESSAGE FROM YOUR PHONE NOW!")
print("   Monitoring modem for 60 seconds...\n")

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected to modem\n")
    
    # Set text mode
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Set storage to ME
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    # Set CNMI to 1,1,0,0,0 (working version)
    print("Setting CNMI to 1,1,0,0,0...")
    ser.write(b'AT+CNMI=1,1,0,0,0\r\n')
    time.sleep(0.5)
    resp = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {resp.strip()}\n")
    
    # Save config
    ser.write(b'AT&W\r\n')
    time.sleep(0.5)
    ser.read_all()
    
    print("Monitoring modem every 2 seconds...\n")
    print("-" * 70)
    
    message_found = False
    
    for i in range(30):  # 60 seconds total
        time.sleep(2)
        
        # Check ME storage
        ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
        time.sleep(0.5)
        cpms_resp = ser.read_all().decode('utf-8', errors='ignore')
        
        # Read messages
        ser.write(b'AT+CMGL="ALL"\r\n')
        time.sleep(1)
        cmgl_resp = ser.read_all().decode('utf-8', errors='ignore')
        
        # Check CNMI setting
        ser.write(b'AT+CNMI?\r\n')
        time.sleep(0.5)
        cnmi_resp = ser.read_all().decode('utf-8', errors='ignore')
        
        timestamp = time.strftime("%H:%M:%S")
        
        if '+CMGL:' in cmgl_resp:
            print(f"\n[{timestamp}] 🎉 MESSAGE FOUND ON MODEM!")
            print(f"CPMS: {cpms_resp.strip()}")
            print(f"CNMI: {cnmi_resp.strip()}")
            print(f"Messages:\n{cmgl_resp[:500]}")
            message_found = True
            break
        elif i % 5 == 0:  # Every 10 seconds
            print(f"[{timestamp}] Checking... CPMS: {cpms_resp.strip()[:50]} | CNMI: {cnmi_resp.strip()[:30]} | No messages")
    
    if not message_found:
        print("\n" + "="*70)
        print("❌ NO MESSAGES FOUND AFTER 60 SECONDS")
        print("="*70)
        print("\nPossible causes:")
        print("1. Message not sent yet (check your phone)")
        print("2. Windows Messaging app intercepting (check Windows)")
        print("3. Carrier routing issue (message not delivered)")
        print("4. Modem not receiving (check signal)")
        print("\nChecking Windows Messaging app...")
        print("   Go to: Settings > Apps > Messaging")
        print("   Disable or uninstall if possible")
    
    ser.close()
    print("\n[OK] Monitor complete")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect: {e}")
    print("Make sure Conductor is stopped!")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

