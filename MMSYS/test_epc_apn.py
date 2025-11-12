#!/usr/bin/env python3
"""
Test EPC APN (epc.tmobile.com) - this is T-Mobile's IMS/VoLTE APN
It might have special routing to internal services like MMSC!
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
        print("="*60)
        print("TESTING EPC APN (epc.tmobile.com)")
        print("This is T-Mobile's IMS/VoLTE APN")
        print("It might have internal routing to MMSC!")
        print("="*60)
        
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        
        # Test connection
        send_at(ser, "AT")
        
        print("\n=== ACTIVATING EPC APN (Context 5) ===")
        
        # Make sure context 5 is configured
        send_at(ser, 'AT+CGDCONT=5,"IP","epc.tmobile.com"', 1)
        
        # Activate it
        send_at(ser, "AT+CGACT=1,5", 3)
        
        # Check what IP we got
        response = send_at(ser, "AT+CGPADDR=5", 1)
        
        # Get detailed info
        response = send_at(ser, "AT+CGCONTRDP=5", 1)
        
        print("\n=== OPENING NETWORK ===")
        
        # Close any existing
        send_at(ser, "AT+NETCLOSE", 2)
        time.sleep(1)
        
        # Open network (should use default/active context)
        send_at(ser, "AT+NETOPEN", 5)
        
        send_at(ser, "AT+IPADDR", 1)
        
        print("\n=== TESTING MMSC CONNECTION ===")
        
        # DNS lookup
        send_at(ser, 'AT+CDNSGIP="mms.msg.eng.t-mobile.com"', 5)
        
        # Try TCP connection
        print("\nAttempting TCP connection to MMSC...")
        response = send_at(ser, 'AT+CIPOPEN=0,"TCP","10.175.85.145",8080', 15)
        
        if "+CIPOPEN: 0,0" in response:
            print("\n" + "="*60)
            print("SUCCESS!!! Connected to MMSC via EPC APN!")
            print("="*60)
            
            # Try a simple HTTP request
            http_test = "GET / HTTP/1.1\r\nHost: mms.msg.eng.t-mobile.com\r\n\r\n"
            send_at(ser, f'AT+CIPSEND=0,{len(http_test)}', 1)
            time.sleep(0.5)
            ser.write(http_test.encode())
            time.sleep(2)
            response = ser.read_all().decode('utf-8', errors='ignore')
            print(f"\nHTTP Response:\n{response}")
            
            send_at(ser, "AT+CIPCLOSE=0", 2)
        else:
            print(f"\n[FAILED] Still can't connect")
            print(f"Error: {response}")
            
            # Try the gateway as proxy?
            print("\n=== TRYING TO USE GATEWAY AS ROUTE ===")
            send_at(ser, "AT+CGCONTRDP=5", 1)
        
        # Cleanup
        send_at(ser, "AT+NETCLOSE", 2)
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


