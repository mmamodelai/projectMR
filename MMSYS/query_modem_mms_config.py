#!/usr/bin/env python3
"""
Query modem for any built-in MMS configuration from SIM card
Carriers often provision MMS settings directly to the SIM
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
        
        print("\n=== QUERYING SIM CARD FOR MMS SETTINGS ===")
        
        # Check SIM provisioning
        send_at(ser, "AT+COPS?", 1)  # Operator
        send_at(ser, "AT+CIMI", 1)   # IMSI
        
        # Try to read SMS service center (similar storage for MMS)
        send_at(ser, "AT+CSCA?", 1)
        
        # Check if SIM has any stored data about MMS
        send_at(ser, "AT+CRSM=176,28486,0,0,0", 2)  # Try to read MMS config from SIM
        
        print("\n=== CHECKING ALL PDP CONTEXTS ===")
        send_at(ser, "AT+CGDCONT?", 1)
        
        print("\n=== CHECKING WHAT THE PHONE CARRIER SENT US ===")
        
        # Try to read OMA-DM (carrier configuration)
        send_at(ser, "AT+CUSATD?", 1)
        
        # Check for any special routing tables
        send_at(ser, "AT+CGCONTRDP=1", 1)  # Get runtime PDP context info
        send_at(ser, "AT+CGCONTRDP=2", 1)
        
        print("\n=== CRITICAL QUESTION ===")
        print("Does the modem have a PUBLIC IP or CGNAT/Private IP?")
        send_at(ser, "AT+CGPADDR=1", 1)
        
        response = send_at(ser, "AT+CGPADDR=1", 1)
        if "48." in response:  # Check if it's a public IP range
            print("\n[INFO] We have what looks like a public IP (48.x.x.x)")
            print("This might be CGNAT (Carrier Grade NAT)")
            print("CGNAT can block access to internal carrier services!")
        
        print("\n=== TRYING TO GET GATEWAY INFO ===")
        send_at(ser, "AT+CGCONTRDP", 2)
        
        ser.close()
        
        print("\n" + "="*60)
        print("HYPOTHESIS:")
        print("="*60)
        print("The modem is on CGNAT (carrier-grade NAT) which gives us")
        print("internet access but BLOCKS internal carrier network access.")
        print("")
        print("Phones work because they use:")
        print("  1. Different APN routing (MMS-specific)")
        print("  2. IMS network instead of internet network")
        print("  3. Special SIM provisioning")
        print("")
        print("POSSIBLE SOLUTION:")
        print("  - Need to find the MMS-specific APN")
        print("  - Or use IMS/VoLTE network instead")
        print("  - Or get carrier to provision MMS access on this SIM")
        print("="*60)
        
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


