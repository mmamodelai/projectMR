#!/usr/bin/env python3
"""
Manual Conductor - SMS Conversation Manager
Similar to IC Viewer but for SMS conversations

Features:
- List conversations with unread indicators
- View full conversation thread
- Customer details panel (linked to CRM)
- Reply to SMS
- Mark as read/unread
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from supabase import create_client, Client
from datetime import datetime
from dateutil import parser, tz
import json
import os

# Supabase Configuration
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

CONFIG_FILE = "manual_conductor_config.json"

class ManualConductor:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Conductor - SMS Manager")
        self.root.geometry("1400x800")
        self.root.configure(bg='#1e1e1e')
        
        # Initialize Supabase
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Load config
        self.config = self._load_config()
        
        # Data
        self.conversations = []
        self.selected_phone = None
        self.messages = []
        self.customer_data = None
        
        # Cache for contact classifications
        self.contact_cache = {}
        self.contact_map = {}  # Phone -> contact info mapping
        
        # Create UI
        self._create_ui()
        
        # Load contact directory FIRST (batch load all customers/budtenders)
        self._load_contact_directory()
        
        # Load data
        self._load_conversations()
    
    def _load_config(self):
        """Load config"""
        default_config = {
            "show_read": True,
            "show_unread": True,
            "auto_refresh": 30  # seconds
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    for key in default_config:
                        if key not in loaded:
                            loaded[key] = default_config[key]
                    return loaded
        except:
            pass
        
        return default_config
    
    def _save_config(self):
        """Save config"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")
    
    def _create_ui(self):
        """Create main UI"""
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1e1e1e')
        style.configure('TLabel', background='#1e1e1e', foreground='#ffffff')
        style.configure('TButton', background='#2d2d2d', foreground='#ffffff')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = ttk.Label(title_frame, text="💬 Manual Conductor", style='Title.TLabel')
        title.pack(side=tk.LEFT)
        
        # Refresh buttons
        refresh_btn = ttk.Button(title_frame, text="🔄 Refresh Messages", command=self._load_conversations)
        refresh_btn.pack(side=tk.RIGHT, padx=5)
        
        refresh_contacts_btn = ttk.Button(title_frame, text="📇 Refresh Contacts", command=self._refresh_contacts)
        refresh_contacts_btn.pack(side=tk.RIGHT, padx=5)
        
        # Stats label
        self.stats_label = ttk.Label(title_frame, text="")
        self.stats_label.pack(side=tk.RIGHT, padx=20)
        
        # Main paned window (3 panels)
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: Conversations List
        self._create_conversations_panel(paned)
        
        # MIDDLE PANEL: Conversation Thread
        self._create_thread_panel(paned)
        
        # RIGHT PANEL: Customer Details
        self._create_customer_panel(paned)
    
    def _create_conversations_panel(self, parent):
        """Create conversations list panel"""
        frame = ttk.Frame(parent, width=300)
        parent.add(frame, weight=1)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header, text="Conversations", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Filter buttons
        filter_frame = ttk.Frame(header)
        filter_frame.pack(side=tk.RIGHT)
        
        self.show_unread_var = tk.BooleanVar(value=self.config["show_unread"])
        self.show_read_var = tk.BooleanVar(value=self.config["show_read"])
        
        unread_chk = ttk.Checkbutton(filter_frame, text="Unread", variable=self.show_unread_var, 
                                      command=self._filter_conversations)
        unread_chk.pack(side=tk.LEFT, padx=2)
        
        read_chk = ttk.Checkbutton(filter_frame, text="Read", variable=self.show_read_var,
                                    command=self._filter_conversations)
        read_chk.pack(side=tk.LEFT, padx=2)
        
        # Treeview
        tree_frame = ttk.Frame(frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.conv_tree = ttk.Treeview(tree_frame, 
                                       columns=("Phone", "Name", "Status", "LastMsg", "Unread"),
                                       show="headings",
                                       yscrollcommand=scroll_y.set)
        scroll_y.config(command=self.conv_tree.yview)
        
        self.conv_tree.heading("Phone", text="Phone Number")
        self.conv_tree.heading("Name", text="Customer")
        self.conv_tree.heading("Status", text="Type")
        self.conv_tree.heading("LastMsg", text="Last Message")
        self.conv_tree.heading("Unread", text="📬")
        
        self.conv_tree.column("Phone", width=120)
        self.conv_tree.column("Name", width=100)
        self.conv_tree.column("Status", width=40)
        self.conv_tree.column("LastMsg", width=80)
        self.conv_tree.column("Unread", width=30)
        
        self.conv_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Bind selection
        self.conv_tree.bind('<<TreeviewSelect>>', self._on_conversation_select)
        
        # Configure tags for unread and customer status
        self.conv_tree.tag_configure('unread', background='#d1ecf1', font=('Arial', 10, 'bold'))
        self.conv_tree.tag_configure('read', background='#2d2d2d')
        self.conv_tree.tag_configure('ib_customer', background='#51cf66')  # Green for known customers
        self.conv_tree.tag_configure('xb_unknown', background='#495057')  # Gray for unknown
    
    def _create_thread_panel(self, parent):
        """Create conversation thread panel"""
        frame = ttk.Frame(parent, width=500)
        parent.add(frame, weight=2)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=(0, 5))
        
        self.thread_title = ttk.Label(header, text="Select a conversation", font=('Arial', 12, 'bold'))
        self.thread_title.pack(side=tk.LEFT)
        
        # Mark as read/unread button
        self.mark_btn = ttk.Button(header, text="Mark as Read", command=self._toggle_read_status)
        self.mark_btn.pack(side=tk.RIGHT, padx=5)
        
        # Thread display
        thread_frame = ttk.Frame(frame)
        thread_frame.pack(fill=tk.BOTH, expand=True)
        
        scroll_y = ttk.Scrollbar(thread_frame, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.thread_text = tk.Text(thread_frame, wrap=tk.WORD, 
                                    yscrollcommand=scroll_y.set,
                                    bg='#2d2d2d', fg='#ffffff',
                                    font=('Arial', 10))
        scroll_y.config(command=self.thread_text.yview)
        self.thread_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure tags for message display
        self.thread_text.tag_config('inbound', foreground='#4dabf7', font=('Arial', 10, 'bold'))
        self.thread_text.tag_config('outbound', foreground='#51cf66', font=('Arial', 10, 'bold'))
        self.thread_text.tag_config('timestamp', foreground='#868e96', font=('Arial', 9))
        self.thread_text.tag_config('content', foreground='#ffffff', font=('Arial', 10))
        
        # Reply frame
        reply_frame = ttk.LabelFrame(frame, text="Quick Reply", padding="5")
        reply_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.reply_entry = ttk.Entry(reply_frame, width=50)
        self.reply_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        send_btn = ttk.Button(reply_frame, text="Send SMS", command=self._send_reply)
        send_btn.pack(side=tk.RIGHT)
        
        # Bind Enter key
        self.reply_entry.bind('<Return>', lambda e: self._send_reply())
    
    def _create_customer_panel(self, parent):
        """Create customer details panel"""
        frame = ttk.Frame(parent, width=350)
        parent.add(frame, weight=1)
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(header, text="Customer Details", font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        
        # Customer info display
        info_frame = ttk.LabelFrame(frame, text="Profile", padding="10")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        
        self.customer_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD, 
                                                        bg='#2d2d2d', fg='#ffffff',
                                                        font=('Courier', 9),
                                                        height=15)
        self.customer_text.pack(fill=tk.BOTH, expand=True)
        
        # Transaction history
        trans_frame = ttk.LabelFrame(frame, text="Recent Transactions", padding="5")
        trans_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll = ttk.Scrollbar(trans_frame, orient=tk.VERTICAL)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_tree = ttk.Treeview(trans_frame,
                                        columns=("Date", "Amount"),
                                        show="headings",
                                        yscrollcommand=trans_scroll.set,
                                        height=10)
        trans_scroll.config(command=self.trans_tree.yview)
        
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.heading("Amount", text="Amount")
        
        self.trans_tree.column("Date", width=100)
        self.trans_tree.column("Amount", width=80)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def _load_contact_directory(self):
        """
        Load ALL customers and budtenders at once and create phone number mapping
        This is MUCH faster than individual queries
        """
        print("Loading contact directory...")
        start_time = datetime.now()
        
        # Try to load from cache file first
        cache_file = "contact_directory_cache.json"
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    self.contact_map = json.load(f)
                print(f"Loaded {len(self.contact_map)} contacts from cache")
                return
            except:
                print("Cache file corrupted, rebuilding...")
        
        self.contact_map = {}
        
        # Load ALL customers_blaze
        print("  Fetching all customers...")
        customers_loaded = 0
        try:
            customers = self.sb.table('customers_blaze').select('phone, first_name, last_name, member_id, vip_status, total_visits, lifetime_value').execute()
            
            for c in customers.data:
                phone = c.get('phone')
                if phone and str(phone).strip():
                    # Normalize phone number - strip all formatting
                    phone_str = str(phone).strip()
                    
                    # Get just the digits
                    digits_only = ''.join(filter(str.isdigit, phone_str))
                    
                    # Create ALL possible variations
                    variations = [
                        phone_str,  # Original
                        digits_only,  # Just digits
                        f"+{digits_only}",  # + prefix
                        f"+1{digits_only}" if not digits_only.startswith('1') else f"+{digits_only}",  # +1 prefix
                    ]
                    variations = list(set(variations))  # Remove duplicates
                    
                    contact_info = {
                        'type': 'IC',
                        'name': f"{c.get('first_name', '')} {c.get('last_name', '')}".strip(),
                        'vip_status': c.get('vip_status'),
                        'total_visits': c.get('total_visits', 0),
                        'lifetime_value': c.get('lifetime_value', 0),
                        'member_id': c.get('member_id'),
                        'data': c
                    }
                    
                    for var in variations:
                        self.contact_map[var] = contact_info
                    
                    customers_loaded += 1
                    
                    # Debug first few
                    if customers_loaded <= 5:
                        print(f"     Customer: {contact_info['name']}, Phone: {phone_str}, Variations: {len(variations)}")
            
            print(f"  Loaded {len(customers.data)} customers ({customers_loaded} with phones)")
        except Exception as e:
            print(f"  Error loading customers: {e}")
        
        # Load ALL budtenders
        print("  Fetching all budtenders...")
        try:
            # Try different column names
            for col_name in ['phone_number', 'phone', 'contact_phone']:
                try:
                    budtenders = self.sb.table('budtenders').select(f'{col_name}, first_name, last_name, dispensary_name').execute()
                    
                    for b in budtenders.data:
                        phone = b.get(col_name)
                        if phone and str(phone).strip():
                            phone_str = str(phone).strip()
                            
                            # Get just the digits
                            digits_only = ''.join(filter(str.isdigit, phone_str))
                            
                            # Create ALL possible variations
                            variations = [
                                phone_str,
                                digits_only,
                                f"+{digits_only}",
                                f"+1{digits_only}" if not digits_only.startswith('1') else f"+{digits_only}",
                            ]
                            variations = list(set(variations))
                            
                            contact_info = {
                                'type': 'XB',
                                'name': f"{b.get('first_name', '')} {b.get('last_name', '')}".strip(),
                                'dispensary': b.get('dispensary_name', 'Unknown'),
                                'data': b
                            }
                            
                            for var in variations:
                                if var not in self.contact_map:  # Don't overwrite IC customers
                                    self.contact_map[var] = contact_info
                    
                    print(f"  Loaded {len(budtenders.data)} budtenders")
                    break  # Found the right column
                except Exception as e:
                    continue  # Try next column name
        except Exception as e:
            print(f"  Error loading budtenders: {e}")
        
        # Save to cache file
        try:
            with open(cache_file, 'w') as f:
                json.dump(self.contact_map, f)
            print(f"Saved contact directory to cache ({len(self.contact_map)} phone variations)")
        except Exception as e:
            print(f"Failed to save cache: {e}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"Contact directory loaded in {elapsed:.1f} seconds")
    
    def _classify_contact(self, phone):
        """
        Classify contact using pre-loaded contact directory (FAST!)
        Returns: ('IC'|'IB'|'XC'|'XB'|'Unknown', customer_name, customer_data)
        """
        # Convert to string first
        phone = str(phone)
        
        # Check memory cache first
        if phone in self.contact_cache:
            return self.contact_cache[phone]
        
        # Look up in contact map
        if phone in self.contact_map:
            contact = self.contact_map[phone]
            contact_type = contact['type']
            
            if contact_type == 'IC':
                name = contact['name']
                result = ('IC', name, contact['data'])
            elif contact_type == 'XB':
                name = f"{contact['name']} @ {contact['dispensary']}"
                result = ('XB', name, contact['data'])
            else:
                result = ('Unknown', phone[-4:], None)
            
            self.contact_cache[phone] = result
            return result
        
        # Not found - mark as unknown (show full phone number)
        result = ('Unknown', phone, None)
        self.contact_cache[phone] = result
        return result
    
    def _load_conversations(self):
        """Load all conversations grouped by phone number"""
        try:
            # Get all messages
            response = self.sb.table('messages').select('*').order('timestamp', desc=True).execute()
            
            if not response.data:
                self.stats_label.config(text="No messages")
                return
            
            # Group by phone number
            conversations_dict = {}
            for msg in response.data:
                phone = str(msg.get('phone_number', 'Unknown'))  # Convert to string
                if phone not in conversations_dict:
                    # Classify contact
                    contact_type, contact_name, contact_data = self._classify_contact(phone)
                    
                    conversations_dict[phone] = {
                        'phone': phone,
                        'contact_type': contact_type,
                        'contact_name': contact_name,
                        'contact_data': contact_data,
                        'last_message_time': msg.get('timestamp'),
                        'unread_count': 0,
                        'total_messages': 0
                    }
                
                conversations_dict[phone]['total_messages'] += 1
                
                # Count unread inbound messages
                if msg.get('status') == 'unread' and msg.get('direction') == 'inbound':
                    conversations_dict[phone]['unread_count'] += 1
            
            # Convert to list and sort by last message time
            self.conversations = sorted(conversations_dict.values(), 
                                        key=lambda x: x['last_message_time'], 
                                        reverse=True)
            
            # Update stats with breakdown
            total = len(self.conversations)
            unread_convs = sum(1 for c in self.conversations if c['unread_count'] > 0)
            total_unread = sum(c['unread_count'] for c in self.conversations)
            
            # Count by type
            ic_count = sum(1 for c in self.conversations if c['contact_type'] == 'IC')
            xb_count = sum(1 for c in self.conversations if c['contact_type'] == 'XB')
            unknown_count = sum(1 for c in self.conversations if c['contact_type'] == 'Unknown')
            
            self.stats_label.config(text=f"📊 {total} conversations | {unread_convs} unread | IC:{ic_count} XB:{xb_count} ?:{unknown_count}")
            
            # Populate tree
            self._populate_conversations()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversations:\n{str(e)}")
    
    def _populate_conversations(self):
        """Populate conversations tree"""
        # Clear tree
        for item in self.conv_tree.get_children():
            self.conv_tree.delete(item)
        
        # Filter conversations
        show_unread = self.show_unread_var.get()
        show_read = self.show_read_var.get()
        
        for conv in self.conversations:
            has_unread = conv['unread_count'] > 0
            
            # Apply filters
            if has_unread and not show_unread:
                continue
            if not has_unread and not show_read:
                continue
            
            # Format data
            phone = conv['phone']
            name = conv['contact_name']
            contact_type = conv['contact_type']
            
            # If unknown, show phone number without + prefix for display
            if contact_type == 'Unknown':
                display_phone = phone.replace('+', '').replace('+1', '')
                name = display_phone
            
            last_msg_time = self._format_time(conv['last_message_time'])
            unread_indicator = f"({conv['unread_count']})" if has_unread else ""
            
            # Choose tag based on unread status AND contact type
            if has_unread:
                tag = 'unread'
            elif contact_type == 'IC':
                tag = 'ib_customer'  # Green for known IC customers
            elif contact_type == 'XB':
                tag = 'ib_customer'  # Green for known XB budtenders
            else:
                tag = 'xb_unknown'  # Gray for unknown
            
            self.conv_tree.insert('', tk.END, 
                                  values=(phone, name, contact_type, last_msg_time, unread_indicator), 
                                  tags=(tag,))
    
    def _filter_conversations(self):
        """Filter conversations based on checkboxes"""
        self.config["show_unread"] = self.show_unread_var.get()
        self.config["show_read"] = self.show_read_var.get()
        self._save_config()
        self._populate_conversations()
    
    def _on_conversation_select(self, event):
        """Load conversation thread when selected"""
        selection = self.conv_tree.selection()
        if not selection:
            return
        
        item = self.conv_tree.item(selection[0])
        phone = item['values'][0]
        
        self.selected_phone = phone
        self._load_conversation_thread(phone)
        self._load_customer_details(phone)
    
    def _load_conversation_thread(self, phone):
        """Load all messages for a phone number"""
        try:
            print(f"Loading messages for phone: {phone} (type: {type(phone)})")
            
            # Convert to string first (in case it's an integer)
            phone = str(phone)
            
            # Try multiple formats - messages might have + prefix
            formats_to_try = [
                phone,
                phone.replace('+', ''),
                f"+{phone}",
                phone.replace('+1', '').replace('+', ''),
            ]
            formats_to_try = list(set(formats_to_try))
            
            print(f"  Trying message formats: {formats_to_try}")
            
            # Build OR query for all formats
            or_conditions = ','.join([f'phone_number.eq.{fmt}' for fmt in formats_to_try])
            
            # Get all messages for this phone (try multiple formats)
            response = self.sb.table('messages').select('*')\
                .or_(or_conditions)\
                .order('timestamp', desc=False)\
                .execute()
            
            print(f"Found {len(response.data) if response.data else 0} messages")
            
            self.messages = response.data or []
            
            # Update title
            contact_type, contact_name, _ = self._classify_contact(phone)
            self.thread_title.config(text=f"Conversation with {contact_name} ({contact_type}) - {phone}")
            
            # Clear thread
            self.thread_text.delete('1.0', tk.END)
            
            if not self.messages:
                self.thread_text.insert('1.0', f"No messages found for {phone}\n\n")
                self.thread_text.insert(tk.END, "This could mean:\n", 'timestamp')
                self.thread_text.insert(tk.END, "• Phone number format mismatch\n", 'content')
                self.thread_text.insert(tk.END, "• Messages were deleted\n", 'content')
                self.thread_text.insert(tk.END, "• Database sync issue\n\n", 'content')
                self.thread_text.insert(tk.END, f"Debug: Searched for '{phone}' and '{normalized_phone}'", 'timestamp')
                return
            
            # Display messages
            for msg in self.messages:
                direction = msg.get('direction', 'unknown')
                content = msg.get('content', '')
                timestamp = self._format_time(msg.get('timestamp'))
                status = msg.get('status', '')
                
                # Direction indicator
                if direction == 'inbound':
                    self.thread_text.insert(tk.END, "👤 CUSTOMER ", 'inbound')
                else:
                    self.thread_text.insert(tk.END, "🤖 MOTA ", 'outbound')
                
                # Timestamp
                self.thread_text.insert(tk.END, f"[{timestamp}] ", 'timestamp')
                
                # Status indicator
                if direction == 'outbound':
                    status_icon = {"sent": "✅", "queued": "⏳", "failed": "❌"}.get(status, "?")
                    self.thread_text.insert(tk.END, f"{status_icon} ", 'timestamp')
                elif status == 'unread':
                    self.thread_text.insert(tk.END, "📬 ", 'timestamp')
                
                self.thread_text.insert(tk.END, f"\n{content}\n\n", 'content')
            
            # Scroll to bottom
            self.thread_text.see(tk.END)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load conversation:\n{str(e)}")
    
    def _load_customer_details(self, phone):
        """Load customer/contact details based on classification"""
        try:
            # Convert to string first
            phone = str(phone)
            
            # Re-classify to get fresh data
            contact_type, contact_name, contact_data = self._classify_contact(phone)
            
            self.customer_data = contact_data
            
            # Clear transactions first
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            if contact_type == 'IC':
                # Internal Customer - show full CRM details
                c = contact_data
                info = f"""
╔══════════════════════════════════════╗
║  INTERNAL CUSTOMER (IC)              ║
╚══════════════════════════════════════╝

NAME: {c.get('first_name', '')} {c.get('last_name', '')}
PHONE: {c.get('phone', '')}
EMAIL: {c.get('email', 'N/A')}
DOB: {c.get('date_of_birth', 'N/A')}

VIP STATUS: {c.get('vip_status', 'N/A')}
TOTAL VISITS: {c.get('total_visits', 0)}
LIFETIME VALUE: ${c.get('lifetime_value', 0):.2f}
LAST VISIT: {c.get('last_visited', 'N/A')}

SMS OPT-IN: {'Yes' if c.get('text_opt_in') else 'No'}
EMAIL OPT-IN: {'Yes' if c.get('email_opt_in') else 'No'}
MEDICAL: {'Yes' if c.get('is_medical') else 'No'}

LOYALTY POINTS: {c.get('loyalty_points', 0)}

ADDRESS:
{c.get('address1', 'N/A')}
{c.get('city', '')}, {c.get('state', '')} {c.get('zip_code', '')}
"""
                self.customer_text.delete('1.0', tk.END)
                self.customer_text.insert('1.0', info)
                
                # Load transactions
                self._load_customer_transactions(c.get('member_id'))
            
            elif contact_type == 'XB':
                # External Budtender - show budtender details
                b = contact_data
                info = f"""
╔══════════════════════════════════════╗
║  EXTERNAL BUDTENDER (XB)             ║
╚══════════════════════════════════════╝

NAME: {b.get('first_name', '')} {b.get('last_name', '')}
DISPENSARY: {b.get('dispensary_name', 'N/A')}
PHONE: {b.get('phone_number', '')}
EMAIL: {b.get('email', 'N/A')}

TOTAL TRANSACTIONS: {b.get('total_transactions', 0)}
TOTAL SALES: ${b.get('total_sales', 0):.2f}
AVG TRANSACTION: ${b.get('avg_transaction_value', 0):.2f}

EMPLOYEE ID: {b.get('employee_id', 'N/A')}
BLAZE EMPLOYEE ID: {b.get('blaze_employee_id', 'N/A')}

ACCOUNT CREATED: {b.get('created_at', 'N/A')[:10]}

⚠️  This is a budtender at another store.
Use wholesale/B2B messaging approach.
"""
                self.customer_text.delete('1.0', tk.END)
                self.customer_text.insert('1.0', info)
            
            elif contact_type == 'IB':
                # Internal Budtender (future)
                info = f"""
╔══════════════════════════════════════╗
║  INTERNAL BUDTENDER (IB)             ║
╚══════════════════════════════════════╝

NAME: {contact_name}
PHONE: {phone}

⚠️  MoTa Silverlake Employee
Use internal team messaging.
"""
                self.customer_text.delete('1.0', tk.END)
                self.customer_text.insert('1.0', info)
            
            elif contact_type == 'XC':
                # External Customer (future - from Google Sheets)
                info = f"""
╔══════════════════════════════════════╗
║  EXTERNAL CUSTOMER (XC)              ║
╚══════════════════════════════════════╝

NAME: {contact_name}
PHONE: {phone}

🎁 Rewards Program Member
Buys MoTa products at other stores.
"""
                self.customer_text.delete('1.0', tk.END)
                self.customer_text.insert('1.0', info)
            
            else:
                # Unknown contact
                info = f"""
╔══════════════════════════════════════╗
║  UNKNOWN CONTACT                     ║
╚══════════════════════════════════════╝

PHONE: {phone}

❌ Not found in any database:
   - Not in customers_blaze (IC)
   - Not in budtenders (XB/IB)
   - Not in external_customers (XC)

This could be:
• New customer (not yet in system)
• Wrong number
• Spam/test message

💡 Consider adding to appropriate database.
"""
                self.customer_text.delete('1.0', tk.END)
                self.customer_text.insert('1.0', info)
            
        except Exception as e:
            print(f"Error loading customer: {e}")
            self.customer_text.delete('1.0', tk.END)
            self.customer_text.insert('1.0', f"Error loading contact:\n{str(e)}")
    
    def _load_customer_transactions(self, member_id):
        """Load recent transactions for customer"""
        try:
            # Clear tree
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            # Get transactions
            response = self.sb.table('transactions_blaze').select('transaction_date, total_amount')\
                .eq('customer_id', member_id)\
                .eq('blaze_status', 'Completed')\
                .order('transaction_date', desc=True)\
                .limit(20)\
                .execute()
            
            if response.data:
                for trans in response.data:
                    date = trans.get('transaction_date', 'N/A')[:10]
                    amount = f"${trans.get('total_amount', 0):.2f}"
                    self.trans_tree.insert('', tk.END, values=(date, amount))
        
        except Exception as e:
            print(f"Error loading transactions: {e}")
    
    def _toggle_read_status(self):
        """Toggle read/unread status for selected conversation"""
        if not self.selected_phone:
            messagebox.showwarning("No Selection", "Please select a conversation first")
            return
        
        try:
            # Check current status
            has_unread = any(m.get('status') == 'unread' and m.get('direction') == 'inbound' 
                            for m in self.messages)
            
            new_status = 'read' if has_unread else 'unread'
            
            # Update all inbound messages for this phone
            self.sb.table('messages').update({'status': new_status})\
                .eq('phone_number', self.selected_phone)\
                .eq('direction', 'inbound')\
                .execute()
            
            # Refresh
            self._load_conversations()
            self._load_conversation_thread(self.selected_phone)
            
            # Update button text
            self.mark_btn.config(text=f"Mark as {'Unread' if new_status == 'read' else 'Read'}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status:\n{str(e)}")
    
    def _send_reply(self):
        """Send SMS reply (queues message)"""
        if not self.selected_phone:
            messagebox.showwarning("No Selection", "Please select a conversation first")
            return
        
        content = self.reply_entry.get().strip()
        if not content:
            messagebox.showwarning("Empty Message", "Please enter a message")
            return
        
        try:
            # Insert message as queued
            self.sb.table('messages').insert({
                'phone_number': self.selected_phone,
                'content': content,
                'direction': 'outbound',
                'status': 'queued',
                'timestamp': datetime.now(tz.tzutc()).isoformat()
            }).execute()
            
            # Clear entry
            self.reply_entry.delete(0, tk.END)
            
            # Refresh conversation
            self._load_conversation_thread(self.selected_phone)
            
            messagebox.showinfo("Success", "Message queued for sending!\n\nConductor system will send it on next poll.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message:\n{str(e)}")
    
    def _refresh_contacts(self):
        """Refresh contact directory from database"""
        # Delete cache file to force reload
        cache_file = "contact_directory_cache.json"
        if os.path.exists(cache_file):
            os.remove(cache_file)
        
        # Clear caches
        self.contact_map = {}
        self.contact_cache = {}
        
        # Reload
        self._load_contact_directory()
        
        # Refresh conversations to show new names
        self._load_conversations()
        
        messagebox.showinfo("Success", f"Contact directory refreshed!\n{len(self.contact_map)} phone variations loaded.")
    
    def _format_time(self, timestamp_str):
        """Format timestamp for display"""
        if not timestamp_str:
            return "N/A"
        try:
            dt = parser.isoparse(timestamp_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=tz.tzutc())
            local_dt = dt.astimezone(tz.tzlocal())
            return local_dt.strftime("%m/%d %I:%M %p")
        except:
            return "Invalid"

def main():
    root = tk.Tk()
    app = ManualConductor(root)
    root.mainloop()

if __name__ == "__main__":
    main()

