#!/usr/bin/env python3
"""
Watch modem for incoming messages in REAL TIME
"""
import serial
import time
from datetime import datetime

COM_PORT = "COM24"
BAUDRATE = 115200

def send_at(ser, command, wait=0.5):
    """Send AT command and return response"""
    ser.write(f"{command}\r\n".encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    return response

print("\n" + "="*60)
print("WATCHING MODEM FOR INCOMING MESSAGES")
print("="*60)
print("\nPress Ctrl+C to stop")
print("\nWaiting for connection window...")

# Wait for Conductor to release COM port
connected = False
for attempt in range(20):
    try:
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
        connected = True
        print(f"\n[OK] Connected to modem at {datetime.now().strftime('%H:%M:%S')}")
        break
    except serial.SerialException:
        print(f".", end="", flush=True)
        time.sleep(0.5)

if not connected:
    print("\n\n[ERROR] Could not connect - Conductor might be polling continuously")
    print("Try stopping Conductor first: STOP_CONDUCTOR.bat")
    exit(1)

time.sleep(1)

# Test modem
response = send_at(ser, "AT")
if "OK" not in response:
    print("[ERROR] Modem not responding")
    ser.close()
    exit(1)

# Set text mode
send_at(ser, "AT+CMGF=1")

# Enable unsolicited message notifications
send_at(ser, "AT+CNMI=2,1,0,0,0")

print("\n" + "="*60)
print("LISTENING FOR INCOMING MESSAGES...")
print("="*60)
print("\n[READY] SEND YOUR TEST MESSAGE NOW!")
print("   Text: 'LIVE TEST 1025' to (619) 558-7489")
print()

try:
    last_check = time.time()
    check_interval = 2  # Check every 2 seconds
    
    while True:
        # Check for unsolicited notifications
        if ser.in_waiting > 0:
            data = ser.read(ser.in_waiting).decode('utf-8', errors='ignore')
            if data.strip():
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] MODEM OUTPUT:")
                print(data)
                
                if "+CMTI:" in data or "+CMT:" in data:
                    print("\n[ALERT] MESSAGE NOTIFICATION RECEIVED!")
                    print("Fetching message...")
                    time.sleep(0.5)
                    
                    # Read all messages
                    response = send_at(ser, 'AT+CMGL="ALL"', 2)
                    print("\nMessages on modem:")
                    print(response)
        
        # Periodic manual check
        if time.time() - last_check > check_interval:
            response = send_at(ser, "AT+CPMS?", 0.5)
            if "+CPMS:" in response:
                # Parse message count
                import re
                match = re.search(r'\+CPMS:\s*"[^"]+",(\d+),(\d+)', response)
                if match:
                    used = int(match.group(1))
                    total = int(match.group(2))
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Storage: {used}/{total}", end="\r", flush=True)
                    
                    if used > 0:
                        print(f"\n\n[FOUND] {used} MESSAGE(S)!")
                        response = send_at(ser, 'AT+CMGL="ALL"', 2)
                        print("\nMessages:")
                        print(response)
                        print("\n[SUCCESS] YOUR MESSAGE ARRIVED!")
                        break
            
            last_check = time.time()
        
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n\n[STOPPED] User interrupted")
except Exception as e:
    print(f"\n\n[ERROR] {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("\n[OK] Disconnected from modem")

print()

