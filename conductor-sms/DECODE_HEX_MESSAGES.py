#!/usr/bin/env python3
"""
Decode hex-encoded messages in database
"""
import json
from supabase import create_client

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

db_config = config['database']
supabase = create_client(db_config['supabase_url'], db_config['supabase_key'])

def decode_hex_message(hex_str):
    """Decode hex/UCS2 encoded message"""
    try:
        # Remove any spaces or non-hex characters
        hex_str = ''.join(c for c in hex_str if c in '0123456789ABCDEFabcdef')
        
        # Try UTF-16 BE (Big Endian) decoding
        # Each character is 4 hex digits (2 bytes)
        if len(hex_str) % 4 == 0:
            decoded = ''
            for i in range(0, len(hex_str), 4):
                hex_char = hex_str[i:i+4]
                try:
                    char_code = int(hex_char, 16)
                    decoded += chr(char_code)
                except:
                    decoded += f'[{hex_char}]'
            return decoded
        return None
    except Exception as e:
        return None

print("\n" + "="*70)
print("DECODING HEX-ENCODED MESSAGES")
print("="*70)

# Get recent messages that look like hex
response = supabase.table("messages").select("*").eq("direction", "inbound").order("timestamp", desc=True).limit(20).execute()

hex_messages = []
for msg in response.data:
    content = msg['content']
    # Check if it looks like hex (lots of digits, 006, 002, etc.)
    if content and len(content) > 10 and all(c in '0123456789ABCDEFabcdef' for c in content.replace(' ', '')[:50]):
        hex_messages.append(msg)

if not hex_messages:
    print("\n[OK] No hex-encoded messages found!")
    print("All recent messages are in plain text.")
else:
    print(f"\n[FOUND] {len(hex_messages)} hex-encoded message(s):\n")
    
    for msg in hex_messages:
        print(f"ID: {msg['id']}")
        print(f"From: {msg['phone_number']}")
        print(f"Time: {msg['timestamp']}")
        print(f"Raw: {msg['content'][:80]}...")
        
        decoded = decode_hex_message(msg['content'])
        if decoded:
            print(f"DECODED: {decoded}")
        else:
            print("DECODED: [Could not decode]")
        print()

print("\n" + "="*70)
print("DIAGNOSIS")
print("="*70)

if hex_messages:
    print("\n[ISSUE] Messages are arriving in UCS2/UTF-16 encoding!")
    print()
    print("ROOT CAUSE:")
    print("  - Modem character set (CSCS) might be wrong")
    print("  - Should be 'GSM' or 'IRA' for plain text")
    print("  - Currently might be 'UCS2' (Unicode)")
    print()
    print("FIX:")
    print("  1. Check character set: AT+CSCS?")
    print("  2. Set to GSM: AT+CSCS=\"GSM\"")
    print("  3. Save: AT&W")
    print()
    print("This happened after the modem reset.")
    print("The CSCS=GSM command in reset script should have fixed it,")
    print("but these messages arrived before the fix.")
else:
    print("\n[OK] All messages are in plain text")
    print("Character set is configured correctly")

print()

