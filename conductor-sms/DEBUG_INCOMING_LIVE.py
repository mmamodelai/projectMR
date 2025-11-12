#!/usr/bin/env python3
"""
LIVE DEBUG - Check both SIM and ME storage for incoming messages
"""

import serial
import time

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("LIVE INCOMING MESSAGE DEBUG")
print("="*70)
print("\n>>> SEND A TEST MESSAGE FROM YOUR PHONE RIGHT NOW!")
print("   Monitoring for 60 seconds...\n")

try:
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected to modem\n")
    
    # Set text mode
    ser.write(b'AT+CMGF=1\r\n')
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
    
    print("Checking BOTH SIM (SM) and ME storage every 3 seconds...\n")
    print("-" * 70)
    
    message_found = False
    
    for i in range(20):  # 60 seconds total
        time.sleep(3)
        timestamp = time.strftime("%H:%M:%S")
        
        # Check SIM storage
        ser.write(b'AT+CPMS="SM","SM","SM"\r\n')
        time.sleep(0.5)
        cpms_sm = ser.read_all().decode('utf-8', errors='ignore')
        
        ser.write(b'AT+CMGL="ALL"\r\n')
        time.sleep(1)
        cmgl_sm = ser.read_all().decode('utf-8', errors='ignore')
        
        # Check ME storage
        ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
        time.sleep(0.5)
        cpms_me = ser.read_all().decode('utf-8', errors='ignore')
        
        ser.write(b'AT+CMGL="ALL"\r\n')
        time.sleep(1)
        cmgl_me = ser.read_all().decode('utf-8', errors='ignore')
        
        if '+CMGL:' in cmgl_sm:
            print(f"\n[{timestamp}] FOUND MESSAGE IN SIM (SM) STORAGE!")
            print(f"CPMS: {cpms_sm.strip()[:80]}")
            print(f"Message:\n{cmgl_sm[:500]}")
            message_found = True
            break
        elif '+CMGL:' in cmgl_me:
            print(f"\n[{timestamp}] FOUND MESSAGE IN ME STORAGE!")
            print(f"CPMS: {cpms_me.strip()[:80]}")
            print(f"Message:\n{cmgl_me[:500]}")
            message_found = True
            break
        elif i % 3 == 0:  # Every 9 seconds
            sm_used = "0"
            me_used = "0"
            if '+CPMS:' in cpms_sm:
                try:
                    parts = cpms_sm.split(',')
                    if len(parts) > 1:
                        sm_used = parts[1].strip()
                except:
                    pass
            if '+CPMS:' in cpms_me:
                try:
                    parts = cpms_me.split(',')
                    if len(parts) > 1:
                        me_used = parts[1].strip()
                except:
                    pass
            print(f"[{timestamp}] SIM: {sm_used}/30 | ME: {me_used}/23 | No messages")
    
    if not message_found:
        print("\n" + "="*70)
        print("NO MESSAGES FOUND AFTER 60 SECONDS")
        print("="*70)
        print("\nDIAGNOSIS:")
        print("1. Message may not have been sent yet")
        print("2. Windows SMS Router Service may be intercepting")
        print("3. Carrier may not be delivering to modem")
        print("4. Modem may not be receiving (check signal)")
        print("\nWINDOWS SERVICES RUNNING:")
        print("  - Phone Service (PhoneSvc)")
        print("  - SMS Router Service (SmsRouter)")
        print("  - Your Phone app (PhoneExperienceHost)")
        print("\nThese may intercept messages before they reach modem!")
    
    ser.close()
    print("\n[OK] Debug complete")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect: {e}")
    print("Make sure Conductor is stopped!")
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

