#!/usr/bin/env python3
"""
Check CNMI and storage settings based on documentation
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
print("CHECKING INCOMING SMS CONFIGURATION")
print("="*70)

try:
    ser = serial.Serial("COM24", 115200, timeout=5)
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n" + "="*70)
    print("CRITICAL: CNMI Setting (How incoming SMS are handled)")
    print("="*70)
    print("From docs:")
    print("  - AT+CNMI=2,1,0,0,0 = Store to memory + send +CMTI notification")
    print("  - AT+CNMI=2,2,0,0,0 = Push full message as +CMT (don't store)")
    print("  - AT+CNMI=1,1,0,0,0 = Discard if busy + notify")
    print()
    
    resp = send_at(ser, "AT+CNMI?", 2)
    
    if "+CNMI: 1,1" in resp:
        print("\n[CURRENT] CNMI=1,1 - Discard if link busy + notify")
        print("[ISSUE] This might drop messages if PC is polling!")
        print("\n[FIX] Should be CNMI=2,1 (buffer if busy)")
    elif "+CNMI: 2,1" in resp:
        print("\n[OK] CNMI=2,1 - Correct (buffer + notify)")
    elif "+CNMI: 2,0" in resp:
        print("\n[CRITICAL] CNMI=2,0 - Messages forwarded to TE, NOT stored!")
        print("This causes auto-deletion!")
    else:
        print(f"\n[UNKNOWN] CNMI setting: {resp}")
    
    print("\n" + "="*70)
    print("STORAGE LOCATION")
    print("="*70)
    print("From docs: By default, messages go to SIM (SM) storage")
    print("We're setting ME, but messages might still go to SM!")
    print()
    
    # Check both storages
    print("\n--- SIM (SM) Storage ---")
    send_at(ser, 'AT+CPMS="SM","SM","SM"')
    resp_sm = send_at(ser, "AT+CPMS?")
    send_at(ser, 'AT+CMGL="ALL"', 2)
    
    print("\n--- Phone (ME) Storage ---")
    send_at(ser, 'AT+CPMS="ME","ME","ME"')
    resp_me = send_at(ser, "AT+CPMS?")
    send_at(ser, 'AT+CMGL="ALL"', 2)
    
    print("\n" + "="*70)
    print("NETWORK MODE (Some networks need 3G for SMS)")
    print("="*70)
    send_at(ser, "AT+CNMP?", 2)
    
    print("\n" + "="*70)
    print("RECOMMENDED FIX")
    print("="*70)
    print()
    print("1. Change CNMI to buffer messages:")
    print("   AT+CNMI=2,1,0,0,0")
    print()
    print("2. Set preferred storage to SM (where messages go by default):")
    print("   AT+CPMS=\"SM\",\"SM\",\"SM\"")
    print()
    print("3. Or check BOTH SM and ME in Conductor")
    print()
    print("4. If still failing, try forcing 3G:")
    print("   AT+CNMP=14")
    print()
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

