#!/usr/bin/env python3
"""
Check modem settings that specifically affect SMS RECEIVING
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
print("CHECKING SMS RECEIVE-SPECIFIC SETTINGS")
print("="*70)

try:
    print("\nConnecting...")
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            break
        except:
            time.sleep(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n=== 1. MESSAGE SERVICE (CSMS) ===")
    print("Controls whether SMS service is enabled")
    resp = send_at(ser, "AT+CSMS?", 2)
    if "ERROR" in resp:
        print("[INFO] CSMS not supported or already enabled")
    
    print("\n=== 2. NEW MESSAGE INDICATION (CNMI) ===")
    print("Current: Should be 1,1,0,0,0")
    resp = send_at(ser, "AT+CNMI?")
    
    print("\n=== 3. MESSAGE WAITING (CMMS) ===")
    print("Controls if modem accepts messages")
    resp = send_at(ser, "AT+CMMS?", 2)
    if "ERROR" in resp:
        print("[INFO] CMMS not supported")
    
    print("\n=== 4. PREFERRED MESSAGE STORAGE (CPMS) ===")
    print("Where incoming messages are stored")
    send_at(ser, "AT+CPMS?")
    
    print("\n=== 5. SERVICE CENTRE ADDRESS (CSCA) ===")
    print("CRITICAL for both send AND receive")
    send_at(ser, "AT+CSCA?")
    
    print("\n=== 6. TEXT MODE PARAMETERS (CSMP) ===")
    send_at(ser, "AT+CSMP?")
    
    print("\n=== 7. CHARACTER SET (CSCS) ===")
    send_at(ser, "AT+CSCS?")
    
    print("\n=== 8. NETWORK SERVICE TYPE (CGSMS) ===")
    print("Controls which network (circuit/packet) for SMS")
    send_at(ser, "AT+CGSMS?")
    
    print("\n=== 9. MESSAGE FORMAT (CMGF) ===")
    send_at(ser, "AT+CMGF?")
    
    print("\n=== 10. PHONE FUNCTIONALITY (CFUN) ===")
    print("If not 1, modem might not receive")
    resp = send_at(ser, "AT+CFUN?")
    if "+CFUN: 1" not in resp:
        print("[WARNING] CFUN is not 1 (full functionality)!")
        print("This might prevent receiving SMS!")
    
    print("\n=== 11. TRYING TO ENABLE SMS RECEPTION ===")
    print("Setting CSMS=0 (enable SMS)")
    resp = send_at(ser, "AT+CSMS=0", 2)
    if "OK" in resp:
        print("[DONE] SMS service enabled")
        send_at(ser, "AT&W")
    
    print("\n=== 12. CHECKING FOR ANY ERROR FLAGS ===")
    send_at(ser, "AT+CMEE=2")  # Enable verbose errors
    send_at(ser, "AT+CEER")     # Get last error
    
    ser.close()
    
    print("\n" + "="*70)
    print("DIAGNOSIS")
    print("="*70)
    print()
    print("If CFUN is not 1, that's the problem!")
    print("If CGSMS is 0 or 1, try setting to 3")
    print("If CNMI is not showing up, modem might be in wrong mode")
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

