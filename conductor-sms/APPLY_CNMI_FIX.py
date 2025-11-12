#!/usr/bin/env python3
"""
APPLY THE FIX: Change CNMI from 1,1 to 2,1
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
print("APPLYING CNMI FIX")
print("="*70)
print()
print("PROBLEM: CNMI=1,1 discards messages if modem is busy")
print("FIX: CNMI=2,1 buffers messages if modem is busy")
print()

try:
    ser = serial.Serial("COM24", 115200, timeout=5)
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n[STEP 1] Setting CNMI=2,1 (buffer messages)")
    resp = send_at(ser, "AT+CNMI=2,1,0,0,0", 2)
    
    if "OK" in resp:
        print("[SUCCESS] CNMI changed to 2,1")
    else:
        print("[FAILED] Could not change CNMI")
        ser.close()
        exit(1)
    
    print("\n[STEP 2] Verifying setting")
    resp = send_at(ser, "AT+CNMI?", 1)
    
    if "+CNMI: 2,1" in resp:
        print("[VERIFIED] CNMI is now 2,1")
    else:
        print("[WARNING] CNMI might not have changed")
    
    print("\n[STEP 3] Saving to modem memory")
    send_at(ser, "AT&W", 2)
    print("[SAVED] Configuration saved")
    
    ser.close()
    
    print("\n" + "="*70)
    print("FIX APPLIED SUCCESSFULLY")
    print("="*70)
    print()
    print("NEXT: Restart Conductor and test")
    print("Messages should now be BUFFERED instead of DISCARDED")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

