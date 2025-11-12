#!/usr/bin/env python3
"""
Test TCP connection to MMSC endpoint
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

def main():
    try:
        print("Connecting to modem...")
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        
        # Test connection
        send_at(ser, "AT")
        
        print("\n=== OPENING NETWORK ===")
        response = send_at(ser, "AT+NETOPEN?", 1)
        
        if "+NETOPEN: 0" in response:
            print("Opening network...")
            send_at(ser, "AT+NETOPEN", 5)
        
        # Get IP
        send_at(ser, "AT+IPADDR", 1)
        
        print("\n=== TESTING DNS RESOLUTION ===")
        send_at(ser, 'AT+CDNSGIP="wholesale.mmsmvno.com"', 5)
        
        print("\n=== TESTING SIMPLE TCP CONNECTION ===")
        print("Trying Google DNS (8.8.8.8:53) first to test TCP...")
        response = send_at(ser, 'AT+CIPOPEN=0,"TCP","8.8.8.8",53', 10)
        
        if "+CIPOPEN: 0,0" in response:
            print("[OK] TCP works! Can connect to external servers")
            send_at(ser, "AT+CIPCLOSE=0", 2)
        else:
            print("[FAILED] TCP doesn't work at all")
        
        print("\n=== NOW TESTING MMSC ENDPOINT ===")
        response = send_at(ser, 'AT+CIPOPEN=1,"TCP","wholesale.mmsmvno.com",8080', 15)
        
        if "+CIPOPEN: 1,0" in response:
            print("[SUCCESS] Connected to MMSC!")
            send_at(ser, "AT+CIPCLOSE=1", 2)
        else:
            print("[FAILED] Cannot connect to MMSC")
            print("Possible reasons:")
            print("  1. DNS resolution failed")
            print("  2. Port 8080 blocked by carrier")
            print("  3. MMSC endpoint incorrect")
            print("  4. Need to use different APN")
        
        # Close network
        send_at(ser, "AT+NETCLOSE", 2)
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


