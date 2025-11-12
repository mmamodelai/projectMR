#!/usr/bin/env python3
"""
Telegraph - SMS Message Manager
View, edit, send, and reply to SMS messages from Supabase

Version: 2.0 (Telegraph - Message Creation & Reply)
Release Date: November 11, 2025

Usage:
    python SMSconductor_DB.py
    OR
    pythonw SMSconductor_DB.py (no console)
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from supabase import create_client, Client
from datetime import datetime, timezone
from dateutil import parser, tz
import threading
import os
import json
try:
    # Optional: load .env for local development; safe no-op if missing
    from dotenv import load_dotenv  # type: ignore
    load_dotenv()
except Exception:
    pass

# Supabase Configuration (read from environment first; fallback to local config.json)
# Provide these via environment or a local .env file:
#   SUPABASE_URL, SUPABASE_ANON_KEY
#   CRM_URL (optional, defaults to SUPABASE_URL)
#   CRM_ANON_KEY (optional, defaults to SUPABASE_ANON_KEY)

# INTERNAL BUILD: Hardcoded credentials for client deployment
_INTERNAL_CREDENTIALS = {
    "url": "https://kiwmwoqrguyrcpjytgte.supabase.co",
    "key": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"
}

SUPABASE_URL = os.getenv("SUPABASE_URL", _INTERNAL_CREDENTIALS["url"]).strip()
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY", _INTERNAL_CREDENTIALS["key"]).strip()
if not SUPABASE_URL or not SUPABASE_KEY:
    # Fallback: try local config.json (used by Conductor)
    try:
        with open("config.json", "r", encoding="utf-8") as _cfgf:
            _cfg = json.load(_cfgf)
            db_cfg = _cfg.get("database", {})
            SUPABASE_URL = (db_cfg.get("supabase_url") or _INTERNAL_CREDENTIALS["url"]).strip()
            SUPABASE_KEY = (db_cfg.get("supabase_key") or _INTERNAL_CREDENTIALS["key"]).strip()
    except Exception:
        pass
if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Supabase credentials not configured.\n"
        "Set SUPABASE_URL and SUPABASE_ANON_KEY in environment/.env, "
        "or add them to config.json -> database.supabase_url/supabase_key."
    )

# Initialize Supabase client (SMS Database)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# CRM Database (for customer name resolution)
CRM_URL = os.getenv("CRM_URL", SUPABASE_URL).strip()
CRM_KEY = os.getenv("CRM_ANON_KEY", SUPABASE_KEY).strip()
crm_supabase: Client = create_client(CRM_URL, CRM_KEY)

# Budtender Campus Database (override via environment if different project)
BT_URL = os.getenv("BT_SUPABASE_URL", CRM_URL).strip()
BT_KEY = os.getenv("BT_SUPABASE_KEY", CRM_KEY).strip()
bt_supabase: Client = create_client(BT_URL, BT_KEY)

# Configurable table names (override via env if needed)
BT_CAMPAIGN_TABLE = os.getenv("BT_CAMPAIGN_TABLE", "campaign_messages")
BT_BUDTENDER_TABLE = os.getenv("BT_BUDTENDER_TABLE", "budtenders")

# Contact name cache
contact_cache = {}

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

def decode_hex_message(content):
    """
    Detect and decode hex-encoded UCS2/UTF-16 messages.
    Returns decoded text if hex-encoded, otherwise returns original content.
    
    Hex-encoded messages appear when modem was in wrong character set mode.
    Format: 0048006500790021... (each character is 4 hex digits)
    """
    if not content or not isinstance(content, str):
        return content
    
    # Check if content looks like hex-encoded UCS2
    # UCS2 hex messages are all hex digits and typically very long
    if len(content) >= 16 and all(c in '0123456789ABCDEFabcdef' for c in content):
        try:
            # Remove spaces if any
            hex_content = content.replace(' ', '')
            
            # Convert hex to bytes (UCS2 = UTF-16BE)
            byte_data = bytes.fromhex(hex_content)
            
            # Decode as UTF-16 Big Endian
            decoded = byte_data.decode('utf-16-be', errors='replace')
            
            # If we got actual text (not just weird characters), return it
            # Check if at least 50% are printable ASCII/common characters
            printable_count = sum(1 for c in decoded if c.isprintable() or c in '\n\r\t')
            if len(decoded) > 0 and (printable_count / len(decoded)) > 0.5:
                return decoded
        except Exception:
            # If decoding fails, return original
            pass
    
    return content

def resolve_contact_name(phone_number):
    """
    Resolve phone number to contact name.
    Checks in order:
    1. Cache (for speed)
    2. CRM customers_blaze table (Internal Customers)
    3. Budtenders table (External Budtenders)
    4. Campaign_messages table (Campaign recipients)
    
    Returns: "Name (phone)" or just "phone" if not found
    """
    global contact_cache
    
    # Check cache first
    if phone_number in contact_cache:
        return contact_cache[phone_number]
    
    try:
        # Normalize phone to 10 digits for matching
        phone_digits = ''.join(filter(str.isdigit, str(phone_number)))
        if len(phone_digits) >= 10:
            phone_10 = phone_digits[-10:]  # Last 10 digits
        else:
            phone_10 = phone_digits
        
        # Check CRM customers_blaze table (IC database) - use LIKE for flexible matching
        try:
            result = crm_supabase.table('customers_blaze').select('name,phone').like('phone', f'%{phone_10}').limit(1).execute()
            
            if result.data and len(result.data) > 0:
                name = result.data[0].get('name', '').strip()
                if name:
                    display = f"{name} ({phone_number})"
                    contact_cache[phone_number] = display
                    return display
        except Exception as e:
            print(f"CRM customers lookup error: {e}")
        
        # Check budtenders table (XB database)
        try:
            result = crm_supabase.table('budtenders').select('first_name,last_name,phone').like('phone', f'%{phone_10}').limit(1).execute()
            
            if result.data and len(result.data) > 0:
                first = result.data[0].get('first_name', '').strip()
                last = result.data[0].get('last_name', '').strip()
                name = f"{first} {last}".strip()
                if name:
                    display = f"{name} ({phone_number})"
                    contact_cache[phone_number] = display
                    return display
        except Exception as e:
            print(f"Budtenders lookup error: {e}")
        
        # Check campaign_messages table (for budtender campaigns)
        try:
            result = crm_supabase.table('campaign_messages').select('customer_name,phone_number').like('phone_number', f'%{phone_10}').limit(1).execute()
            
            if result.data and len(result.data) > 0:
                name = result.data[0].get('customer_name', '').strip()
                if name:
                    display = f"{name} ({phone_number})"
                    contact_cache[phone_number] = display
                    return display
        except Exception as e:
            print(f"Campaign messages lookup error: {e}")
        
        # Cache the phone number as-is
        contact_cache[phone_number] = phone_number
        return phone_number
        
    except Exception as e:
        print(f"Error resolving contact: {e}")
        return phone_number

def utc_to_local(utc_str):
    """Convert UTC timestamp string to local timezone"""
    if not utc_str:
        return "N/A"
    try:
        # Parse timestamp
        dt = parser.isoparse(utc_str)
        
        # If timestamp is naive (no timezone), assume it's already in local time
        # and add 7 hours to fix SMS modem timestamps that come in as local
        if dt.tzinfo is None:
            from datetime import timedelta
            dt = dt.replace(tzinfo=tz.tzutc()) + timedelta(hours=7)
        
        # Ensure the datetime is in UTC before converting to local
        if dt.tzinfo != tz.tzutc():
            dt = dt.astimezone(tz.tzutc())
        
        # Convert to local timezone for display
        local_dt = dt.astimezone(tz.tzlocal())
        
        # Format: "2025-10-13 12:14:15 PM PDT"
        return local_dt.strftime("%Y-%m-%d %I:%M:%S %p %Z")
    except Exception as e:
        return f"Invalid: {str(e)[:20]}"

class SMSViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegraph - SMS Message Manager [v2.0]")
        self.root.geometry("1400x800")
        
        # Auto-refresh state
        self.live_mode = tk.BooleanVar(value=False)
        self.refresh_timer_id = None
        self.refresh_interval = 15000  # 15 seconds in milliseconds
        
        # Smaller heading style for dense tables
        try:
            style = ttk.Style()
            style.configure('Small.Treeview.Heading', font=('Arial', 9))
            style.configure('Small.Treeview', rowheight=20)
        except Exception:
            pass
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title and live mode toggle
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        title = ttk.Label(header_frame, text="📱 Telegraph - SMS Message Manager  [v2.0]", font=("Arial", 16, "bold"))
        title.pack(side=tk.LEFT)
        
        # Live mode checkbox with last refresh time
        live_frame = ttk.Frame(header_frame)
        live_frame.pack(side=tk.RIGHT, padx=10)
        self.live_indicator = ttk.Label(live_frame, text="●", font=("Arial", 14), foreground="gray")
        self.live_indicator.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(live_frame, text="Live Mode (15s refresh)", 
                       variable=self.live_mode, 
                       command=self.toggle_live_mode).pack(side=tk.LEFT)
        self.last_refresh_label = ttk.Label(live_frame, text="", 
                                            font=("Arial", 8), foreground="gray")
        self.last_refresh_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Configure grid weights for notebook
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        
        # Load Budtender DB config if available
        try:
            self._load_bt_config_if_any()
        except Exception:
            pass
        
        # Create tabs
        self._create_all_messages_tab()
        self._create_conversations_tab()
        self._create_first_texts_tab()
        self._create_suggested_tab()  # SUG - needs approval
        self._create_approved_tab()   # APR - ready to schedule
        self._create_scheduled_tab()  # SCH - scheduled campaign messages
        
    def _create_all_messages_tab(self):
        """Create the All Messages tab (original view)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📋 All Messages")
        
        # Stats frame
        stats_frame = ttk.LabelFrame(tab, text="Statistics", padding="10")
        stats_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="Loading...", font=("Arial", 10))
        self.stats_label.pack()
        
        # Buttons frame
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(btn_frame, text="➕ New Message", command=self.compose_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🔄 Refresh", command=self.load_messages).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Show Failed Only", command=self.show_failed_only).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Edit Selected", command=self.edit_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑️ Delete Selected", command=self.delete_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📤 Mark as Sent", command=lambda: self.change_status('sent')).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="📥 Mark as Queued", command=lambda: self.change_status('queued')).pack(side=tk.LEFT, padx=5)
        
        # Messages tree
        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Scrollbars
        tree_scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        tree_scroll_x = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Tree
        self.tree = ttk.Treeview(tree_frame, 
                                  columns=("ID", "Phone", "Direction", "Status", "Content", "Timestamp"),
                                  show="headings",
                                  yscrollcommand=tree_scroll_y.set,
                                  xscrollcommand=tree_scroll_x.set,
                                  height=20)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)
        
        # Column headings (clickable for sorting)
        self.tree.heading("ID", text="ID", command=lambda: self.sort_column("ID"))
        self.tree.heading("Phone", text="Phone Number", command=lambda: self.sort_column("Phone"))
        self.tree.heading("Direction", text="Direction", command=lambda: self.sort_column("Direction"))
        self.tree.heading("Status", text="Status", command=lambda: self.sort_column("Status"))
        self.tree.heading("Content", text="Message Content", command=lambda: self.sort_column("Content"))
        self.tree.heading("Timestamp", text="Timestamp ⬇", command=lambda: self.sort_column("Timestamp"))
        
        # Column widths
        self.tree.column("ID", width=80)
        self.tree.column("Phone", width=150)
        self.tree.column("Direction", width=100)
        self.tree.column("Status", width=100)
        self.tree.column("Content", width=350)
        self.tree.column("Timestamp", width=230)  # Wider for local time format
        
        # Grid layout
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scroll_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scroll_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        
        # Detail panel
        detail_frame = ttk.LabelFrame(tab, text="Message Details", padding="10")
        detail_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 0), pady=10)
        
        self.detail_text = scrolledtext.ScrolledText(detail_frame, width=40, height=25, wrap=tk.WORD)
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Bind right-click event
        self.tree.bind('<Button-3>', self.show_context_menu)
        
        # Create context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="💬 Reply", command=self.reply_to_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="✏️ Edit Message", command=self.edit_message)
        self.context_menu.add_command(label="⏰ Edit Timestamp", command=self.edit_message_timestamp)
        self.context_menu.add_command(label="🗑️ Delete Message", command=self.delete_message)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="➕ Add to Reply Messages", command=self.add_to_reply_messages)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📭 Mark as Unread", command=lambda: self.change_status('unread'))
        self.context_menu.add_command(label="📥 Mark as Queued", command=lambda: self.change_status('queued'))
        self.context_menu.add_command(label="📤 Mark as Sent", command=lambda: self.change_status('sent'))
        self.context_menu.add_command(label="❌ Mark as Failed", command=lambda: self.change_status('failed'))
        self.context_menu.add_command(label="✅ Mark as Read", command=lambda: self.change_status('read'))
        
        # Bind double-click on phone number to reply
        self.tree.bind('<Double-1>', self.on_double_click_reply)
        
        # Load initial data
        self.load_messages()
    
    def _create_conversations_tab(self):
        """Create the Conversations tab for manual replies"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="💬 Reply to Messages")
        
        # Instructions
        info_frame = ttk.Frame(tab)
        info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=10)
        ttk.Label(info_frame, text="📲 Unread Messages - Click to reply, Right-click to mark as read", 
                  font=("Arial", 12, "bold")).pack(anchor=tk.W)
        ttk.Label(info_frame, text="Marking as 'read' removes from this tab | Messages will be sent by conductor_system.py", 
                  font=("Arial", 9), foreground="gray").pack(anchor=tk.W)
        
        # Left side - Incoming messages list
        left_frame = ttk.LabelFrame(tab, text="📥 Unread Messages (Right-click to Mark Read)", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(10, 5), pady=10)
        
        # Listbox with scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        list_scroll = ttk.Scrollbar(list_frame)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.conv_listbox = tk.Listbox(list_frame, font=("Arial", 10), 
                                        yscrollcommand=list_scroll.set, height=25)
        self.conv_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.config(command=self.conv_listbox.yview)
        
        self.conv_listbox.bind('<<ListboxSelect>>', self.on_conversation_select)
        self.conv_listbox.bind('<Button-3>', self.show_conversation_context_menu)  # Right-click
        
        # Refresh button for incoming messages
        ttk.Button(left_frame, text="🔄 Refresh Incoming", 
                   command=self.load_conversations).pack(pady=(10, 0))
        
        # Middle - Conversation view and reply
        middle_frame = ttk.Frame(tab)
        middle_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=10)
        
        # Conversation history
        history_frame = ttk.LabelFrame(middle_frame, text="📜 Conversation History", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.conv_history = scrolledtext.ScrolledText(history_frame, width=60, height=12, 
                                                       wrap=tk.WORD, font=("Arial", 10))
        self.conv_history.pack(fill=tk.BOTH, expand=True)
        self.conv_history.config(state=tk.DISABLED)
        
        # Suggested Message section (NEW!)
        suggested_frame = ttk.LabelFrame(middle_frame, text="💡 Suggested Message", padding="10")
        suggested_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Suggested message display (read-only)
        self.suggested_message = scrolledtext.ScrolledText(suggested_frame, width=60, height=3,
                                                           wrap=tk.WORD, font=("Arial", 10),
                                                           background="#ffffcc", state=tk.DISABLED)
        self.suggested_message.pack(fill=tk.BOTH, expand=True)
        
        # Buttons for suggested message
        suggested_buttons = ttk.Frame(suggested_frame)
        suggested_buttons.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(suggested_buttons, text="✅ APPROVE", 
                   command=self.approve_suggested, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(suggested_buttons, text="✏️ Edit", 
                   command=self.edit_suggested).pack(side=tk.LEFT, padx=5)
        ttk.Button(suggested_buttons, text="❌ Reject", 
                   command=self.reject_suggested).pack(side=tk.LEFT, padx=5)
        
        # Reply section (smaller now)
        reply_frame = ttk.LabelFrame(middle_frame, text="✍️ Your Reply", padding="10")
        reply_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Customer info
        self.conv_customer_label = ttk.Label(reply_frame, text="Select a message to reply", 
                                             font=("Arial", 10, "bold"))
        self.conv_customer_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Reply text area (half size now - 3 lines instead of 6)
        self.reply_text = scrolledtext.ScrolledText(reply_frame, width=60, height=3, 
                                                     wrap=tk.WORD, font=("Arial", 10))
        self.reply_text.pack(fill=tk.X)
        
        # Character counter
        self.char_counter = ttk.Label(reply_frame, text="0 / 160 characters", 
                                      font=("Arial", 9), foreground="gray")
        self.char_counter.pack(anchor=tk.E, pady=(5, 0))
        self.reply_text.bind('<KeyRelease>', self.update_char_count)
        
        # Notes/Feedback section (NEW!)
        notes_label = ttk.Label(reply_frame, text="📝 Notes/Feedback (Why you changed/approved):", 
                                font=("Arial", 9, "bold"))
        notes_label.pack(anchor=tk.W, pady=(10, 5))
        
        self.feedback_text = scrolledtext.ScrolledText(reply_frame, width=60, height=3,
                                                       wrap=tk.WORD, font=("Arial", 9),
                                                       background="#f0f8ff")
        self.feedback_text.pack(fill=tk.X)
        
        # Send / approval buttons
        button_frame = ttk.Frame(reply_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Button(button_frame, text="✅ MARK APPROVED", command=self.mark_approved).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(button_frame, text="📤 SEND IMMEDIATELY", 
                   command=self.send_reply, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="🗑️ Clear", 
                   command=lambda: (self.reply_text.delete('1.0', tk.END), self.feedback_text.delete('1.0', tk.END))).pack(side=tk.RIGHT)
        
        # Right side - Baseball Card (Fixed panel)
        right_frame = ttk.LabelFrame(tab, text="⚾ Customer/Budtender Info", padding="10")
        right_frame.grid(row=1, column=2, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 10), pady=10)
        
        self.baseball_card = scrolledtext.ScrolledText(right_frame, width=45, height=30, 
                                                       wrap=tk.WORD, font=("Courier", 9),
                                                       background="#f0f0f0")
        self.baseball_card.pack(fill=tk.BOTH, expand=True)
        self.baseball_card.config(state=tk.DISABLED)
        self.baseball_card.insert('1.0', "Select a conversation to view\ncustomer/budtender info")
        self.baseball_card.config(state=tk.DISABLED)
        
        # Configure grid weights (3 columns now!)
        tab.columnconfigure(0, weight=1)  # Left: Messages list
        tab.columnconfigure(1, weight=2)  # Middle: Conversation + Reply
        tab.columnconfigure(2, weight=1)  # Right: Baseball card
        tab.rowconfigure(1, weight=1)
        
        # Store selected conversation
        self.selected_conversation = None
        
        # Store suggested message data (NEW!)
        self.current_suggested_id = None
        self.current_suggested_data = None
        
        # Load conversations
        self.load_conversations()
        
    def show_failed_only(self):
        """Show only failed messages"""
        try:
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch ONLY failed messages
            response = supabase.table('messages').select('*').eq('status', 'failed').order('timestamp', desc=True).execute()
            messages = response.data if hasattr(response, 'data') else []
            
            if not messages:
                self.stats_label.config(text="No failed messages found")
                messagebox.showinfo("No Failed Messages", "No failed messages found in the database")
                return
            
            # Populate tree with failed messages
            for msg in messages:
                msg_id = str(msg.get('id', ''))[:8]
                phone = str(msg.get('phone_number', ''))
                if not phone or phone.strip() == '':
                    phone = "[EMPTY PHONE]"
                direction = str(msg.get('direction', ''))
                status = str(msg.get('status', ''))
                content_full = str(msg.get('content', ''))
                # Decode hex-encoded messages
                content_full = decode_hex_message(content_full)
                content = content_full[:50] + ('...' if len(content_full) > 50 else '')
                timestamp_utc = msg.get('timestamp', '')
                timestamp_local = utc_to_local(timestamp_utc)
                
                # Highlight failed messages in red
                self.tree.insert('', tk.END, values=(msg_id, phone, direction, status, content, timestamp_local), tags=('failed',))
            
            # Configure tag
            self.tree.tag_configure('failed', background='#f8d7da', foreground='#721c24')
            
            # Update stats
            self.stats_label.config(text=f"Showing {len(messages)} FAILED messages (Click Refresh to show all)")
            
            messagebox.showwarning("Failed Messages", 
                                  f"Found {len(messages)} failed messages!\n\n"
                                  "Common issues:\n"
                                  "- Empty phone numbers\n"
                                  "- Invalid phone format\n"
                                  "- Modem errors\n\n"
                                  "Check the list and fix or delete these messages.")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to load failed messages:\n{str(e)}\n\n{error_detail}")
    
    def load_messages(self):
        """Load all messages from Supabase"""
        try:
            # Clear tree
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Fetch messages
            response = supabase.table('messages').select('*').order('timestamp', desc=True).execute()
            messages = response.data if hasattr(response, 'data') else []
            
            if not messages:
                self.stats_label.config(text="No messages found")
                return
            
            # Populate tree
            for msg in messages:
                # Safely get values with type checking
                msg_id = str(msg.get('id', ''))[:8]  # Short ID
                phone = str(msg.get('phone_number', ''))
                # Highlight empty/invalid phone numbers
                if not phone or phone.strip() == '':
                    phone = "[EMPTY PHONE]"
                elif phone == '+1XXXXXXXXXX':
                    phone = "[PLACEHOLDER]"
                direction = str(msg.get('direction', ''))
                status = str(msg.get('status', ''))
                content_full = str(msg.get('content', ''))
                # Decode hex-encoded messages
                content_full = decode_hex_message(content_full)
                content = content_full[:50] + ('...' if len(content_full) > 50 else '')
                timestamp_utc = msg.get('timestamp', '')
                timestamp_local = utc_to_local(timestamp_utc)  # Convert to local time!
                
                # Color code by status
                tag = status
                self.tree.insert('', tk.END, values=(msg_id, phone, direction, status, content, timestamp_local), tags=(tag,))
            
            # Configure tags
            self.tree.tag_configure('sent', background='#d4edda')
            self.tree.tag_configure('failed', background='#f8d7da')
            self.tree.tag_configure('queued', background='#fff3cd')
            self.tree.tag_configure('unread', background='#d1ecf1')
            
            # Update stats
            total = len(messages)
            sent = sum(1 for m in messages if str(m.get('status', '')) == 'sent')
            queued = sum(1 for m in messages if str(m.get('status', '')) == 'queued')
            failed = sum(1 for m in messages if str(m.get('status', '')) == 'failed')
            unread = sum(1 for m in messages if str(m.get('status', '')) == 'unread')
            
            self.stats_label.config(text=f"Total: {total} | Sent: {sent} | Queued: {queued} | Failed: {failed} | Unread: {unread}")
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            messagebox.showerror("Error", f"Failed to load messages:\n{str(e)}\n\n{error_detail}")
    
    def sort_column(self, col):
        """Sort treeview by column (toggle ascending/descending)"""
        # Get current items
        items = [(self.tree.set(item, col), item) for item in self.tree.get_children('')]
        
        # Determine sort order
        if hasattr(self, '_last_sort_col') and self._last_sort_col == col:
            self._sort_reverse = not getattr(self, '_sort_reverse', False)
        else:
            self._sort_reverse = True if col == "Timestamp" else False  # Timestamp defaults to desc (newest first)
        
        self._last_sort_col = col
        
        # Sort
        items.sort(reverse=self._sort_reverse)
        
        # Reorder tree
        for index, (_, item) in enumerate(items):
            self.tree.move(item, '', index)
        
        # Update column headers to show sort direction
        for c in ("ID", "Phone", "Direction", "Status", "Content", "Timestamp"):
            arrow = ""
            if c == col:
                arrow = " ⬇" if self._sort_reverse else " ⬆"
            self.tree.heading(c, text=self.tree.heading(c)['text'].split(' ⬇')[0].split(' ⬆')[0] + arrow)
    
    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Select the row under mouse
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)
    
    def on_select(self, event):
        """Show full message details when selected"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        msg_id = str(item['values'][0])
        
        try:
            # Fetch all messages and find matching one
            response = supabase.table('messages').select('*').execute()
            matching_msg = None
            for msg in response.data:
                if str(msg.get('id', '')).startswith(msg_id):
                    matching_msg = msg
                    break
            
            if matching_msg:
                msg = matching_msg
                
                # Display details (with local time conversion)
                timestamp_utc = msg.get('timestamp', '')
                timestamp_local = utc_to_local(timestamp_utc)
                
                # Decode hex-encoded content
                content = decode_hex_message(msg.get('content', ''))
                
                details = f"""ID: {msg.get('id', '')}
Phone: {msg.get('phone_number', '')}
Direction: {msg.get('direction', '')}
Status: {msg.get('status', '')}
Timestamp: {timestamp_local}

--- Message Content ---
{content}

--- Message Hash ---
{msg.get('message_hash', 'N/A')}
"""
                self.detail_text.delete('1.0', tk.END)
                self.detail_text.insert('1.0', details)
        except Exception as e:
            self.detail_text.delete('1.0', tk.END)
            self.detail_text.insert('1.0', f"Error loading details:\n{str(e)}")
    
    def edit_message(self):
        """Edit selected message content"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to edit")
            return
        
        item = self.tree.item(selection[0])
        msg_id = str(item['values'][0])
        
        try:
            # Fetch all messages and find matching one
            response = supabase.table('messages').select('*').execute()
            msg = None
            for m in response.data:
                if str(m.get('id', '')).startswith(msg_id):
                    msg = m
                    break
            
            if not msg:
                messagebox.showerror("Error", "Message not found")
                return
    
            full_id = msg['id']
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Message")
            edit_window.geometry("600x400")
            
            ttk.Label(edit_window, text=f"Editing: {msg['phone_number']}", font=("Arial", 12, "bold")).pack(pady=10)
            
            text_widget = scrolledtext.ScrolledText(edit_window, width=70, height=15, wrap=tk.WORD)
            text_widget.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
            text_widget.insert('1.0', msg['content'])
            
            def save():
                new_content = text_widget.get('1.0', tk.END).strip()
                try:
                    supabase.table('messages').update({'content': new_content}).eq('id', full_id).execute()
                    # Success - no popup, just refresh
                    edit_window.destroy()
                    self.load_messages()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update:\n{str(e)}")
            
            ttk.Button(edit_window, text="💾 Save", command=save).pack(pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit message:\n{str(e)}")
    
    def delete_message(self):
        """Delete selected message"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to delete")
            return
        
        item = self.tree.item(selection[0])
        msg_id = str(item['values'][0])
        
        # Removed confirmation dialog - direct delete
        
        try:
            # Fetch all messages and find matching one
            response = supabase.table('messages').select('id').execute()
            full_id = None
            for m in response.data:
                if str(m.get('id', '')).startswith(msg_id):
                    full_id = m['id']
                    break
            
            if full_id:
                supabase.table('messages').delete().eq('id', full_id).execute()
                self.load_messages()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete:\n{str(e)}")
    
    def change_status(self, new_status):
        """Change status of selected message"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message")
            return
        
        item = self.tree.item(selection[0])
        msg_id = str(item['values'][0])
        
        try:
            # Fetch all messages and find matching one
            response = supabase.table('messages').select('id').execute()
            full_id = None
            for m in response.data:
                if str(m.get('id', '')).startswith(msg_id):
                    full_id = m['id']
                    break
            
            if full_id:
                supabase.table('messages').update({'status': new_status}).eq('id', full_id).execute()
                self.load_messages()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status:\n{str(e)}")
    
    def compose_message(self, phone_number=None):
        """Open compose message window"""
        compose_window = tk.Toplevel(self.root)
        compose_window.title("Telegraph - Compose Message")
        compose_window.geometry("600x500")
        compose_window.transient(self.root)
        compose_window.grab_set()
        
        # Phone number field
        phone_frame = ttk.Frame(compose_window, padding="10")
        phone_frame.pack(fill=tk.X)
        ttk.Label(phone_frame, text="Phone Number:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
        phone_entry = ttk.Entry(phone_frame, width=25, font=("Arial", 10))
        phone_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        if phone_number:
            phone_entry.insert(0, phone_number)
        
        # Message field
        msg_frame = ttk.Frame(compose_window, padding="10")
        msg_frame.pack(fill=tk.BOTH, expand=True)
        ttk.Label(msg_frame, text="Message:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        message_text = scrolledtext.ScrolledText(msg_frame, width=70, height=15, wrap=tk.WORD, font=("Arial", 10))
        message_text.pack(fill=tk.BOTH, expand=True, pady=(5, 0))
        
        # Character count
        char_count_label = ttk.Label(msg_frame, text="0 characters", font=("Arial", 8), foreground="gray")
        char_count_label.pack(anchor=tk.W)
        
        def update_char_count():
            count = len(message_text.get('1.0', tk.END).strip())
            char_count_label.config(text=f"{count} characters")
            if count > 160:
                char_count_label.config(foreground="orange")
            else:
                char_count_label.config(foreground="gray")
        
        message_text.bind('<KeyRelease>', lambda e: update_char_count())
        
        # Schedule option
        schedule_frame = ttk.Frame(compose_window, padding="10")
        schedule_frame.pack(fill=tk.X)
        schedule_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(schedule_frame, text="Schedule for later", variable=schedule_var).pack(side=tk.LEFT, padx=5)
        
        # Date/time picker (hidden until schedule is checked)
        datetime_frame = ttk.Frame(compose_window, padding="10")
        
        ttk.Label(datetime_frame, text="Date:").pack(side=tk.LEFT, padx=5)
        date_entry = ttk.Entry(datetime_frame, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        ttk.Label(datetime_frame, text="Time (HH:MM):").pack(side=tk.LEFT, padx=5)
        time_entry = ttk.Entry(datetime_frame, width=8)
        time_entry.pack(side=tk.LEFT, padx=5)
        time_entry.insert(0, datetime.now().strftime("%H:%M"))
        
        def toggle_schedule():
            if schedule_var.get():
                datetime_frame.pack(fill=tk.X, before=button_frame)
            else:
                datetime_frame.pack_forget()
        
        schedule_var.trace('w', lambda *args: toggle_schedule())
        
        # Buttons
        button_frame = ttk.Frame(compose_window, padding="10")
        button_frame.pack(fill=tk.X)
        
        def send_message():
            phone = phone_entry.get().strip()
            message = message_text.get('1.0', tk.END).strip()
            
            if not phone:
                messagebox.showwarning("Missing Phone", "Please enter a phone number")
                return
            
            if not message:
                messagebox.showwarning("Empty Message", "Please enter a message")
                return
            
            normalized_phone = normalize_phone_number(phone)
            
            try:
                if schedule_var.get():
                    # Schedule message
                    date_str = date_entry.get().strip()
                    time_str = time_entry.get().strip()
                    
                    try:
                        # Parse date and time
                        schedule_dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
                        schedule_dt = schedule_dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
                        
                        # Insert into scheduled_messages table
                        supabase.table('scheduled_messages').insert({
                            'phone_number': normalized_phone,
                            'message_content': message,
                            'scheduled_time': schedule_dt.isoformat(),
                            'status': 'pending'
                        }).execute()
                        
                        messagebox.showinfo("Scheduled", f"Message scheduled for {date_str} {time_str}\nPhone: {normalized_phone}")
                    except ValueError as e:
                        messagebox.showerror("Invalid Date/Time", f"Please use format:\nDate: YYYY-MM-DD\nTime: HH:MM\n\nError: {str(e)}")
                        return
                else:
                    # Send immediately (queue)
                    supabase.table('messages').insert({
                        'phone_number': normalized_phone,
                        'content': message,
                        'direction': 'outbound',
                        'status': 'queued',
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }).execute()
                    
                    messagebox.showinfo("Queued", f"Message queued for immediate send\nPhone: {normalized_phone}")
                
                compose_window.destroy()
                self.load_messages()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message:\n{str(e)}")
        
        ttk.Button(button_frame, text="📤 Send Now", command=send_message).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Cancel", command=compose_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def reply_to_selected(self):
        """Reply to selected message"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to reply to")
            return
        
        item = self.tree.item(selection[0])
        phone = item['values'][1]  # Phone number is in column 1
        
        if phone:
            self.compose_message(phone_number=phone)
        else:
            messagebox.showwarning("No Phone", "Selected message has no phone number")
    
    def on_double_click_reply(self, event):
        """Handle double-click on message to reply"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        phone = item['values'][1]  # Phone number is in column 1
        
        if phone:
            self.compose_message(phone_number=phone)
    
    def add_to_reply_messages(self):
        """Add selected outbound message to Reply Messages by creating a user-initiated inbound message"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message first")
            return
        
        item = self.tree.item(selection[0])
        phone_number = str(item['values'][1])  # Phone column
        direction = str(item['values'][2])  # Direction column
        
        # Validate this is an outbound message
        if direction != 'outbound':
            messagebox.showwarning("Invalid Selection", 
                                 "This feature is only for outbound messages.\n\n"
                                 "Select an outbound message to initiate a follow-up conversation.")
            return
        
        # Confirm action
        contact_display = resolve_contact_name(phone_number)
        if not messagebox.askyesno("Add to Reply Messages", 
                                   f"Create a follow-up conversation with:\n{contact_display}\n\n"
                                   f"This will add a 'user-initiated' message to the Reply tab."):
            return
        
        try:
            # Normalize phone number
            normalized_phone = normalize_phone_number(phone_number)
            
            # Create a mock incoming message
            supabase.table('messages').insert({
                'phone_number': normalized_phone,
                'content': 'user-initiated',
                'direction': 'inbound',
                'status': 'unread',
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'message_hash': None
            }).execute()
            
            messagebox.showinfo("Success", 
                              f"Added to Reply Messages!\n\n"
                              f"Contact: {contact_display}\n"
                              f"Phone: {normalized_phone}\n\n"
                              f"You can now find them in the 'Reply to Messages' tab.")
            
            # Refresh All Messages view
            self.load_messages()
            
            # Refresh Reply to Messages view (if it exists)
            if hasattr(self, 'load_conversations'):
                self.load_conversations()
            
            # Optional: Switch to Reply to Messages tab
            try:
                self.notebook.select(1)  # Switch to tab index 1 (Reply to Messages)
            except:
                pass  # Silently fail if tab switching doesn't work
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add to Reply Messages:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def edit_message_timestamp(self):
        """Edit timestamp of selected message in database"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to edit timestamp")
            return
        
        item = self.tree.item(selection[0])
        msg_id = str(item['values'][0])
        
        try:
            # Fetch all messages and find matching one
            response = supabase.table('messages').select('*').execute()
            msg = None
            for m in response.data:
                if str(m.get('id', '')).startswith(msg_id):
                    msg = m
                    break
            
            if not msg:
                messagebox.showerror("Error", "Message not found")
                return
    
            full_id = msg['id']
            current_timestamp = msg['timestamp']
            
            # Parse current timestamp
            from dateutil import parser
            current_dt = parser.isoparse(current_timestamp)
            
            # Create edit dialog
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Edit Message Timestamp")
            edit_window.geometry("400x250")
            
            ttk.Label(edit_window, text="Edit Message Timestamp", font=("Arial", 12, "bold")).pack(pady=10)
            
            # Current timestamp display
            current_local = current_dt.astimezone(tz.tzlocal())
            current_str = current_local.strftime("%Y-%m-%d %I:%M %p %Z")
            ttk.Label(edit_window, text=f"Current: {current_str}").pack(pady=5)
            
            # Input frame
            input_frame = ttk.Frame(edit_window)
            input_frame.pack(pady=20, padx=20, fill=tk.X)
            
            ttk.Label(input_frame, text="New Date & Time:").pack(anchor=tk.W)
            
            # Date entry
            date_frame = ttk.Frame(input_frame)
            date_frame.pack(fill=tk.X, pady=5)
            ttk.Label(date_frame, text="Date (YYYY-MM-DD):", width=20).pack(side=tk.LEFT)
            date_entry = ttk.Entry(date_frame)
            date_entry.insert(0, current_local.strftime("%Y-%m-%d"))
            date_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Time entry
            time_frame = ttk.Frame(input_frame)
            time_frame.pack(fill=tk.X, pady=5)
            ttk.Label(time_frame, text="Time (HH:MM AM/PM):", width=20).pack(side=tk.LEFT)
            time_entry = ttk.Entry(time_frame)
            time_entry.insert(0, current_local.strftime("%I:%M %p"))
            time_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            def save_timestamp():
                try:
                    # Parse new timestamp
                    date_str = date_entry.get().strip()
                    time_str = time_entry.get().strip()
                    datetime_str = f"{date_str} {time_str}"
                    
                    # Parse and convert to UTC
                    new_dt = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
                    new_dt = new_dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
                    
                    # Update in database
                    supabase.table('messages').update({
                        'timestamp': new_dt.isoformat()
                    }).eq('id', full_id).execute()
                    
                    # Refresh display
                    edit_window.destroy()
                    self.load_messages()
                    messagebox.showinfo("Success", "Timestamp updated successfully!")
                    
                except ValueError as e:
                    messagebox.showerror("Invalid Format", f"Please use correct format:\nDate: YYYY-MM-DD\nTime: HH:MM AM/PM\n\nError: {str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to update timestamp:\n{str(e)}")
            
            # Buttons
            btn_frame = ttk.Frame(edit_window)
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="💾 Save", command=save_timestamp).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to edit timestamp:\n{str(e)}")
    
    def create_test_conversation(self):
        """Create a test conversation with back-and-forth messages"""
        conv_window = tk.Toplevel(self.root)
        conv_window.title("💬 Test Conversation Builder")
        conv_window.geometry("800x700")
        
        # Instructions
        ttk.Label(conv_window, 
                  text="Build a test conversation to test AI context understanding",
                  font=("Arial", 12, "bold")).pack(pady=10)
        
        # Phone number input
        phone_frame = ttk.Frame(conv_window)
        phone_frame.pack(pady=10, padx=20, fill=tk.X)
        ttk.Label(phone_frame, text="Phone Number:", width=15).pack(side=tk.LEFT)
        phone_entry = ttk.Entry(phone_frame, width=20)
        phone_entry.insert(0, "+16199773020")  # Default test number
        phone_entry.pack(side=tk.LEFT, padx=5)
        
        # Message list frame
        list_frame = ttk.LabelFrame(conv_window, text="Conversation Preview", padding=10)
        list_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Listbox to show messages
        list_scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        message_listbox = tk.Listbox(list_frame, yscrollcommand=list_scroll.set, height=15, font=("Courier", 10))
        list_scroll.config(command=message_listbox.yview)
        message_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        list_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind right-click for timestamp editing
        message_listbox.bind('<Button-3>', lambda e: show_message_context_menu(e, message_listbox))
        
        # Store messages
        conversation_messages = []
        
        def add_message(direction):
            """Add a message to the conversation"""
            content = message_entry.get().strip()
            if not content:
                messagebox.showwarning("Empty Message", "Please enter message content")
                return
            
            # Create timestamp (each message 2 minutes apart, chronological order)
            from datetime import timedelta
            base_time = datetime.now(tz.tzutc())
            offset_minutes = len(conversation_messages) * 2
            msg_time = base_time - timedelta(minutes=offset_minutes)
            
            msg = {
                "direction": direction,
                "content": content,
                "timestamp": msg_time
            }
            conversation_messages.append(msg)
            
            # Refresh the entire list to maintain proper order
            refresh_message_list()
            
            # Clear entry
            message_entry.delete(0, tk.END)
            message_entry.focus()
        
        def clear_conversation():
            """Clear all messages"""
            conversation_messages.clear()
            message_listbox.delete(0, tk.END)
        
        def show_message_context_menu(event, listbox):
            """Show context menu for message editing"""
            # Select the item under mouse
            index = listbox.nearest(event.y)
            if index >= 0:
                listbox.selection_clear(0, tk.END)
                listbox.selection_set(index)
                
                # Create context menu
                context_menu = tk.Menu(listbox, tearoff=0)
                context_menu.add_command(label="✏️ Edit Timestamp", 
                                       command=lambda: edit_message_timestamp(index))
                context_menu.add_command(label="🗑️ Delete Message", 
                                       command=lambda: delete_message(index))
                context_menu.tk_popup(event.x_root, event.y_root)
        
        def edit_message_timestamp(index):
            """Edit timestamp of selected message"""
            if index < 0 or index >= len(conversation_messages):
                return
            
            msg = conversation_messages[index]
            current_time = msg['timestamp']
            
            # Create edit dialog
            edit_window = tk.Toplevel(conv_window)
            edit_window.title("Edit Timestamp")
            edit_window.geometry("400x200")
            
            ttk.Label(edit_window, text="Edit Message Timestamp", font=("Arial", 12, "bold")).pack(pady=10)
            
            # Current timestamp display
            current_str = current_time.strftime("%Y-%m-%d %I:%M %p")
            ttk.Label(edit_window, text=f"Current: {current_str}").pack(pady=5)
            
            # Input frame
            input_frame = ttk.Frame(edit_window)
            input_frame.pack(pady=20, padx=20, fill=tk.X)
            
            ttk.Label(input_frame, text="New Date & Time:").pack(anchor=tk.W)
            
            # Date entry
            date_frame = ttk.Frame(input_frame)
            date_frame.pack(fill=tk.X, pady=5)
            ttk.Label(date_frame, text="Date (YYYY-MM-DD):", width=20).pack(side=tk.LEFT)
            date_entry = ttk.Entry(date_frame)
            date_entry.insert(0, current_time.strftime("%Y-%m-%d"))
            date_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            # Time entry
            time_frame = ttk.Frame(input_frame)
            time_frame.pack(fill=tk.X, pady=5)
            ttk.Label(time_frame, text="Time (HH:MM AM/PM):", width=20).pack(side=tk.LEFT)
            time_entry = ttk.Entry(time_frame)
            time_entry.insert(0, current_time.strftime("%I:%M %p"))
            time_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            
            def save_timestamp():
                try:
                    # Parse new timestamp
                    date_str = date_entry.get().strip()
                    time_str = time_entry.get().strip()
                    datetime_str = f"{date_str} {time_str}"
                    
                    # Parse and convert to UTC
                    new_dt = datetime.strptime(datetime_str, "%Y-%m-%d %I:%M %p")
                    new_dt = new_dt.replace(tzinfo=tz.tzlocal()).astimezone(tz.tzutc())
                    
                    # Update message
                    conversation_messages[index]['timestamp'] = new_dt
                    
                    # Refresh listbox
                    refresh_message_list()
                    
                    edit_window.destroy()
                    
                except ValueError as e:
                    messagebox.showerror("Invalid Format", f"Please use correct format:\nDate: YYYY-MM-DD\nTime: HH:MM AM/PM\n\nError: {str(e)}")
            
            # Buttons
            btn_frame = ttk.Frame(edit_window)
            btn_frame.pack(pady=20)
            ttk.Button(btn_frame, text="💾 Save", command=save_timestamp).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ Cancel", command=edit_window.destroy).pack(side=tk.LEFT, padx=5)
        
        def delete_message(index):
            """Delete selected message"""
            if index < 0 or index >= len(conversation_messages):
                return
            
            if messagebox.askyesno("Delete Message", "Are you sure you want to delete this message?"):
                conversation_messages.pop(index)
                refresh_message_list()
        
        def refresh_message_list():
            """Refresh the message listbox display in chronological order"""
            message_listbox.delete(0, tk.END)
            # Sort messages by timestamp (oldest first)
            sorted_messages = sorted(conversation_messages, key=lambda x: x['timestamp'])
            for msg in sorted_messages:
                direction_icon = "👤" if msg['direction'] == "inbound" else "🤖"
                time_str = msg['timestamp'].strftime("%I:%M %p")
                content = msg['content']
                display_text = f"{time_str} {direction_icon} {content}"
                message_listbox.insert(tk.END, display_text)
        
        def save_conversation():
            """Save conversation to database"""
            phone = phone_entry.get().strip()
            if not phone:
                messagebox.showerror("Error", "Please enter a phone number")
                return
            
            if not conversation_messages:
                messagebox.showerror("Error", "No messages to save")
                return
            
            try:
                # Insert messages in chronological order (oldest first)
                for msg in reversed(conversation_messages):
                    supabase.table('messages').insert({
                        'phone_number': phone,
                        'content': msg['content'],
                        'direction': msg['direction'],
                        'status': 'read' if msg['direction'] == 'outbound' else 'unread',
                        'timestamp': msg['timestamp'].isoformat(),
                        'message_hash': None
                    }).execute()
                
                messagebox.showinfo("Success", f"✅ Saved {len(conversation_messages)} messages!")
                conv_window.destroy()
                self.load_messages()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save conversation:\n{str(e)}")
        
        # Message input frame
        input_frame = ttk.LabelFrame(conv_window, text="Add Message", padding=10)
        input_frame.pack(pady=10, padx=20, fill=tk.X)
        
        message_entry = ttk.Entry(input_frame, width=60)
        message_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        message_entry.focus()
        
        # Quick add buttons
        btn_frame = ttk.Frame(input_frame)
        btn_frame.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(btn_frame, text="👤 Add Customer", 
                   command=lambda: add_message("inbound")).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="🤖 Add Bot Reply", 
                   command=lambda: add_message("outbound")).pack(side=tk.LEFT, padx=2)
        
        # Bind Enter key
        message_entry.bind('<Return>', lambda e: add_message("inbound"))
        message_entry.bind('<Shift-Return>', lambda e: add_message("outbound"))
        
        # Quick templates
        template_frame = ttk.LabelFrame(conv_window, text="Quick Templates", padding=10)
        template_frame.pack(pady=10, padx=20, fill=tk.X)
        
        def use_template(template_text):
            message_entry.delete(0, tk.END)
            message_entry.insert(0, template_text)
            message_entry.focus()
        
        templates = [
            "What's my points balance?",
            "Tell me about OG Kush",
            "What are the effects of Blue Dream?",
            "What have I bought before?",
            "Show me relaxing strains"
        ]
        
        for template in templates:
            ttk.Button(template_frame, text=template, 
                      command=lambda t=template: use_template(t)).pack(side=tk.LEFT, padx=5)
        
        # Bottom buttons
        bottom_frame = ttk.Frame(conv_window)
        bottom_frame.pack(pady=20, padx=20, fill=tk.X)
        
        ttk.Button(bottom_frame, text="🗑️ Clear All", 
                   command=clear_conversation).pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_frame, text="❌ Cancel", 
                   command=conv_window.destroy).pack(side=tk.RIGHT, padx=5)
        ttk.Button(bottom_frame, text="💾 Save Conversation to Database", 
                   command=save_conversation, style="Accent.TButton").pack(side=tk.RIGHT, padx=5)
        
        # Help text
        help_text = """
💡 Tips:
• Press ENTER to add as Customer message
• Press SHIFT+ENTER to add as Bot reply
• Messages display in chronological order (oldest first)
• Right-click any message to edit timestamp or delete
• Use templates for common test scenarios
• All messages will be saved to the database when you click Save
"""
        ttk.Label(conv_window, text=help_text, justify=tk.LEFT, 
                  foreground="gray").pack(pady=10, padx=20)
    
    def load_conversations(self):
        """Load UNREAD incoming messages grouped by phone number"""
        try:
            self.conv_listbox.delete(0, tk.END)
            
            # Fetch ONLY UNREAD inbound messages
            response = supabase.table('messages').select('*').eq('direction', 'inbound').eq('status', 'unread').order('timestamp', desc=True).execute()
            messages = response.data if hasattr(response, 'data') else []
            
            if not messages:
                self.conv_listbox.insert(tk.END, "No unread messages (all caught up! ✅)")
                return
            
            # Group by phone number (most recent first)
            phone_map = {}
            for msg in messages:
                phone = str(msg.get('phone_number', ''))
                if phone not in phone_map:
                    phone_map[phone] = msg
            
            # Display grouped conversations
            for phone, msg in phone_map.items():
                content = str(msg.get('content', ''))[:40]
                timestamp = utc_to_local(msg.get('timestamp', ''))
                
                # Resolve contact name
                contact_display = resolve_contact_name(phone)
                
                # Format: 💬 contact_name | timestamp | preview
                display = f"💬 {contact_display} | {timestamp[:16]} | {content}..."
                self.conv_listbox.insert(tk.END, display)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversations:\n{str(e)}")
    
    def on_conversation_select(self, event):
        """Handle conversation selection"""
        selection = self.conv_listbox.curselection()
        if not selection:
            return
        
        try:
            # Extract phone number from selected line
            selected_text = self.conv_listbox.get(selection[0])
            if "No incoming messages" in selected_text:
                return
            
            # Parse phone number from format:
            # "📖 Name (+phone) | timestamp | preview" OR "📖 +phone | timestamp | preview"
            parts = selected_text.split('|')
            if len(parts) < 2:
                return
            
            first_part = parts[0].strip()  # "📖 Name (+phone)" or "📖 +phone"
            
            # Check if there's a phone in parentheses (name resolved)
            if '(' in first_part and ')' in first_part:
                # Extract phone from parentheses: "Name (+16193683370)" -> "+16193683370"
                phone = first_part.split('(')[1].split(')')[0].strip()
            else:
                # No parentheses, phone is the last word: "📖 +16193683370"
                phone = first_part.split()[-1]
            
            # Store selected conversation
            self.selected_conversation = phone
            
            # Update customer label with resolved name
            contact_display = resolve_contact_name(phone)
            self.conv_customer_label.config(text=f"💬 Replying to: {contact_display}")
            
            # Load conversation history
            self.load_conversation_history(phone)
            
            # Load baseball card info
            self.load_baseball_card(phone)
            
            # Load suggested message (NEW!)
            self.load_suggested_message(phone)
            
            # Clear reply text
            self.reply_text.delete('1.0', tk.END)
            self.feedback_text.delete('1.0', tk.END)
            self.update_char_count()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversation:\n{str(e)}")
    
    def load_conversation_history(self, phone):
        """Load full conversation history for a phone number"""
        try:
            # Fetch all messages for this phone number
            response = supabase.table('messages').select('*').eq('phone_number', phone).order('timestamp', desc=False).execute()
            messages = response.data if hasattr(response, 'data') else []
            
            # Clear and populate history
            self.conv_history.config(state=tk.NORMAL)
            self.conv_history.delete('1.0', tk.END)
            
            if not messages:
                self.conv_history.insert(tk.END, "No messages found\n")
            else:
                for msg in messages:
                    timestamp = utc_to_local(msg.get('timestamp', ''))
                    direction = str(msg.get('direction', ''))
                    content = str(msg.get('content', ''))
                    # Decode hex-encoded messages
                    content = decode_hex_message(content)
                    status = str(msg.get('status', ''))
                    
                    if direction == 'inbound':
                        prefix = "👤 THEM:"
                        self.conv_history.insert(tk.END, f"\n{timestamp}\n{prefix}\n", "customer")
                    else:
                        prefix = "🤖 YOU:"
                        self.conv_history.insert(tk.END, f"\n{timestamp} [{status}]\n{prefix}\n", "bot")
                    
                    self.conv_history.insert(tk.END, f"{content}\n")
                    self.conv_history.insert(tk.END, "-" * 80 + "\n")
                
                # Tag colors
                self.conv_history.tag_config("customer", foreground="#0066cc", font=("Arial", 10, "bold"))
                self.conv_history.tag_config("bot", foreground="#009900", font=("Arial", 10, "bold"))
            
            self.conv_history.config(state=tk.DISABLED)
            self.conv_history.see(tk.END)
            
        except Exception as e:
            self.conv_history.config(state=tk.NORMAL)
            self.conv_history.delete('1.0', tk.END)
            self.conv_history.insert(tk.END, f"Error loading history:\n{str(e)}")
            self.conv_history.config(state=tk.DISABLED)
    
    def load_baseball_card(self, phone):
        """Load customer or budtender baseball card info"""
        try:
            self.baseball_card.config(state=tk.NORMAL)
            self.baseball_card.delete('1.0', tk.END)
            
            # Normalize phone to 10 digits for lookup
            phone_digits = ''.join(filter(str.isdigit, str(phone)))
            if len(phone_digits) >= 10:
                phone_10 = phone_digits[-10:]  # Last 10 digits
            else:
                phone_10 = phone_digits
            
            # PRIORITY 1: Check budtender first
            budtender = crm_supabase.table('budtenders').select('*').like('phone', f'%{phone_10}').execute()
            
            if budtender.data and len(budtender.data) > 0:
                # It's a budtender!
                bt = budtender.data[0]
                bt_name = f"{bt.get('first_name', '')} {bt.get('last_name', '')}".strip() or 'Unknown'
                
                card_text = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    EXTERNAL BUDTENDER (BT)                       ║
╚══════════════════════════════════════════════════════════════════╝

NAME:          {bt_name}
DISPENSARY:    {bt.get('dispensary_name', 'N/A')}
PHONE:         {bt.get('phone', 'N/A')}
POINTS:        {bt.get('points', 0):,}
EMAIL:         {bt.get('email', 'N/A')}
"""
                self.baseball_card.insert('1.0', card_text)
                self.baseball_card.config(state=tk.DISABLED)
                return
            
            # PRIORITY 2: Check customers_blaze (IC Database)
            customer = crm_supabase.table('customers_blaze').select('*').like('phone', f'%{phone_10}').execute()
            
            if customer.data and len(customer.data) > 0:
                # It's a customer! Show IC baseball card with FULL metrics
                c = customer.data[0]
                member_id = c.get('member_id')
                
                try:
                    # Calculate full metrics (like IC Viewer)
                    metrics = self._calculate_ic_metrics(member_id)
                    
                    # Build detailed customer card
                    card_text = self._build_ic_card(c, metrics)
                except Exception as e:
                    # Fallback to simple card if metrics fail
                    print(f"Metrics calculation failed, using simple card: {e}")
                    card_text = f"""
╔══════════════════════════════════════════════════════╗
║         BASEBALL CARD - INTERNAL CUSTOMER           ║
╚══════════════════════════════════════════════════════╝

NAME:  {c.get('name', 'Unknown')}
PHONE: {c.get('phone', 'N/A')}
EMAIL: {c.get('email', 'N/A')}
VIP:   {c.get('vip_status', 'Regular')}

[!] Full metrics unavailable - click refresh or check console
"""
                
                self.baseball_card.insert('1.0', card_text)
                self.baseball_card.config(state=tk.DISABLED)
                return
            
            # Unknown contact
            self.baseball_card.insert('1.0', f"""
╔══════════════════════════════════════════════════════════════════╗
║                        UNKNOWN CONTACT                           ║
╚══════════════════════════════════════════════════════════════════╝

PHONE:         {phone}

This contact is not found in:
  - External Budtender Database (budtenders)
  - Internal Customer Database (customers_blaze)
""")
            
            self.baseball_card.config(state=tk.DISABLED)
            
        except Exception as e:
            self.baseball_card.config(state=tk.NORMAL)
            self.baseball_card.delete('1.0', tk.END)
            self.baseball_card.insert(tk.END, f"Error loading info:\n{str(e)}")
            self.baseball_card.config(state=tk.DISABLED)
    
    def update_char_count(self, event=None):
        """Update character counter"""
        content = self.reply_text.get('1.0', tk.END).strip()
        char_count = len(content)
        
        if char_count > 160:
            self.char_counter.config(text=f"{char_count} / 160 characters (WILL BE SPLIT)", foreground="orange")
        elif char_count > 140:
            self.char_counter.config(text=f"{char_count} / 160 characters", foreground="orange")
        else:
            self.char_counter.config(text=f"{char_count} / 160 characters", foreground="gray")
    
    def show_conversation_context_menu(self, event):
        """Show right-click context menu for conversations"""
        # Select the item under cursor
        index = self.conv_listbox.nearest(event.y)
        self.conv_listbox.selection_clear(0, tk.END)
        self.conv_listbox.selection_set(index)
        
        # Create context menu
        context_menu = tk.Menu(self.root, tearoff=0)
        context_menu.add_command(label="✅ Mark as Read (Remove from list)", 
                                command=self.mark_conversation_as_read)
        context_menu.add_separator()
        context_menu.add_command(label="Cancel", command=lambda: None)
        
        # Show menu
        try:
            context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            context_menu.grab_release()
    
    def mark_conversation_as_read(self):
        """Mark all messages from this conversation as read"""
        selection = self.conv_listbox.curselection()
        if not selection:
            return
        
        try:
            # Get phone number from selection
            display_text = self.conv_listbox.get(selection[0])
            if "No unread messages" in display_text:
                return
            
            # Extract phone number from display text
            # Format: "💬 Name (phone) | timestamp | preview"
            phone = None
            if '(' in display_text and ')' in display_text:
                phone = display_text.split('(')[1].split(')')[0].strip()
            
            if not phone:
                messagebox.showwarning("Error", "Could not extract phone number")
                return
            
            # Normalize phone
            phone = normalize_phone_number(phone)
            
            # Confirm
            if not messagebox.askyesno("Mark as Read", 
                                      f"Mark all messages from {phone} as read?\n\n"
                                      f"This will remove them from the Reply tab."):
                return
            
            # Update ALL messages from this phone to 'read'
            supabase.table('messages').update({
                'status': 'read'
            }).eq('phone_number', phone).eq('direction', 'inbound').eq('status', 'unread').execute()
            
            messagebox.showinfo("Success", f"Marked conversation as read!\n\nRefreshing list...")
            
            # Refresh conversations list
            self.load_conversations()
            
            # Clear conversation display
            self.conv_text.delete('1.0', tk.END)
            self.reply_entry.delete('1.0', tk.END)
            self.current_reply_phone = None
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to mark as read:\n{str(e)}")
            import traceback
            traceback.print_exc()
    
    def send_reply(self):
        """Send reply by queuing it in the database"""
        if not self.selected_conversation:
            messagebox.showwarning("No Conversation", "Please select a conversation first")
            return
        
        reply_content = self.reply_text.get('1.0', tk.END).strip()
        if not reply_content:
            messagebox.showwarning("Empty Message", "Please enter a reply message")
            return
        
        try:
            # Normalize phone number to E.164 format before queuing
            normalized_phone = normalize_phone_number(self.selected_conversation)
            
            # Log if normalization changed the number
            if normalized_phone != self.selected_conversation:
                print(f"Normalized phone for queuing: {self.selected_conversation} -> {normalized_phone}")
            
            # Insert reply into database with status='queued' (SPLIT BY [BUBBLE] MARKERS)
            # Split reply into separate SMS bubbles
            bubbles = reply_content.split('[BUBBLE]')
            bubbles = [b.strip() for b in bubbles if b.strip()]  # Remove empty/whitespace-only bubbles
            
            if len(bubbles) == 0:
                # No [BUBBLE] markers found, send as single message
                bubbles = [reply_content]
            
            # Insert each bubble as separate queued message
            for bubble in bubbles:
                supabase.table('messages').insert({
                    'phone_number': normalized_phone,  # Use normalized phone
                    'content': bubble,
                    'direction': 'outbound',
                    'status': 'queued',
                    'timestamp': datetime.utcnow().isoformat()
                }).execute()
            
            # Show success with both original and normalized number if different
            phone_display = self.selected_conversation
            if normalized_phone != self.selected_conversation:
                phone_display = f"{self.selected_conversation} (normalized to {normalized_phone})"
            
            messagebox.showinfo("Reply Queued", 
                              f"Reply queued successfully!\n\n"
                              f"To: {phone_display}\n"
                              f"Bubbles: {len(bubbles)} SMS message(s)\n"
                              f"First: {bubbles[0][:50]}...\n\n"
                              f"conductor_system.py will send within 5-10 seconds.")
            
            # Clear reply text
            self.reply_text.delete('1.0', tk.END)
            self.update_char_count()
            
            # Refresh conversation history
            self.load_conversation_history(self.selected_conversation)
            
            # Refresh incoming list
            self.load_conversations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to queue reply:\n{str(e)}")
    def load_suggested_message(self, phone):
        """Load suggested message from campaign_messages table"""
        try:
            # Query campaign_messages for this phone with status='SUG'
            response = crm_supabase.table('campaign_messages').select('*').eq('phone_number', phone).eq('status', 'SUG').limit(1).execute()
            
            self.suggested_message.config(state=tk.NORMAL)
            self.suggested_message.delete('1.0', tk.END)
            
            if response.data and len(response.data) > 0:
                # Found a suggested message!
                suggestion = response.data[0]
                self.current_suggested_id = suggestion.get('id')
                self.current_suggested_data = suggestion
                
                message = suggestion.get('message_content', '')
                # Decode hex-encoded messages (if any)
                message = decode_hex_message(message)
                strategy = suggestion.get('strategy_type', '')
                confidence = suggestion.get('confidence', '')
                reasoning = suggestion.get('reasoning', '')
                
                # Display with metadata
                display = f"[{strategy.upper()}] {message}\n\n"
                if reasoning:
                    display += f"AI Reasoning: {reasoning[:100]}..."
                
                self.suggested_message.insert('1.0', display)
            else:
                # No suggested message
                self.current_suggested_id = None
                self.current_suggested_data = None
                self.suggested_message.insert('1.0', "No suggested message for this contact")
            
            self.suggested_message.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading suggested message: {e}")
            self.suggested_message.config(state=tk.NORMAL)
            self.suggested_message.delete('1.0', tk.END)
            self.suggested_message.insert('1.0', f"Error: {e}")
            self.suggested_message.config(state=tk.DISABLED)
            self.current_suggested_id = None
            self.current_suggested_data = None
    
    def approve_suggested(self):
        """Approve suggested message (changes status SUG → APR, ready for scheduling)"""
        if not self.current_suggested_id:
            messagebox.showwarning(
                "No Suggestion",
                "No suggested message to approve.\nIf you wrote your own message, use 'MARK APPROVED' below to save it as approved."
            )
            return
        
        try:
            feedback = self.feedback_text.get('1.0', tk.END).strip()
            phone = self.current_suggested_data.get('phone_number')
            message = self.current_suggested_data.get('message_content')
            
            # Update campaign_messages: SUG → APR (approved, ready for scheduling)
            crm_supabase.table('campaign_messages').update({
                'status': 'APR',
                'reviewed_by': 'Manual Approval',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': feedback if feedback else 'Approved as-is'
            }).eq('id', self.current_suggested_id).execute()
            # Also persist a feedback/training record (best-effort)
            try:
                crm_supabase.table('message_feedback').insert({
                    'campaign_message_id': self.current_suggested_id,
                    'suggested_message': message,
                    'suggested_reasoning': self.current_suggested_data.get('reasoning'),
                    'suggested_strategy': self.current_suggested_data.get('strategy_type'),
                    'action': 'approved',
                    'final_message': self.reply_text.get('1.0', tk.END).strip() or message,
                    'human_reasoning': feedback if feedback else 'Approved as-is',
                    'customer_id': phone,
                    'reviewed_by': 'SMS Viewer'
                }).execute()
            except Exception as _e:
                print(f"Warning: could not insert message_feedback for approved: {_e}")
            
            messagebox.showinfo("Approved", 
                              f"Message approved! (SUG → APR)\n\n"
                              f"Status: Ready for scheduling\n\n"
                              f"Next step: Run scheduler to assign send time\n"
                              f"(APR → SCH → queued → sent)")
            
            # Clear and reload
            self.load_suggested_message(phone)
            self.feedback_text.delete('1.0', tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve message:\n{str(e)}")
    
    def _resize_sug_message(self, width: int):
        """Resize message column in master view via slider."""
        try:
            self.sug_tree.column("message_full", width=max(200, int(width)))
        except Exception:
            pass
    
    def _update_sug_selection_count(self, event=None):
        """Update selection counter label"""
        try:
            count = len(self.sug_tree.selection())
            if count > 0:
                self.sug_selection_label.config(text=f"✓ {count} selected")
            else:
                self.sug_selection_label.config(text="")
        except:
            pass
    
    def _show_sug_context_menu(self, event):
        """Show context menu for Campaign Master tree with workflow actions."""
        selection = self.sug_tree.selection()
        if not selection:
            return
        
        try:
            menu = tk.Menu(self.root, tearoff=0)
            
            # Check status of first selected item
            first_item = self.sug_tree.item(selection[0])
            status = first_item['values'][0] if first_item['values'] else ''
            
            # Add workflow actions based on status
            if status == 'SUG':
                menu.add_command(label="✅ Approve Selected", command=self._bulk_approve_selected_campaigns)
                menu.add_separator()
            elif status == 'APR':
                menu.add_command(label="📅 Schedule Selected...", command=lambda: self._bulk_schedule_with_bullseye(self.sug_tree))
                menu.add_separator()
                menu.add_command(label="⬅️ Roll Back to Suggested", command=lambda: self._bulk_rollback_status(self.sug_tree, 'SUG'))
            elif status == 'SCH':
                menu.add_command(label="⬅️ Roll Back to Approved", command=lambda: self._bulk_rollback_status(self.sug_tree, 'APR'))
            
            menu.add_separator()
            menu.add_command(label="✏️ Edit Selected", command=lambda: self.edit_message_popup(self.sug_tree, table_name=BT_CAMPAIGN_TABLE))
            menu.add_command(label="🗑️ Delete Selected", command=lambda: self._bulk_delete_selected(self.sug_tree))
            
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
    
    def _show_apr_context_menu(self, event):
        """Show context menu for Approved tree."""
        selection = self.apr_tree.selection()
        if not selection:
            return
        
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="📅 Schedule Selected...", command=lambda: self._bulk_schedule_with_bullseye(self.apr_tree))
            menu.add_separator()
            menu.add_command(label="⬅️ Roll Back to Suggested", command=lambda: self._bulk_rollback_status(self.apr_tree, 'SUG'))
            menu.add_separator()
            menu.add_command(label="✏️ Edit Selected", command=lambda: self.edit_message_popup(self.apr_tree, table_name=BT_CAMPAIGN_TABLE))
            menu.add_command(label="🗑️ Delete Selected", command=lambda: self._bulk_delete_selected(self.apr_tree))
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
    
    def _show_sched_context_menu(self, event):
        """Show context menu for Scheduled tree."""
        selection = self.sched_tree.selection()
        if not selection:
            return
        
        try:
            menu = tk.Menu(self.root, tearoff=0)
            menu.add_command(label="⬅️ Roll Back to Approved", command=lambda: self._bulk_rollback_status(self.sched_tree, 'APR'))
            menu.add_command(label="❌ Cancel Selected", command=self.cancel_scheduled)
            menu.add_separator()
            menu.add_command(label="✏️ Edit Selected", command=lambda: self.edit_message_popup(self.sched_tree, table_name=BT_CAMPAIGN_TABLE))
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass
    
    def _bulk_rollback_status(self, tree, target_status):
        """Roll back selected messages to a previous status."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select one or more rows first.")
            return
        
        try:
            ids = []
            for item_id in selection:
                item = tree.item(item_id)
                tags = item.get('tags') or []
                if tags:
                    ids.append(tags[0])
            
            if not ids:
                messagebox.showwarning("No IDs", "Could not resolve selected IDs.")
                return
            
            # Confirm action
            status_name = {"SUG": "Suggested", "APR": "Approved", "SCH": "Scheduled"}.get(target_status, target_status)
            confirm = messagebox.askyesno("Confirm Rollback", 
                                         f"Roll back {len(ids)} message(s) to {status_name}?")
            if not confirm:
                return
            
            # Bulk update
            update_data = {
                'status': target_status,
                'reviewed_at': datetime.now(timezone.utc).isoformat()
            }
            
            # Clear scheduled_for if rolling back from SCH
            if target_status in ('SUG', 'APR'):
                update_data['scheduled_for'] = None
            
            bt_supabase.table(BT_CAMPAIGN_TABLE).update(update_data).in_('id', ids).execute()
            
            messagebox.showinfo("Success", f"Rolled back {len(ids)} message(s) to {status_name}.")
            
            # Refresh views
            self.load_suggested_overview()
            self.load_approved_overview()
            self.load_scheduled_overview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Rollback failed:\n{e}")
    
    def _bulk_delete_selected(self, tree):
        """Delete selected messages."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select one or more rows first.")
            return
        
        try:
            ids = []
            for item_id in selection:
                item = tree.item(item_id)
                tags = item.get('tags') or []
                if tags:
                    ids.append(tags[0])
            
            if not ids:
                messagebox.showwarning("No IDs", "Could not resolve selected IDs.")
                return
            
            # Confirm deletion
            confirm = messagebox.askyesno("Confirm Deletion", 
                                         f"Permanently delete {len(ids)} message(s)?")
            if not confirm:
                return
            
            # Bulk delete
            bt_supabase.table(BT_CAMPAIGN_TABLE).delete().in_('id', ids).execute()
            
            messagebox.showinfo("Success", f"Deleted {len(ids)} message(s).")
            
            # Refresh views
            self.load_suggested_overview()
            self.load_approved_overview()
            self.load_scheduled_overview()
            
        except Exception as e:
            messagebox.showerror("Error", f"Deletion failed:\n{e}")
    
    def _bulk_schedule_with_bullseye(self, tree):
        """Schedule selected messages with Bullseye timing feature."""
        selection = tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select one or more messages first.")
            return
        
        try:
            # Get IDs
            ids = []
            for item_id in selection:
                item = tree.item(item_id)
                tags = item.get('tags') or []
                if tags:
                    ids.append(tags[0])
            
            if not ids:
                messagebox.showwarning("No IDs", "Could not resolve selected IDs.")
                return
            
            # Show Bullseye dialog
            self._show_bullseye_dialog(ids)
            
        except Exception as e:
            messagebox.showerror("Error", f"Schedule failed:\n{e}")
            import traceback
            traceback.print_exc()
    
    def _show_bullseye_dialog(self, message_ids):
        """Show dialog for Bullseye scheduling."""
        import random
        from datetime import timedelta
        from dateutil import tz
        
        dialog = tk.Toplevel(self.root)
        dialog.title(f"📅 Bullseye Scheduler - {len(message_ids)} Messages")
        dialog.geometry("550x500")  # Taller to show all controls
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Info
        info_frame = ttk.LabelFrame(dialog, text="Scheduling Info", padding="10")
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(info_frame, text=f"Scheduling {len(message_ids)} messages", font=("Arial", 10, "bold")).pack()
        ttk.Label(info_frame, text="Messages will be spaced 5-7 minutes apart", foreground="gray").pack()
        ttk.Label(info_frame, text="Break every 8-10 messages (randomized for safety)", foreground="gray").pack()
        
        # Target Time
        time_frame = ttk.LabelFrame(dialog, text="Target Time", padding="10")
        time_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(time_frame, text="Date (MM/DD/YYYY):").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        date_entry = ttk.Entry(time_frame, width=15)
        date_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Default to tomorrow
        tomorrow = datetime.now(tz.gettz('America/Los_Angeles')) + timedelta(days=1)
        date_entry.insert(0, tomorrow.strftime("%m/%d/%Y"))
        
        ttk.Label(time_frame, text="Time (HH:MM AM/PM):").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        time_entry = ttk.Entry(time_frame, width=15)
        time_entry.grid(row=1, column=1, padx=5, pady=5)
        time_entry.insert(0, "5:00 PM")
        
        # Day of week display
        day_label = ttk.Label(time_frame, text="", foreground="blue", font=("Arial", 9, "italic"))
        day_label.grid(row=2, column=0, columnspan=2, pady=5)
        
        def update_day_of_week(event=None):
            """Update day of week display when date changes"""
            try:
                date_str = date_entry.get().strip()
                date_obj = datetime.strptime(date_str, "%m/%d/%Y")
                day_name = date_obj.strftime("%A")  # Full day name (e.g., "Tuesday")
                day_label.config(text=f"📅 {day_name}")
            except:
                day_label.config(text="")
        
        # Bind date entry to update day of week
        date_entry.bind('<KeyRelease>', update_day_of_week)
        date_entry.bind('<FocusOut>', update_day_of_week)
        update_day_of_week()  # Show initial day
        
        # Queue Options
        queue_frame = ttk.LabelFrame(dialog, text="Queue Mode", padding="10")
        queue_frame.pack(fill=tk.X, padx=10, pady=10)
        
        queue_mode_var = tk.StringVar(value="target")
        add_to_queue_var = tk.BooleanVar(value=False)
        
        ttk.Radiobutton(queue_frame, text="📅 Use Target Time (Bullseye positioning)", 
                       variable=queue_mode_var, value="target").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(queue_frame, text="➕ Add to Current Queue (append to end of scheduled messages)", 
                       variable=queue_mode_var, value="queue").pack(anchor=tk.W, padx=5, pady=2)
        
        # Bullseye Position (only visible when target mode is selected)
        position_frame = ttk.LabelFrame(dialog, text="Bullseye Position (for Target Time mode)", padding="10")
        position_frame.pack(fill=tk.X, padx=10, pady=10)
        
        position_var = tk.StringVar(value="begins")
        
        ttk.Radiobutton(position_frame, text="Begins at - First message at target time", 
                       variable=position_var, value="begins").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(position_frame, text="Middle - Middle message at target time", 
                       variable=position_var, value="middle").pack(anchor=tk.W, padx=5, pady=2)
        ttk.Radiobutton(position_frame, text="Ends at - Last message at target time", 
                       variable=position_var, value="ends").pack(anchor=tk.W, padx=5, pady=2)
        
        # Buttons
        btn_frame = ttk.Frame(dialog)
        btn_frame.pack(pady=10)
        
        def schedule_messages():
            try:
                pst_tz = tz.gettz('America/Los_Angeles')
                queue_mode = queue_mode_var.get()
                
                # Determine starting time
                if queue_mode == "queue":
                    # Find last scheduled message time (MASTER QUEUE)
                    result = bt_supabase.table(BT_CAMPAIGN_TABLE).select('scheduled_for').eq('status', 'SCH').order('scheduled_for', desc=True).limit(1).execute()
                    
                    if result.data and result.data[0].get('scheduled_for'):
                        # Continue from last scheduled time
                        last_scheduled = parser.parse(result.data[0]['scheduled_for'])
                        current_time = last_scheduled.astimezone(pst_tz) + timedelta(minutes=random.randint(5, 7))
                    else:
                        # No queue exists, start now
                        current_time = datetime.now(pst_tz)
                else:
                    # Use target time (classic Bullseye mode)
                    date_str = date_entry.get().strip()
                    time_str = time_entry.get().strip()
                    target_dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p")
                    current_time = pst_tz.localize(target_dt)
                
                # Calculate schedule times with randomization
                num_messages = len(message_ids)
                schedule_times = []
                
                # Respect scheduling windows (9am-8pm, skip certain days)
                def next_valid_time(dt):
                    """Ensure time is within 9am-8pm window"""
                    while True:
                        hour = dt.hour
                        # If before 9am, jump to 9am
                        if hour < 9:
                            dt = dt.replace(hour=9, minute=0, second=0)
                        # If after 8pm, jump to 9am next day
                        elif hour >= 20:
                            dt = dt + timedelta(days=1)
                            dt = dt.replace(hour=9, minute=0, second=0)
                        else:
                            break
                    return dt
                
                current_time = next_valid_time(current_time)
                
                for i in range(num_messages):
                    schedule_times.append(current_time)
                    
                    # Random spacing: 5-7 minutes
                    spacing = random.randint(5, 7)
                    
                    # Add break every 8-10 messages
                    if (i + 1) % random.randint(8, 10) == 0 and i < num_messages - 1:
                        spacing += random.randint(10, 15)  # Extra break time
                    
                    current_time = current_time + timedelta(minutes=spacing)
                    current_time = next_valid_time(current_time)  # Respect windows
                
                # Adjust based on Bullseye position (only in target mode)
                if queue_mode == "target":
                    position = position_var.get()
                    date_str = date_entry.get().strip()
                    time_str = time_entry.get().strip()
                    target_dt = datetime.strptime(f"{date_str} {time_str}", "%m/%d/%Y %I:%M %p")
                    target_dt = pst_tz.localize(target_dt)
                    
                    if position == "middle":
                        middle_idx = len(schedule_times) // 2
                        offset = schedule_times[middle_idx] - target_dt
                        schedule_times = [t - offset for t in schedule_times]
                    elif position == "ends":
                        offset = schedule_times[-1] - target_dt
                        schedule_times = [t - offset for t in schedule_times]
                
                # Update messages in database (preserving order)
                for msg_id, sched_time in zip(message_ids, schedule_times):
                    bt_supabase.table(BT_CAMPAIGN_TABLE).update({
                        'status': 'SCH',
                        'scheduled_for': sched_time.astimezone(timezone.utc).isoformat(),
                        'reviewed_at': datetime.now(timezone.utc).isoformat()
                    }).eq('id', msg_id).execute()
                
                mode_text = "Added to queue" if queue_mode == "queue" else "Scheduled"
                messagebox.showinfo("Success", f"{mode_text} {len(message_ids)} messages!\n\n"
                                              f"First: {schedule_times[0].strftime('%m/%d %I:%M %p')}\n"
                                              f"Last: {schedule_times[-1].strftime('%m/%d %I:%M %p')}")
                dialog.destroy()
                
                # Refresh views
                self.load_suggested_overview()
                self.load_approved_overview()
                self.load_scheduled_overview()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to schedule:\n{e}")
                import traceback
                traceback.print_exc()
        
        ttk.Button(btn_frame, text="📅 Schedule Messages", command=schedule_messages).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="❌ Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _bulk_approve_selected_campaigns(self):
        """Approve all selected rows in Campaign Master (SUG → APR)."""
        selection = self.sug_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Select one or more rows first.")
            return
        try:
            ids = []
            for item_id in selection:
                item = self.sug_tree.item(item_id)
                tags = item.get('tags') or []
                if tags:
                    ids.append(tags[0])
            if not ids:
                messagebox.showwarning("No IDs", "Could not resolve selected IDs.")
                return
            # Bulk update
            crm_supabase.table('campaign_messages').update({
                'status': 'APR',
                'reviewed_by': 'Bulk Approval',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': 'Bulk approved from Campaign Master'
            }).in_('id', ids).execute()
            messagebox.showinfo("Approved", f"Approved {len(ids)} message(s).")
            self.load_suggested_overview()
            self.load_approved_overview()
        except Exception as e:
            messagebox.showerror("Error", f"Bulk approve failed:\n{e}")
    def edit_suggested(self):
        """Copy suggested message to reply box for editing"""
        if not self.current_suggested_data:
            messagebox.showwarning("No Suggestion", "No suggested message to edit")
            return
        
        # Copy suggested message to reply box
        message = self.current_suggested_data.get('message_content', '')
        self.reply_text.delete('1.0', tk.END)
        self.reply_text.insert('1.0', message)
        self.update_char_count()
        
        # Add note prompt
        self.feedback_text.delete('1.0', tk.END)
        self.feedback_text.insert('1.0', "Why did you edit the AI suggestion? (e.g., 'Too generic for VIP')")
        
        messagebox.showinfo("Edit Mode", "Suggested message copied to reply box.\n\nEdit as needed, add feedback, then click 'SEND IMMEDIATELY'")
    
    def reject_suggested(self):
        """Reject suggested message with feedback"""
        if not self.current_suggested_id:
            messagebox.showwarning("No Suggestion", "No suggested message to reject")
            return
        
        feedback = self.feedback_text.get('1.0', tk.END).strip()
        if not feedback:
            messagebox.showwarning("Feedback Required", "Please provide feedback on why you're rejecting this message.\n\nThis helps improve AI suggestions.")
            return
        
        try:
            # 1. Update campaign_messages: SUG -> rejected
            crm_supabase.table('campaign_messages').update({
                'status': 'rejected',
                'reviewed_by': 'Manual Rejection',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': feedback
            }).eq('id', self.current_suggested_id).execute()
            
            # 2. Save to message_feedback for AI training
            phone = self.current_suggested_data.get('phone_number')
            message = self.current_suggested_data.get('message_content')
            
            crm_supabase.table('message_feedback').insert({
                'campaign_message_id': self.current_suggested_id,
                'suggested_message': message,
                'suggested_reasoning': self.current_suggested_data.get('reasoning'),
                'suggested_strategy': self.current_suggested_data.get('strategy_type'),
                'action': 'rejected',
                'final_message': None,
                'human_reasoning': feedback,
                'customer_id': phone,
                'reviewed_by': 'SMS Viewer'
            }).execute()
            
            messagebox.showinfo("Rejected", f"Message rejected and feedback saved for AI training.")
            
            # Clear and reload
            self.load_suggested_message(phone)
            self.feedback_text.delete('1.0', tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject message:\n{str(e)}")
    
    def mark_approved(self):
        """Save approval + feedback even when no suggested message exists."""
        if not self.selected_conversation:
            messagebox.showwarning("No Conversation", "Please select a conversation first")
            return
        final_msg = self.reply_text.get('1.0', tk.END).strip()
        if not final_msg:
            messagebox.showwarning("Empty Message", "Please enter a reply message to mark as approved.")
            return
        try:
            phone = normalize_phone_number(self.selected_conversation)
            notes = self.feedback_text.get('1.0', tk.END).strip()
            # Best-effort include snapshot of baseball card inside notes
            snapshot = ""
            try:
                self.baseball_card.config(state=tk.NORMAL)
                snapshot = self.baseball_card.get('1.0', tk.END).strip()
                self.baseball_card.config(state=tk.DISABLED)
            except Exception:
                pass
            notes_with_snapshot = (notes + ("\n\n--- BASEBALL_CARD ---\n" + snapshot if snapshot else "")).strip()
            payload = {
                'campaign_message_id': self.current_suggested_id,
                'customer_id': phone,
                'action': 'approved' if self.current_suggested_id else 'approved_manual',
                'suggested_message': (self.current_suggested_data.get('message_content') if self.current_suggested_data else None),
                'suggested_reasoning': (self.current_suggested_data.get('reasoning') if self.current_suggested_data else None),
                'suggested_strategy': (self.current_suggested_data.get('strategy_type') if self.current_suggested_data else None),
                'final_message': final_msg,
                'human_reasoning': notes_with_snapshot if notes_with_snapshot else 'Approved manual message',
                'reviewed_by': 'SMS Viewer'
            }
            # If there is a suggested message, also mark APR
            if self.current_suggested_id:
                crm_supabase.table('campaign_messages').update({
                    'status': 'APR',
                    'reviewed_by': 'Manual Approval',
                    'reviewed_at': datetime.now(timezone.utc).isoformat(),
                    'feedback_notes': notes if notes else 'Approved via reply box'
                }).eq('id', self.current_suggested_id).execute()
            # Save feedback/training record (best-effort; ignore if table missing)
            try:
                crm_supabase.table('message_feedback').insert(payload).execute()
            except Exception as fe:
                # Ignore missing-table errors; proceed without blocking
                err_text = str(fe)
                if "could not find the table" not in err_text.lower():
                    print(f"message_feedback insert warning: {fe}")
            messagebox.showinfo("Saved", "Approval saved. You can still send the message immediately.")
            # Clear notes; keep reply so user can still send it
            self.feedback_text.delete('1.0', tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save approval/feedback:\n{str(e)}")
    def _calculate_ic_metrics(self, member_id):
        """Calculate full customer metrics (like IC Viewer)"""
        try:
            from collections import Counter, defaultdict
            from datetime import datetime
            
            # Get all transactions
            trans_result = crm_supabase.table('transactions').select('*').eq('customer_id', member_id).order('date', desc=True).execute()
            transactions = trans_result.data if trans_result.data else []
            
            if not transactions:
                return {}
            
            # Calculate metrics
            total_visits = len(transactions)
            total_revenue = sum(float(t.get('total_amount', 0)) for t in transactions)
            avg_revenue_per_visit = total_revenue / total_visits if total_visits > 0 else 0
            
            # Visit frequency
            dates = [datetime.fromisoformat(t['date'].replace('Z', '+00:00')) for t in transactions if t.get('date')]
            if len(dates) > 1:
                dates_sorted = sorted(dates)
                total_days = (dates_sorted[-1] - dates_sorted[0]).days
                avg_days_between = total_days / (len(dates) - 1) if len(dates) > 1 else 0
                visits_per_month = (len(dates) / total_days * 30) if total_days > 0 else 0
            else:
                avg_days_between = None
                visits_per_month = None
            
            # Get transaction items
            transaction_ids = [t['transaction_id'] for t in transactions]
            if not transaction_ids:
                items = []
            else:
                items_result = crm_supabase.table('transaction_items').select('*').in_('transaction_id', transaction_ids).execute()
                items = items_result.data if items_result.data else []
            
            # Top categories
            categories = [item.get('category') for item in items if item.get('category')]
            category_counts = Counter(categories).most_common(3)
            
            # Top brands by revenue
            brand_revenue = defaultdict(float)
            brand_category_revenue = defaultdict(lambda: defaultdict(float))
            for item in items:
                brand = item.get('brand', 'Unknown')
                category = item.get('category', 'Unknown')
                revenue = float(item.get('total_price', 0))
                brand_revenue[brand] += revenue
                brand_category_revenue[brand][category] += revenue
            
            top_brands = sorted(brand_revenue.items(), key=lambda x: x[1], reverse=True)[:3]
            
            # Top products
            product_counts = defaultdict(lambda: {'count': 0, 'revenue': 0})
            for item in items:
                name = item.get('product_name', 'Unknown')
                product_counts[name]['count'] += 1
                product_counts[name]['revenue'] += float(item.get('total_price', 0))
            
            top_products = sorted(
                [{'name': k, **v} for k, v in product_counts.items()],
                key=lambda x: x['revenue'],
                reverse=True
            )[:3]
            
            # Preferences
            locations = [t.get('shop_location') for t in transactions if t.get('shop_location')]
            payments = [t.get('payment_type') for t in transactions if t.get('payment_type')]
            
            return {
                'total_visits': total_visits,
                'total_revenue': total_revenue,
                'avg_revenue_per_visit': avg_revenue_per_visit,
                'avg_days_between_visits': avg_days_between,
                'visits_per_month': visits_per_month,
                'top_categories': category_counts,
                'favorite_brands': top_brands,
                'top_products': top_products,
                'favorite_category': category_counts[0][0] if category_counts else 'Unknown',
                'preferred_location': Counter(locations).most_common(1)[0][0] if locations else 'Unknown',
                'preferred_payment': Counter(payments).most_common(1)[0][0] if payments else 'Unknown',
                'brand_breakdown': dict(brand_revenue),
                'brand_category_breakdown': {k: dict(v) for k, v in brand_category_revenue.items()},
                'last_5_transactions': transactions[:5]
            }
        except Exception as e:
            import traceback
            print(f"Error calculating metrics: {e}")
            print(traceback.format_exc())
            return {}
    
    def _build_ic_card(self, customer, metrics):
        """Build detailed IC baseball card (like IC Viewer)"""
        total_visits = metrics.get('total_visits', customer.get('total_visits', 0))
        lifetime_value = metrics.get('total_revenue', customer.get('lifetime_value', 0))
        avg_revenue_per_visit = metrics.get('avg_revenue_per_visit', 0)
        avg_days_between = metrics.get('avg_days_between_visits')
        visits_per_month = metrics.get('visits_per_month')
        
        visit_frequency = f"Every {avg_days_between:.1f} days" if avg_days_between else "N/A"
        visit_velocity = f"{visits_per_month:.2f}/month" if visits_per_month else "N/A"
        
        favorite_category = metrics.get('favorite_category', 'Unknown')
        preferred_location = metrics.get('preferred_location', 'Unknown')
        preferred_payment = metrics.get('preferred_payment', 'Unknown')
        
        top_categories = metrics.get('top_categories', [])
        category_lines = [f"    • {name} ({count} visits)" for name, count in top_categories] or ['    No data']
        
        top_brands = metrics.get('favorite_brands', [])
        brand_lines = [f"    • {name}: ${revenue:.2f}" for name, revenue in top_brands] or ['    No data']
        
        top_products = metrics.get('top_products', [])
        product_lines = [f"    • {p['name'][:25]} ({p['count']}x | ${p['revenue']:.2f})" for p in top_products] or ['    No data']
        
        # Last 5 transactions (enhanced: Date | Day | Time | Budtender | Spend | % MOTA)
        from datetime import datetime
        last_5 = metrics.get('last_5_transactions', [])
        transaction_lines = []
        if last_5:
            for t in last_5:
                # Parse date/time
                if t.get('date'):
                    try:
                        dt = datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d')
                        day_str = dt.strftime('%a')
                        time_str = dt.strftime('%I:%M %p')
                    except Exception:
                        date_str = t['date'][:10]
                        day_str = '???'
                        time_str = t['date'][11:16] if len(t['date']) > 16 else '??:??'
                else:
                    date_str, day_str, time_str = 'N/A', '???', '??:??'
                
                # Budtender resolve
                budtender = 'Unknown'
                try:
                    sid = t.get('seller_id')
                    if sid:
                        emp = crm_supabase.table('employees_blaze').select('name').eq('employee_id', sid).limit(1).execute()
                        if emp.data:
                            budtender = emp.data[0].get('name') or 'Unknown'
                except Exception:
                    pass
                if len(budtender) > 13:
                    budtender = budtender[:13]
                
                # Spend
                amount = float(t.get('total_amount', 0) or 0)
                
                # Percent MOTA
                mota_pct = 0
                try:
                    tid = t.get('transaction_id')
                    if tid:
                        its = crm_supabase.table('transaction_items').select('brand,total_price').eq('transaction_id', tid).execute()
                        if its.data:
                            total_spend = sum(float(i.get('total_price', 0) or 0) for i in its.data)
                            mota_spend = sum(float(i.get('total_price', 0) or 0) for i in its.data if (i.get('brand') or '').upper().find('MOTA') >= 0)
                            mota_pct = int((mota_spend / total_spend) * 100) if total_spend > 0 else 0
                except Exception:
                    mota_pct = 0
                
                transaction_lines.append(f"    {date_str:<10} {day_str:>3} {time_str:>9} {budtender:<13} ${amount:>7.2f} {mota_pct:>3}%")
        else:
            transaction_lines = ['    No transactions']
        
        card = f"""
╔══════════════════════════════════════════════════════╗
║         BASEBALL CARD - INTERNAL CUSTOMER           ║
╚══════════════════════════════════════════════════════╝

NAME: {customer.get('name', 'Unknown')}
      {customer.get('member_id', 'N/A')} 
      {customer.get('vip_status', 'Regular')} 
      Churn: {customer.get('churn_risk', 'N/A')}

KEY STATS
   Lifetime Value:        ${lifetime_value:,.2f}
   Total Visits:          {total_visits}
   Avg Transaction:       ${avg_revenue_per_visit:.2f}
   Visits/Month:          {visit_velocity}
   Visit Frequency:       {visit_frequency}
   Days Since Last:       {customer.get('days_since_last_visit', 'N/A')}

PURCHASE HABITS
   Top Category:    {favorite_category}
   Fav Brands:
{chr(10).join(brand_lines)}

TOP PRODUCTS
{chr(10).join(product_lines)}

PREFERENCES
   Location:   {preferred_location}
   Payment:    {preferred_payment}

CONTACT
   Phone: {customer.get('phone', 'N/A')}
   Email: {customer.get('email', 'N/A')}

        LAST 5 VISITS
           Date       Day Time      Budtender      Spend   MOTA
           --------------------------------------------------------
{chr(10).join(transaction_lines)}

TIMELINE
   Member Since: {customer.get('created_at', 'N/A')[:10] if customer.get('created_at') else 'N/A'}
   Last Visit:   {customer.get('last_visited', 'N/A')}
"""
        return card


    def _create_first_texts_tab(self):
        """Create the First Texts tab - approve suggested messages before first contact"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📨 First Texts")
        
        # Top bar - Campaign selector
        top_bar = ttk.Frame(tab)
        top_bar.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(top_bar, text="📋 Campaign:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 10))
        
        self.campaign_selector = ttk.Combobox(top_bar, width=30, state="readonly")
        self.campaign_selector['values'] = [
            "Budtender Welcome Campaign",
            "Win-Back Campaigns (Coming Soon)",
            "VIP Promos (Coming Soon)",
            "Re-Engagement (Coming Soon)"
        ]
        self.campaign_selector.current(0)
        self.campaign_selector.pack(side=tk.LEFT)
        self.campaign_selector.bind('<<ComboboxSelected>>', lambda e: self.load_first_texts())
        
        # Instructions
        instructions = ttk.Label(tab, text="💡 Approve AI-generated first contact messages • Select contact → Review → Approve/Edit/Reject",
                                font=("Arial", 10), foreground="#666")
        instructions.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(5, 0))
        
        # Create PanedWindow for resizable columns
        paned = tk.PanedWindow(tab, orient=tk.HORIZONTAL, sashwidth=5, sashrelief=tk.RAISED, background="#ccc")
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left - Suggested Messages List
        left_frame = ttk.LabelFrame(paned, text="📋 Suggested Messages (Click to Review)", padding="10")
        
        self.first_texts_listbox = tk.Listbox(left_frame, width=40, height=20, font=("Arial", 10))
        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.first_texts_listbox.yview)
        self.first_texts_listbox.config(yscrollcommand=scrollbar.set)
        self.first_texts_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.first_texts_listbox.bind('<<ListboxSelect>>', self.on_first_text_select)
        
        buttons_row = ttk.Frame(left_frame)
        buttons_row.pack(pady=(10, 0), fill=tk.X)
        ttk.Button(buttons_row, text="🔄 Reload Suggestions",
                   command=self.load_first_texts).pack(side=tk.LEFT)
        
        paned.add(left_frame, minsize=250)
        
        # Middle - Suggested Message + Edit Area (RESIZABLE SECTIONS)
        middle_frame = ttk.Frame(paned)
        
        # Vertical PanedWindow for resizable sections
        middle_paned = tk.PanedWindow(middle_frame, orient=tk.VERTICAL, sashwidth=5, sashrelief=tk.RAISED, background="#ccc")
        middle_paned.pack(fill=tk.BOTH, expand=True)
        
        # Section 1: Suggested Message Display
        suggested_frame = ttk.LabelFrame(middle_paned, text="💡 AI Suggested Message", padding="10")
        self.ft_suggested = scrolledtext.ScrolledText(suggested_frame, width=60, height=6,
                                                      wrap=tk.WORD, font=("Arial", 10),
                                                      background="#ffffcc", state=tk.DISABLED)
        self.ft_suggested.pack(fill=tk.BOTH, expand=True)
        middle_paned.add(suggested_frame, minsize=100)
        
        # Section 2: Edit/Reply Area
        edit_frame = ttk.LabelFrame(middle_paned, text="✍️ Your Edit (if needed)", padding="10")
        self.ft_contact_label = ttk.Label(edit_frame, text="Select a contact to review",
                                          font=("Arial", 10, "bold"))
        self.ft_contact_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.ft_edit_text = scrolledtext.ScrolledText(edit_frame, width=60, height=4,
                                                      wrap=tk.WORD, font=("Arial", 10))
        self.ft_edit_text.pack(fill=tk.BOTH, expand=True)
        
        self.ft_char_counter = ttk.Label(edit_frame, text="0 / 160 characters",
                                         font=("Arial", 9), foreground="gray")
        self.ft_char_counter.pack(anchor=tk.E, pady=(5, 0))
        self.ft_edit_text.bind('<KeyRelease>', self.update_ft_char_count)
        middle_paned.add(edit_frame, minsize=80)
        
        # Section 3: Notes/Feedback
        notes_frame = ttk.LabelFrame(middle_paned, text="📝 Notes/Reasoning", padding="10")
        self.ft_feedback = scrolledtext.ScrolledText(notes_frame, width=60, height=3,
                                                     wrap=tk.WORD, font=("Arial", 9),
                                                     background="#f0f8ff")
        self.ft_feedback.pack(fill=tk.BOTH, expand=True)
        middle_paned.add(notes_frame, minsize=60)
        
        # Workflow explanation
        workflow_label = ttk.Label(middle_frame, 
                                   text="ℹ️ 'Approve & Send' marks as approved AND queues to Conductor (sends within 5 seconds)",
                                   font=("Arial", 8), foreground="#0066cc", background="#e3f2fd")
        workflow_label.pack(fill=tk.X, pady=(10, 5))
        
        # Action Buttons
        button_frame = ttk.Frame(middle_frame)
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        ttk.Button(button_frame, text="✅ Approve & Send",
                   command=self.ft_approve, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="✏️ Edit & Approve",
                   command=self.ft_edit_approve).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="❌ Reject",
                   command=self.ft_reject).pack(side=tk.LEFT, padx=5)
        
        paned.add(middle_frame, minsize=400)
        
        # Right - Baseball Card
        right_frame = ttk.LabelFrame(paned, text="⚾ Contact Info", padding="10")
        
        self.ft_baseball_card = scrolledtext.ScrolledText(right_frame, width=45, height=30,
                                                          wrap=tk.WORD, font=("Courier", 9),
                                                          background="#f0f0f0")
        self.ft_baseball_card.pack(fill=tk.BOTH, expand=True)
        self.ft_baseball_card.config(state=tk.DISABLED)
        
        paned.add(right_frame, minsize=300)
        
        # Store current selection
        self.ft_current_suggestion = None
        
        # Scheduler footer (packed at bottom for this tab)
        try:
            footer = ttk.LabelFrame(tab, text="Scheduling Guidelines (Weekly Windows)", padding="6")
            footer.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=(0, 10))
            self._create_weekly_scheduler_controls(footer)
            self._load_scheduler_settings()
        except Exception:
            pass
        
        # Load suggestions
        self.load_first_texts()
    
    def load_first_texts(self):
        """Load all suggested messages (status='SUG') from campaign_messages"""
        try:
            self.first_texts_listbox.delete(0, tk.END)
            
            # Query only SUG status messages (ready for approval) from main SMS database
            response = supabase.table('campaign_messages').select('*').eq('status', 'SUG').order('id').execute()
            suggestions = response.data if response.data else []
            
            if not suggestions:
                self.first_texts_listbox.insert(tk.END, "No suggested messages found")
            else:
                for sug in suggestions:
                    # Extract dispensary from reasoning JSON
                    dispensary = 'Unknown'
                    reasoning = sug.get('reasoning')
                    if reasoning:
                        try:
                            import json
                            if isinstance(reasoning, str):
                                reasoning_json = json.loads(reasoning)
                            elif isinstance(reasoning, dict):
                                reasoning_json = reasoning
                            else:
                                reasoning_json = {}
                            dispensary = reasoning_json.get('dispensary_name', 'Unknown')
                        except:
                            dispensary = 'Unknown'
                    
                    name = sug.get('customer_name', 'Unknown')
                    phone = sug.get('phone_number', '')
                    display = f"○ {dispensary} | {name} | {phone}"
                    self.first_texts_listbox.insert(tk.END, display)
            
            self.ft_suggestions_data = suggestions
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suggestions:\n{str(e)}")
    
    def on_first_text_select(self, event):
        """Handle first text selection"""
        selection = self.first_texts_listbox.curselection()
        if not selection or not hasattr(self, 'ft_suggestions_data'):
            return
        
        try:
            idx = selection[0]
            if idx >= len(self.ft_suggestions_data):
                return
            
            suggestion = self.ft_suggestions_data[idx]
            self.ft_current_suggestion = suggestion
            
            # Display suggested message
            self.ft_suggested.config(state=tk.NORMAL)
            self.ft_suggested.delete('1.0', tk.END)
            
            message = suggestion.get('message_content', '')
            # Decode hex-encoded messages (if any)
            message = decode_hex_message(message)
            strategy = suggestion.get('strategy_type', '')
            confidence = suggestion.get('confidence', '')
            reasoning = suggestion.get('reasoning', '')
            
            display = f"[{strategy.upper()}] {confidence}\n\n{message}\n\n"
            if reasoning:
                display += f"AI Reasoning: {reasoning}"
            
            self.ft_suggested.insert('1.0', display)
            self.ft_suggested.config(state=tk.DISABLED)
            
            # Update contact label
            name = suggestion.get('customer_name', 'Unknown')
            phone = suggestion.get('phone_number', '')
            self.ft_contact_label.config(text=f"📨 First text to: {name} ({phone})")
            
            # Copy message to edit box
            self.ft_edit_text.delete('1.0', tk.END)
            self.ft_edit_text.insert('1.0', message)
            self.update_ft_char_count()
            
            # Clear feedback
            self.ft_feedback.delete('1.0', tk.END)
            
            # Load baseball card (budtender lookup)
            self.load_ft_baseball_card(phone)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load suggestion:\n{str(e)}")
    
    def load_ft_baseball_card(self, phone):
        """Load budtender baseball card for first texts"""
        try:
            phone_10 = ''.join(filter(str.isdigit, phone))[-10:]
            
            self.ft_baseball_card.config(state=tk.NORMAL)
            self.ft_baseball_card.delete('1.0', tk.END)
            
            # Look up budtender in main SMS database
            bt = supabase.table('budtenders').select('*').like('phone', f'%{phone_10}').execute()
            
            if bt.data and len(bt.data) > 0:
                b = bt.data[0]
                name = f"{b.get('first_name', '')} {b.get('last_name', '')}".strip()
                card = f"""
EXTERNAL BUDTENDER (BT)

NAME:        {name}
DISPENSARY:  {b.get('dispensary_name', 'N/A')}
PHONE:       {b.get('phone', 'N/A')}
EMAIL:       {b.get('email', 'N/A')}
POINTS:      {b.get('points', 0):,}

This is a FIRST CONTACT message.
They have not texted us yet.
"""
                self.ft_baseball_card.insert('1.0', card)
            else:
                # Fallback: derive context from current suggestion if available
                suggestion = getattr(self, 'ft_current_suggestion', None) or {}
                name = suggestion.get('customer_name') or 'Unknown'
                # Reasoning can be JSON or text; attempt to parse
                dispensary = ''
                tshirt = ''
                front_logo = ''
                back_logo = ''
                try:
                    import json
                    rs = suggestion.get('reasoning')
                    if isinstance(rs, str):
                        rsj = json.loads(rs)
                    elif isinstance(rs, dict):
                        rsj = rs
                    else:
                        rsj = {}
                    dispensary = rsj.get('dispensary_name') or ''
                    tshirt = rsj.get('tshirt_size') or ''
                    front_logo = rsj.get('front_logo') or ''
                    back_logo = rsj.get('back_logo') or ''
                except Exception:
                    pass
                lines = [
                    "EXTERNAL BUDTENDER (from campaign)",
                    "",
                    f"NAME:        {name}",
                    f"PHONE:       {phone}",
                ]
                if dispensary:
                    lines.append(f"DISPENSARY:  {dispensary}")
                if tshirt or front_logo or back_logo:
                    lines.append("")
                    lines.append("MERCH: Budtender welcome gift details")
                    if tshirt:
                        lines.append(f"  • T-Shirt Size: {tshirt}")
                    if front_logo:
                        lines.append(f"  • Front Logo:  {front_logo}")
                    if back_logo:
                        lines.append(f"  • Sleeve/Back: {back_logo}")
                if not (dispensary or tshirt or front_logo or back_logo):
                    lines.append("")
                    lines.append("No BT record found and no campaign details available.")
                self.ft_baseball_card.insert('1.0', "\n".join(lines))
            
            self.ft_baseball_card.config(state=tk.DISABLED)
            
        except Exception as e:
            print(f"Error loading baseball card: {e}")
    
    def update_ft_char_count(self, event=None):
        """Update character count for first texts"""
        text = self.ft_edit_text.get('1.0', tk.END).strip()
        count = len(text)
        if count > 140:
            self.ft_char_counter.config(text=f"{count} / 160 characters - Getting long!", foreground="orange")
        elif count > 160:
            self.ft_char_counter.config(text=f"{count} / 160 characters - TOO LONG!", foreground="red")
        else:
            self.ft_char_counter.config(text=f"{count} / 160 characters", foreground="gray")
    
    def ft_approve(self):
        """Approve suggested message as-is"""
        if not self.ft_current_suggestion:
            messagebox.showwarning("No Selection", "Please select a contact first")
            return
        
        try:
            suggestion_id = self.ft_current_suggestion.get('id')
            phone = self.ft_current_suggestion.get('phone_number')
            original_message = self.ft_current_suggestion.get('message_content')
            feedback = self.ft_feedback.get('1.0', tk.END).strip()
            
            # 1. Update campaign_messages: SUG -> approved
            supabase.table('campaign_messages').update({
                'status': 'approved',
                'reviewed_by': 'First Texts Tab',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': feedback if feedback else 'Approved as-is'
            }).eq('id', suggestion_id).execute()
            
            # 2. Queue to conductor (SPLIT BY [BUBBLE] MARKERS)
            # Split message into separate SMS bubbles
            bubbles = original_message.split('[BUBBLE]')
            bubbles = [b.strip() for b in bubbles if b.strip()]  # Remove empty/whitespace-only bubbles
            
            if len(bubbles) == 0:
                # No [BUBBLE] markers found, send as single message
                bubbles = [original_message]
            
            # Insert each bubble as separate queued message
            for bubble in bubbles:
                supabase.table('messages').insert({
                    'phone_number': normalize_phone_number(phone),
                    'content': bubble,
                    'status': 'queued',
                    'direction': 'outbound',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }).execute()
            
            # 3. Log to message_feedback (best-effort)
            try:
                supabase.table('message_feedback').insert({
                'campaign_message_id': suggestion_id,
                'suggested_message': original_message,
                'suggested_reasoning': self.ft_current_suggestion.get('reasoning'),
                'suggested_strategy': self.ft_current_suggestion.get('strategy_type'),
                'action': 'approved',
                'final_message': original_message,
                'human_reasoning': feedback if feedback else 'Approved without changes',
                'customer_id': phone,
                'reviewed_by': 'First Texts Tab'
                }).execute()
            except Exception as fe:
                if 'could not find the table' not in str(fe).lower():
                    print(f'message_feedback insert warning: {fe}')
            
            messagebox.showinfo("Approved", f"Message approved and queued!\n\n{len(bubbles)} SMS bubble(s) will be sent within 5-10 seconds.")
            
            # Reload list
            self.load_first_texts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve:\n{str(e)}")
    
    def ft_edit_approve(self):
        """Approve with edits"""
        if not self.ft_current_suggestion:
            messagebox.showwarning("No Selection", "Please select a contact first")
            return
        
        try:
            suggestion_id = self.ft_current_suggestion.get('id')
            phone = self.ft_current_suggestion.get('phone_number')
            original_message = self.ft_current_suggestion.get('message_content')
            edited_message = self.ft_edit_text.get('1.0', tk.END).strip()
            feedback = self.ft_feedback.get('1.0', tk.END).strip()
            
            if not feedback:
                messagebox.showwarning("Feedback Required", "Please explain why you edited the message.\n\nThis helps improve AI suggestions.")
                return
            
            # 1. Update campaign_messages: SUG -> approved
            supabase.table('campaign_messages').update({
                'status': 'approved',
                'reviewed_by': 'First Texts Tab (Edited)',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': feedback
            }).eq('id', suggestion_id).execute()
            
            # 2. Queue EDITED message to conductor (SPLIT BY [BUBBLE] MARKERS)
            # Split edited message into separate SMS bubbles
            bubbles = edited_message.split('[BUBBLE]')
            bubbles = [b.strip() for b in bubbles if b.strip()]  # Remove empty/whitespace-only bubbles
            
            if len(bubbles) == 0:
                # No [BUBBLE] markers found, send as single message
                bubbles = [edited_message]
            
            # Insert each bubble as separate queued message
            for bubble in bubbles:
                supabase.table('messages').insert({
                    'phone_number': normalize_phone_number(phone),
                    'content': bubble,
                    'status': 'queued',
                    'direction': 'outbound',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }).execute()
            
            # 3. Log to message_feedback with BOTH messages (best-effort)
            try:
                supabase.table('message_feedback').insert({
                'campaign_message_id': suggestion_id,
                'suggested_message': original_message,
                'suggested_reasoning': self.ft_current_suggestion.get('reasoning'),
                'suggested_strategy': self.ft_current_suggestion.get('strategy_type'),
                'action': 'edited',
                'final_message': edited_message,
                'human_reasoning': feedback,
                'customer_id': phone,
                'reviewed_by': 'First Texts Tab'
                }).execute()
            except Exception as fe:
                if 'could not find the table' not in str(fe).lower():
                    print(f'message_feedback insert warning: {fe}')
            
            messagebox.showinfo("Approved with Edits", f"Edited message approved and queued!\n\n{len(bubbles)} SMS bubble(s) will be sent within 5-10 seconds.")
            
            # Reload list
            self.load_first_texts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to approve edits:\n{str(e)}")
    
    def ft_reject(self):
        """Reject suggested message"""
        if not self.ft_current_suggestion:
            messagebox.showwarning("No Selection", "Please select a contact first")
            return
        
        feedback = self.ft_feedback.get('1.0', tk.END).strip()
        if not feedback:
            messagebox.showwarning("Feedback Required", "Please explain why you're rejecting.\n\nThis is critical for AI training!")
            return
        
        try:
            suggestion_id = self.ft_current_suggestion.get('id')
            phone = self.ft_current_suggestion.get('phone_number')
            message = self.ft_current_suggestion.get('message_content')
            
            # 1. Update campaign_messages: SUG -> rejected
            supabase.table('campaign_messages').update({
                'status': 'rejected',
                'reviewed_by': 'First Texts Tab',
                'reviewed_at': datetime.now(timezone.utc).isoformat(),
                'feedback_notes': feedback
            }).eq('id', suggestion_id).execute()
            
            # 2. Log to message_feedback (best-effort)
            try:
                supabase.table('message_feedback').insert({
                'campaign_message_id': suggestion_id,
                'suggested_message': message,
                'suggested_reasoning': self.ft_current_suggestion.get('reasoning'),
                'suggested_strategy': self.ft_current_suggestion.get('strategy_type'),
                'action': 'rejected',
                'final_message': None,
                'human_reasoning': feedback,
                'customer_id': phone,
                'reviewed_by': 'First Texts Tab'
                }).execute()
            except Exception as fe:
                if 'could not find the table' not in str(fe).lower():
                    print(f'message_feedback insert warning: {fe}')
            
            messagebox.showinfo("Rejected", "Message rejected and feedback saved for AI training.")
            
            # Reload list
            self.load_first_texts()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to reject:\n{str(e)}")

    def _save_bt_config(self, url: str, key: str, campaign_table: str, bt_table: str) -> None:
        try:
            cfg = {
                "url": url,
                "key": key,
                "campaign_table": campaign_table,
                "budtender_table": bt_table,
            }
            with open(os.path.join(os.path.dirname(__file__), 'bt_config.json'), 'w', encoding='utf-8') as f:
                json.dump(cfg, f, indent=2)
        except Exception:
            pass

    def _load_bt_config_if_any(self) -> None:
        global BT_URL, BT_KEY, BT_CAMPAIGN_TABLE, BT_BUDTENDER_TABLE, bt_supabase
        try:
            cfg_path = os.path.join(os.path.dirname(__file__), 'bt_config.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    cfg = json.load(f)
                BT_URL = cfg.get('url') or BT_URL
                BT_KEY = cfg.get('key') or BT_KEY
                BT_CAMPAIGN_TABLE = cfg.get('campaign_table') or BT_CAMPAIGN_TABLE
                BT_BUDTENDER_TABLE = cfg.get('budtender_table') or BT_BUDTENDER_TABLE
                bt_supabase = create_client(BT_URL, BT_KEY)
        except Exception:
            pass

    def configure_bt_database(self):
        """Open a small dialog to set BT Supabase credentials and tables"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Configure Budtender Database")
        dialog.transient(self.root)
        dialog.grab_set()
        frm = ttk.Frame(dialog, padding=12)
        frm.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Supabase URL").grid(row=0, column=0, sticky=tk.W, pady=4)
        url_entry = ttk.Entry(frm, width=60)
        url_entry.grid(row=0, column=1, sticky=tk.W)
        url_entry.insert(0, BT_URL)

        ttk.Label(frm, text="Supabase Key").grid(row=1, column=0, sticky=tk.W, pady=4)
        key_entry = ttk.Entry(frm, width=60, show="*")
        key_entry.grid(row=1, column=1, sticky=tk.W)
        key_entry.insert(0, BT_KEY)

        ttk.Label(frm, text="Campaign Table").grid(row=2, column=0, sticky=tk.W, pady=4)
        camp_entry = ttk.Entry(frm, width=40)
        camp_entry.grid(row=2, column=1, sticky=tk.W)
        camp_entry.insert(0, BT_CAMPAIGN_TABLE)

        ttk.Label(frm, text="Budtenders Table").grid(row=3, column=0, sticky=tk.W, pady=4)
        bt_entry = ttk.Entry(frm, width=40)
        bt_entry.grid(row=3, column=1, sticky=tk.W)
        bt_entry.insert(0, BT_BUDTENDER_TABLE)

        def on_save():
            nonlocal url_entry, key_entry, camp_entry, bt_entry
            url = url_entry.get().strip()
            key = key_entry.get().strip()
            camp = camp_entry.get().strip() or 'campaign_messages'
            bt_t = bt_entry.get().strip() or 'budtenders'
            if not url or not key:
                messagebox.showwarning("Missing", "Please enter Supabase URL and Key")
                return
            # Persist and rewire globals
            self._save_bt_config(url, key, camp, bt_t)
            try:
                global BT_URL, BT_KEY, BT_CAMPAIGN_TABLE, BT_BUDTENDER_TABLE, bt_supabase
                BT_URL, BT_KEY = url, key
                BT_CAMPAIGN_TABLE, BT_BUDTENDER_TABLE = camp, bt_t
                bt_supabase = create_client(BT_URL, BT_KEY)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to initialize client: {e}")
                return
            dialog.destroy()
            self.load_first_texts()

        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        ttk.Button(btns, text="Save", command=on_save).pack(side=tk.RIGHT)
        ttk.Button(btns, text="Cancel", command=dialog.destroy).pack(side=tk.RIGHT, padx=(0, 6))
    
    def _create_suggested_tab(self):
        """Create MASTER Campaign View - shows ALL campaign messages (SUG, APR, SCH)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="🎯 Campaign Master")
        
        # Title
        title_frame = ttk.Frame(tab)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        ttk.Label(title_frame, text="Campaign Master View (All Statuses)", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        btn_container = ttk.Frame(title_frame)
        btn_container.pack(side=tk.RIGHT)
        ttk.Button(btn_container, text="🔄 Refresh", command=self.load_suggested_overview).pack(side=tk.LEFT, padx=2)
        
        # Schedule controls
        ttk.Label(btn_container, text="Schedule:").pack(side=tk.LEFT, padx=(10, 2))
        self.schedule_count_entry = ttk.Entry(btn_container, width=5)
        self.schedule_count_entry.pack(side=tk.LEFT, padx=2)
        self.schedule_count_entry.insert(0, "3")
        ttk.Button(btn_container, text="📅 Schedule", command=self.schedule_n_approved).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_container, text="📅 Schedule ALL", command=self.schedule_all_approved).pack(side=tk.LEFT, padx=2)
        
        # Stats with selection counter
        stats_frame = ttk.Frame(tab)
        stats_frame.grid(row=1, column=0, pady=5, padx=10, sticky=tk.W)
        
        self.sug_stats_label = ttk.Label(stats_frame, text="Loading...", font=("Arial", 10))
        self.sug_stats_label.pack(side=tk.LEFT)
        
        self.sug_selection_label = ttk.Label(stats_frame, text="", font=("Arial", 10, "bold"), foreground="blue")
        self.sug_selection_label.pack(side=tk.LEFT, padx=10)
        
        # Treeview - MASTER VIEW with all columns
        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        
        columns = ("status", "name", "phone", "dispensary", "campaign", "scheduled_time", "message_full")
        self.sug_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        try:
            self.sug_tree.configure(style='Small.Treeview')
        except Exception:
            pass
        
        # Sortable columns - bind sorting
        self.sug_tree.heading("status", text="Status ↕", command=lambda: self.sort_tree_column(self.sug_tree, "status", False))
        self.sug_tree.heading("name", text="Name ↕", command=lambda: self.sort_tree_column(self.sug_tree, "name", False))
        self.sug_tree.heading("phone", text="Phone ↕", command=lambda: self.sort_tree_column(self.sug_tree, "phone", False))
        self.sug_tree.heading("dispensary", text="Dispensary ↕", command=lambda: self.sort_tree_column(self.sug_tree, "dispensary", False))
        self.sug_tree.heading("campaign", text="Campaign ↕", command=lambda: self.sort_tree_column(self.sug_tree, "campaign", False))
        self.sug_tree.heading("scheduled_time", text="Scheduled For (PST) ↕", command=lambda: self.sort_tree_column(self.sug_tree, "scheduled_time", False))
        self.sug_tree.heading("message_full", text="Message ↕", command=lambda: self.sort_tree_column(self.sug_tree, "message_full", False))
        
        self.sug_tree.column("status", width=60)
        self.sug_tree.column("name", width=110)
        self.sug_tree.column("phone", width=95)
        self.sug_tree.column("dispensary", width=110)
        self.sug_tree.column("campaign", width=140)
        self.sug_tree.column("scheduled_time", width=140)
        self.sug_tree.column("message_full", width=800, stretch=True)  # Wider for message content
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.sug_tree.xview)
        self.sug_tree.configure(xscrollcommand=h_scrollbar.set)
        
        # Vertical scrollbar
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sug_tree.yview)
        self.sug_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.sug_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        
        # Double-click to open in Reply tab
        self.sug_tree.bind('<Double-Button-1>', self.open_campaign_in_reply)
        # Right-click context menu for bulk approve
        self.sug_tree.bind('<Button-3>', self._show_sug_context_menu)
        # Update selection counter
        self.sug_tree.bind('<<TreeviewSelect>>', self._update_sug_selection_count)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, pady=10)
        ttk.Label(btn_frame, text="Double-click to open | Enter number + Schedule (e.g., 10), or Schedule ALL | Status: SUG=Suggested, APR=Approved, SCH=Scheduled", foreground="gray").pack()
        
        # Scheduler footer
        try:
            footer = ttk.LabelFrame(tab, text="Scheduling Guidelines (Weekly Windows)", padding="6")
            footer.grid(row=5, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
            self._create_weekly_scheduler_controls(footer)
            self._load_scheduler_settings()
        except Exception:
            pass
        
        # Message width slider
        slider_frame = ttk.Frame(tab)
        slider_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        ttk.Label(slider_frame, text="Message Column Width").pack(side=tk.LEFT)
        self.sug_msg_width = tk.IntVar(value=800)
        width_scale = ttk.Scale(slider_frame, from_=400, to=1400, orient=tk.HORIZONTAL,
                                variable=self.sug_msg_width, command=lambda v: self._resize_sug_message(int(float(v))))
        width_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        # Load data
        self.load_suggested_overview()
    
    def _create_approved_tab(self):
        """Create Approved Messages tab - shows APR status (ready to schedule)"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="✅ Approved")
        
        # Title
        title_frame = ttk.Frame(tab)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        ttk.Label(title_frame, text="Approved Messages (APR)", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        btn_container = ttk.Frame(title_frame)
        btn_container.pack(side=tk.RIGHT)
        ttk.Button(btn_container, text="🔄 Refresh", command=self.load_approved_overview).pack(side=tk.LEFT, padx=2)
        
        # Schedule controls (use same entry as master tab)
        ttk.Label(btn_container, text="Schedule:").pack(side=tk.LEFT, padx=(10, 2))
        self.apr_schedule_entry = ttk.Entry(btn_container, width=5)
        self.apr_schedule_entry.pack(side=tk.LEFT, padx=2)
        self.apr_schedule_entry.insert(0, "3")
        ttk.Button(btn_container, text="📅 Schedule", command=self.schedule_n_approved).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_container, text="📅 Schedule ALL", command=self.schedule_all_approved).pack(side=tk.LEFT, padx=2)
        
        # Stats
        self.apr_stats_label = ttk.Label(tab, text="Loading...", font=("Arial", 10))
        self.apr_stats_label.grid(row=1, column=0, pady=5, padx=10, sticky=tk.W)
        
        # Treeview
        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        
        columns = ("name", "phone", "dispensary", "campaign", "message_full")
        self.apr_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        try:
            self.apr_tree.configure(style='Small.Treeview')
        except Exception:
            pass
        
        # Sortable columns
        self.apr_tree.heading("name", text="Name ↕", command=lambda: self.sort_tree_column(self.apr_tree, "name", False))
        self.apr_tree.heading("phone", text="Phone ↕", command=lambda: self.sort_tree_column(self.apr_tree, "phone", False))
        self.apr_tree.heading("dispensary", text="Dispensary ↕", command=lambda: self.sort_tree_column(self.apr_tree, "dispensary", False))
        self.apr_tree.heading("campaign", text="Campaign ↕", command=lambda: self.sort_tree_column(self.apr_tree, "campaign", False))
        self.apr_tree.heading("message_full", text="Message ↕", command=lambda: self.sort_tree_column(self.apr_tree, "message_full", False))
        
        self.apr_tree.column("name", width=120)
        self.apr_tree.column("phone", width=95)
        self.apr_tree.column("dispensary", width=110)
        self.apr_tree.column("campaign", width=140)
        self.apr_tree.column("message_full", width=800, stretch=True)
        
        # Scrollbars
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.apr_tree.xview)
        self.apr_tree.configure(xscrollcommand=h_scrollbar.set)
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.apr_tree.yview)
        self.apr_tree.configure(yscrollcommand=v_scrollbar.set)
        
        self.apr_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scrollbar.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        
        # Double-click to open
        self.apr_tree.bind('<Double-Button-1>', self.open_apr_in_reply)
        # Right-click context menu
        self.apr_tree.bind('<Button-3>', self._show_apr_context_menu)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, pady=10)
        ttk.Label(btn_frame, text="Double-click to open | Enter number + Schedule, or Schedule ALL", foreground="gray").pack()
        
        # Scheduler footer
        try:
            footer = ttk.LabelFrame(tab, text="Scheduling Guidelines (Weekly Windows)", padding="6")
            footer.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
            self._create_weekly_scheduler_controls(footer)
            self._load_scheduler_settings()
        except Exception:
            pass
        
        # Load data
        self.load_approved_overview()
    
    def _create_scheduled_tab(self):
        """Create Scheduled Messages tab - shows upcoming campaign sends"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="📅 Scheduled")
        
        # Title
        title_frame = ttk.Frame(tab)
        title_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=10, padx=10)
        ttk.Label(title_frame, text="Scheduled Campaign Messages", font=("Arial", 14, "bold")).pack(side=tk.LEFT)
        ttk.Button(title_frame, text="🔄 Refresh", command=self.load_scheduled).pack(side=tk.RIGHT)
        
        # Stats
        self.sched_stats_label = ttk.Label(tab, text="Loading...", font=("Arial", 10))
        self.sched_stats_label.grid(row=1, column=0, pady=5, padx=10, sticky=tk.W)
        
        # Treeview for scheduled messages
        tree_frame = ttk.Frame(tab)
        tree_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10, padx=10)
        
        columns = ("name", "phone", "dispensary", "scheduled_time", "message_preview")
        self.sched_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=20)
        try:
            self.sched_tree.configure(style='Small.Treeview')
        except Exception:
            pass
        
        # Sortable columns
        self.sched_tree.heading("name", text="Name ↕", command=lambda: self.sort_tree_column(self.sched_tree, "name", False))
        self.sched_tree.heading("phone", text="Phone ↕", command=lambda: self.sort_tree_column(self.sched_tree, "phone", False))
        self.sched_tree.heading("dispensary", text="Dispensary ↕", command=lambda: self.sort_tree_column(self.sched_tree, "dispensary", False))
        self.sched_tree.heading("scheduled_time", text="Scheduled For (PST) ↕", command=lambda: self.sort_tree_column(self.sched_tree, "scheduled_time", False))
        self.sched_tree.heading("message_preview", text="Message Preview ↕", command=lambda: self.sort_tree_column(self.sched_tree, "message_preview", False))
        
        self.sched_tree.column("name", width=150)
        self.sched_tree.column("phone", width=120)
        self.sched_tree.column("dispensary", width=150)
        self.sched_tree.column("scheduled_time", width=180)
        self.sched_tree.column("message_preview", width=300)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.sched_tree.yview)
        self.sched_tree.configure(yscrollcommand=scrollbar.set)
        
        self.sched_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        tab.columnconfigure(0, weight=1)
        tab.rowconfigure(2, weight=1)
        
        # Double-click to open
        self.sched_tree.bind('<Double-Button-1>', self.open_scheduled_in_reply)
        # Right-click context menu
        self.sched_tree.bind('<Button-3>', self._show_sched_context_menu)
        
        # Buttons
        btn_frame = ttk.Frame(tab)
        btn_frame.grid(row=3, column=0, pady=10)
        ttk.Button(btn_frame, text="❌ Cancel Selected", command=self.cancel_scheduled).pack(side=tk.LEFT, padx=5)
        
        # Scheduling Guidelines (weekly windows)
        guide = ttk.LabelFrame(tab, text="Scheduling Guidelines (Weekly Windows)", padding="10")
        guide.grid(row=4, column=0, sticky=(tk.W, tk.E), padx=10, pady=(0, 10))
        self._create_weekly_scheduler_controls(guide)
        
        # Load scheduled messages
        self.load_scheduled()
        # Load scheduler settings after UI exists
        try:
            self._load_scheduler_settings()
        except Exception:
            pass
    
    def load_scheduled(self):
        """Load scheduled messages from campaign_messages table"""
        try:
            # Get scheduled messages
            response = crm_supabase.table('campaign_messages').select('*').eq('status', 'SCH').order('scheduled_for').execute()
            
            # Clear tree
            for item in self.sched_tree.get_children():
                self.sched_tree.delete(item)
            
            if not response.data:
                self.sched_stats_label.config(text="No scheduled messages")
                return
            
            messages = response.data
            self.sched_stats_label.config(text=f"Total scheduled: {len(messages)} messages")
            
            # Populate tree
            for msg in messages:
                name = msg.get('customer_name', 'Unknown')
                phone = msg.get('phone_number', '')
                scheduled = msg.get('scheduled_for', '')
                content = msg.get('message_content', '')
                # Decode hex-encoded messages (if any)
                content = decode_hex_message(content)
                
                # Convert to PST
                try:
                    dt = parser.isoparse(scheduled)
                    pst = tz.gettz('America/Los_Angeles')
                    dt_pst = dt.astimezone(pst)
                    time_str = dt_pst.strftime('%I:%M:%S %p %b %d')
                except:
                    time_str = scheduled
                
                # Get dispensary from reasoning
                dispensary = 'Unknown'
                try:
                    reasoning = msg.get('reasoning', '{}')
                    reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
                    dispensary = reasoning_data.get('dispensary_name', 'Unknown')
                except:
                    pass
                
                # Message preview
                preview = content[:50] + '...' if len(content) > 50 else content
                preview = preview.replace('\n', ' ')
                
                self.sched_tree.insert('', 'end', values=(name, phone, dispensary, time_str, preview), tags=(str(msg.get('id')),))
        
        except Exception as e:
            self.sched_stats_label.config(text=f"Error: {e}")
            print(f"Error loading scheduled: {e}")
            import traceback
            traceback.print_exc()
    
    # -------------------------
    # Scheduling guidelines UI
    # -------------------------
    def _create_weekly_scheduler_controls(self, parent):
        """Create Monday-Sunday start/end controls with dates and 'today' highlight."""
        from datetime import datetime, timedelta
        self.schedule_entries = {}
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        row0 = ttk.Frame(parent)
        row0.pack(fill=tk.X)
        
        # Compute the next upcoming date for each named weekday, keeping Monday..Sunday order
        next_dates = self._compute_next_week_dates()
        today_name = datetime.now().strftime("%A")
        
        for idx, day in enumerate(days):
            col = ttk.Frame(row0, padding=(5, 5))
            col.pack(side=tk.LEFT, expand=True, fill=tk.X)
            
            date_str = next_dates.get(day, "")
            lab = ttk.Label(col, text=f"{day}\n{date_str}", font=("Arial", 9, "bold"))
            if day == today_name:
                try:
                    lab.configure(foreground="green")
                except Exception:
                    pass
            lab.pack()
            
            start_var = tk.StringVar(value="")
            end_var = tk.StringVar(value="")
            start = ttk.Entry(col, width=8, textvariable=start_var)
            end = ttk.Entry(col, width=8, textvariable=end_var)
            ttk.Label(col, text="Start").pack()
            start.pack()
            ttk.Label(col, text="End").pack()
            end.pack()
            
            self.schedule_entries[day] = {"start": start, "end": end, "label": lab}
        
        # Controls row
        ctrl = ttk.Frame(parent)
        ctrl.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(ctrl, text="💾 Save Windows", command=self._save_scheduler_settings).pack(side=tk.LEFT)
        ttk.Button(ctrl, text="📅 Use Today", command=self._refresh_week_dates).pack(side=tk.LEFT, padx=10)
    
    def _compute_next_week_dates(self):
        """Return mapping of weekday name -> 'MMM DD' for the next occurrence from today forward."""
        from datetime import datetime, timedelta
        today = datetime.now()
        # Map weekday index to name in Monday..Sunday order
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        result = {}
        for i, name in enumerate(days):
            # Python Monday=0...Sunday=6
            target = i  # weekday index
            delta = (target - today.weekday()) % 7
            day_dt = today + timedelta(days=delta)
            result[name] = day_dt.strftime("%b %d")
        return result
    
    def _refresh_week_dates(self):
        """Refresh the labels to reflect current dates and highlight today's day."""
        from datetime import datetime
        next_dates = self._compute_next_week_dates()
        today_name = datetime.now().strftime("%A")
        for day, parts in self.schedule_entries.items():
            lab = parts.get("label")
            if not lab:
                continue
            try:
                lab.configure(text=f"{day}\n{next_dates.get(day, '')}")
                lab.configure(foreground="green" if day == today_name else "black")
            except Exception:
                pass
    
    def _load_scheduler_settings(self):
        """Load windows from Supabase (scheduler_windows) or local JSON fallback."""
        import json as _json
        from datetime import datetime
        # Defaults
        defaults = {
            "Monday": {"start": "09:00", "end": "20:00"},
            "Tuesday": {"start": "09:00", "end": "20:00"},
            "Wednesday": {"start": "09:00", "end": "20:00"},
            "Thursday": {"start": "09:00", "end": "20:00"},
            "Friday": {"start": "09:00", "end": "20:00"},
            "Saturday": {"start": "10:00", "end": "18:00"},
            "Sunday": {"start": "10:00", "end": "16:00"},
        }
        windows = defaults
        # Try Supabase first
        try:
            resp = crm_supabase.table('scheduler_windows').select('*').eq('id', 'default').limit(1).execute()
            if resp.data:
                row = resp.data[0]
                data = row.get('windows') or {}
                if isinstance(data, str):
                    data = _json.loads(data)
                if isinstance(data, dict):
                    windows = {**defaults, **data}
        except Exception as e:
            # Fallback to local file
            try:
                with open('scheduler_windows.json', 'r', encoding='utf-8') as f:
                    windows = {**defaults, **_json.load(f)}
            except Exception:
                pass
        # Populate UI
        for day, vals in windows.items():
            if day in self.schedule_entries:
                self.schedule_entries[day]['start'].delete(0, tk.END)
                self.schedule_entries[day]['start'].insert(0, vals.get('start', ''))
                self.schedule_entries[day]['end'].delete(0, tk.END)
                self.schedule_entries[day]['end'].insert(0, vals.get('end', ''))
        # Refresh labels/highlight
        self._refresh_week_dates()
    
    def _save_scheduler_settings(self):
        """Persist windows to Supabase table scheduler_windows (id='default'); fallback to local file."""
        import json as _json
        from datetime import datetime, timezone
        windows = {}
        for day, parts in self.schedule_entries.items():
            start = parts['start'].get().strip()
            end = parts['end'].get().strip()
            windows[day] = {"start": start, "end": end}
        # Try Supabase upsert
        try:
            crm_supabase.table('scheduler_windows').upsert({
                'id': 'default',
                'windows': windows,
                'updated_at': datetime.now(timezone.utc).isoformat()
            }).execute()
            messagebox.showinfo("Saved", "Scheduling windows saved to database.")
        except Exception as e:
            # Fallback to local JSON
            try:
                with open('scheduler_windows.json', 'w', encoding='utf-8') as f:
                    _json.dump(windows, f, indent=2)
                messagebox.showinfo("Saved", "Scheduling windows saved locally (scheduler_windows.json).")
            except Exception as e2:
                messagebox.showerror("Error", f"Failed to save settings:\n{e2}")
    
    def cancel_scheduled(self):
        """Cancel selected scheduled message"""
        selection = self.sched_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a message to cancel")
            return
        
        if not messagebox.askyesno("Confirm", "Cancel this scheduled message?"):
            return
        
        try:
            item = self.sched_tree.item(selection[0])
            msg_id = item['tags'][0]
            
            # Update status from SCH to cancelled
            crm_supabase.table('campaign_messages').update({
                'status': 'cancelled',
                'scheduled_for': None
            }).eq('id', msg_id).execute()
            
            messagebox.showinfo("Success", "Message cancelled")
            self.load_scheduled()
            self.load_suggested_overview()  # Refresh master view
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel: {e}")
    
    def open_scheduled_in_reply(self, event):
        """Double-click handler for scheduled messages - open popup editor"""
        self.edit_message_popup(self.sched_tree, table_name=BT_CAMPAIGN_TABLE)
    
    def load_suggested_overview(self):
        """Load ALL campaign messages (SUG, APR, SCH, sent) - MASTER VIEW"""
        try:
            # Get ALL campaign messages
            response = crm_supabase.table('campaign_messages').select('*').order('generated_at').execute()
            
            # Clear tree
            for item in self.sug_tree.get_children():
                self.sug_tree.delete(item)
            
            if not response.data:
                self.sug_stats_label.config(text="No campaign messages")
                return
            
            messages = response.data
            
            # Count by status
            counts = {}
            for msg in messages:
                status = msg.get('status', 'unknown')
                counts[status] = counts.get(status, 0) + 1
            
            stats_text = f"Total: {len(messages)} | "
            stats_text += " | ".join([f"{k}: {v}" for k, v in sorted(counts.items())])
            self.sug_stats_label.config(text=stats_text)
            
            # Populate tree
            for msg in messages:
                status = msg.get('status', '?')
                name = msg.get('customer_name', 'Unknown')
                phone = msg.get('phone_number', '')
                content = msg.get('message_content', '')
                # Decode hex-encoded messages (if any)
                content = decode_hex_message(content)
                campaign = msg.get('campaign_name', 'Unknown')
                scheduled = msg.get('scheduled_for', '')
                
                # Get dispensary
                dispensary = 'Unknown'
                try:
                    reasoning = msg.get('reasoning', '{}')
                    reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
                    dispensary = reasoning_data.get('dispensary_name', 'Unknown')
                except:
                    pass
                
                # Format scheduled time
                scheduled_str = ''
                if scheduled:
                    try:
                        dt = parser.isoparse(scheduled)
                        pst = tz.gettz('America/Los_Angeles')
                        dt_pst = dt.astimezone(pst)
                        scheduled_str = dt_pst.strftime('%I:%M %p %b %d')
                    except:
                        scheduled_str = scheduled
                
                # Full message (no truncation, clean formatting)
                # Replace double newlines with single space, single newlines with space
                full_msg = content.replace('\n\n', ' ').replace('\n', ' ').strip()
                
                # Color code by status
                tag = f"status_{status}"
                self.sug_tree.insert('', 'end', 
                                    values=(status, name, phone, dispensary, campaign, scheduled_str, full_msg), 
                                    tags=(str(msg.get('id')), tag))
            
            # Configure tag colors
            self.sug_tree.tag_configure('status_SUG', background='#FFF9E6')  # Light yellow
            self.sug_tree.tag_configure('status_APR', background='#E6F7FF')  # Light blue
            self.sug_tree.tag_configure('status_SCH', background='#E6FFE6')  # Light green
            self.sug_tree.tag_configure('status_sent', background='#C8E6C9')  # Green (done!)
        
        except Exception as e:
            self.sug_stats_label.config(text=f"Error: {e}")
            print(f"Error loading campaign master: {e}")
            import traceback
            traceback.print_exc()
    
    def edit_message_popup(self, tree, table_name="campaign_messages"):
        """Show popup editor for message (double-click handler)"""
        selection = tree.selection()
        if not selection:
            return
        
        try:
            item = tree.item(selection[0])
            values = item['values']
            tags = tree.item(selection[0], 'tags')
            record_id = tags[0] if tags else None
            
            # Extract data based on tree type
            if tree == self.sug_tree:
                # columns: status, name, phone, dispensary, campaign, scheduled_time, message_full
                name, phone, dispensary, message = values[1], values[2], values[3], values[6]
            elif tree == self.apr_tree:
                # columns: name, phone, dispensary, campaign, message_full
                name, phone, dispensary, message = values[0], values[1], values[2], values[4]
            elif tree == self.sched_tree:
                # columns: name, phone, dispensary, scheduled_time, message_preview
                name, phone, dispensary, message = values[0], values[1], values[2], values[4]
            else:
                return
            
            # Get actual full message from database (in case preview was truncated)
            try:
                if record_id:
                    result = bt_supabase.table(table_name).select('id, content').eq('id', record_id).single().execute()
                    if result.data:
                        message = result.data['content']
            except:
                pass  # Use values from tree if query fails
            
            # Create popup dialog
            popup = tk.Toplevel(self.root)
            popup.title(f"Edit Message - {name} ({phone})")
            popup.geometry("700x600")  # Taller to show all controls
            popup.transient(self.root)
            popup.grab_set()
            
            # Info label with dispensary
            info_text = f"Editing message for: {name}"
            if dispensary:
                info_text += f" - {dispensary}"
            info_text += f" ({phone})"
            info_label = ttk.Label(popup, text=info_text, font=("Arial", 10, "bold"))
            info_label.pack(pady=10, padx=10)
            
            # Text editor
            text_frame = ttk.Frame(popup)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
            text_scroll = ttk.Scrollbar(text_frame)
            text_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            
            text_editor = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=text_scroll.set, font=("Arial", 11))
            text_editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            text_scroll.config(command=text_editor.yview)
            
            text_editor.insert('1.0', message)
            
            # Character count
            char_count_label = ttk.Label(popup, text=f"Characters: {len(message)}", foreground="gray")
            char_count_label.pack(pady=5)
            
            def update_char_count(event=None):
                count = len(text_editor.get('1.0', 'end-1c'))
                char_count_label.config(text=f"Characters: {count}")
            
            text_editor.bind('<KeyRelease>', update_char_count)
            
            # Buttons
            btn_frame = ttk.Frame(popup)
            btn_frame.pack(pady=10)
            
            def save_changes():
                new_content = text_editor.get('1.0', 'end-1c').strip()
                if not new_content:
                    messagebox.showerror("Error", "Message cannot be empty")
                    return
                
                try:
                    # Update in database
                    if not record_id:
                        raise ValueError("No record ID found")
                    bt_supabase.table(table_name).update({'content': new_content}).eq('id', record_id).execute()
                    messagebox.showinfo("Success", "Message updated successfully!")
                    popup.destroy()
                    
                    # Refresh the appropriate view
                    if tree == self.sug_tree:
                        self.load_suggested_overview()
                    elif tree == self.apr_tree:
                        self.load_approved_overview()
                    elif tree == self.sched_tree:
                        self.load_scheduled_overview()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save: {e}")
            
            def cancel():
                popup.destroy()
            
            ttk.Button(btn_frame, text="💾 Save Changes", command=save_changes).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="❌ Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
            
            # Focus on text editor
            text_editor.focus_set()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open editor: {e}")
            import traceback
            traceback.print_exc()
    
    def sort_tree_column(self, tree, col, reverse):
        """Sort tree contents by column (case-insensitive, strips whitespace)"""
        try:
            # Get all items with normalized sort keys
            items = []
            for item in tree.get_children(''):
                val = tree.set(item, col)
                # Normalize for sorting: strip whitespace, convert to lowercase
                sort_key = str(val).strip().lower() if val else ''
                items.append((sort_key, val, item))
            
            # Sort items by normalized key
            items.sort(key=lambda x: x[0], reverse=reverse)
            
            # Rearrange items in tree
            for index, (sort_key, val, item) in enumerate(items):
                tree.move(item, '', index)
            
            # Update heading to toggle sort direction
            current_text = tree.heading(col, 'text')
            base_text = current_text.replace(' ↑', '').replace(' ↓', '').replace(' ↕', '')
            
            if reverse:
                new_text = f"{base_text} ↓"
            else:
                new_text = f"{base_text} ↑"
            
            tree.heading(col, text=new_text, command=lambda: self.sort_tree_column(tree, col, not reverse))
            
        except Exception as e:
            print(f"Sort error: {e}")
    
    def open_campaign_in_reply(self, event):
        """Double-click handler for suggested messages - open popup editor"""
        self.edit_message_popup(self.sug_tree, table_name=BT_CAMPAIGN_TABLE)
    
    def load_approved_overview(self):
        """Load APR messages"""
        try:
            response = crm_supabase.table('campaign_messages').select('*').eq('status', 'APR').order('generated_at').execute()
            
            # Clear tree
            for item in self.apr_tree.get_children():
                self.apr_tree.delete(item)
            
            if not response.data:
                self.apr_stats_label.config(text="No approved messages (ready to schedule)")
                return
            
            messages = response.data
            self.apr_stats_label.config(text=f"Total approved: {len(messages)} messages (ready to schedule)")
            
            # Populate tree
            for msg in messages:
                name = msg.get('customer_name', 'Unknown')
                phone = msg.get('phone_number', '')
                content = msg.get('message_content', '')
                # Decode hex-encoded messages (if any)
                content = decode_hex_message(content)
                campaign = msg.get('campaign_name', 'Unknown')
                
                # Get dispensary
                dispensary = 'Unknown'
                try:
                    reasoning = msg.get('reasoning', '{}')
                    reasoning_data = json.loads(reasoning) if isinstance(reasoning, str) else reasoning
                    dispensary = reasoning_data.get('dispensary_name', 'Unknown')
                except:
                    pass
                
                # Full message (no truncation, clean formatting)
                full_msg = content.replace('\n\n', ' ').replace('\n', ' ').strip()
                
                self.apr_tree.insert('', 'end', values=(name, phone, dispensary, campaign, full_msg), tags=(str(msg.get('id')),))
        
        except Exception as e:
            self.apr_stats_label.config(text=f"Error: {e}")
            print(f"Error loading APR: {e}")
            import traceback
            traceback.print_exc()
    
    def open_apr_in_reply(self, event):
        """Double-click handler for approved messages - open popup editor"""
        self.edit_message_popup(self.apr_tree, table_name=BT_CAMPAIGN_TABLE)
    
    def schedule_n_approved(self):
        """Schedule N APR messages (from input box)"""
        # Get count from entry box
        try:
            count_str = self.schedule_count_entry.get() if hasattr(self, 'schedule_count_entry') else self.apr_schedule_entry.get()
            count = int(count_str)
            if count <= 0:
                messagebox.showwarning("Invalid", "Please enter a number greater than 0")
                return
        except ValueError:
            messagebox.showwarning("Invalid", "Please enter a valid number")
            return
        
        if not messagebox.askyesno("Schedule Messages", 
                                   f"Schedule {count} messages?\n\n"
                                   "They will be spaced 5-7 minutes apart."):
            return
        
        try:
            # Call Supabase function with batch size
            result = crm_supabase.rpc('schedule_approved_messages', {'batch_size': count}).execute()
            
            if result.data and len(result.data) > 0:
                scheduled_count = result.data[0].get('scheduled_count', 0)
                next_time = result.data[0].get('next_send_time', '')
                
                messagebox.showinfo("Success", 
                                  f"Scheduled {scheduled_count} messages!\n\n"
                                  f"Last scheduled for: {next_time}\n\n"
                                  f"Check 'Scheduled' tab to see timeline.")
                
                # Refresh all campaign tabs
                self.load_suggested_overview()  # Master view
                self.load_approved_overview()   # APR view
                self.load_scheduled()           # SCH view
            else:
                messagebox.showinfo("Done", "No messages to schedule")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule: {e}")
            import traceback
            traceback.print_exc()
    
    def schedule_all_approved(self):
        """Schedule ALL APR messages (no limit)"""
        # Get current APR count
        try:
            response = crm_supabase.table('campaign_messages').select('id', count='exact').eq('status', 'APR').execute()
            apr_count = response.count if hasattr(response, 'count') else 0
        except:
            apr_count = "unknown"
        
        if not messagebox.askyesno("Schedule ALL Messages", 
                                   f"Schedule ALL {apr_count} approved messages?\n\n"
                                   "They will be spaced 5-7 minutes apart.\n"
                                   "This may take a while!"):
            return
        
        try:
            # Call Supabase function with batch_size=0 (means ALL)
            result = crm_supabase.rpc('schedule_approved_messages', {'batch_size': 0}).execute()
            
            if result.data and len(result.data) > 0:
                scheduled_count = result.data[0].get('scheduled_count', 0)
                next_time = result.data[0].get('next_send_time', '')
                
                messagebox.showinfo("Success", 
                                  f"Scheduled {scheduled_count} messages!\n\n"
                                  f"Last scheduled for: {next_time}\n\n"
                                  f"Check 'Scheduled' tab to see timeline.")
                
                # Refresh all campaign tabs
                self.load_suggested_overview()  # Master view
                self.load_approved_overview()   # APR view
                self.load_scheduled()           # SCH view
            else:
                messagebox.showinfo("Done", "No messages to schedule")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule: {e}")
            import traceback
            traceback.print_exc()


    def toggle_live_mode(self):
        """Toggle auto-refresh on/off"""
        if self.live_mode.get():
            # Turn on live mode
            self.live_indicator.config(foreground="green")
            self.start_auto_refresh()
        else:
            # Turn off live mode
            self.live_indicator.config(foreground="gray")
            self.stop_auto_refresh()
    
    def start_auto_refresh(self):
        """Start the auto-refresh timer"""
        self.auto_refresh()
    
    def stop_auto_refresh(self):
        """Stop the auto-refresh timer"""
        if self.refresh_timer_id:
            self.root.after_cancel(self.refresh_timer_id)
            self.refresh_timer_id = None
    
    def auto_refresh(self):
        """Auto-refresh all tabs every 15 seconds"""
        if not self.live_mode.get():
            return  # Stop if live mode was turned off
        
        try:
            # Refresh current tab based on what's visible
            current_tab = self.notebook.index(self.notebook.select())
            
            if current_tab == 0:  # All Messages
                self.load_messages()
            elif current_tab == 1:  # Reply to Messages
                self.load_conversations()
            elif current_tab == 2:  # First Texts
                self.load_first_texts()
            elif current_tab == 3:  # Campaign Master
                self.load_suggested_overview()
            elif current_tab == 4:  # Approved
                self.load_approved_overview()
            elif current_tab == 5:  # Scheduled
                self.load_scheduled()
            
            # Update last refresh timestamp
            from datetime import datetime
            now = datetime.now()
            self.last_refresh_label.config(text=f"Last: {now.strftime('%I:%M:%S %p')}")
        
        except Exception as e:
            print(f"Auto-refresh error: {e}")
        
        # Schedule next refresh
        self.refresh_timer_id = self.root.after(self.refresh_interval, self.auto_refresh)


if __name__ == "__main__":
    root = tk.Tk()
    app = SMSViewer(root)
    root.mainloop()
