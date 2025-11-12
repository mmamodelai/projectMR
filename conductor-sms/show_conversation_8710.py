#!/usr/bin/env python3
"""
Show full conversation history with +13502068710 (Rebecca)
Decodes hex-encoded messages to plain text
"""

import os
import sys
import json
from supabase import create_client, Client

def load_config():
    """Load Supabase config"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        config = json.load(f)
    return config['database']

def is_hex_encoded(content):
    """Check if message content is hex-encoded UCS2"""
    if not content:
        return False
    # UCS2 hex messages start with 4-digit hex codes (0048, 0065, etc)
    if len(content) > 8 and all(c in '0123456789ABCDEFabcdef' for c in content[:8]):
        return True
    return False

def decode_hex_message(hex_content):
    """Decode UCS2/UTF-16 hex message to plain text"""
    try:
        # Remove spaces if any
        hex_content = hex_content.replace(' ', '')
        
        # Convert hex to bytes (UCS2 = UTF-16BE)
        byte_data = bytes.fromhex(hex_content)
        
        # Decode as UTF-16 Big Endian
        decoded = byte_data.decode('utf-16-be', errors='replace')
        
        return decoded
    except Exception as e:
        return f"[DECODE ERROR: {e}]"

def format_timestamp(ts):
    """Format timestamp for display"""
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %I:%M:%S %p')
    except:
        return ts

def main():
    print("=" * 70)
    print("CONVERSATION HISTORY: +13502068710 (Rebecca)")
    print("=" * 70)
    
    # Load config and connect
    db_config = load_config()
    supabase: Client = create_client(db_config['supabase_url'], db_config['supabase_key'])
    
    # Query all messages from/to this number
    phone = "+13502068710"
    response = supabase.table("messages").select("*").eq(
        "phone_number", phone
    ).order("timestamp", desc=False).execute()
    
    messages = response.data
    
    if not messages:
        print(f"\n[NO MESSAGES] No conversation found with {phone}")
        return
    
    print(f"\n[FOUND] {len(messages)} message(s) in conversation\n")
    
    # Display each message
    for i, msg in enumerate(messages, 1):
        msg_id = msg.get('id')
        direction = msg.get('direction', 'unknown')
        timestamp = msg.get('timestamp', 'N/A')
        content = msg.get('content', '')
        status = msg.get('status', 'unknown')
        
        # Decode if hex-encoded
        is_hex = is_hex_encoded(content)
        if is_hex:
            decoded_content = decode_hex_message(content)
            content_display = f"{decoded_content}\n    [ORIGINAL HEX: {content[:50]}...]"
        else:
            content_display = content
        
        # Format direction
        if direction == 'inbound':
            arrow = "<- FROM"
            phone_display = phone
        else:
            arrow = "-> TO"
            phone_display = phone
        
        # Print message
        print(f"[{i}] ID: {msg_id} | {format_timestamp(timestamp)}")
        print(f"    {arrow} {phone_display} | Status: {status}")
        if is_hex:
            print(f"    [HEX-ENCODED MESSAGE - DECODED:]")
        print(f"    {content_display}")
        print()

if __name__ == "__main__":
    main()

