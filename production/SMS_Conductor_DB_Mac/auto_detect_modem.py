#!/usr/bin/env python3
"""
Auto-Detect Modem Port
Finds the Simcom modem on any COM port and updates config.json

Usage:
    python auto_detect_modem.py
"""

import json
import serial.tools.list_ports
import os
import sys

CONFIG_PATH = "config.json"

def find_modem_port():
    """Find the Simcom modem's AT PORT on any COM port"""
    ports = serial.tools.list_ports.comports()
    
    print("Scanning for Simcom modem...")
    for port in ports:
        # Look for Simcom AT PORT
        if "Simcom" in port.description and "AT PORT" in port.description:
            print(f"  Found modem AT PORT: {port.device}")
            return port.device
    
    # Fallback: look for any Simcom device
    for port in ports:
        if "Simcom" in port.description:
            print(f"  Found Simcom device: {port.device} ({port.description})")
            return port.device
    
    print("  ERROR: No Simcom modem found!")
    return None

def update_config(port):
    """Update config.json with the new port"""
    if not os.path.exists(CONFIG_PATH):
        print(f"ERROR: {CONFIG_PATH} not found!")
        return False
    
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = json.load(f)
        
        old_port = config["modem"]["port"]
        config["modem"]["port"] = port
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"  Updated: {old_port} → {port}")
        return True
    except Exception as e:
        print(f"ERROR updating config: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  AUTO-DETECT MODEM PORT")
    print("=" * 50)
    print()
    
    port = find_modem_port()
    if port:
        if update_config(port):
            print()
            print("✓ Success! Modem port updated.")
            print(f"  Now using: {port}")
            sys.exit(0)
    
    print()
    print("✗ Failed to auto-detect modem!")
    sys.exit(1)



