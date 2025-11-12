#!/usr/bin/env python3
"""
Check Network Registration and Carrier Message Queue Status
Diagnoses why messages might not be arriving from T-Mobile network
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

def check_network_status():
    """Check network registration and carrier connection status"""
    print("=" * 70)
    print("CHECKING NETWORK REGISTRATION & CARRIER STATUS")
    print("=" * 70)
    print()
    
    try:
        ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=TIMEOUT)
        print(f"[OK] Connected to modem on {COM_PORT}\n")
        
        # Set text mode
        send_at_command(ser, "AT+CMGF=1", 1)
        
        # 1. Check Network Registration (CREG)
        print("1. NETWORK REGISTRATION STATUS:")
        print("-" * 70)
        creg = send_at_command(ser, "AT+CREG?")
        print(creg)
        
        # Parse CREG response
        if "+CREG: 0,1" in creg or "+CREG: 0,5" in creg:
            print("   [OK] REGISTERED on home network")
        elif "+CREG: 0,2" in creg:
            print("   [WARN] SEARCHING for network...")
        elif "+CREG: 0,3" in creg:
            print("   [ERROR] REGISTRATION DENIED")
        elif "+CREG: 0,0" in creg:
            print("   [ERROR] NOT REGISTERED")
        else:
            print("   [WARN] Unknown registration status")
        print()
        
        # 2. Check GPRS Registration (CGREG)
        print("2. GPRS/DATA REGISTRATION STATUS:")
        print("-" * 70)
        cgreg = send_at_command(ser, "AT+CGREG?")
        print(cgreg)
        
        if "+CGREG: 0,1" in cgreg or "+CGREG: 0,5" in cgreg:
            print("   [OK] GPRS REGISTERED")
        else:
            print("   [INFO] GPRS not registered (SMS doesn't need this)")
        print()
        
        # 3. Check Signal Strength
        print("3. SIGNAL STRENGTH:")
        print("-" * 70)
        csq = send_at_command(ser, "AT+CSQ")
        print(csq)
        
        if "+CSQ:" in csq:
            try:
                parts = csq.split("+CSQ: ")[1].split(",")[0]
                rssi = int(parts.strip())
                if rssi >= 20:
                    print(f"   [OK] EXCELLENT signal ({rssi})")
                elif rssi >= 15:
                    print(f"   [OK] GOOD signal ({rssi})")
                elif rssi >= 10:
                    print(f"   [WARN] FAIR signal ({rssi})")
                elif rssi >= 5:
                    print(f"   [WARN] WEAK signal ({rssi})")
                else:
                    print(f"   [ERROR] VERY WEAK signal ({rssi})")
            except:
                pass
        print()
        
        # 4. Check Operator (should show T-Mobile)
        print("4. NETWORK OPERATOR:")
        print("-" * 70)
        cops = send_at_command(ser, "AT+COPS?")
        print(cops)
        if "T-Mobile" in cops or "310260" in cops or "310026" in cops:
            print("   [OK] Connected to T-Mobile network")
        print()
        
        # 5. Check Modem Phone Number (IMSI)
        print("5. MODEM IDENTITY:")
        print("-" * 70)
        cimi = send_at_command(ser, "AT+CIMI")
        print(f"IMSI: {cimi}")
        print()
        
        # 6. Check Message Storage Status
        print("6. MESSAGE STORAGE STATUS:")
        print("-" * 70)
        
        # Check ME storage
        cpms_me = send_at_command(ser, 'AT+CPMS="ME","ME","ME"')
        print(f"ME Storage: {cpms_me}")
        if "+CPMS:" in cpms_me:
            parts = cpms_me.split("+CPMS: ")[1].split(",")
            used_me = int(parts[0])
            total_me = int(parts[1])
            print(f"   ME: {used_me}/{total_me} messages")
        
        # Check SIM storage
        cpms_sm = send_at_command(ser, 'AT+CPMS="SM","SM","SM"')
        print(f"SIM Storage: {cpms_sm}")
        if "+CPMS:" in cpms_sm:
            parts = cpms_sm.split("+CPMS: ")[1].split(",")
            used_sm = int(parts[0])
            total_sm = int(parts[1])
            print(f"   SIM: {used_sm}/{total_sm} messages")
        print()
        
        # 7. Check CNMI Settings (message routing)
        print("7. MESSAGE ROUTING SETTINGS:")
        print("-" * 70)
        cnmi = send_at_command(ser, "AT+CNMI?")
        print(cnmi)
        if "+CNMI: 2,0,0,0,0" in cnmi:
            print("   [OK] CNMI=2,0,0,0,0 (Store in memory, no forwarding)")
        print()
        
        # 8. Try to query for RECEIVED UNREAD messages specifically
        print("8. CHECKING FOR UNREAD MESSAGES:")
        print("-" * 70)
        
        # Set to ME storage
        send_at_command(ser, 'AT+CPMS="ME","ME","ME"', 1)
        unread_me = send_at_command(ser, 'AT+CMGL="REC UNREAD"', 2)
        if "+CMGL:" in unread_me:
            count = unread_me.count("+CMGL:")
            print(f"   Found {count} UNREAD messages in ME storage")
            print(unread_me[:500])  # Show first 500 chars
        else:
            print("   No unread messages in ME storage")
        
        # Set to SIM storage
        send_at_command(ser, 'AT+CPMS="SM","SM","SM"', 1)
        unread_sm = send_at_command(ser, 'AT+CMGL="REC UNREAD"', 2)
        if "+CMGL:" in unread_sm:
            count = unread_sm.count("+CMGL:")
            print(f"   Found {count} UNREAD messages in SIM storage")
            print(unread_sm[:500])
        else:
            print("   No unread messages in SIM storage")
        print()
        
        # 9. DIAGNOSIS
        print("=" * 70)
        print("DIAGNOSIS:")
        print("=" * 70)
        
        if "+CREG: 0,1" not in creg and "+CREG: 0,5" not in creg:
            print("[ERROR] PROBLEM: Modem is NOT registered on network!")
            print("   -> Messages from carrier cannot be delivered")
            print("   -> Check antenna, SIM card, or network coverage")
        else:
            print("[OK] Modem IS registered on network")
            print("   -> Carrier can deliver messages")
        
        if "+CSQ:" in csq:
            try:
                rssi = int(csq.split("+CSQ: ")[1].split(",")[0].strip())
                if rssi < 10:
                    print("[WARN] WARNING: Weak signal strength")
                    print("   -> Messages may be delayed or lost")
            except:
                pass
        
        print()
        print("NOTE: If registered but no messages arriving:")
        print("  - Messages may be queued on T-Mobile's network")
        print("  - T-Mobile queues messages for 24-48 hours when device offline")
        print("  - Messages should auto-deliver when modem registers")
        print("  - Try power cycling modem to force re-registration")
        
        ser.close()
        print("\n[OK] Check complete")
        
    except serial.SerialException as e:
        print(f"[ERROR] Cannot connect to modem: {e}")
        print("Make sure Conductor is stopped before running this check")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    check_network_status()

