#!/usr/bin/env python3
"""
Try forcing 3G mode for SMS (from docs)
Some LTE networks require 3G for SMS
"""
import serial
import time

def send_at(ser, cmd, wait=1.0):
    print(f"\n>> {cmd}")
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    resp = ser.read_all().decode('utf-8', errors='ignore')
    print(f"<< {resp.strip()}")
    return resp

print("\n" + "="*70)
print("FORCING 3G MODE FOR SMS")
print("="*70)
print()
print("From docs:")
print("'some networks only allow SMS over 4G if VoLTE is enabled'")
print("'try forcing 3G mode (AT+CNMP=14 for WCDMA only)'")
print()

try:
    print("Connecting...")
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            break
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n=== CURRENT NETWORK MODE ===")
    resp = send_at(ser, "AT+CNMP?", 2)
    
    if "+CNMP: 2" in resp:
        print("[CURRENT] Automatic mode (2G/3G/4G auto)")
    elif "+CNMP: 38" in resp:
        print("[CURRENT] LTE only mode")
    elif "+CNMP: 14" in resp:
        print("[CURRENT] Already in 3G (WCDMA) mode")
    
    print("\n=== CURRENT NETWORK INFO ===")
    send_at(ser, "AT+COPS?", 2)
    send_at(ser, "AT+CREG?")
    send_at(ser, "AT+CEREG?")
    
    print("\n=== SWITCHING TO 3G (WCDMA) MODE ===")
    print("This forces SMS over 3G network...")
    resp = send_at(ser, "AT+CNMP=14", 3)
    
    if "OK" in resp:
        print("\n[SUCCESS] Switched to 3G mode")
        print("Modem will re-register on 3G network...")
        print("Wait 10-20 seconds for registration...")
        
        time.sleep(5)
        print("\n=== CHECKING REGISTRATION ===")
        send_at(ser, "AT+CREG?", 2)
        send_at(ser, "AT+COPS?", 2)
        
        print("\n=== SAVING CONFIGURATION ===")
        send_at(ser, "AT&W", 2)
        print("[SAVED] 3G mode saved to modem")
    else:
        print("\n[FAILED] Could not switch to 3G")
    
    ser.close()
    
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print()
    print("1. Wait 20 seconds for modem to register on 3G")
    print("2. Send a test SMS to (619) 558-7489")
    print("3. Watch Conductor for incoming message")
    print()
    print("If this works, SMS needs 3G on your network!")
    print()
    print("To switch back to auto:")
    print("  AT+CNMP=2")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

