#!/usr/bin/env python3
"""
Check SM (SIM) storage - messages might be going there!
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
print("CHECKING SIM (SM) STORAGE FOR MESSAGES")
print("="*70)
print()
print("From docs: 'SIM7600 typically uses SM by default for SMS storage'")
print("Conductor only checks ME - messages might be in SM!")
print()

try:
    print("Waiting for COM port...")
    for i in range(15):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            print("[OK] Connected")
            break
        except:
            print(".", end="", flush=True)
            time.sleep(0.5)
    else:
        print("\n[ERROR] Cannot connect - will check after Conductor releases port")
        exit(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    send_at(ser, "AT+CMGF=1")
    
    print("\n=== CHECKING SM (SIM) STORAGE ===")
    send_at(ser, 'AT+CPMS="SM","SM","SM"')
    resp = send_at(ser, "AT+CPMS?")
    
    # Check for messages
    resp = send_at(ser, 'AT+CMGL="ALL"', 2)
    
    if "+CMGL:" in resp:
        count = resp.count("+CMGL:")
        print(f"\n[FOUND] {count} MESSAGE(S) IN SIM STORAGE!")
        print("\nTHIS IS THE PROBLEM!")
        print("Messages are going to SM, but Conductor only checks ME!")
        print()
        print("Messages:")
        print(resp)
    else:
        print("\n[EMPTY] No messages in SM storage")
        print("\nChecking ME storage too...")
        send_at(ser, 'AT+CPMS="ME","ME","ME"')
        resp = send_at(ser, 'AT+CMGL="ALL"', 2)
        if "+CMGL:" in resp:
            print("[FOUND] Messages in ME storage")
        else:
            print("[EMPTY] No messages in ME either")
            print("\nMessages truly aren't reaching the modem!")
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")

