#!/usr/bin/env python3
"""
Check data connection status and try alternative activation methods
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
        
        print("\n=== CHECKING DATA CONNECTION STATUS ===")
        
        # Check GPRS attachment
        send_at(ser, "AT+CGATT?")
        
        # Check PDP contexts
        send_at(ser, "AT+CGDCONT?")
        
        # Check if context is already active
        send_at(ser, "AT+CGACT?")
        
        # Check network registration
        send_at(ser, "AT+CREG?")
        send_at(ser, "AT+CGREG?")  # GPRS registration
        
        # Get IP address if already connected
        send_at(ser, "AT+CGPADDR=1")
        
        print("\n=== TRYING ALTERNATIVE ACTIVATION ===")
        
        # Method 1: Check if already activated
        response = send_at(ser, "AT+CGACT?")
        if "+CGACT: 1,1" in response:
            print("[OK] PDP context already active!")
        else:
            # Method 2: Deactivate first, then activate
            print("Deactivating first...")
            send_at(ser, "AT+CGACT=0,1", 2)
            
            print("Now activating...")
            send_at(ser, "AT+CGACT=1,1", 5)
        
        # Check status after
        send_at(ser, "AT+CGACT?")
        send_at(ser, "AT+CGPADDR=1")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


