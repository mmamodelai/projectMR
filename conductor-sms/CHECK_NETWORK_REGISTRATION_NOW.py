#!/usr/bin/env python3
"""
Check network registration - modem might not be registered after reset
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
print("CHECKING NETWORK REGISTRATION STATUS")
print("="*70)

try:
    print("\nWaiting for modem...")
    for i in range(15):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            print("[OK] Connected")
            break
        except:
            print(".", end="", flush=True)
            time.sleep(0.5)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n=== NETWORK REGISTRATION ===")
    resp = send_at(ser, "AT+CREG?", 2)
    
    if "+CREG: 0,1" in resp or "+CREG: 0,5" in resp:
        print("[OK] Registered on network")
    elif "+CREG: 0,2" in resp:
        print("[WARNING] Searching for network...")
    elif "+CREG: 0,0" in resp:
        print("[ERROR] Not registered!")
    
    print("\n=== LTE REGISTRATION ===")
    send_at(ser, "AT+CEREG?", 2)
    
    print("\n=== SIGNAL STRENGTH ===")
    send_at(ser, "AT+CSQ", 1)
    
    print("\n=== NETWORK OPERATOR ===")
    send_at(ser, "AT+COPS?", 3)
    
    print("\n=== NETWORK MODE ===")
    send_at(ser, "AT+CNMP?", 1)
    
    print("\n=== SMS CENTER ===")
    send_at(ser, "AT+CSCA?", 1)
    
    print("\n=== TRYING TO SEND TEST MESSAGE TO VERIFY ===")
    print("Sending test to verify modem CAN send...")
    send_at(ser, "AT+CMGF=1")
    send_at(ser, 'AT+CMGS="+16199773020"')
    time.sleep(0.5)
    ser.write(b"Modem test - can you receive this?\x1A")
    time.sleep(3)
    resp = ser.read_all().decode('utf-8', errors='ignore')
    print(f"<< {resp.strip()}")
    
    if "+CMGS:" in resp:
        print("\n[OK] Modem CAN send SMS (network is working)")
    else:
        print("\n[FAILED] Modem cannot send - network issue!")
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

