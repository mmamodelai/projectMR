#!/usr/bin/env python3
"""
Analyze modem storage management and identify potential issues
"""
import serial
import time
import json
from datetime import datetime

def send_at(ser, cmd, wait=1.0):
    ser.write(f"{cmd}\r\n".encode())
    time.sleep(wait)
    return ser.read_all().decode('utf-8', errors='ignore')

print("\n" + "="*70)
print("MODEM STORAGE MANAGEMENT ANALYSIS")
print("="*70)

try:
    # Connect to modem
    print("\nConnecting to modem...")
    for i in range(10):
        try:
            ser = serial.Serial("COM24", 115200, timeout=5)
            print("[OK] Connected")
            break
        except:
            time.sleep(1)
    
    time.sleep(1)
    send_at(ser, "AT")
    
    # Check ME (Phone Memory) capacity
    print("\n=== ME (PHONE MEMORY) STORAGE ===")
    send_at(ser, 'AT+CPMS="ME","ME","ME"')
    resp = send_at(ser, "AT+CPMS?")
    print(resp)
    
    # Parse capacity
    import re
    match = re.search(r'"ME",(\d+),(\d+)', resp)
    if match:
        me_used = int(match.group(1))
        me_total = int(match.group(2))
        me_percent = (me_used / me_total * 100) if me_total > 0 else 0
        print(f"\nME: {me_used}/{me_total} ({me_percent:.1f}% full)")
    
    # Check SM (SIM Card) capacity
    print("\n=== SM (SIM CARD) STORAGE ===")
    send_at(ser, 'AT+CPMS="SM","SM","SM"')
    resp = send_at(ser, "AT+CPMS?")
    print(resp)
    
    match = re.search(r'"SM",(\d+),(\d+)', resp)
    if match:
        sm_used = int(match.group(1))
        sm_total = int(match.group(2))
        sm_percent = (sm_used / sm_total * 100) if sm_total > 0 else 0
        print(f"\nSM: {sm_used}/{sm_total} ({sm_percent:.1f}% full)")
    
    ser.close()
    
    # Analyze Conductor's deletion behavior
    print("\n" + "="*70)
    print("CONDUCTOR DELETION ANALYSIS")
    print("="*70)
    
    # Check logs for deletion activity
    print("\nChecking recent logs for message deletion...")
    try:
        with open('logs/conductor_system.log', 'r') as f:
            lines = f.readlines()
            
            # Look for deletion commands
            deletion_lines = [l for l in lines[-500:] if 'AT+CMGD' in l]
            if deletion_lines:
                print(f"\n[OK] Found {len(deletion_lines)} deletion commands in last 500 log lines")
                print("Sample deletions:")
                for line in deletion_lines[-5:]:
                    print(f"  {line.strip()}")
            else:
                print("\n[WARNING] No deletion commands found in recent logs!")
                print("Messages might not be getting deleted after processing!")
    except Exception as e:
        print(f"Could not read logs: {e}")
    
    # Calculate storage health
    print("\n" + "="*70)
    print("STORAGE HEALTH ASSESSMENT")
    print("="*70)
    
    total_capacity = me_total + sm_total
    total_used = me_used + sm_used
    total_free = total_capacity - total_used
    
    print(f"\nTotal Capacity: {total_capacity} messages")
    print(f"  - ME (Phone): {me_total} messages")
    print(f"  - SM (SIM):   {sm_total} messages")
    print()
    print(f"Current Usage:  {total_used}/{total_capacity} messages ({(total_used/total_capacity*100):.1f}% full)")
    print(f"Free Space:     {total_free} messages")
    
    # Calculate time to fill
    print("\n=== TIME TO FILL CALCULATION ===")
    
    # Check config for poll interval
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            poll_interval = config.get('polling', {}).get('interval', 5)
            print(f"\nPoll interval: {poll_interval} seconds")
    except:
        poll_interval = 5
    
    # If messages aren't deleted, calculate fill time
    print(f"\nScenario 1: Messages NOT deleted (BROKEN)")
    print(f"  - Capacity: {total_capacity} messages")
    print(f"  - Poll interval: {poll_interval} seconds")
    print(f"  - Time to poll each message: {poll_interval}s")
    print(f"  - Time to fill: {total_capacity * poll_interval / 60:.1f} minutes")
    print(f"  - Result: System would stop receiving in ~{total_capacity * poll_interval / 60:.0f} minutes")
    
    print(f"\nScenario 2: Messages deleted after processing (WORKING)")
    print(f"  - Capacity: {total_capacity} messages")
    print(f"  - Max messages in queue: ~{poll_interval} (messages arriving during poll)")
    print(f"  - Storage usage: 0-5 messages typically")
    print(f"  - Result: System runs indefinitely")
    
    # Status
    print("\n" + "="*70)
    print("VERDICT")
    print("="*70)
    
    if total_used == 0:
        print("\n[HEALTHY] Storage is empty")
        print("  - Messages are being deleted after processing")
        print("  - No risk of filling up")
    elif total_used < 5:
        print("\n[HEALTHY] Storage has minimal usage")
        print(f"  - {total_used} message(s) in storage")
        print("  - This is normal during processing")
        print("  - No immediate risk")
    elif total_used < 10:
        print("\n[CAUTION] Storage has moderate usage")
        print(f"  - {total_used} message(s) in storage")
        print("  - Check if deletions are working")
        print("  - Monitor for increase")
    else:
        print("\n[WARNING] Storage is accumulating messages!")
        print(f"  - {total_used} message(s) in storage")
        print("  - Deletions may not be working")
        print("  - Risk of filling up")
    
    # Recommendations
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    print()
    
    if total_used == 0:
        print("✓ System is healthy - no action needed")
        print()
        print("Prevention:")
        print("  - Storage monitoring is already in code")
        print("  - Emergency cleanup at 90% full (line 392 in conductor_system.py)")
        print("  - Messages deleted immediately after save to database")
    else:
        print("! Check deletion behavior:")
        print("  1. Watch logs for 'AT+CMGD' commands")
        print("  2. Verify storage stays at 0 between polls")
        print("  3. If storage grows, deletion is broken")
        print()
        print("Manual cleanup if needed:")
        print("  AT+CMGD=1,4  (delete all messages)")
    
    print()
    
except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

