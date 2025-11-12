#!/usr/bin/env python3
"""
RESET MODEM TO SMS DEFAULTS
Remove MMS configuration that broke SMS
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
print("RESETTING MODEM TO SMS DEFAULTS")
print("="*70)
print()
print("Removing MMS configuration that broke SMS...")
print()

try:
    print("Connecting to modem...")
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            print("[OK] Connected")
            break
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n=== RESETTING TO FACTORY SMS DEFAULTS ===")
    
    # Reset to factory defaults
    print("\n1. Factory reset (keeps SIM/network settings)")
    send_at(ser, "ATZ", 2)
    
    # Set text mode
    print("\n2. Set text mode")
    send_at(ser, "AT+CMGF=1")
    
    # Reset SMS center (T-Mobile)
    print("\n3. Set SMS Center (SMSC)")
    send_at(ser, 'AT+CSCA="+12063130004",145', 2)
    
    # Reset character set
    print("\n4. Reset character set to default")
    send_at(ser, 'AT+CSCS="GSM"', 1)
    
    # Reset SMS parameters
    print("\n5. Reset SMS parameters")
    send_at(ser, "AT+CSMP=17,167,0,0", 2)
    
    # Set storage to ME (not SM)
    print("\n6. Set storage to ME")
    send_at(ser, 'AT+CPMS="ME","ME","ME"', 1)
    
    # Set CNMI (store messages, notify)
    print("\n7. Set CNMI=1,1 (working setting)")
    send_at(ser, "AT+CNMI=1,1,0,0,0", 1)
    
    # CRITICAL: Remove any MMS-specific APN settings
    print("\n8. Reset to default network mode (auto 2G/3G/4G)")
    send_at(ser, "AT+CNMP=2", 2)
    
    # Reset CGSMS (network service for SMS)
    print("\n9. Set CGSMS=3 (prefer packet-switched)")
    send_at(ser, "AT+CGSMS=3", 2)
    
    # Save all settings
    print("\n10. Save configuration to modem")
    resp = send_at(ser, "AT&W", 2)
    
    if "OK" in resp:
        print("\n[SUCCESS] Configuration saved!")
    
    # Verify settings
    print("\n=== VERIFYING CONFIGURATION ===")
    send_at(ser, "AT+CMGF?")
    send_at(ser, "AT+CPMS?")
    send_at(ser, "AT+CNMI?")
    send_at(ser, "AT+CSCA?")
    
    ser.close()
    
    print("\n" + "="*70)
    print("MODEM RESET COMPLETE")
    print("="*70)
    print()
    print("[DONE] Modem configured for SMS (MMS settings removed)")
    print()
    print("NEXT STEPS:")
    print("1. Restart Conductor (it should pick up new config)")
    print("2. Send test SMS to (619) 558-7489")
    print("3. Message should arrive within 5-10 seconds")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

