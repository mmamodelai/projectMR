#!/usr/bin/env python3
"""
Check which TCP/IP command set the SIM7600 supports
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
        
        print("\n=== TESTING TCP/IP COMMAND SETS ===")
        
        print("\n--- Method 1: CIP Commands (Older) ---")
        send_at(ser, "AT+CIPSTATUS", 1)
        send_at(ser, "AT+CIPMODE?", 1)
        
        print("\n--- Method 2: NETOPEN Commands (Newer/Preferred for SIM7600) ---")
        send_at(ser, "AT+NETOPEN?", 1)
        send_at(ser, "AT+IPADDR", 1)
        send_at(ser, "AT+NETSTAT", 1)
        
        print("\n--- Checking Network Status ---")
        send_at(ser, "AT+CGACT?", 1)  # PDP active?
        send_at(ser, "AT+CGPADDR=1", 1)  # IP assigned?
        
        ser.close()
        
        print("\n=== RECOMMENDATION ===")
        print("If AT+NETOPEN responds, use Method 2 (NETOPEN)")
        print("If AT+CIPSTATUS responds, use Method 1 (CIP)")
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


