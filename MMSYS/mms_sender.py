#!/usr/bin/env python3
"""
MMS Sender - Send long text messages as MMS via carrier MMSC
Direct HTTP POST to Mint Mobile's MMS gateway
"""
import serial
import time
import json
import sys
import struct
from datetime import datetime

class MMSSender:
    def __init__(self, config_path="config.json"):
        """Initialize MMS sender with configuration"""
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.modem = None
        self.debug = self.config['settings']['debug_mode']
        
    def log(self, message):
        """Log message if debug mode enabled"""
        if self.debug:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {message}")
    
    def send_at(self, command, wait=1.0, expect_ok=True):
        """Send AT command and return response"""
        self.log(f">> {command}")
        self.modem.write(f"{command}\r\n".encode())
        time.sleep(wait)
        response = self.modem.read_all().decode('utf-8', errors='ignore')
        self.log(f"<< {response.strip()}")
        
        if expect_ok and "OK" not in response:
            raise Exception(f"Command failed: {command}\nResponse: {response}")
        
        return response
    
    def connect_modem(self):
        """Connect to modem and verify it's working"""
        self.log("Connecting to modem...")
        port = self.config['modem']['port']
        baudrate = self.config['modem']['baudrate']
        
        self.modem = serial.Serial(
            port=port,
            baudrate=baudrate,
            timeout=self.config['modem']['timeout']
        )
        time.sleep(1)
        
        # Test connection
        self.send_at("AT")
        self.log("[OK] Modem connected")
        
        # Get modem info
        response = self.send_at("ATI")
        if "SIM7600" in response:
            self.log("[OK] SIM7600 modem detected")
        
        return True
    
    def disconnect_modem(self):
        """Disconnect from modem"""
        if self.modem and self.modem.is_open:
            self.modem.close()
            self.log("Modem disconnected")
    
    def setup_data_connection(self):
        """Configure PDP context and activate data connection"""
        self.log("\n=== Setting up data connection ===")
        
        apn = self.config['mms']['apn']
        
        # Check if already attached to GPRS
        response = self.send_at("AT+CGATT?")
        if "+CGATT: 0" in response:
            self.log("Attaching to GPRS network...")
            self.send_at("AT+CGATT=1", wait=5)
        
        # Configure PDP context (context 1, IP, APN)
        self.log(f"Configuring PDP context with APN: {apn}")
        self.send_at(f'AT+CGDCONT=1,"IP","{apn}"')
        
        # Check if PDP context is already active
        response = self.send_at("AT+CGACT?", wait=1, expect_ok=False)
        
        if "+CGACT: 1,1" in response:
            self.log("[OK] PDP context already active")
        else:
            # Activate PDP context
            self.log("Activating PDP context...")
            response = self.send_at("AT+CGACT=1,1", wait=3, expect_ok=False)
            
            if "ERROR" in response:
                raise Exception("Failed to activate data connection")
        
        # Get assigned IP address
        response = self.send_at("AT+CGPADDR=1")
        if "+CGPADDR" in response:
            self.log(f"[OK] Data connection established - {response.strip()}")
            return True
        else:
            raise Exception("No IP address assigned")
    
    def encode_wsp_string(self, text):
        """Encode string in WSP format (null-terminated)"""
        return text.encode('utf-8') + b'\x00'
    
    def encode_mms_message(self, from_number, to_number, message_text):
        """
        Encode MMS message in WAP/WSP format
        This is the binary encoding that carriers expect
        """
        self.log("\n=== Encoding MMS message ===")
        
        # MMS message structure (simplified M-Send.req PDU)
        pdu = b''
        
        # Message Type: m-send-req (0x80)
        pdu += b'\x8C\x80'
        
        # Transaction ID (unique ID for this message)
        transaction_id = str(int(time.time()))
        pdu += b'\x98' + self.encode_wsp_string(transaction_id)
        
        # MMS Version: 1.0 (0x10)
        pdu += b'\x8D\x90'
        
        # From: Your phone number
        from_encoded = self.encode_wsp_string(f"{from_number}/TYPE=PLMN")
        pdu += b'\x89' + bytes([0x80 + len(from_encoded)]) + from_encoded
        
        # To: Recipient phone number
        to_encoded = self.encode_wsp_string(f"{to_number}/TYPE=PLMN")
        pdu += b'\x97' + bytes([0x80 + len(to_encoded)]) + to_encoded
        
        # Subject (optional)
        subject = "MMS Message"
        pdu += b'\x96' + self.encode_wsp_string(subject)
        
        # Content-Type: application/vnd.wap.multipart.related
        pdu += b'\x84\xB3'
        
        # Message body (text/plain part)
        message_bytes = message_text.encode('utf-8')
        
        # Add text part
        pdu += b'\x00'  # Number of parts (will be 1)
        pdu += struct.pack('>I', len(message_bytes) + 20)  # Part length
        pdu += b'\x00'  # Headers length
        
        # Content-Type: text/plain
        pdu += b'\x83\x00'  # text/plain header
        pdu += b'\x8A\x80'  # Charset: UTF-8
        
        # The actual message text
        pdu += message_bytes
        
        self.log(f"Encoded PDU length: {len(pdu)} bytes")
        return pdu
    
    def send_http_post(self, pdu_data):
        """
        Send HTTP POST to MMSC endpoint via TCP
        Uses SIM7600 NETOPEN command set (newer method)
        """
        self.log("\n=== Establishing TCP connection ===")
        
        mmsc_url = self.config['mms']['mmsc']
        mmsc_port = self.config['mms']['mmsc_port']
        
        # Extract host from URL
        host = mmsc_url.replace('http://', '').split('/')[0]
        path = '/' + '/'.join(mmsc_url.replace('http://', '').split('/')[1:])
        
        self.log(f"Connecting to {host}:{mmsc_port}")
        
        # Step 1: Open network interface (SIM7600 NETOPEN method)
        response = self.send_at('AT+NETOPEN?', wait=1, expect_ok=False)
        
        if "+NETOPEN: 0" in response:
            # Network not open, open it
            self.log("Opening network interface...")
            response = self.send_at('AT+NETOPEN', wait=5, expect_ok=False)
            if "Network opened" not in response and "+NETOPEN: 0" not in response:
                raise Exception(f"Failed to open network: {response}")
            self.log("[OK] Network opened")
        else:
            self.log("[OK] Network already open")
        
        # Step 2: Get IP address
        response = self.send_at('AT+IPADDR', wait=1, expect_ok=False)
        if "+IPADDR" in response:
            self.log(f"[OK] IP address: {response.strip()}")
        
        # Step 3: Open TCP connection (link_num=0)
        self.log(f"Opening TCP connection to {host}:{mmsc_port}...")
        response = self.send_at(f'AT+CIPOPEN=0,"TCP","{host}",{mmsc_port}', 
                                 wait=10, expect_ok=False)
        
        if "+CIPOPEN: 0,0" not in response and "CONNECT" not in response:
            raise Exception(f"TCP connection failed: {response}")
        
        self.log("[OK] TCP connected")
        time.sleep(1)
        
        # Step 4: Build HTTP POST request
        http_request = f"POST {path} HTTP/1.1\r\n"
        http_request += f"Host: {host}:{mmsc_port}\r\n"
        http_request += "Content-Type: application/vnd.wap.mms-message\r\n"
        http_request += f"Content-Length: {len(pdu_data)}\r\n"
        http_request += "User-Agent: MMSYS/1.0\r\n"
        http_request += "Connection: close\r\n"
        http_request += "\r\n"
        
        http_bytes = http_request.encode() + pdu_data
        
        self.log(f"\n=== Sending HTTP POST ===")
        self.log(f"Total size: {len(http_bytes)} bytes")
        
        # Step 5: Send data (link_num=0)
        self.send_at(f'AT+CIPSEND=0,{len(http_bytes)}', wait=1, expect_ok=False)
        time.sleep(0.5)
        
        # Send the actual HTTP request + MMS PDU
        self.modem.write(http_bytes)
        self.log("Data sent, waiting for response...")
        time.sleep(3)
        
        # Step 6: Read response
        response = self.modem.read_all().decode('utf-8', errors='ignore')
        self.log(f"Response:\n{response}")
        
        # Step 7: Close connection
        self.send_at('AT+CIPCLOSE=0', wait=2, expect_ok=False)
        
        # Check for success indicators
        if "200 OK" in response or "M-Send.conf" in response:
            self.log("\n[SUCCESS] MMS accepted by carrier!")
            return True
        else:
            self.log("\n[WARNING] Unexpected response - check logs")
            return False
    
    def send_mms(self, to_number, message_text, from_number="+16199773020"):
        """
        Main method: Send MMS message
        
        Args:
            to_number: Recipient phone number (E.164 format)
            message_text: Message content (can be long)
            from_number: Sender phone number (defaults to your number)
        
        Returns:
            bool: True if sent successfully
        """
        try:
            print("\n" + "="*60)
            print("MMS SENDER - Long Message as Single Bubble")
            print("="*60)
            print(f"From: {from_number}")
            print(f"To: {to_number}")
            print(f"Message length: {len(message_text)} characters")
            print("="*60 + "\n")
            
            # Connect to modem
            self.connect_modem()
            
            # Setup data connection
            self.setup_data_connection()
            
            # Encode MMS message
            pdu = self.encode_mms_message(from_number, to_number, message_text)
            
            # Send via HTTP POST
            success = self.send_http_post(pdu)
            
            return success
            
        except Exception as e:
            self.log(f"\n[ERROR] {e}")
            import traceback
            traceback.print_exc()
            return False
        
        finally:
            self.disconnect_modem()

def main():
    """Command-line interface"""
    if len(sys.argv) < 3:
        print("Usage: python mms_sender.py <phone_number> <message>")
        print("Example: python mms_sender.py +16199773020 'Long message here...'")
        sys.exit(1)
    
    to_number = sys.argv[1]
    message = sys.argv[2]
    
    sender = MMSSender()
    success = sender.send_mms(to_number, message)
    
    if success:
        print("\n" + "="*60)
        print("SUCCESS! MMS sent as single bubble!")
        print("Check your phone - should arrive as ONE message.")
        print("="*60)
        sys.exit(0)
    else:
        print("\n" + "="*60)
        print("FAILED - Check logs above for details")
        print("="*60)
        sys.exit(1)

if __name__ == "__main__":
    main()

