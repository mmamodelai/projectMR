#!/usr/bin/env python3
"""
IC Viewer - BLAZE v5 HYBRID
Uses server-side RPC function for blazing fast performance
"""

import tkinter as tk
from tkinter import ttk, messagebox, Toplevel
from supabase import create_client, Client
from datetime import datetime
import json
import os

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

CONFIG_FILE = "viewer_config.json"

# Column definitions
CUSTOMER_COLUMNS = {
    "FirstName": {"label": "First Name", "width": 100},
    "LastName": {"label": "Last Name", "width": 120},
    "DOB": {"label": "Date of Birth", "width": 90},
    "Phone": {"label": "Phone", "width": 110},
    "Email": {"label": "Email", "width": 150},
    "TextOptIn": {"label": "SMS Opt-In", "width": 70},
    "EmailOptIn": {"label": "Email Opt-In", "width": 80},
    "Medical": {"label": "Medical", "width": 60},
    "Visits": {"label": "Visits", "width": 50},
    "Lifetime": {"label": "Lifetime $", "width": 80},
    "VIP": {"label": "VIP Status", "width": 70},
    "LastVisit": {"label": "Last Visit", "width": 100},
    "City": {"label": "City", "width": 100},
    "State": {"label": "State", "width": 50},
}

TRANSACTION_COLUMNS = {
    "Date": {"label": "Date", "width": 100},
    "Amount": {"label": "Amount", "width": 80},
    "Tax": {"label": "Tax", "width": 70},
    "Payment": {"label": "Payment", "width": 90},
    "Budtender": {"label": "Budtender", "width": 120},
    "Status": {"label": "Status", "width": 90},
}

ITEM_COLUMNS = {
    "Product": {"label": "Product", "width": 200},
    "Brand": {"label": "Brand", "width": 100},
    "Qty": {"label": "Qty", "width": 50},
    "TotalPrice": {"label": "Total $", "width": 80},
}

class BlazeCustomerViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("IC Viewer v5 - HYBRID (Server-Side)")
        self.root.geometry("2600x1200")
        
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        self.dark_panel = "#2a2a2a"
        
        self.root.configure(bg=self.bg_color)
        
        # Data
        self.customers = []
        self.transactions = []
        self.current_customer = None
        self.seller_names = {}  # Cache for resolved names
        self.view_mode = "customers"  # "customers" or "transactions"
        self.use_rpc = False  # Will switch to True after testing
        
        # Load config
        self.config = self._load_config()
        
        self._create_ui()
        self._test_rpc_availability()
        self._load_customers()
    
    
    def _get_seller_name(self, seller_id):
        """Get seller name - direct lookup in employees_blaze table"""
        if not seller_id:
            return "Unknown"

        # Check cache first
        cached_name = self.seller_names.get(seller_id)
        if cached_name is not None:
            return cached_name

        # Direct lookup in employees_blaze table
        try:
            result = self.sb.table('employees_blaze').select('name').eq('employee_id', seller_id).execute()
            if result.data and len(result.data) > 0:
                name = result.data[0]['name']
                if name:
                    self.seller_names[seller_id] = name
                    return name
        except:
            pass

        # Final fallback - just return the ID (no "Seller #" prefix)
        self.seller_names[seller_id] = seller_id
        return seller_id

    def _switch_view_mode(self, mode):
        """Switch between customers and transactions view"""
        if self.view_mode == mode:
            return  # Already in this mode

        self.view_mode = mode

        # Update UI elements
        if mode == "transactions":
            self.panel_title_label.config(text="LATEST TRANSACTIONS")
            self._update_tree_columns()
            self._load_transactions()
        else:
            self.panel_title_label.config(text="CUSTOMERS")
            self._update_tree_columns()
            self._load_customers()

    def _toggle_column(self, column_name):
        """Toggle visibility of a column in customers view"""
        visible_cols = self.config["visible_columns"]["customers"]
        
        if self.column_vars[column_name].get():
            # Show column
            if column_name not in visible_cols:
                visible_cols.append(column_name)
                self.status_label.config(text=f"Showing {CUSTOMER_COLUMNS[column_name]['label']}")
        else:
            # Hide column
            if column_name in visible_cols:
                visible_cols.remove(column_name)
                self.status_label.config(text=f"Hiding {CUSTOMER_COLUMNS[column_name]['label']}")
        
        # Save config
        self._save_config()
        
        # Refresh tree columns
        self._update_tree_columns()
        
        # Reload data to reflect new columns
        if self.view_mode == "customers":
            self._load_customers()

    def _load_transactions(self):
        """Load latest 1000 transactions"""
        import time
        start = time.time()

        try:
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)

            self.status_label.config(text="Loading latest transactions...")
            self.root.update()

            # Get latest 1000 transactions with all fields
            result = self.sb.table('transactions_blaze').select(
                'transaction_id, customer_id, total_amount, total_tax, created_at, seller_id, blaze_status, payment_type'
            ).order('created_at', desc=True).limit(1000).execute()

            self.transactions = result.data if result.data else []

            # Display transactions with all columns
            for trans in self.transactions:
                values = []
                for col in ["Date", "Customer", "Amount", "Tax", "Payment", "Seller", "Status"]:
                    if col == "Date":
                        val = self._format_date_time(trans.get('created_at', 'N/A'))
                    elif col == "Customer":
                        # Get customer name
                        customer_id = trans.get('customer_id')
                        if customer_id:
                            try:
                                cust_result = self.sb.table('customers_blaze').select('name, first_name, last_name').eq('member_id', customer_id).execute()
                                if cust_result.data:
                                    cust = cust_result.data[0]
                                    val = cust.get('name') or f"{cust.get('first_name', '')} {cust.get('last_name', '')}".strip() or 'Unknown'
                                else:
                                    val = 'Unknown'
                            except:
                                val = 'Unknown'
                        else:
                            val = 'Unknown'
                    elif col == "Amount":
                        val = f"${trans.get('total_amount', 0):.2f}"
                    elif col == "Tax":
                        val = f"${trans.get('total_tax', 0):.2f}"
                    elif col == "Payment":
                        payment = trans.get('payment_type', 'N/A')
                        val = payment if payment else 'Cash'
                    elif col == "Seller":
                        val = self._get_seller_name(trans.get('seller_id'))
                    elif col == "Status":
                        status = trans.get('blaze_status', 'Completed')
                        val = status if status else 'Completed'

                    values.append(val)

                self.cust_tree.insert('', tk.END, values=tuple(values), iid=trans.get('transaction_id'))

            elapsed = time.time() - start
            self.stats_label.config(text=f"{len(self.transactions)} transactions (latest first) - {elapsed:.2f}s")
            self.status_label.config(text="Ready")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions:\n{str(e)}")
            self.status_label.config(text="ERROR")

    def _test_rpc_availability(self):
        """Test if RPC function exists"""
        try:
            result = self.sb.rpc('get_customers_fast', {
                'filter_email': False,
                'filter_phone': False,
                'days_cutoff': 365
            }).limit(1).execute()
            
            if result.data is not None:
                self.use_rpc = True
                print("✓ RPC function available - using FAST mode")
                self.root.title("IC Viewer v5 - HYBRID (FAST MODE)")
            else:
                print("✗ RPC function not found - using fallback mode")
        except Exception as e:
            print(f"✗ RPC function not available: {e}")
            print("  Run sql_scripts/HYBRID_SOLUTION_step2_create_fast_query.sql first")
    
    def _load_config(self):
        """Load config"""
        default_config = {
            "filters": {"has_email": False, "has_phone": True, "last_visited": True, "days": 365},
            "visible_columns": {
                "customers": ["FirstName", "LastName", "Phone", "Email", "TextOptIn", "Visits", "Lifetime", "VIP", "LastVisit"],
                "transactions": ["Date", "Amount", "Payment", "Budtender", "Status"],
                "items": ["Product", "Brand", "Qty", "TotalPrice"]
            },
            "column_widths": {}
        }
        
        try:
            if os.path.exists(CONFIG_FILE):
                with open(CONFIG_FILE, 'r') as f:
                    loaded = json.load(f)
                    # Deep merge - ensure nested keys exist
                    for key in default_config:
                        if key not in loaded:
                            loaded[key] = default_config[key]
                        elif isinstance(default_config[key], dict):
                            # Merge nested dictionaries
                            for subkey in default_config[key]:
                                if subkey not in loaded[key]:
                                    loaded[key][subkey] = default_config[key][subkey]
                    return loaded
        except Exception as e:
            print(f"Config load error: {e}, using defaults")
        
        return default_config
    
    def _save_config(self):
        """Save config"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def _create_ui(self):
        """Create UI"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = tk.Label(
            title_frame,
            text="IC VIEWER v5 - HYBRID (Testing RPC...)",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Filters
        self._create_filter_bar(main_frame)
        
        # Search
        self._create_search_bar(main_frame)
        
        # 3-panel layout
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg=self.bg_color, sashwidth=5)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT: Customers
        self._create_customers_panel(content_paned)
        
        # RIGHT: Vertical split
        right_paned = tk.PanedWindow(content_paned, orient=tk.VERTICAL, bg=self.bg_color, sashwidth=5)
        content_paned.add(right_paned)
        
        # RIGHT TOP: Transactions
        self._create_transactions_panel(right_paned)
        
        # RIGHT BOTTOM: 3-way split
        bottom_paned = tk.PanedWindow(right_paned, orient=tk.HORIZONTAL, bg=self.bg_color, sashwidth=5)
        right_paned.add(bottom_paned)
        
        self._create_items_panel(bottom_paned)
        self._create_details_panel(bottom_paned)
        self._create_brand_panel(bottom_paned)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10),
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X, pady=(5, 0))
    
    def _create_filter_bar(self, parent):
        """Create filter bar"""
        filter_frame = tk.Frame(parent, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_email = tk.BooleanVar(value=self.config["filters"]["has_email"])
        self.filter_phone = tk.BooleanVar(value=self.config["filters"]["has_phone"])
        self.filter_recent = tk.BooleanVar(value=self.config["filters"]["last_visited"])
        
        tk.Checkbutton(filter_frame, text="Has Email", variable=self.filter_email, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, font=("Arial", 11), command=self._save_filter_state).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(filter_frame, text="Has Phone", variable=self.filter_phone, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, font=("Arial", 11), command=self._save_filter_state).pack(side=tk.LEFT, padx=(0, 15))
        tk.Checkbutton(filter_frame, text="Last Visited Within:", variable=self.filter_recent, bg=self.bg_color, fg=self.fg_color, selectcolor=self.bg_color, font=("Arial", 11), command=self._save_filter_state).pack(side=tk.LEFT, padx=(0, 5))
        
        self.days_var = tk.StringVar(value=str(self.config["filters"]["days"]))
        days_entry = tk.Entry(filter_frame, textvariable=self.days_var, width=5, font=("Arial", 11))
        days_entry.pack(side=tk.LEFT, padx=(0, 5))
        days_entry.bind('<Return>', lambda e: self._apply_filters())
        days_entry.bind('<FocusOut>', lambda e: self._save_filter_state())
        
        tk.Label(filter_frame, text="days", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Button(filter_frame, text="Apply Filters", command=self._apply_filters, bg=self.accent_color, fg="white", font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, padx=(0, 10))

        # View mode and display toggle
        tk.Button(filter_frame, text="👥 Customers", command=lambda: self._switch_view_mode("customers"), bg="#2196F3", fg="white", font=("Arial", 10, "bold"), padx=10).pack(side=tk.LEFT, padx=(0, 10))
        
        # Display dropdown menu for column visibility
        display_menu_button = tk.Menubutton(filter_frame, text="👁 Display", bg="#9C27B0", fg="white", font=("Arial", 10, "bold"), padx=10, relief=tk.RAISED)
        display_menu_button.pack(side=tk.LEFT, padx=(0, 10))
        
        display_menu = tk.Menu(display_menu_button, tearoff=0)
        display_menu_button.config(menu=display_menu)
        
        # Create BooleanVars for each toggleable column
        self.column_vars = {}
        toggleable_columns = ["FirstName", "LastName", "DOB", "Phone", "Email", "TextOptIn", "EmailOptIn"]
        
        for col in toggleable_columns:
            is_visible = col in self.config["visible_columns"]["customers"]
            self.column_vars[col] = tk.BooleanVar(value=is_visible)
            col_label = CUSTOMER_COLUMNS[col]["label"]
            display_menu.add_checkbutton(
                label=col_label,
                variable=self.column_vars[col],
                command=lambda c=col: self._toggle_column(c)
            )

        self.stats_label = tk.Label(filter_frame, text="Loading...", bg=self.bg_color, fg="#00ff00", font=("Arial", 11, "bold"))
        self.stats_label.pack(side=tk.RIGHT)
    
    def _create_search_bar(self, parent):
        """Create search bar"""
        search_frame = tk.Frame(parent, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 11))
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<Return>', lambda e: self._apply_filters())
    
    def _create_customers_panel(self, parent):
        """Create main data panel (customers or transactions)"""
        left_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(left_frame, width=900)

        # Dynamic title based on view mode
        self.panel_title_label = tk.Label(left_frame, text="CUSTOMERS", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color)
        self.panel_title_label.pack(pady=(0, 5))

        cust_tree_frame = tk.Frame(left_frame, bg=self.bg_color)
        cust_tree_frame.pack(fill=tk.BOTH, expand=True)

        cust_scroll_y = tk.Scrollbar(cust_tree_frame)
        cust_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cust_scroll_x = tk.Scrollbar(cust_tree_frame, orient=tk.HORIZONTAL)
        cust_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        # Start with customers columns
        visible_cols = self.config["visible_columns"]["customers"]
        self.cust_tree = ttk.Treeview(cust_tree_frame, columns=tuple(visible_cols), show="headings", yscrollcommand=cust_scroll_y.set, xscrollcommand=cust_scroll_x.set)

        self._update_tree_columns()
        self._bind_tree_events()

        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_scroll_y.config(command=self.cust_tree.yview)
        cust_scroll_x.config(command=self.cust_tree.xview)

    def _update_tree_columns(self):
        """Update tree columns based on current view mode"""
        # Clear existing columns
        for col in self.cust_tree['columns']:
            self.cust_tree.heading(col, text="")
            self.cust_tree.column(col, width=0)

        if self.view_mode == "transactions":
            # Transaction columns - more detailed like main view
            trans_columns = {
                "Date": {"label": "Date/Time", "width": 120},
                "Customer": {"label": "Customer", "width": 140},
                "Amount": {"label": "Amount", "width": 80},
                "Tax": {"label": "Tax", "width": 60},
                "Payment": {"label": "Payment", "width": 90},
                "Seller": {"label": "Budtender", "width": 120},
                "Status": {"label": "Status", "width": 90}
            }

            self.cust_tree['columns'] = tuple(trans_columns.keys())
            for col in trans_columns:
                self.cust_tree.heading(col, text=trans_columns[col]["label"], 
                                      command=lambda c=col: self._sort_tree_column(self.cust_tree, c, False))
                self.cust_tree.column(col, width=trans_columns[col]["width"])
        else:
            # Customer columns
            visible_cols = self.config["visible_columns"]["customers"]
            self.cust_tree['columns'] = tuple(visible_cols)
            for col in visible_cols:
                col_info = CUSTOMER_COLUMNS[col]
                self.cust_tree.heading(col, text=col_info["label"],
                                      command=lambda c=col: self._sort_tree_column(self.cust_tree, c, False))
                width = self.config["column_widths"].get("customers", {}).get(col, col_info["width"])
                self.cust_tree.column(col, width=width)

    def _bind_tree_events(self):
        """Bind tree events based on current view mode"""
        # Clear existing bindings
        self.cust_tree.unbind('<<TreeviewSelect>>')

        if self.view_mode == "transactions":
            self.cust_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        else:
            self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)

    def _sort_tree_column(self, tree, col, reverse):
        """Sort tree contents when a column is clicked"""
        data = [(tree.set(child, col), child) for child in tree.get_children('')]
        
        # Try numeric sort first, fall back to string sort
        try:
            # Remove $ and , for numeric columns
            data.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '')), reverse=reverse)
        except:
            data.sort(reverse=reverse)
        
        for index, (val, child) in enumerate(data):
            tree.move(child, '', index)
        
        # Reverse sort next time
        tree.heading(col, command=lambda: self._sort_tree_column(tree, col, not reverse))

    def _create_transactions_panel(self, parent):
        """Create transactions panel"""
        self.trans_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.trans_frame, height=350)
        
        tk.Label(self.trans_frame, text="TRANSACTIONS", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        trans_tree_frame = tk.Frame(self.trans_frame, bg=self.bg_color)
        trans_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll = tk.Scrollbar(trans_tree_frame)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        visible_cols = self.config["visible_columns"]["transactions"]
        self.trans_tree = ttk.Treeview(trans_tree_frame, columns=tuple(visible_cols), show="headings", yscrollcommand=trans_scroll.set)
        
        for col in visible_cols:
            col_info = TRANSACTION_COLUMNS[col]
            self.trans_tree.heading(col, text=col_info["label"],
                                   command=lambda c=col: self._sort_tree_column(self.trans_tree, c, False))
            width = self.config["column_widths"].get("transactions", {}).get(col, col_info["width"])
            self.trans_tree.column(col, width=width)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll.config(command=self.trans_tree.yview)
        self.trans_tree.bind('<<TreeviewSelect>>', self._existing_transaction_select)
    
    def _create_items_panel(self, parent):
        """Create items panel"""
        self.items_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.items_frame, width=400)
        
        tk.Label(self.items_frame, text="ITEMS", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        items_tree_frame = tk.Frame(self.items_frame, bg=self.bg_color)
        items_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        items_scroll = tk.Scrollbar(items_tree_frame)
        items_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        visible_cols = self.config["visible_columns"]["items"]
        self.items_tree = ttk.Treeview(items_tree_frame, columns=tuple(visible_cols), show="headings", yscrollcommand=items_scroll.set)
        
        for col in visible_cols:
            col_info = ITEM_COLUMNS[col]
            self.items_tree.heading(col, text=col_info["label"])
            width = self.config["column_widths"].get("items", {}).get(col, col_info["width"])
            self.items_tree.column(col, width=width)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scroll.config(command=self.items_tree.yview)
    
    def _create_details_panel(self, parent):
        """Create details panel (Baseball Card)"""
        self.detail_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.detail_frame, width=400)
        
        tk.Label(self.detail_frame, text="⚾ BASEBALL CARD", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        detail_scroll_frame = tk.Frame(self.detail_frame, bg=self.dark_panel)
        detail_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        detail_scroll = tk.Scrollbar(detail_scroll_frame)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(detail_scroll_frame, bg=self.dark_panel, fg=self.fg_color, font=("Courier New", 9), yscrollcommand=detail_scroll.set, wrap=tk.WORD)
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.config(command=self.detail_text.yview)
    
    def _create_brand_panel(self, parent):
        """Create brand panel"""
        self.brand_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.brand_frame, width=400)
        
        tk.Label(self.brand_frame, text="REVENUE BY BRAND", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        brand_scroll_frame = tk.Frame(self.brand_frame, bg=self.dark_panel)
        brand_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        brand_scroll = tk.Scrollbar(brand_scroll_frame)
        brand_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.brand_tree = ttk.Treeview(brand_scroll_frame, columns=("Brand", "Revenue", "Count", "Avg"), show="headings", yscrollcommand=brand_scroll.set)
        
        self.brand_tree.heading("Brand", text="Brand")
        self.brand_tree.heading("Revenue", text="Revenue")
        self.brand_tree.heading("Count", text="Count")
        self.brand_tree.heading("Avg", text="Avg Sale")
        
        self.brand_tree.column("Brand", width=150)
        self.brand_tree.column("Revenue", width=90)
        self.brand_tree.column("Count", width=60)
        self.brand_tree.column("Avg", width=80)
        
        self.brand_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        brand_scroll.config(command=self.brand_tree.yview)
    
    def _save_filter_state(self):
        """Save filter state"""
        self.config["filters"]["has_email"] = self.filter_email.get()
        self.config["filters"]["has_phone"] = self.filter_phone.get()
        self.config["filters"]["last_visited"] = self.filter_recent.get()
        try:
            self.config["filters"]["days"] = int(self.days_var.get())
        except:
            pass
        self._save_config()
    
    def _apply_filters(self):
        """Apply filters"""
        self._save_filter_state()
        self._load_customers()
    
    def _load_customers(self):
        """Load customers using RPC or fallback"""
        import time
        start = time.time()
        
        try:
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            self.status_label.config(text="Loading...")
            self.root.update()
            
            if self.use_rpc:
                # FAST MODE: Use server-side RPC
                if self.filter_recent.get():
                    try:
                        days = int(self.days_var.get())
                    except ValueError:
                        days = 365
                else:
                    # default safeguard to avoid full-table scans
                    days = 365
                search = self.search_var.get().strip() if self.search_var.get().strip() else None
                
                result = self.sb.rpc('get_customers_fast', {
                    'filter_email': self.filter_email.get(),
                    'filter_phone': self.filter_phone.get(),
                    'days_cutoff': days,
                    'search_term': search
                }).execute()
                
                self.customers = result.data if result.data else []
            else:
                # FALLBACK: Old method
                messagebox.showwarning("RPC Not Available", 
                    "Server-side function not found!\n\n"
                    "Run these SQL scripts first:\n"
                    "1. HYBRID_SOLUTION_step1_backfill.sql\n"
                    "2. HYBRID_SOLUTION_step2_create_fast_query.sql")
                return
            
            # Display customers
            visible_cols = self.config["visible_columns"]["customers"]
            
            for cust in self.customers:
                values = []
                for col in visible_cols:
                    if col == "FirstName":
                        val = cust.get('first_name') or (cust.get('name', 'N/A').split(' ')[0] if cust.get('name') else 'N/A')
                    elif col == "LastName":
                        val = cust.get('last_name') or (cust.get('name', 'N/A').split(' ')[-1] if cust.get('name') else 'N/A')
                    elif col == "DOB":
                        val = self._format_date_only(cust.get('date_of_birth', 'N/A'))
                    elif col == "Phone":
                        val = cust.get('phone', 'N/A')
                    elif col == "Email":
                        val = cust.get('email', 'N/A')
                    elif col == "TextOptIn":
                        val = "Yes" if cust.get('text_opt_in') else "No"
                    elif col == "EmailOptIn":
                        val = "Yes" if cust.get('email_opt_in') else "No"
                    elif col == "Medical":
                        val = "Yes" if cust.get('is_medical') else "No"
                    elif col == "Visits":
                        val = cust.get('total_visits', 0)
                    elif col == "Lifetime":
                        val = f"${cust.get('lifetime_value', 0):.2f}"
                    elif col == "VIP":
                        val = cust.get('vip_status', 'N/A')
                    elif col == "LastVisit":
                        val = cust.get('last_visited', 'N/A')
                    elif col == "City":
                        val = cust.get('city', 'N/A')
                    elif col == "State":
                        val = cust.get('state', 'N/A')
                    else:
                        val = "N/A"
                    
                    values.append(val)
                
                self.cust_tree.insert('', tk.END, values=tuple(values), iid=cust.get('member_id'))
            
            elapsed = time.time() - start
            
            filters = []
            if self.filter_email.get(): filters.append("Email")
            if self.filter_phone.get(): filters.append("Phone")
            if self.filter_recent.get(): filters.append(f"<{self.days_var.get()}d")
            
            filter_text = " + ".join(filters) if filters else "No filters"
            mode = "FAST RPC" if self.use_rpc else "Fallback"
            self.stats_label.config(text=f"{len(self.customers)} customers ({filter_text}) - {elapsed:.2f}s [{mode}]")
            self.status_label.config(text="Ready")
            
            # Auto-select the first (most recent) customer
            if len(self.customers) > 0:
                children = self.cust_tree.get_children()
                if children:
                    self.cust_tree.selection_set(children[0])
                    self.cust_tree.focus(children[0])
                    self.cust_tree.see(children[0])
                    # Trigger the selection event to load their data
                    self._on_customer_select(None)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
            self.status_label.config(text="ERROR")
    
    def _on_customer_select(self, event):
        """Customer selected"""
        import time
        start = time.time()
        
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        member_id = selection[0]
        
        try:
            result = self.sb.table('customers_blaze').select('*').eq('member_id', member_id).execute()
            self.current_customer = result.data[0] if result.data else None
            
            if self.current_customer:
                self._display_customer_details()
                self._load_transactions(member_id)
                self._load_brand_analysis(member_id)
            
            elapsed = time.time() - start
            self.status_label.config(text=f"Loaded in {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer:\n{str(e)}")

    def _on_transaction_select(self, event):
        """Transaction selected in main view"""
        selection = self.cust_tree.selection()
        if not selection:
            return

        transaction_id = selection[0]

        # Find the transaction data
        selected_trans = None
        for trans in self.transactions:
            if trans.get('transaction_id') == transaction_id:
                selected_trans = trans
                break

        if selected_trans:
            # Load transaction details in the right panel
            self._load_transaction_items(transaction_id)

            # Load customer details for the transaction
            customer_id = selected_trans.get('customer_id')
            if customer_id:
                try:
                    cust_result = self.sb.table('customers_blaze').select('*').eq('member_id', customer_id).execute()
                    if cust_result.data:
                        self.current_customer = cust_result.data[0]
                        self._display_customer_details()
                        self._load_brand_analysis(customer_id)
                except:
                    pass

    def _existing_transaction_select(self, event):
        """Transaction selected"""
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        self._load_transaction_items(transaction_id)
    
    def _load_transactions(self, member_id):
        """Load transactions"""
        try:
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            result = self.sb.table('transactions_blaze').select(
                'transaction_id, date, total_amount, total_tax, payment_type, blaze_status, seller_id'
            ).eq('customer_id', member_id).order('date', desc=True).limit(100).execute()
            
            visible_cols = self.config["visible_columns"]["transactions"]
            
            for trans in result.data:
                values = []
                for col in visible_cols:
                    if col == "Date":
                        val = trans.get('date', 'N/A')[:10]
                    elif col == "Amount":
                        val = f"${trans.get('total_amount', 0):.2f}"
                    elif col == "Tax":
                        val = f"${trans.get('total_tax', 0):.2f}"
                    elif col == "Payment":
                        val = trans.get('payment_type', 'N/A')
                    elif col == "Budtender":
                        val = self._get_seller_name(trans.get('seller_id'))
                    elif col == "Status":
                        val = trans.get('blaze_status', 'N/A')
                    else:
                        val = "N/A"
                    
                    values.append(val)
                
                self.trans_tree.insert('', tk.END, values=tuple(values), iid=trans['transaction_id'])
        
        except Exception as e:
            print(f"Failed to load transactions: {e}")
    
    def _load_transaction_items(self, transaction_id):
        """Load transaction items"""
        try:
            print(f"DEBUG: Loading items for transaction: {transaction_id}")
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            result = self.sb.table('transaction_items_blaze').select(
                'id, product_name, brand, quantity, total_price, unit_price'
            ).eq('transaction_id', transaction_id).order('id', desc=True).execute()
            print(f"DEBUG: Found {len(result.data) if result.data else 0} items")
            
            visible_cols = self.config["visible_columns"]["items"]
            
            for item in result.data:
                values = []
                for col in visible_cols:
                    if col == "Product":
                        val = item.get('product_name', 'N/A')
                    elif col == "Brand":
                        brand = item.get('brand')
                        val = brand if brand and brand.strip() else "Unknown"
                    elif col == "Qty":
                        val = f"{item.get('quantity', 0):.1f}"
                    elif col == "TotalPrice":
                        # Calculate total_price if NULL: unit_price * quantity
                        total_price = item.get('total_price')
                        if total_price is None or total_price == 0:
                            unit_price = item.get('unit_price', 0) or 0
                            quantity = item.get('quantity', 0) or 0
                            total_price = unit_price * quantity
                        val = f"${total_price:.2f}"
                    else:
                        val = "N/A"
                    
                    values.append(val)
                
                self.items_tree.insert('', tk.END, values=tuple(values))
        
        except Exception as e:
            print(f"Failed to load items: {e}")
    
    def _format_date_only(self, date_str):
        """Format date string to YYYY-MM-DD only (no timezone conversion)"""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        try:
            # If it's already just a date (YYYY-MM-DD), return as-is
            if len(str(date_str)) == 10 and str(date_str).count('-') == 2:
                return str(date_str)
            # If it has time/timezone info, extract just the date part
            return str(date_str).split('T')[0].split(' ')[0]
        except:
            return str(date_str)

    def _format_date_time(self, date_str):
        """Format date string to readable date/time"""
        if not date_str or date_str == 'N/A':
            return 'N/A'
        try:
            # Extract date and time parts
            if 'T' in str(date_str):
                date_part, time_part = str(date_str).split('T')
                # Remove timezone if present
                time_part = time_part.split('+')[0].split('.')[0]
                return f"{date_part} {time_part}"
            else:
                return str(date_str)
        except:
            return str(date_str)

    def _display_customer_details(self):
        """Display comprehensive customer details with advanced analytics"""
        self.detail_text.delete('1.0', tk.END)

        if not self.current_customer:
            return

        c = self.current_customer
        member_id = c.get('member_id')

        # Format dates
        dob = self._format_date_only(c.get('date_of_birth'))
        joined = self._format_date_only(c.get('date_joined'))
        last_visit = self._format_date_only(c.get('last_visited'))

        # Calculate age from DOB
        age = self._calculate_age(c.get('date_of_birth'))

        # Get customer name (handle both name field and first/last split)
        customer_name = c.get('name')
        if not customer_name:
            first = c.get('first_name', '')
            last = c.get('last_name', '')
            customer_name = f"{first} {last}".strip() if first or last else 'Unknown'

        # Medical status
        medical_status = "Medical" if c.get('is_medical') else "Recreational"

        # Member status
        member_status = c.get('member_status', 'Unknown')

        # VIP status with color coding
        vip_status = c.get('vip_status', 'New')
        vip_display = f"🏆 {vip_status}" if vip_status == 'VIP' else f"⭐ {vip_status}"

        # Activity stats
        total_visits = c.get('total_visits', 0)
        lifetime_value = c.get('lifetime_value', 0)
        avg_transaction = lifetime_value / total_visits if total_visits > 0 else 0
        days_since_visit = c.get('days_since_last_visit', 0)

        # Calculate visit frequency (visits per month)
        member_since_days = self._calculate_days_since(c.get('date_joined'))
        visit_frequency = (total_visits / (member_since_days / 30)) if member_since_days > 0 else 0

        # Recency status
        if days_since_visit <= 30:
            recency = "🟢 Active"
        elif days_since_visit <= 90:
            recency = "🟡 Recent"
        else:
            recency = "🔴 Inactive"

        # Contact preferences
        sms_pref = "📱 Yes" if c.get('text_opt_in') else "🚫 No"
        email_pref = "📧 Yes" if c.get('email_opt_in') else "🚫 No"

        # Loyalty points
        loyalty_points = c.get('loyalty_points')
        points_display = f"{loyalty_points} pts" if loyalty_points else "N/A"

        # Get advanced analytics (requires database queries)
        analytics = self._get_customer_analytics(member_id)

        # Get last 5 visits
        last_visits = self._get_last_visits(member_id, limit=5)

        # Age demographics
        age_group = self._get_age_group(age)

        details = f"""
╔════════════════════════════════════════════════════════╗
║              ⚾ BASEBALL CARD                           ║
╚════════════════════════════════════════════════════════╝

👤 {customer_name}
   {age} years old • {age_group} • {medical_status}

📊 KEY STATS
   
   💰 Lifetime Value:        ${lifetime_value:,.2f}
   🎯 Total Visits:          {total_visits}
   💵 Avg Transaction:       ${avg_transaction:.2f}
   📅 Visits/Month:          {visit_frequency:.1f}
   
   {vip_display}
   {recency} ({days_since_visit} days)

🛒 PURCHASE HABITS
   
   Items/Transaction:  {analytics.get('avg_items_per_transaction', 'N/A')}
   Top Category:       {analytics.get('top_category', 'N/A')}
   Favorite Brands:    {analytics.get('preferred_brands', 'N/A')[:50]}
   
💰 TOP BRANDS BY REVENUE
{self._format_top_brands(member_id)}

📞 CONTACT
   
   Phone:  {c.get('phone', 'N/A')}
   Email:  {c.get('email', 'N/A')}
   
   SMS:   {sms_pref}   Email: {email_pref}

📅 LAST 5 VISITS
   
{last_visits}

📅 TIMELINE
   
   Member Since:  {joined}
   Last Visit:    {last_visit}
   
╚════════════════════════════════════════════════════════╝
"""

        self.detail_text.insert('1.0', details)

    def _calculate_age(self, dob_str):
        """Calculate age from date of birth"""
        if not dob_str:
            return "Unknown"
        try:
            from datetime import datetime
            if isinstance(dob_str, str) and 'T' in dob_str:
                dob_date = datetime.fromisoformat(dob_str.replace('Z', '+00:00'))
            else:
                # Assume YYYY-MM-DD format
                dob_date = datetime.strptime(str(dob_str)[:10], '%Y-%m-%d')

            today = datetime.now()
            age = today.year - dob_date.year - ((today.month, today.day) < (dob_date.month, dob_date.day))
            return age
        except:
            return "Unknown"

    def _calculate_days_since(self, date_str):
        """Calculate days since a given date"""
        if not date_str:
            return 0
        try:
            from datetime import datetime
            if isinstance(date_str, str) and 'T' in date_str:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(str(date_str)[:10], '%Y-%m-%d')

            today = datetime.now()
            delta = today - date_obj
            return delta.days
        except:
            return 0

    def _get_customer_analytics(self, member_id):
        """Get advanced analytics for customer purchasing behavior"""
        analytics = {
            'avg_items_per_transaction': 'N/A',
            'top_category': 'N/A',
            'preferred_brands': 'N/A'
        }

        if not member_id:
            return analytics

        try:
            # First get transaction IDs for this customer
            transactions = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).execute()
            trans_ids = [t['transaction_id'] for t in transactions.data] if transactions.data else []

            if not trans_ids:
                return analytics

            # Then get transaction items for those transactions
            trans_items = self.sb.table('transaction_items_blaze').select(
                'transaction_id, product_name, brand, quantity'
            ).in_('transaction_id', trans_ids).execute()

            if trans_items.data:
                # Calculate average items per transaction
                trans_groups = {}
                brand_counts = {}
                category_keywords = {
                    'Flower': ['flower', 'bud', 'nug', 'cannabis', 'prepacks', 'pre-roll'],
                    'Edibles': ['edibles', 'gummy', 'chocolate', 'cookie', 'brownie', 'candy', 'chews'],
                    'Concentrates': ['concentrates', 'oil', 'wax', 'shatter', 'crumble', 'hash', 'live resin'],
                    'Vaporizers': ['vaporizers', 'cartridge', 'vape', 'pen', 'disposable', 'pods'],
                    'Topicals': ['topicals', 'cream', 'lotion', 'salve', 'balm', 'ointment'],
                    'Tinctures': ['tinctures', 'tincture', 'drop', 'liquid', 'sublingual'],
                    'Accessories': ['accessories', 'pipe', 'paper', 'lighter', 'grinder', 'bong']
                }

                category_counts = {cat: 0 for cat in category_keywords.keys()}

                for item in trans_items.data:
                    trans_id = item['transaction_id']
                    if trans_id not in trans_groups:
                        trans_groups[trans_id] = []
                    trans_groups[trans_id].append(item)

                    # Count brands
                    brand = item.get('brand', 'Unknown')
                    if brand and brand != 'Unknown':
                        brand_counts[brand] = brand_counts.get(brand, 0) + item.get('quantity', 1)

                    # Categorize products - try product_name first, then category field
                    product_name = item.get('product_name') or ''
                    category_name = item.get('category') or ''

                    # Use category field if available (more reliable)
                    if category_name:
                        category_name = category_name.lower()
                        for category, keywords in category_keywords.items():
                            if any(keyword in category_name for keyword in keywords):
                                category_counts[category] += item.get('quantity', 1)
                                break
                    # Fallback to product name matching
                    elif product_name:
                        product_name = product_name.lower()
                        for category, keywords in category_keywords.items():
                            if any(keyword in product_name for keyword in keywords):
                                category_counts[category] += item.get('quantity', 1)
                                break

                # Calculate averages
                total_items = sum(len(items) for items in trans_groups.values())
                total_transactions = len(trans_groups)
                analytics['avg_items_per_transaction'] = f"{total_items / total_transactions:.1f}" if total_transactions > 0 else 'N/A'

                # Find top category
                if category_counts:
                    top_category = max(category_counts.items(), key=lambda x: x[1])
                    if top_category[1] > 0:
                        analytics['top_category'] = f"{top_category[0]} ({int(top_category[1])})"
                    else:
                        analytics['top_category'] = 'N/A'

                # Find preferred brands (top 3)
                if brand_counts:
                    top_brands = sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    analytics['preferred_brands'] = ', '.join([f"{brand} ({int(count)})" for brand, count in top_brands])

        except Exception as e:
            print(f"Analytics error: {e}")

        return analytics

    def _get_last_visits(self, member_id, limit=5):
        """Get last N visits with details: Date, Day, Time, Budtender, Spend, % MOTA"""
        if not member_id:
            return "   No visit history available"

        try:
            print(f"DEBUG: Getting last visits for member_id: {member_id}")
            # Get last N transactions (using 'date' not 'created_at' for actual transaction date)
            result = self.sb.table('transactions_blaze').select(
                'transaction_id, date, total_amount, seller_id'
            ).eq('customer_id', member_id).order('date', desc=True).limit(limit).execute()
            print(f"DEBUG: Found {len(result.data) if result.data else 0} transactions")

            if not result.data or len(result.data) == 0:
                return "   No visits recorded"

            visits_text = []
            for trans in result.data:
                # Parse date/time (using 'date' field for actual transaction date)
                trans_date = trans.get('date', '')
                if trans_date:
                    from datetime import datetime
                    try:
                        dt = datetime.fromisoformat(trans_date.replace('Z', '+00:00'))
                        date_str = dt.strftime('%Y-%m-%d')
                        day_str = dt.strftime('%a')  # Mon, Tue, etc.
                        time_str = dt.strftime('%I:%M %p')  # 02:30 PM
                    except:
                        date_str = trans_date[:10]
                        day_str = '???'
                        time_str = trans_date[11:16] if len(trans_date) > 16 else '??:??'
                else:
                    date_str = 'N/A'
                    day_str = '???'
                    time_str = '??:??'

                # Get budtender name
                budtender = self._get_seller_name(trans.get('seller_id'))
                if len(budtender) > 12:
                    budtender = budtender[:12]

                # Get spend
                spend = trans.get('total_amount', 0)

                # Calculate % MOTA products
                trans_id = trans.get('transaction_id')
                mota_pct = self._calculate_mota_percentage(trans_id)

                # Format line with proper spacing
                visit_line = f"   {date_str:<10} {day_str:>3} {time_str:>9} {budtender:<13} ${spend:>7.2f} {mota_pct:>3}%"
                visits_text.append(visit_line)

            if visits_text:
                header = "   Date       Day Time      Budtender      Spend   MOTA"
                separator = "   " + "-" * 56
                return header + "\n" + separator + "\n" + "\n".join(visits_text)
            else:
                return "   No visits recorded"

        except Exception as e:
            print(f"Error getting last visits: {e}")
            return f"   Error loading visits: {str(e)}"

    def _calculate_mota_percentage(self, transaction_id):
        """Calculate percentage of MOTA products in a transaction"""
        try:
            # Get all items for this transaction
            items_result = self.sb.table('transaction_items_blaze').select(
                'brand, total_price'
            ).eq('transaction_id', transaction_id).execute()

            if not items_result.data or len(items_result.data) == 0:
                return 0

            total_spend = 0
            mota_spend = 0

            for item in items_result.data:
                price = item.get('total_price', 0)
                brand = item.get('brand', '')
                
                total_spend += price
                if brand and 'MOTA' in brand.upper():
                    mota_spend += price

            if total_spend > 0:
                return int((mota_spend / total_spend) * 100)
            else:
                return 0

        except Exception as e:
            print(f"Error calculating MOTA %: {e}")
            return 0

    def _get_age_group(self, age):
        """Categorize age into demographic groups"""
        if age == "Unknown":
            return "Unknown"
        try:
            age_num = int(age)
            if age_num < 21:
                return "Under 21"
            elif age_num <= 25:
                return "21-25"
            elif age_num <= 30:
                return "26-30"
            elif age_num <= 35:
                return "31-35"
            elif age_num <= 45:
                return "36-45"
            elif age_num <= 55:
                return "46-55"
            else:
                return "55+"
        except:
            return "Unknown"

    def _format_top_brands(self, member_id):
        """Format top 5 brands for baseball card with count"""
        try:
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data:
                return "   No brand data available"
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            brand_data = {}
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select('brand, total_price, unit_price, quantity').in_('transaction_id', batch_ids).execute()
                
                for item in items_result.data:
                    brand = item.get('brand')
                    if brand and brand.strip() and brand.strip().lower() != 'unknown':
                        # Calculate price from unit_price * quantity if total_price is null
                        price = item.get('total_price')
                        if price is None or price == 0:
                            unit_price = item.get('unit_price', 0) or 0
                            quantity = item.get('quantity', 1) or 1
                            price = unit_price * quantity
                        
                        if brand not in brand_data:
                            brand_data[brand] = {'revenue': 0, 'count': 0}
                        brand_data[brand]['revenue'] += price
                        brand_data[brand]['count'] += 1
            
            sorted_brands = sorted(brand_data.items(), key=lambda x: x[1]['revenue'], reverse=True)[:5]
            
            if not sorted_brands:
                return "   No brand data available"
            
            # Format as compact list with count
            output = []
            for i, (brand, data) in enumerate(sorted_brands, 1):
                output.append(f"   {i}. {brand[:20]:<20} ${data['revenue']:>8,.2f} ({data['count']} purchases)")
            
            return "\n".join(output)
        except Exception as e:
            return f"   Error loading brand data: {str(e)}"

    def _load_brand_analysis(self, member_id):
        """Load revenue by brand"""
        try:
            for item in self.brand_tree.get_children():
                self.brand_tree.delete(item)
            
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data:
                return
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            brand_data = {}
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select('brand, total_price').in_('transaction_id', batch_ids).execute()
                
                for item in items_result.data:
                    brand = item.get('brand')
                    if brand and brand.strip() and brand.strip().lower() != 'unknown':
                        price = item.get('total_price', 0) or 0
                        
                        if brand not in brand_data:
                            brand_data[brand] = {"revenue": 0, "count": 0}
                        
                        brand_data[brand]["revenue"] += price
                        brand_data[brand]["count"] += 1
            
            sorted_brands = sorted(brand_data.items(), key=lambda x: x[1]["revenue"], reverse=True)
            
            for brand, data in sorted_brands[:20]:
                avg = data["revenue"] / data["count"] if data["count"] > 0 else 0
                self.brand_tree.insert('', tk.END, values=(
                    brand,
                    f"${data['revenue']:.2f}",
                    data['count'],
                    f"${avg:.2f}"
                ))
            
        except Exception as e:
            print(f"Failed to load brand analysis: {e}")

def main():
    root = tk.Tk()
    app = BlazeCustomerViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

