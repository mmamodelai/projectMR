#!/usr/bin/env python3
"""
Test MMS with HTTP proxy configuration
Many carriers require going through a proxy to reach MMSC
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
        
        print("\n=== CHECKING FOR MMS PROXY SETTINGS ===")
        
        # Some modems support proxy configuration
        send_at(ser, "AT+CGPROXY?", 1)
        
        print("\n=== TRYING DIFFERENT PDP CONTEXT TYPE ===")
        
        # Try creating a context specifically for MMS (not just IP, but MMS type)
        # Context 3 for MMS
        send_at(ser, 'AT+CGDCONT=3,"IP","fast.t-mobile.com"', 1)
        
        # Try setting PDP type to include MMS
        send_at(ser, 'AT+CGDCONT=3,"IP","fast.t-mobile.com","0.0.0.0",0,0,0,0,0,0,0', 1)
        
        # Activate this context
        send_at(ser, "AT+CGACT=1,3", 3)
        
        # Check if we got different routing
        send_at(ser, "AT+CGPADDR=3", 1)
        
        print("\n=== CHECKING NETWORK INTERFACE TYPE ===")
        
        # Check what interfaces are available
        send_at(ser, "AT+CGPIAF?", 1)  # IP address format
        
        print("\n=== TRYING TO USE SPECIFIC PDP FOR TCP ===")
        
        # Close any existing network
        send_at(ser, "AT+NETCLOSE", 2)
        
        # Try opening network with specific context
        send_at(ser, "AT+NETOPEN=,,3", 5)  # Use context 3
        
        send_at(ser, "AT+IPADDR", 1)
        
        print("\n=== TESTING CONNECTION AGAIN ===")
        response = send_at(ser, 'AT+CDNSGIP="mms.msg.eng.t-mobile.com"', 5)
        
        send_at(ser, 'AT+CIPOPEN=0,"TCP","10.175.85.145",8080', 15)
        
        # Close
        send_at(ser, "AT+CIPCLOSE=0", 2)
        send_at(ser, "AT+NETCLOSE", 2)
        
        ser.close()
        
        print("\n=== ALTERNATE APPROACH: CHECK MODEM'S INTERNAL MMS SUPPORT ===")
        print("Some SIM7600 variants have built-in MMS relay...")
        print("This might require updated firmware or different AT command set.")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


