#!/usr/bin/env python3
"""
MMS Test Script - Send long text as MMS
Uses Mint Mobile APN settings from user's configuration
"""
import serial
import time
import sys

# Mint Mobile MMS Configuration
APN = "Wholesale"
MMSC = "http://wholesale.mmsmvno.com/mms/wapenc"
MMS_PROXY = ""  # Leave blank per config
MMS_PORT = "8080"
COM_PORT = "COM24"
BAUDRATE = 115200

def send_at(ser, command, wait=1.0, show=True):
    """Send AT command and return response"""
    if show:
        print(f">> {command}")
    ser.write(f"{command}\r\n".encode())
    time.sleep(wait)
    response = ser.read_all().decode('utf-8', errors='ignore')
    if show:
        print(f"<< {response.strip()}")
    return response

def configure_mms_apn(ser):
    """Configure APN for MMS"""
    print("\n=== Configuring APN for MMS ===")
    
    # Set APN
    send_at(ser, f'AT+CGDCONT=1,"IP","{APN}"', 1)
    
    # Configure MMS settings (SIM7600 specific)
    send_at(ser, f'AT+CMMSCFG="{MMSC}","{MMS_PROXY}","{MMS_PORT}"', 1)
    
    # Set to MMS mode
    send_at(ser, 'AT+CMMSINIT', 2)
    
    # Check status
    response = send_at(ser, 'AT+CMMSINIT?', 1)
    if "1" in response:
        print("[OK] MMS initialized")
        return True
    else:
        print("[ERROR] MMS init failed")
        return False

def send_mms_text(ser, phone, message, subject=""):
    """
    Send MMS with long text (no image)
    This is the key: MMS can handle longer text than SMS
    """
    print(f"\n=== Sending MMS to {phone} ===")
    print(f"Message length: {len(message)} characters")
    
    # Edit MMS message
    response = send_at(ser, 'AT+CMMSEDIT=1', 1)
    if "OK" not in response:
        print("[ERROR] Failed to enter edit mode")
        return False
    
    # Add recipient
    response = send_at(ser, f'AT+CMMSRECP="{phone}"', 1)
    if "OK" not in response:
        print("[ERROR] Failed to add recipient")
        return False
    
    # Set subject (optional)
    if subject:
        send_at(ser, f'AT+CMMSDOWN="SUBJECT",{len(subject)},10000', 0.5, False)
        ser.write(subject.encode())
        time.sleep(0.5)
        ser.read_all()  # Clear response
    
    # Send text content
    # Note: MMS can handle much longer text than SMS (up to ~1000+ chars)
    print(f"Sending {len(message)} character text...")
    response = send_at(ser, f'AT+CMMSDOWN="TEXT",{len(message)},10000', 0.5, False)
    
    # Send the actual text
    ser.write(message.encode())
    time.sleep(1.0)
    response = ser.read_all().decode('utf-8', errors='ignore')
    print(f"Text upload: {response.strip()}")
    
    # Send the MMS
    print("\nSending MMS...")
    response = send_at(ser, 'AT+CMMSSEND', 10)  # May take longer
    
    if "OK" in response or "+CMMSSEND" in response:
        print("[OK] MMS sent successfully!")
        return True
    else:
        print(f"[ERROR] MMS send failed: {response}")
        return False

def main():
    phone = "+16199773020"
    
    # Long message without emojis (sanitized version of AI response)
    message = """Based on my review of the documentation, here's what I found about MMS capabilities:

MMS Status Summary

What We Know Works:
SMS sending/receiving: Fully operational via AT commands
Modem hardware: SIM7600G-H CAN technically send MMS
Carrier info: T-Mobile/Mint Mobile network

What's Required for MMS:
Data session management via APN - You just provided these settings!
MIME multipart message encoding for images/media
HTTP POST to MMSC endpoint carrier gateway
Media file handling resize, format conversion

NEW: You Have the Missing Piece!
The image shows Mint Mobile's MMS configuration with APN Wholesale and MMSC endpoint.

Previous Investigation Summary from October 2025:
Gammu installed v1.42.0 can send SMS
python-gammu v3.2.4 Python bindings working
MMS files created but later deleted during project reorganization"""

    print(f"Message length: {len(message)} characters")
    print(f"(Regular SMS would split this into {len(message)//150 + 1} separate messages)")
    
    try:
        print(f"\nConnecting to modem on {COM_PORT}...")
        ser = serial.Serial(COM_PORT, BAUDRATE, timeout=5)
        time.sleep(1)
        
        # Test connection
        response = send_at(ser, "AT", 1)
        if "OK" not in response:
            print("[ERROR] Modem not responding")
            return
        
        print("[OK] Modem connected")
        
        # Check signal
        response = send_at(ser, "AT+CSQ", 1)
        
        # Configure and send
        if configure_mms_apn(ser):
            success = send_mms_text(ser, phone, message)
            
            if success:
                print("\n" + "="*60)
                print("SUCCESS! MMS SENT!")
                print("="*60)
                print(f"To: {phone}")
                print(f"Length: {len(message)} chars (single message)")
                print("\nCheck your phone - should arrive as ONE message,")
                print("not multiple SMS bubbles!")
            else:
                print("\n[ERROR] MMS send failed - check logs above")
        
        ser.close()
        
    except serial.SerialException as e:
        print(f"\n[ERROR] Serial port error: {e}")
        print("Make sure:")
        print("  1. Conductor is stopped (COM port available)")
        print("  2. Modem is connected")
        print("  3. COM24 is correct port")
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

