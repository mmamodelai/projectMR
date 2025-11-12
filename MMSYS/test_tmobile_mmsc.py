#!/usr/bin/env python3
"""
Test T-Mobile's MMSC endpoint
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
        
        print("\n=== TRYING T-MOBILE APN ===")
        
        # Try T-Mobile's APN
        send_at(ser, 'AT+CGDCONT=2,"IP","fast.t-mobile.com"', 1)
        send_at(ser, "AT+CGACT=1,2", 3)
        send_at(ser, "AT+CGPADDR=2", 1)
        
        print("\n=== OPENING NETWORK ON NEW CONTEXT ===")
        response = send_at(ser, "AT+NETOPEN?", 1)
        
        if "+NETOPEN: 0" in response:
            print("Opening network...")
            send_at(ser, "AT+NETOPEN", 5)
        
        # Get IP
        send_at(ser, "AT+IPADDR", 1)
        
        print("\n=== TESTING T-MOBILE MMSC DNS ===")
        response = send_at(ser, 'AT+CDNSGIP="mms.msg.eng.t-mobile.com"', 5)
        
        if "CDNSGIP" in response and "ERROR" not in response:
            # Extract IP
            lines = response.split('\n')
            for line in lines:
                if "+CDNSGIP:" in line and "," in line:
                    parts = line.split('"')
                    if len(parts) >= 4:
                        mmsc_ip = parts[3]
                        print(f"\n[SUCCESS] T-Mobile MMSC resolved to: {mmsc_ip}")
                        
                        print("\n=== TESTING TCP CONNECTION TO T-MOBILE MMSC ===")
                        response = send_at(ser, f'AT+CIPOPEN=0,"TCP","{mmsc_ip}",8080', 15)
                        
                        if "+CIPOPEN: 0,0" in response:
                            print("\n" + "="*60)
                            print("SUCCESS! Connected to T-Mobile MMSC!")
                            print("="*60)
                            send_at(ser, "AT+CIPCLOSE=0", 2)
                        else:
                            print(f"\n[FAILED] Cannot connect to {mmsc_ip}:8080")
                            print(f"Response: {response}")
        
        # Close network
        send_at(ser, "AT+NETCLOSE", 2)
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


