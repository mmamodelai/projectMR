#!/usr/bin/env python3
"""Check BOTH ME and SIM storage for messages"""
import serial
import time

def send_at(ser, cmd, wait=0.5):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

print("\n" + "="*60)
print("CHECKING BOTH ME AND SIM STORAGE")
print("="*60)

try:
    print("\nWaiting for COM port...")
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            break
        except:
            print(".", end="", flush=True)
            time.sleep(1)
    else:
        print("\n[ERROR] Cannot connect - Conductor is using port")
        print("Messages in logs show ME is empty (0/23)")
        print("\nBUT - check if messages are in SIM storage!")
        exit(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    # Check ME storage
    print("\n=== ME (PHONE MEMORY) STORAGE ===")
    send_at(ser, 'AT+CPMS="ME","ME","ME"')
    resp = send_at(ser, "AT+CPMS?")
    print(resp)
    resp = send_at(ser, 'AT+CMGL="ALL"', 2)
    print(resp)
    me_has_msgs = "+CMGL:" in resp
    
    # Check SIM storage
    print("\n=== SM (SIM CARD) STORAGE ===")
    send_at(ser, 'AT+CPMS="SM","SM","SM"')
    resp = send_at(ser, "AT+CPMS?")
    print(resp)
    resp = send_at(ser, 'AT+CMGL="ALL"', 2)
    print(resp)
    sim_has_msgs = "+CMGL:" in resp
    
    ser.close()
    
    print("\n" + "="*60)
    print("RESULT:")
    print("="*60)
    if me_has_msgs:
        print("[FOUND] Messages in ME storage!")
    if sim_has_msgs:
        print("[FOUND] Messages in SIM storage!")
        print("\n[CRITICAL] Conductor only checks ME, not SIM!")
        print("This is why messages aren't being received!")
    if not me_has_msgs and not sim_has_msgs:
        print("[EMPTY] No messages in either storage")
        print("\nThis means messages aren't reaching the modem at all")
        print("Check:")
        print("  1. SMSC (Service Center) address")
        print("  2. Network registration")  
        print("  3. SIM card status")
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

