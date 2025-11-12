#!/usr/bin/env python3
"""
EMERGENCY: Check modem for messages RIGHT NOW
"""
import serial
import time
import re

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
        print("\n" + "="*60)
        print("EMERGENCY MODEM CHECK")
        print("="*60)
        
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        
        # Test connection
        response = send_at(ser, "AT")
        if "OK" not in response:
            print("\n[ERROR] Modem not responding!")
            return
        
        print("\n[OK] Modem connected")
        
        print("\n=== CHECKING MESSAGE STORAGE ===")
        
        # Check storage capacity
        response = send_at(ser, "AT+CPMS?", 2)
        
        # Parse storage info
        if "+CPMS:" in response:
            # Extract numbers like: +CPMS: "SM",5,30,"SM",5,30,"SM",5,30
            match = re.search(r'\+CPMS:\s*"[^"]+",(\d+),(\d+)', response)
            if match:
                used = int(match.group(1))
                total = int(match.group(2))
                print(f"\n[STORAGE] {used}/{total} messages")
                
                if used > 0:
                    print(f"\n[WARNING] {used} messages sitting on modem!")
                    print("These haven't been picked up by Conductor!")
                else:
                    print("\n[OK] Modem storage empty")
        
        # List ALL messages
        print("\n=== CHECKING FOR ANY MESSAGES ===")
        response = send_at(ser, 'AT+CMGL="ALL"', 3)
        
        # Count messages
        message_count = response.count('+CMGL:')
        
        if message_count > 0:
            print(f"\n[ALERT] FOUND {message_count} MESSAGE(S) ON MODEM!")
            print("\nMessages:")
            print(response)
            print("\n[WARNING] These messages are NOT in the database!")
            print("Conductor needs to be running to process them.")
        else:
            print("\n[OK] No messages found on modem")
            print("If you just sent messages, they might not have arrived yet")
            print("OR they were already processed and deleted")
        
        # Check signal
        print("\n=== MODEM STATUS ===")
        response = send_at(ser, "AT+CSQ", 1)
        if "+CSQ:" in response:
            match = re.search(r'\+CSQ:\s*(\d+),', response)
            if match:
                signal = int(match.group(1))
                print(f"Signal strength: {signal}/31 ({'Excellent' if signal > 25 else 'Good' if signal > 15 else 'Fair' if signal > 10 else 'Poor'})")
        
        # Check network registration
        send_at(ser, "AT+CREG?", 1)
        
        ser.close()
        
        print("\n" + "="*60)
        print("DIAGNOSIS:")
        print("="*60)
        if message_count > 0:
            print("[PROBLEM] Messages are sitting on modem")
            print("[PROBLEM] Conductor is NOT running (not processing them)")
            print("\n[FIX] Start Conductor:")
            print("   cd C:\\Dev\\conductor\\conductor-sms")
            print("   python conductor_system.py")
        else:
            print("[OK] Modem is clear (no unprocessed messages)")
            print("[WARNING] Conductor is NOT running")
            print("\nIf messages were sent:")
            print("  1. They might still be in transit (carrier delay)")
            print("  2. They were already processed and deleted")
            print("  3. Check Supabase to see if they're in the database")
            print("\n[FIX] TO RECEIVE NEW MESSAGES: Start Conductor:")
            print("   cd C:\\Dev\\conductor\\conductor-sms")
            print("   python conductor_system.py")
        print("="*60)
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Cannot access modem: {e}")
        print("\nPossible reasons:")
        print("  1. Another program is using COM24")
        print("  2. Modem disconnected")
        print("  3. Wrong COM port")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

