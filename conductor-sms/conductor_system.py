#!/usr/bin/env python3
"""
Conductor SMS System v2.0 - Improved Production Version
Part of Conductor SMS System

Architecture:
    Polling-based, connect/disconnect pattern
    Never holds COM port for more than configured max time
    
Improvements over v1.0:
    - JSON configuration file
    - Regex-based message parsing (handles multi-line)
    - Batch outgoing sends
    - Duplicate detection
    - Log rotation
    - Preserves modem timestamps
    - Better error handling
    - Database indexes for performance
"""

import serial
import serial.tools.list_ports
import sqlite3
import logging
from logging.handlers import RotatingFileHandler
import time
import re
import hashlib
import json
import os
from datetime import datetime, timezone
import sys
from supabase import create_client, Client

def normalize_phone_number(phone):
    """
    Normalize phone number to E.164 format (+1XXXXXXXXXX)
    Handles: 619-977-3020, (619) 977-3020, 6199773020, +16199773020
    Returns: +16199773020
    """
    if not phone or not isinstance(phone, str):
        return phone
    
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # If it starts with 1 and has 11 digits, add +
    if len(digits) == 11 and digits[0] == '1':
        return '+' + digits
    
    # If it has 10 digits, assume US number, add +1
    if len(digits) == 10:
        return '+1' + digits
    
    # If it already has +, return as-is
    if phone.startswith('+'):
        return phone
    
    # Otherwise return original (might be international or invalid)
    return phone

# Load configuration
CONFIG_FILE = "config.json"

def load_config():
    """Load configuration from JSON file"""
    config_path = os.path.join(os.path.dirname(__file__), CONFIG_FILE)
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: Configuration file '{CONFIG_FILE}' not found!")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in configuration file: {e}")
        sys.exit(1)

config = load_config()

# Setup logging with rotation
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

log_level = getattr(logging, config['logging']['level'].upper(), logging.INFO)
max_bytes = config['logging']['max_file_size_mb'] * 1024 * 1024
backup_count = config['logging']['backup_count']

logging.basicConfig(
    level=log_level,
    format='%(asctime)s - Conductor - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            os.path.join(log_dir, "conductor_system.log"),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Conductor")


class ConductorSystem:
    """Main conductor system with polling architecture"""
    
    def __init__(self):
        """Initialize conductor system from configuration"""
        self.port = config['modem']['port']
        self.baudrate = config['modem']['baudrate']
        self.modem_timeout = config['modem']['timeout']
        self.at_timeout = config['modem']['at_command_timeout']
        self.send_timeout = config['modem']['send_timeout']
        
        self.db_path = config['database']['path']
        self.db_timeout = config['database']['connection_timeout']
        self.use_wal = config['database']['use_wal_mode']
        self.use_supabase = config['database'].get('use_supabase', False)
        
        # Initialize Supabase client if enabled
        self.supabase: Client = None
        if self.use_supabase:
            supabase_url = config['database']['supabase_url']
            supabase_key = config['database']['supabase_key']
            self.supabase = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized")
        
        self.poll_interval = config['polling']['interval']
        self.batch_outgoing = config['polling']['batch_outgoing']
        self.max_batch_size = config['polling']['max_batch_size']
        self.pause_between_ops = config['polling']['pause_between_operations']
        
        self.duplicate_detection = config['features']['duplicate_detection']
        self.preserve_timestamps = config['features']['preserve_modem_timestamps']
        self.health_check = config['features']['modem_health_check']
        
        self.log_at_commands = config['logging']['log_at_commands']
        
        self.connection = None
        self.running = False
        
        # Initialize database
        self._initialize_db()
        
        logger.info("Conductor System v2.0 initialized")
        logger.info(f"Configuration: Port={self.port}, Poll={self.poll_interval}s, Batch={self.batch_outgoing}")
        logger.info(f"Database: {'Supabase' if self.use_supabase else 'SQLite'} ({self.db_path})")
    
    def _initialize_db(self):
        """Initialize database with schema and indexes"""
        if self.use_supabase:
            # Supabase table already exists from setup script
            logger.info("Using Supabase database (table already exists)")
            return
            
        # SQLite initialization
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
            # Enable WAL mode if configured
            if self.use_wal:
                conn.execute("PRAGMA journal_mode=WAL")
                logger.info("Database WAL mode enabled")
            
            # Create messages table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    modem_timestamp TEXT,
                    status TEXT NOT NULL,
                    direction TEXT NOT NULL,
                    modem_index TEXT,
                    message_hash TEXT,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    retry_count INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON messages(status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_direction ON messages(direction)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON messages(timestamp)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_message_hash ON messages(message_hash)")
            
            conn.commit()
            logger.info("SQLite database initialized with indexes")
    
    def _connect_modem(self):
        """Connect to modem via serial port with improved conflict handling"""
        # Always disconnect first to ensure clean state
        self._disconnect_modem()
        time.sleep(0.1)  # Brief pause to let port release
        
        try:
            self.connection = serial.Serial(
                self.port,
                self.baudrate,
                timeout=self.modem_timeout
            )
            time.sleep(0.5)  # Let connection stabilize
            
            # Test connection with simple AT command
            try:
                self.connection.write(b'AT\r\n')
                time.sleep(0.1)
                response = self.connection.read_all().decode('utf-8', errors='ignore')
                if 'OK' not in response:
                    logger.warning(f"Modem response unclear: {response}")
            except Exception as e:
                logger.warning(f"Could not test modem connection: {e}")
            
            return True
        except serial.SerialException as e:
            logger.error(f"Cannot connect to modem on {self.port}: {e}")
            available_ports = [p.device for p in serial.tools.list_ports.comports()]
            logger.info(f"Available ports: {available_ports}")
            
            # Check if port is in use by another process
            if "in use" in str(e).lower() or "resource is in use" in str(e).lower():
                logger.warning("COM port appears to be in use by another process")
                logger.info("This might be due to:")
                logger.info("- Another Conductor instance running")
                logger.info("- Flash SMS tool using the port")
                logger.info("- Another application accessing the modem")
                logger.info("Try closing other applications or restarting Conductor")
            
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to modem: {e}")
            return False
    
    def _disconnect_modem(self):
        """Disconnect from modem"""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception as e:
                logger.error(f"Error closing modem connection: {e}")
    
    def _send_at_command(self, command, timeout=None):
        """Send AT command and return response"""
        if timeout is None:
            timeout = self.at_timeout
        
        try:
            if self.log_at_commands:
                logger.debug(f"AT Command: {command}")
            
            self.connection.write(f"{command}\r\n".encode())
            
            # Active polling loop until OK/ERROR or timeout
            response = ""
            start_time = time.time()
            while time.time() - start_time < timeout:
                if self.connection.in_waiting:
                    data = self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                    response += data
                    if 'OK' in response or 'ERROR' in response:
                        break
                time.sleep(0.05)
            
            if self.log_at_commands:
                logger.debug(f"Response: {response[:200]}")
            
            return response
        except Exception as e:
            logger.error(f"AT command failed: {e}")
            return None
    
    def _parse_modem_timestamp(self, timestamp_str):
        """
        Parse modem timestamp format: "25/09/30,22:45:10-28"
        Returns ISO format timestamp or None
        """
        try:
            # Extract date and time, ignore timezone for now
            match = re.match(r'(\d{2})/(\d{2})/(\d{2}),(\d{2}):(\d{2}):(\d{2})', timestamp_str)
            if match:
                yy, mm, dd, hh, mi, ss = match.groups()
                # Assume 20xx for year
                year = 2000 + int(yy)
                dt = datetime(year, int(mm), int(dd), int(hh), int(mi), int(ss))
                return dt.isoformat()
        except Exception as e:
            logger.warning(f"Could not parse modem timestamp '{timestamp_str}': {e}")
        return None
    
    def _calculate_message_hash(self, phone_number, content):
        """Calculate hash for duplicate detection"""
        if not self.duplicate_detection:
            return None
        
        # Hash based on phone number and content
        data = f"{phone_number}|{content}".encode('utf-8')
        return hashlib.sha256(data).hexdigest()[:16]
    
    def _is_duplicate(self, message_hash):
        """Check if message hash already exists in recent messages"""
        if not self.duplicate_detection or not message_hash:
            return False
        
        try:
            with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                # Check for duplicate in last 24 hours
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM messages 
                    WHERE message_hash = ? 
                    AND timestamp > datetime('now', '-1 day')
                """, (message_hash,))
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            logger.error(f"Error checking for duplicate: {e}")
            return False
    
    def _parse_messages(self, response):
        """
        Parse AT+CMGL response using regex
        Handles multi-line messages properly
        
        Returns list of dicts: {'index', 'status', 'phone', 'timestamp', 'content'}
        """
        messages = []
        
        # Regex pattern for +CMGL header
        # Example: +CMGL: 1,"REC UNREAD","+16199773020","","25/09/30,22:45:10-28"
        header_pattern = r'\+CMGL:\s*(\d+),"([^"]+)","([^"]+)","[^"]*","([^"]+)"'
        
        lines = response.split('\r\n')
        i = 0
        
        while i < len(lines):
            line = lines[i]
            
            # Check if this line is a message header
            match = re.search(header_pattern, line)
            if match:
                index = match.group(1)
                status = match.group(2)
                phone = match.group(3)
                modem_timestamp = match.group(4)
                
                # Content is on following lines until next +CMGL or OK
                content_lines = []
                i += 1
                while i < len(lines):
                    if lines[i].startswith('+CMGL:') or lines[i].strip() == 'OK':
                        break
                    if lines[i].strip():  # Skip empty lines
                        content_lines.append(lines[i])
                    i += 1
                
                content = '\n'.join(content_lines).strip()
                
                if content:  # Only add if content exists
                    messages.append({
                        'index': index,
                        'status': status,
                        'phone': phone,
                        'modem_timestamp': modem_timestamp,
                        'content': content
                    })
                
                continue
            
            i += 1
        
        return messages
    
    def _check_storage_capacity(self):
        """Check modem storage capacity and warn if getting full"""
        try:
            response = self._send_at_command('AT+CPMS?')
            if response and '+CPMS:' in response:
                # Parse: +CPMS: "ME",5,23,"ME",5,23,"ME",5,23
                import re
                match = re.search(r'"ME",(\d+),(\d+)', response)
                if match:
                    used = int(match.group(1))
                    total = int(match.group(2))
                    percent = (used / total) * 100 if total > 0 else 0
                    
                    if percent > 80:
                        logger.warning(f"⚠️ Modem storage {percent:.0f}% full ({used}/{total})!")
                    
                    if percent >= 90:
                        logger.error(f"🚨 CRITICAL: Modem storage {percent:.0f}% full! Emergency cleanup!")
                        # Delete all read messages
                        self._send_at_command('AT+CMGD=1,1')  # Delete all read messages
                        logger.info("Emergency cleanup: deleted all read messages")
                    
                    return used, total
        except Exception as e:
            logger.error(f"Failed to check storage: {e}")
        return 0, 0
    
    def check_incoming_messages(self):
        """Check for incoming messages (improved with regex parsing)"""
        logger.info("Checking for incoming messages...")
        
        # Always disconnect first to ensure clean state
        self._disconnect_modem()
        
        if not self._connect_modem():
            logger.error("Cannot connect to modem for incoming check")
            self._disconnect_modem()  # Ensure disconnect even on failure
            return
        
        connection_start = time.time()
        
        # Check storage capacity BEFORE reading messages
        used, total = self._check_storage_capacity()
        if used > 0:
            logger.debug(f"Modem storage: {used}/{total} messages")
        
        try:
            # Set text mode
            self._send_at_command("AT+CMGF=1")
            
            # Set SMS storage to Phone Memory (ME) - more reliable than SIM
            self._send_at_command('AT+CPMS="ME","ME","ME"')
            
            # CRITICAL FIX: Mode 1,1 = Keep messages in storage + notify on arrival
            # This prevents auto-deletion of messages before Conductor can read them!
            # Previously was 2,0 which caused messages to be auto-deleted
            self._send_at_command('AT+CNMI=1,1,0,0,0')
            
            # Read all messages from phone memory
            response = self._send_at_command('AT+CMGL="ALL"')
            
            if response and '+CMGL:' in response:
                messages = self._parse_messages(response)
                
                for msg in messages:
                    # Calculate hash for duplicate detection
                    msg_hash = self._calculate_message_hash(msg['phone'], msg['content'])
                    
                    if self._is_duplicate(msg_hash):
                        logger.warning(f"Duplicate message detected from {msg['phone']}, skipping")
                        # Still delete from modem
                        self._send_at_command(f"AT+CMGD={msg['index']}")
                        continue
                    
                    # Save to database
                    self._save_incoming_message(
                        msg['phone'],
                        msg['content'],
                        msg['index'],
                        msg['modem_timestamp'],
                        msg_hash
                    )
                    
                    # Delete from modem
                    self._send_at_command(f"AT+CMGD={msg['index']}")
                    
                    logger.info(f"Processed message {msg['index']} from {msg['phone'][:10]}****")
                
                if messages:
                    logger.info(f"Found and processed {len(messages)} incoming messages")
            else:
                logger.info("No messages found on modem")
            
            connection_time = time.time() - connection_start
            logger.debug(f"Incoming check completed in {connection_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Error checking incoming messages: {e}")
        finally:
            self._disconnect_modem()
    
    def _save_incoming_message(self, phone_number, content, modem_index, modem_timestamp, msg_hash):
        """Save incoming message to database"""
        try:
            # Use UTC time with timezone info to avoid system clock issues
            timestamp = datetime.now(timezone.utc).isoformat()
            parsed_modem_ts = None
            
            if self.preserve_timestamps and modem_timestamp:
                parsed_modem_ts = self._parse_modem_timestamp(modem_timestamp)
            
            message_data = {
                'phone_number': phone_number,
                'content': content,
                'timestamp': timestamp,
                'modem_timestamp': parsed_modem_ts,
                'status': 'unread',
                'direction': 'inbound',
                'modem_index': modem_index,
                'message_hash': msg_hash
            }
            
            if self.use_supabase:
                result = self.supabase.table('messages').insert(message_data).execute()
                logger.debug(f"Saved to Supabase: {result.data}")
            else:
                with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                    conn.execute("""
                        INSERT INTO messages 
                        (phone_number, content, timestamp, modem_timestamp, status, direction, modem_index, message_hash)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (phone_number, content, timestamp, parsed_modem_ts, 'unread', 'inbound', modem_index, msg_hash))
                    conn.commit()
        except Exception as e:
            logger.error(f"Error saving incoming message: {e}")
    
    def _sanitize_message(self, message):
        """Sanitize message for GSM character set"""
        if not config['features'].get('sanitize_non_gsm', False):
            return message
        
        # Replace smart quotes, em-dashes, ellipsis with GSM equivalents
        sanitized = message
        sanitized = sanitized.replace('"', '"').replace('"', '"')  # Smart quotes → straight
        sanitized = sanitized.replace(''', "'").replace(''', "'")  # Smart apostrophes
        sanitized = sanitized.replace('–', '-').replace('—', '-')  # Em/en-dash → hyphen
        sanitized = sanitized.replace('…', '...')  # Ellipsis → three dots
        
        # Remove other non-ASCII characters
        sanitized = sanitized.encode('ascii', errors='ignore').decode('ascii')
        
        # Collapse multiple spaces
        sanitized = ' '.join(sanitized.split())
        
        return sanitized
    
    def _split_message(self, message):
        """Split long message into chunks at word boundaries"""
        max_length = config['features'].get('max_sms_length', 150)
        
        # If short enough, return as single chunk
        if len(message) <= max_length:
            return [message]
        
        chunks = []
        remaining = message
        
        while remaining:
            if len(remaining) <= max_length:
                chunks.append(remaining)
                break
            
            # Find last space within limit
            split_at = remaining.rfind(' ', 0, max_length)
            if split_at == -1:
                # No space found, force split at limit
                split_at = max_length
            
            chunks.append(remaining[:split_at].strip())
            remaining = remaining[split_at:].strip()
        
        return chunks
    
    def check_failed_messages(self):
        """Check failed messages and retry them with exponential backoff"""
        logger.info("Checking failed messages for retry...")
        
        try:
            # Get retry configuration
            max_retries = config.get('retry', {}).get('max_retries', 5)
            base_delay = config.get('retry', {}).get('base_delay_seconds', 30)
            exponential_backoff = config.get('retry', {}).get('exponential_backoff', True)
            max_delay = config.get('retry', {}).get('max_delay_seconds', 480)
            
            if self.use_supabase:
                # Get failed messages that haven't exceeded max retries
                result = self.supabase.table('messages').select('*').eq('status', 'failed').lt('retry_count', max_retries).order('id').limit(10).execute()
                failed_messages = result.data
            else:
                # SQLite query
                with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute("""
                        SELECT * FROM messages 
                        WHERE status = 'failed' AND retry_count < ?
                        ORDER BY id ASC 
                        LIMIT 10
                    """, (max_retries,))
                    failed_messages = cursor.fetchall()
            
            # Filter out messages that are already sent (shouldn't happen but safety check)
            failed_messages = [msg for msg in failed_messages if msg['status'] == 'failed']
            
            if not failed_messages:
                return
            
            logger.info(f"Found {len(failed_messages)} failed message(s) eligible for retry")
            
            # Retry each failed message
            for message in failed_messages:
                # Calculate exponential backoff delay
                if exponential_backoff:
                    retry_delay = min(base_delay * (2 ** (message['retry_count'] - 1)), max_delay)
                else:
                    retry_delay = base_delay
                
                # Check if enough time has passed since last attempt
                last_attempt = datetime.fromisoformat(message['updated_at'].replace('Z', '+00:00'))
                time_since_attempt = (datetime.now(timezone.utc) - last_attempt).total_seconds()
                
                if time_since_attempt < retry_delay:
                    continue  # Not time to retry yet
                
                logger.info(f"Retrying message {message['id']} (attempt {message['retry_count'] + 1}, waited {time_since_attempt:.0f}s)")
                
                # Double-check the message is still failed before requeuing
                if self.use_supabase:
                    # Verify status is still failed before updating
                    check_result = self.supabase.table('messages').select('status').eq('id', message['id']).single().execute()
                    if check_result.data and check_result.data['status'] == 'failed':
                        self.supabase.table('messages').update({
                            'status': 'queued',
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', message['id']).eq('status', 'failed').execute()
                    else:
                        logger.warning(f"Message {message['id']} status changed, skipping retry")
                else:
                    with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                        # Verify status is still failed before updating
                        cursor = conn.execute("SELECT status FROM messages WHERE id = ?", (message['id'],))
                        result = cursor.fetchone()
                        if result and result[0] == 'failed':
                            conn.execute("""
                                UPDATE messages 
                                SET status = 'queued', updated_at = CURRENT_TIMESTAMP 
                                WHERE id = ? AND status = 'failed'
                            """, (message['id'],))
                            conn.commit()
                        else:
                            logger.warning(f"Message {message['id']} status changed, skipping retry")
                
        except Exception as e:
            logger.error(f"Error checking failed messages: {e}")
    
    def check_scheduled_messages(self):
        """Check scheduled_messages table and queue messages when time arrives"""
        if not self.use_supabase:
            # Scheduled messages only work with Supabase
            return
        
        try:
            # Query scheduled_messages where scheduled_for <= now
            now = datetime.now(timezone.utc).isoformat()
            response = self.supabase.table('scheduled_messages')\
                .select('*')\
                .eq('status', 'scheduled')\
                .lte('scheduled_for', now)\
                .execute()
            
            if not response.data:
                return
            
            scheduled_msgs = response.data
            logger.info(f"Found {len(scheduled_msgs)} scheduled messages ready to send")
            
            for sched_msg in scheduled_msgs:
                try:
                    msg_id = sched_msg.get('id')
                    phone = sched_msg.get('phone_number')
                    content = sched_msg.get('message_content', '')
                    name = sched_msg.get('customer_name', 'Unknown')
                    
                    # Split by [BUBBLE] markers
                    bubbles = content.split('[BUBBLE]')
                    bubbles = [b.strip() for b in bubbles if b.strip()]
                    
                    if len(bubbles) == 0:
                        bubbles = [content]
                    
                    logger.info(f"Queuing scheduled message for {name} ({phone}): {len(bubbles)} bubble(s)")
                    
                    # Insert each bubble as separate queued message
                    for bubble in bubbles:
                        self.supabase.table('messages').insert({
                            'phone_number': phone,
                            'content': bubble,
                            'status': 'queued',
                            'direction': 'outbound',
                            'timestamp': datetime.now(timezone.utc).isoformat()
                        }).execute()
                    
                    # Update scheduled_messages status to 'sent'
                    self.supabase.table('scheduled_messages').update({
                        'status': 'sent',
                        'sent_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', msg_id).execute()
                    
                    logger.info(f"Scheduled message {msg_id} converted to {len(bubbles)} queued message(s)")
                    
                except Exception as e:
                    logger.error(f"Error processing scheduled message {sched_msg.get('id')}: {e}")
                    # Mark as failed
                    try:
                        self.supabase.table('scheduled_messages').update({
                            'status': 'failed',
                            'error_message': str(e)
                        }).eq('id', sched_msg.get('id')).execute()
                    except:
                        pass
        
        except Exception as e:
            logger.error(f"Error checking scheduled messages: {e}")
    
    def process_campaign_scheduler(self):
        """Call Supabase RPC to process scheduled campaign messages"""
        if not self.use_supabase:
            return
        
        try:
            # Call the Supabase function that handles everything
            result = self.supabase.rpc('process_scheduled_messages').execute()
            
            if result.data and len(result.data) > 0:
                processed = result.data[0].get('processed_count', 0)
                queued = result.data[0].get('messages_queued', 0)
                
                if processed > 0:
                    logger.info(f"Campaign Scheduler: Processed {processed} scheduled messages, queued {queued} SMS bubbles")
        
        except Exception as e:
            logger.error(f"Error calling campaign scheduler: {e}")

    def check_outgoing_queue(self):
        """Check outgoing queue and send messages (batch mode supported)"""
        logger.info("Checking outgoing queue...")
        
        try:
            if self.use_supabase:
                # Supabase query
                limit = self.max_batch_size if self.batch_outgoing else 1
                result = self.supabase.table('messages').select('*').eq('status', 'queued').order('id').limit(limit).execute()
                messages = result.data
            else:
                # SQLite query
                with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                    conn.row_factory = sqlite3.Row
                    
                    if self.batch_outgoing:
                        cursor = conn.execute("""
                            SELECT * FROM messages 
                            WHERE status = 'queued' 
                            ORDER BY id ASC 
                            LIMIT ?
                        """, (self.max_batch_size,))
                    else:
                        cursor = conn.execute("""
                            SELECT * FROM messages 
                            WHERE status = 'queued' 
                            ORDER BY id ASC 
                            LIMIT 1
                        """)
                    messages = cursor.fetchall()
            
            if not messages:
                logger.info("No queued messages")
                return
            
            logger.info(f"Found {len(messages)} queued message(s)")
            
            # Send each message (with automatic splitting if needed)
            for message in messages:
                # Sanitize message first
                content = message['content']
                if config['features'].get('sanitize_non_gsm', False):
                    content = self._sanitize_message(content)
                
                # Split into chunks if needed
                chunks = []
                if config['features'].get('enable_long_sms', False):
                    chunks = self._split_message(content)
                else:
                    chunks = [content]
                
                # Log splitting info
                if len(chunks) > 1:
                    logger.info(f"Message {message['id']} split into {len(chunks)} chunks")
                
                # Send all chunks
                all_success = True
                for i, chunk in enumerate(chunks):
                    chunk_num = f" (chunk {i+1}/{len(chunks)})" if len(chunks) > 1 else ""
                    success = self._send_sms_message(message['phone_number'], chunk)
                    
                    if not success:
                        all_success = False
                        logger.error(f"Failed to send chunk {i+1}/{len(chunks)} for message {message['id']}")
                        break
                    
                    # Add delay between chunks
                    if i < len(chunks) - 1:
                        delay_ms = config['features'].get('chunk_delay_ms', 750)
                        logger.info(f"Waiting {delay_ms}ms before next chunk...")
                        time.sleep(delay_ms / 1000.0)
                
                # Update status based on overall success
                if all_success:
                    if self.use_supabase:
                        self.supabase.table('messages').update({
                            'status': 'sent',
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', message['id']).execute()
                    else:
                        with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                            conn.execute("""
                                UPDATE messages 
                                SET status = 'sent', updated_at = CURRENT_TIMESTAMP 
                                WHERE id = ?
                            """, (message['id'],))
                            conn.commit()
                    logger.info(f"Message {message['id']} sent successfully")
                else:
                    # Increment retry count
                    new_retry_count = message['retry_count'] + 1
                    if self.use_supabase:
                        self.supabase.table('messages').update({
                            'status': 'failed',
                            'retry_count': new_retry_count,
                            'updated_at': datetime.now(timezone.utc).isoformat()
                        }).eq('id', message['id']).execute()
                    else:
                        with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                            conn.execute("""
                                UPDATE messages 
                                SET status = 'failed', retry_count = ?, updated_at = CURRENT_TIMESTAMP 
                                WHERE id = ?
                            """, (new_retry_count, message['id']))
                            conn.commit()
                    logger.error(f"Message {message['id']} failed (retry {new_retry_count})")
                
                # Small pause between batch sends
                if self.batch_outgoing and len(messages) > 1:
                    time.sleep(0.1)
        
        except Exception as e:
            logger.error(f"Error processing outgoing queue: {e}")
    
    def _send_sms_message(self, phone_number, message):
        """Send SMS message via modem"""
        # Normalize phone number to E.164 format
        normalized_phone = normalize_phone_number(phone_number)
        if normalized_phone != phone_number:
            logger.info(f"Normalized phone: {phone_number} -> {normalized_phone}")
        
        logger.info(f"Sending SMS to {normalized_phone[:7]}****: {message[:50]}...")
        
        # Always disconnect first to ensure clean state
        self._disconnect_modem()
        
        if not self._connect_modem():
            logger.error("Cannot connect to modem for sending")
            self._disconnect_modem()  # Ensure disconnect even on failure
            return False
        
        connection_start = time.time()
        
        try:
            # Set text mode
            self._send_at_command("AT+CMGF=1")
            
            # Send SMS
            self.connection.write(f'AT+CMGS="{normalized_phone}"\r\n'.encode())
            time.sleep(0.5)  # Wait for '>' prompt
            self.connection.write((message + '\x1A').encode())  # Message + Ctrl+Z
            
            # Wait for confirmation
            response = ""
            start_time = time.time()
            while time.time() - start_time < self.send_timeout:
                if self.connection.in_waiting:
                    data = self.connection.read(self.connection.in_waiting).decode('utf-8', errors='ignore')
                    response += data
                    if 'OK' in response:
                        connection_time = time.time() - connection_start
                        logger.info(f"SMS sent successfully in {connection_time:.2f}s")
                        return True
                    elif 'ERROR' in response:
                        logger.error(f"SMS send failed: {response}")
                        return False
                time.sleep(0.1)
            
            logger.warning("No confirmation received from modem (timeout)")
            return False
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
        finally:
            self._disconnect_modem()
    
    def modem_health_check(self):
        """Perform basic modem health check"""
        if not self.health_check:
            return True
        
        logger.info("Performing modem health check...")
        
        if not self._connect_modem():
            return False
        
        try:
            # Test basic AT command
            response = self._send_at_command("AT")
            if not response or 'OK' not in response:
                logger.error("Modem not responding to AT command")
                return False
            
            # Check signal quality
            response = self._send_at_command("AT+CSQ")
            if response and '+CSQ:' in response:
                logger.info(f"Signal quality: {response.strip()}")
            
            logger.info("Modem health check passed")
            return True
            
        except Exception as e:
            logger.error(f"Modem health check failed: {e}")
            return False
        finally:
            self._disconnect_modem()
    
    def get_status(self):
        """Get system status"""
        try:
            if self.use_supabase:
                # Supabase queries
                total_result = self.supabase.table('messages').select('id', count='exact').execute()
                total_messages = total_result.count
                
                unread_result = self.supabase.table('messages').select('id', count='exact').eq('status', 'unread').execute()
                unread_messages = unread_result.count
                
                queued_result = self.supabase.table('messages').select('id', count='exact').eq('status', 'queued').execute()
                queued_messages = queued_result.count
                
                sent_result = self.supabase.table('messages').select('id', count='exact').eq('status', 'sent').execute()
                sent_messages = sent_result.count
                
                failed_result = self.supabase.table('messages').select('id', count='exact').eq('status', 'failed').execute()
                failed_messages = failed_result.count
            else:
                # SQLite queries
                with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM messages")
                    total_messages = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'unread'")
                    unread_messages = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'queued'")
                    queued_messages = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'sent'")
                    sent_messages = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE status = 'failed'")
                    failed_messages = cursor.fetchone()[0]
            
            return {
                'total_messages': total_messages,
                'unread_messages': unread_messages,
                'queued_messages': queued_messages,
                'sent_messages': sent_messages,
                'failed_messages': failed_messages,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting status: {e}")
            return None
    
    def add_test_message(self, phone_number, message):
        """Add test message to outgoing queue"""
        try:
            timestamp = datetime.now(timezone.utc).isoformat()
            msg_hash = self._calculate_message_hash(phone_number, message)
            
            message_data = {
                'phone_number': phone_number,
                'content': message,
                'timestamp': timestamp,
                'status': 'queued',
                'direction': 'outbound',
                'message_hash': msg_hash
            }
            
            if self.use_supabase:
                result = self.supabase.table('messages').insert(message_data).execute()
                msg_id = result.data[0]['id']
            else:
                with sqlite3.connect(self.db_path, timeout=self.db_timeout) as conn:
                    conn.execute("""
                        INSERT INTO messages 
                        (phone_number, content, timestamp, status, direction, message_hash)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (phone_number, message, timestamp, 'queued', 'outbound', msg_hash))
                    conn.commit()
                    
                    cursor = conn.execute("SELECT last_insert_rowid()")
                    msg_id = cursor.fetchone()[0]
            
            print(f"Message queued successfully!")
            print(f"ID: {msg_id}")
            print(f"Phone: {phone_number}")
            print(f"Message: {message}")
            
            return msg_id
        except Exception as e:
            logger.error(f"Error adding test message: {e}")
            print(f"ERROR: {e}")
            return None
    
    def run_conductor_loop(self):
        """Main conductor loop"""
        logger.info(f"Starting Conductor System v2.0 - Polling every {self.poll_interval} seconds")
        logger.info(f"Batch mode: {'Enabled' if self.batch_outgoing else 'Disabled'}")
        
        # Initial health check
        if self.health_check:
            if not self.modem_health_check():
                logger.warning("Initial health check failed, but continuing...")
        
        self.running = True
        cycle_count = 0
        
        while self.running:
            try:
                cycle_count += 1
                cycle_start = time.time()
                logger.info(f"=== Conductor Cycle {cycle_count} ===")
                
                # 1. Process scheduled messages (move SCH -> queued when time arrives)
                self.process_campaign_scheduler()
                time.sleep(self.pause_between_ops)
                
                # 2. Check for incoming messages
                self.check_incoming_messages()
                time.sleep(self.pause_between_ops)
                
                # 3. Check failed messages for retry
                self.check_failed_messages()
                time.sleep(self.pause_between_ops)
                
                # 4. Check outgoing queue
                self.check_outgoing_queue()
                time.sleep(self.pause_between_ops)
                
                # 4. Show status
                status = self.get_status()
                if status:
                    logger.info(f"Status: {status['total_messages']} total, "
                              f"{status['unread_messages']} unread, "
                              f"{status['queued_messages']} queued, "
                              f"{status['sent_messages']} sent, "
                              f"{status['failed_messages']} failed")
                
                # 4. Calculate elapsed time and adjust sleep
                cycle_time = time.time() - cycle_start
                sleep_time = max(0, self.poll_interval - cycle_time)
                
                logger.info(f"Cycle {cycle_count} complete in {cycle_time:.2f}s. "
                          f"Waiting {sleep_time:.2f}s...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("Conductor system stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in conductor loop: {e}", exc_info=True)
                time.sleep(5)
        
        self.running = False
        logger.info("Conductor system stopped")


def main():
    """Main entry point"""
    conductor = ConductorSystem()
    
    # CLI interface
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'test' and len(sys.argv) >= 4:
            phone_number = sys.argv[2]
            message = ' '.join(sys.argv[3:])
            conductor.add_test_message(phone_number, message)
        
        elif command == 'status':
            status = conductor.get_status()
            if status:
                print("\n=== Conductor System Status ===")
                print(f"Total Messages: {status['total_messages']}")
                print(f"Unread: {status['unread_messages']}")
                print(f"Queued: {status['queued_messages']}")
                print(f"Sent: {status['sent_messages']}")
                print(f"Failed: {status['failed_messages']}")
                print(f"Timestamp: {status['timestamp']}")
        
        elif command == 'health':
            result = conductor.modem_health_check()
            print(f"Health check: {'PASSED' if result else 'FAILED'}")
        
        else:
            print("Usage:")
            print("  python conductor_system.py              - Start conductor loop")
            print("  python conductor_system.py test <phone> <message>  - Queue test message")
            print("  python conductor_system.py status       - Show system status")
            print("  python conductor_system.py health       - Check modem health")
    
    else:
        # Start main loop
        conductor.run_conductor_loop()


if __name__ == "__main__":
    main()

