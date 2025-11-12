#!/usr/bin/env python3
"""
Fix SMS receiving - check all critical settings
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
print("FIXING SMS RECEIVING - COMPLETE DIAGNOSTIC")
print("="*70)

try:
    ser = serial.Serial("COM24", 115200, timeout=5)
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n" + "="*70)
    print("1. TEXT MODE")
    print("="*70)
    send_at(ser, "AT+CMGF=1")
    
    print("\n" + "="*70)
    print("2. SERVICE CENTER ADDRESS (SMSC) - CRITICAL!")
    print("="*70)
    resp = send_at(ser, "AT+CSCA?", 2)
    
    if '""' in resp or '+CSCA:' not in resp:
        print("\n[CRITICAL] NO SMSC CONFIGURED!")
        print("Modem cannot receive SMS without SMSC!")
        print("\nSetting T-Mobile SMSC...")
        send_at(ser, 'AT+CSCA="+12063130004",145', 2)
        print("\n[FIXED] SMSC set to T-Mobile: +12063130004")
    else:
        print("\n[OK] SMSC is configured")
    
    print("\n" + "="*70)
    print("3. NETWORK SERVICE FOR SMS (CGSMS)")
    print("="*70)
    resp = send_at(ser, "AT+CGSMS?", 2)
    
    if "+CGSMS: 0" in resp or "+CGSMS: 1" in resp:
        print("\n[ISSUE] CGSMS set to circuit-switched only")
        print("LTE networks need packet-switched SMS!")
        print("\nFIXING...")
        send_at(ser, "AT+CGSMS=3", 2)
        print("\n[FIXED] CGSMS=3 (prefer packet-switched, fallback to circuit)")
    else:
        print("\n[OK] CGSMS configured correctly")
    
    print("\n" + "="*70)
    print("4. NETWORK REGISTRATION")
    print("="*70)
    resp = send_at(ser, "AT+CREG?")
    if "+CREG: 0,1" in resp or "+CREG: 0,5" in resp:
        print("[OK] Registered on network")
    else:
        print("[WARNING] Not properly registered!")
        print(resp)
    
    print("\n" + "="*70)
    print("5. NETWORK OPERATOR")
    print("="*70)
    send_at(ser, "AT+COPS?", 3)
    
    print("\n" + "="*70)
    print("6. SMS STORAGE CONFIGURATION")
    print("="*70)
    send_at(ser, 'AT+CPMS="ME","ME","ME"')
    
    print("\n" + "="*70)
    print("7. MESSAGE INDICATION (CNMI)")
    print("="*70)
    send_at(ser, "AT+CNMI=1,1,0,0,0")
    
    print("\n" + "="*70)
    print("8. SAVE CONFIGURATION")
    print("="*70)
    resp = send_at(ser, "AT&W", 2)
    if "OK" in resp:
        print("\n[SAVED] Configuration saved to modem memory")
    
    print("\n" + "="*70)
    print("9. SIM STATUS")
    print("="*70)
    send_at(ser, "AT+CPIN?")
    
    print("\n" + "="*70)
    print("10. SIGNAL STRENGTH")
    print("="*70)
    resp = send_at(ser, "AT+CSQ")
    
    ser.close()
    
    print("\n" + "="*70)
    print("CONFIGURATION COMPLETE")
    print("="*70)
    print()
    print("[DONE] Modem reconfigured for SMS receiving")
    print()
    print("NEXT STEPS:")
    print("1. Restart Conductor")
    print("2. Send test message to (619) 558-7489")
    print("3. Message should arrive within 5-10 seconds")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

