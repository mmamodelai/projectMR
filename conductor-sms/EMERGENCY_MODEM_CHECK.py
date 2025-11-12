#!/usr/bin/env python3
"""Emergency modem diagnostic - check everything"""

import serial
import time
import sys

COM_PORT = "COM24"
BAUD_RATE = 115200

print("\n" + "="*70)
print("EMERGENCY MODEM DIAGNOSTIC - CHECKING EVERYTHING")
print("="*70 + "\n")

try:
    print(f"[1/10] Connecting to {COM_PORT}...")
    ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=5)
    time.sleep(1)
    print("[OK] Connected!\n")
    
    # Test modem
    print("[2/10] Testing modem response...")
    ser.write(b'AT\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    if 'OK' not in response:
        print(f"[ERROR] Modem not responding! Response: {response}")
        ser.close()
        sys.exit(1)
    print("[OK] Modem responding\n")
    
    # Set text mode
    print("[3/10] Setting text mode...")
    ser.write(b'AT+CMGF=1\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Check CNMI setting
    print("[4/10] Checking CNMI setting (message notification mode)...")
    ser.write(b'AT+CNMI?\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"CNMI Setting: {response.strip()}\n")
    
    # Set CNMI to correct value
    print("[5/10] Setting CNMI to 1,1,0,0,0 (store messages)...")
    ser.write(b'AT+CNMI=1,1,0,0,0\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Check SIM storage
    print("[6/10] Checking SIM (SM) storage...")
    ser.write(b'AT+CPMS="SM","SM","SM"\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"SIM Storage: {response.strip()}\n")
    
    # Read messages from SIM
    print("[7/10] Reading messages from SIM (SM)...")
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)
    response_sm = ser.read_all().decode('utf-8', errors='ignore')
    print(f"SIM Messages Response:\n{response_sm}\n")
    
    if '+CMGL:' in response_sm:
        sm_count = response_sm.count('+CMGL:')
        print(f"[FOUND] {sm_count} MESSAGE(S) ON SIM!\n")
    else:
        print("[NONE] NO MESSAGES ON SIM\n")
    
    # Check ME storage
    print("[8/10] Checking Phone Memory (ME) storage...")
    ser.write(b'AT+CPMS="ME","ME","ME"\r\n')
    time.sleep(0.5)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"ME Storage: {response.strip()}\n")
    
    # Read messages from ME
    print("[9/10] Reading messages from Phone Memory (ME)...")
    ser.write(b'AT+CMGL="ALL"\r\n')
    time.sleep(2)
    response_me = ser.read_all().decode('utf-8', errors='ignore')
    print(f"ME Messages Response:\n{response_me}\n")
    
    if '+CMGL:' in response_me:
        me_count = response_me.count('+CMGL:')
        print(f"[FOUND] {me_count} MESSAGE(S) IN PHONE MEMORY!\n")
    else:
        print("[NONE] NO MESSAGES IN PHONE MEMORY\n")
    
    # Save configuration
    print("[10/10] Saving configuration...")
    ser.write(b'AT&W\r\n')
    time.sleep(1)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Response: {response.strip()}\n")
    
    # Summary
    print("\n" + "="*70)
    print("DIAGNOSTIC SUMMARY")
    print("="*70)
    
    total_found = 0
    if '+CMGL:' in response_sm:
        total_found += response_sm.count('+CMGL:')
    if '+CMGL:' in response_me:
        total_found += response_me.count('+CMGL:')
    
    if total_found > 0:
        print(f"[FOUND] TOTAL MESSAGES FOUND: {total_found}")
        print("   -> Messages are on the modem!")
        print("   -> Conductor should detect them after restart")
    else:
        print("[NONE] NO MESSAGES FOUND ON MODEM")
        print("   -> Either:")
        print("     1. Messages haven't arrived yet")
        print("     2. Messages were already deleted")
        print("     3. Messages are being routed elsewhere")
    
    print("\nCNMI Setting: 1,1,0,0,0 (should store messages)")
    print("Configuration saved: AT&W")
    print("\n" + "="*70 + "\n")
    
    ser.close()
    print("[OK] Diagnostic complete. Modem disconnected.")
    
except serial.SerialException as e:
    print(f"\n[ERROR] Cannot connect to modem!")
    print(f"Error: {e}")
    print("\nCheck:")
    print("1. Is modem connected to COM24?")
    print("2. Is another program using the modem?")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

