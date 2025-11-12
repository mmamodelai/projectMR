#!/usr/bin/env python3
"""
Check if modem supports automatic SMS concatenation
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
print("CHECKING SMS CONCATENATION SUPPORT")
print("="*60)

try:
    # Wait for connection window
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
        print("\n[ERROR] Cannot connect - Conductor might be polling")
        print("This is OK - read the findings below:")
        raise Exception("Cannot connect")
    
    time.sleep(1)
    
    # Test modem
    response = send_at(ser, "AT")
    if "OK" not in response:
        print("[ERROR] Modem not responding")
        ser.close()
        exit(1)
    
    print("\n" + "="*60)
    print("TESTING CONCATENATION SETTINGS")
    print("="*60)
    
    # Check current SMS settings
    print("\n1. Current SMS format:")
    send_at(ser, "AT+CMGF?")
    
    print("\n2. Current concatenation setting:")
    response = send_at(ser, "AT+CSMP?")
    
    print("\n3. Check if modem supports CSCS (character set):")
    send_at(ser, "AT+CSCS?")
    
    print("\n4. Try setting concatenation ON:")
    response = send_at(ser, "AT+CSMP=17,167,0,0")
    
    if "OK" in response:
        print("\n[SUCCESS] Modem accepted concatenation command!")
        print("This setting tells modem to handle long SMS")
    else:
        print("\n[FAILED] Modem doesn't support AT+CSMP")
    
    print("\n5. Check CMGF=0 (PDU mode) support:")
    response = send_at(ser, "AT+CMGF=0")
    if "OK" in response:
        print("[OK] PDU mode supported")
        # Switch back to text mode
        send_at(ser, "AT+CMGF=1")
    
    ser.close()
    
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "="*60)
print("DIAGNOSIS")
print("="*60)
print()
print("PROBLEM: Conductor is receiving PARTS of long messages separately")
print()
print("SOLUTION OPTIONS:")
print()
print("1. MODEM AUTO-CONCATENATION (easiest)")
print("   - Use AT+CSMP=17,167,0,0 before reading messages")
print("   - Modem automatically joins multi-part SMS")
print("   - Need to verify if SIM7600 supports this")
print()
print("2. PDU MODE + MANUAL PARSING (more reliable)")
print("   - Switch to AT+CMGF=0 (PDU mode)")
print("   - Parse UDH (User Data Header) to detect parts")
print("   - Store parts in memory until all arrive")
print("   - Reassemble and save complete message")
print()
print("3. WAIT & DELAY (quick fix, not perfect)")
print("   - When receiving message, wait 2-3 seconds")
print("   - Read ALL messages on modem")
print("   - If multiple messages from same number within 5 seconds:")
print("     * Combine them in order")
print("     * Save as single message")
print()
print("RECOMMENDATION: Try #1 first (add AT+CSMP to Conductor)")
print("                If fails, implement #2 (PDU mode)")
print()

