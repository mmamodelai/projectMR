#!/usr/bin/env python3
"""
Force Network Re-registration to Trigger Queued Message Delivery
This forces the modem to re-register with T-Mobile network, which may
trigger delivery of any messages queued on the carrier's side.
"""

import serial
import time
import sys

COM_PORT = "COM24"
BAUD_RATE = 115200
TIMEOUT = 5

def send_at_command(ser, command, timeout=3):
    """Send AT command and return response"""
    ser.write(f"{command}\r\n".encode())
    time.sleep(timeout)
    response = ser.read_all().decode('utf-8', errors='ignore')
    return response.strip()

def force_reregistration():
    """Force modem to re-register with network"""
    print("=" * 70)
    print("FORCING NETWORK RE-REGISTRATION")
    print("=" * 70)
    print()
    print("This will:")
    print("  1. Disconnect from network")
    print("  2. Re-register with T-Mobile network")
    print("  3. Trigger delivery of any queued messages")
    print()
    
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"[OK] Connected to modem on {COM_PORT}\n")
        
        # Check current registration
        print("1. Current registration status:")
        creg_before = send_at_command(ser, "AT+CREG?", 1)
        print(f"   {creg_before}\n")
        
        # Force network deregistration
        print("2. Forcing network deregistration...")
        # AT+COPS=2 forces deregistration
        response = send_at_command(ser, "AT+COPS=2", 3)
        print(f"   {response}\n")
        
        # Wait a moment
        print("3. Waiting 3 seconds...")
        time.sleep(3)
        
        # Force re-registration (automatic mode)
        print("4. Forcing re-registration (automatic mode)...")
        # AT+COPS=0 forces automatic registration
        response = send_at_command(ser, "AT+COPS=0", 5)
        print(f"   {response}\n")
        
        # Wait for registration
        print("5. Waiting for network registration (10 seconds)...")
        time.sleep(10)
        
        # Check registration status
        print("6. Checking registration status:")
        creg_after = send_at_command(ser, "AT+CREG?", 1)
        print(f"   {creg_after}\n")
        
        # Check operator
        print("7. Checking network operator:")
        cops = send_at_command(ser, "AT+COPS?", 2)
        print(f"   {cops}\n")
        
        # Now check for messages
        print("8. Checking for messages after re-registration:")
        send_at_command(ser, "AT+CMGF=1", 1)
        
        # Check ME storage
        send_at_command(ser, 'AT+CPMS="ME","ME","ME"', 1)
        messages_me = send_at_command(ser, 'AT+CMGL="ALL"', 2)
        if "+CMGL:" in messages_me:
            count = messages_me.count("+CMGL:")
            print(f"   [FOUND] {count} messages in ME storage!")
            print(f"   {messages_me[:300]}...")
        else:
            print("   [NONE] No messages in ME storage")
        
        # Check SIM storage
        send_at_command(ser, 'AT+CPMS="SM","SM","SM"', 1)
        messages_sm = send_at_command(ser, 'AT+CMGL="ALL"', 2)
        if "+CMGL:" in messages_sm:
            count = messages_sm.count("+CMGL:")
            print(f"   [FOUND] {count} messages in SIM storage!")
            print(f"   {messages_sm[:300]}...")
        else:
            print("   [NONE] No messages in SIM storage")
        
        print()
        print("=" * 70)
        print("RE-REGISTRATION COMPLETE")
        print("=" * 70)
        print()
        print("If messages were queued on T-Mobile's network, they should")
        print("have been delivered during re-registration.")
        print()
        print("Next steps:")
        print("  1. Send a test message NOW")
        print("  2. Wait 30 seconds")
        print("  3. Run CHECK_MODEM_MEMORY.py to verify it arrived")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"[ERROR] Cannot connect to modem: {e}")
        print("Make sure Conductor is stopped before running this")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    force_reregistration()

