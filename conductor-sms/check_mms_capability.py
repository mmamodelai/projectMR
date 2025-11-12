#!/usr/bin/env python3
"""
Check what MMS-related AT commands the SIM7600G-H supports
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
        
        # Get modem info
        print("\n=== MODEM INFORMATION ===")
        send_at(ser, "ATI")  # Manufacturer info
        send_at(ser, "AT+CGMM")  # Model
        send_at(ser, "AT+CGMR")  # Firmware version
        
        print("\n=== TESTING MMS COMMANDS ===")
        
        # Try different MMS command sets
        commands = [
            "AT+CMMS?",  # More messages to send (standard)
            "AT+CMMSINIT?",  # MMS init (SIMCom specific)
            "AT+CMMSCFG?",  # MMS config (SIMCom)
            "AT+SAPBR?",  # Bearer profile (data connection)
            "AT+CGATT?",  # GPRS attach status
            "AT+CGDCONT?",  # PDP context
            "AT+CSCA?",  # SMS service center
        ]
        
        for cmd in commands:
            send_at(ser, cmd, 1)
        
        print("\n=== TESTING DATA CONNECTION ===")
        
        # Check if we need to establish data connection first
        send_at(ser, "AT+CGATT?", 1)  # GPRS attached?
        send_at(ser, "AT+CGDCONT?", 1)  # PDP context defined?
        send_at(ser, "AT+SAPBR=2,1", 1)  # Query bearer profile
        
        print("\n=== CONCLUSION ===")
        print("If AT+SAPBR commands work, we can establish data connection for MMS")
        print("If AT+CMMSINIT works, modem has built-in MMS support")
        print("If both fail, we need to send MMS via HTTP POST manually")
        
        ser.close()
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


