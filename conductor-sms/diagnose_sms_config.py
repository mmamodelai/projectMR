#!/usr/bin/env python3
"""
Diagnose modem SMS configuration
"""
import serial
import time

COM_PORT = "COM24"
BAUDRATE = 115200

def send_at(ser, command, wait=1.0):
    """Send AT command and return response"""
    print(f"\n>> {command}")
    ser.write(f"{command}\r\n".encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"<< {response.strip()}")
    return response

print("\n" + "="*60)
print("SMS MODEM CONFIGURATION DIAGNOSIS")
print("="*60)

try:
    print("\nWaiting for modem...")
    connected = False
    for attempt in range(10):
        try:
            ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
            connected = True
            print("[OK] Connected")
            break
        except serial.SerialException:
            print(".", end="", flush=True)
            time.sleep(1)
    
    if not connected:
        print("\n[ERROR] Cannot connect")
        exit(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    print("\n" + "="*60)
    print("CRITICAL SMS SETTINGS")
    print("="*60)
    
    print("\n1. SMS Format (should be 1 for text mode):")
    send_at(ser, "AT+CMGF?")
    
    print("\n2. SMS Storage Location:")
    send_at(ser, "AT+CPMS?")
    
    print("\n3. New Message Indication (CNMI):")
    response = send_at(ser, "AT+CNMI?")
    
    print("\n4. Network Service Type (CRITICAL):")
    response = send_at(ser, "AT+CGSMS?", 2)
    
    if "+CGSMS: 0" in response:
        print("\n[CRITICAL] FOUND THE PROBLEM!")
        print("CGSMS=0 means SMS ONLY via circuit-switched (2G)")
        print("Your modem might be on LTE-only network!")
        print("\nFIXING NOW...")
        send_at(ser, "AT+CGSMS=3", 2)
        print("\nSet to CGSMS=3 (prefer GPRS/LTE, fallback to circuit-switched)")
    elif "+CGSMS: 1" in response:
        print("\n[ISSUE] CGSMS=1 (circuit-switched only)")
        print("This might not work on LTE-only networks")
        print("\nFIXING...")
        send_at(ser, "AT+CGSMS=3", 2)
    elif "+CGSMS: 3" in response:
        print("\n[OK] CGSMS=3 (correct setting)")
    
    print("\n5. Network Registration:")
    send_at(ser, "AT+CREG?")
    
    print("\n6. Network Operator:")
    send_at(ser, "AT+COPS?", 3)
    
    print("\n7. SIM Status:")
    send_at(ser, "AT+CPIN?")
    
    print("\n8. Service Center Address (SMSC):")
    response = send_at(ser, "AT+CSCA?", 2)
    
    if '""' in response or 'CSCA:' not in response:
        print("\n[WARNING] No SMSC configured!")
        print("Modem cannot send/receive SMS without SMSC")
        print("\nTrying to set T-Mobile SMSC...")
        send_at(ser, 'AT+CSCA="+12063130004"', 2)
    
    print("\n9. Check if SMS can be received:")
    send_at(ser, "AT+CNMA=?")
    
    print("\n" + "="*60)
    print("RECONFIGURING FOR RELIABILITY")
    print("="*60)
    
    # Apply best settings
    send_at(ser, "AT+CMGF=1")  # Text mode
    send_at(ser, 'AT+CPMS="ME","ME","ME"')  # Use ME storage
    send_at(ser, "AT+CNMI=1,1,0,0,0")  # Store and notify
    send_at(ser, "AT+CGSMS=3")  # Prefer packet-switched
    send_at(ser, "AT&W")  # Save configuration
    
    print("\n[DONE] Configuration saved")
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print()
print("1. Restart Conductor (it should pick up new config)")
print("2. Send a test message to (619) 558-7489")
print("3. Watch Conductor window for incoming")
print()
print("If STILL not working:")
print("  - Power cycle the modem (unplug USB, wait 10 sec, plug back)")
print("  - Check Mint Mobile account SMS settings")
print("  - Try a different SIM card")
print()

