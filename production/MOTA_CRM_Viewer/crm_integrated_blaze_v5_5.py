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

CONFIG_FILE = "viewer_config_v5_5.json"

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
    "LastVisit": {"label": "Last Visit", "width": 120},
    "LastBudtender": {"label": "Last Budtender", "width": 120},
    "LastSpent": {"label": "Last Spent", "width": 80},
    "City": {"label": "City", "width": 100},
    "State": {"label": "State", "width": 50},
}

TRANSACTION_COLUMNS = {
    "Date": {"label": "Date/Time", "width": 120},
    "Amount": {"label": "Amount", "width": 80},
    "Tax": {"label": "Tax", "width": 70},
    "Payment": {"label": "Payment", "width": 90},
    "Budtender": {"label": "Budtender", "width": 120},
    "Status": {"label": "Status", "width": 90},
    "MOTAPercent": {"label": "% MOTA", "width": 70},
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
        self.auto_refresh_id = None  # For live updates
        
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

    def _toggle_column(self, panel_type, column_name):
        """Toggle visibility of a column in any panel"""
        visible_cols = self.config["visible_columns"][panel_type]
        
        # Get the appropriate column definition
        col_defs = {
            "customers": CUSTOMER_COLUMNS,
            "transactions": TRANSACTION_COLUMNS,
            "items": ITEM_COLUMNS
        }
        col_def = col_defs[panel_type]
        
        if self.column_vars[panel_type][column_name].get():
            # Show column
            if column_name not in visible_cols:
                visible_cols.append(column_name)
                self.status_label.config(text=f"Showing {col_def[column_name]['label']} in {panel_type}")
        else:
            # Hide column
            if column_name in visible_cols:
                visible_cols.remove(column_name)
                self.status_label.config(text=f"Hiding {col_def[column_name]['label']} from {panel_type}")
        
        # Save config
        self._save_config()
        
        # Refresh appropriate panel
        if panel_type == "customers":
            self._update_tree_columns()
            if self.view_mode == "customers":
                self._load_customers()
        elif panel_type == "transactions":
            # Refresh transaction tree columns
            self._refresh_transaction_columns()
        elif panel_type == "items":
            # Refresh items tree columns
            self._refresh_items_columns()
    
    def _refresh_transaction_columns(self):
        """Refresh transaction panel columns"""
        visible_cols = self.config["visible_columns"]["transactions"]
        self.trans_tree['columns'] = tuple(visible_cols)
        for col in visible_cols:
            col_info = TRANSACTION_COLUMNS[col]
            self.trans_tree.heading(col, text=col_info["label"])
            self.trans_tree.column(col, width=col_info["width"])
        # Reload current customer's transactions
        if self.current_customer:
            self._load_transactions(self.current_customer.get('member_id'))
    
    def _refresh_items_columns(self):
        """Refresh items panel columns"""
        visible_cols = self.config["visible_columns"]["items"]
        self.items_tree['columns'] = tuple(visible_cols)
        for col in visible_cols:
            col_info = ITEM_COLUMNS[col]
            self.items_tree.heading(col, text=col_info["label"])
            self.items_tree.column(col, width=col_info["width"])
        # Reload current transaction's items
        selected = self.trans_tree.selection()
        if selected:
            trans_id = self.trans_tree.item(selected[0])['values'][0] if self.trans_tree.item(selected[0])['values'] else None
            if trans_id:
                self._load_transaction_items(trans_id)

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
        """Skip RPC test - we load last 100 visitors directly (simple and fast!)"""
        self.use_rpc = False
        print("Simple mode: Loading last 100 visitors (fast & efficient)")
        self.root.title("IC Viewer v5.5 - REDESIGNED (4-Panel Layout)")
    
    def _load_config(self):
        """Load config"""
        default_config = {
            "filters": {"has_email": False, "has_phone": True, "last_visited": True, "days": 365},
            "visible_columns": {
                "customers": ["FirstName", "LastName", "Phone", "Visits", "Lifetime", "VIP", "LastVisit", "LastBudtender", "LastSpent"],
                "transactions": ["Date", "Amount", "Payment", "Budtender", "MOTAPercent"],
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
        """Create UI with tabbed interface"""
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = tk.Label(
            title_frame,
            text="IC VIEWER v5.5 - LIVE BUDTENDER DASHBOARD",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        self.title_label.pack(side=tk.LEFT)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab', background=self.dark_panel, foreground=self.fg_color, padding=[20, 10], font=('Arial', 12, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', self.accent_color)], foreground=[('selected', 'white')])
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Customer View
        customer_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(customer_tab, text="📊 CUSTOMERS")
        self._create_customer_tab(customer_tab)
        
        # Tab 2: Budtender Dashboard
        budtender_tab = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(budtender_tab, text="🎯 LIVE BUDTENDER DASHBOARD")
        self._create_budtender_tab(budtender_tab)
        
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
        
        # Bind tab change event
        self.notebook.bind('<<NotebookTabChanged>>', self._on_tab_changed)
    
    def _create_customer_tab(self, parent):
        """Create customer view tab"""
        # Filters
        self._create_filter_bar(parent)
        
        # Search
        self._create_search_bar(parent)
        
        # 3-panel layout
        content_paned = tk.PanedWindow(parent, orient=tk.HORIZONTAL, bg=self.bg_color, sashwidth=5)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT: Customers
        self._create_customers_panel(content_paned)
        
        # RIGHT: Horizontal 3-way split
        right_paned = tk.PanedWindow(content_paned, orient=tk.HORIZONTAL, bg=self.bg_color, sashwidth=5)
        content_paned.add(right_paned)
        
        # VERTICAL stack: Items on top, Transactions on bottom (same column, 400px)
        trans_items_paned = tk.PanedWindow(right_paned, orient=tk.VERTICAL, bg=self.bg_color, sashwidth=5)
        right_paned.add(trans_items_paned, width=400)
        
        self._create_items_panel(trans_items_paned)         # TOP (smaller)
        self._create_transactions_panel(trans_items_paned)  # BOTTOM (smaller)
        
        # Baseball Card and Visit Analytics
        self._create_details_panel(right_paned)       # WIDE (700px)
        self._create_visit_frequency_panel(right_paned)  # Medium (400px)
    
    def _create_budtender_tab(self, parent):
        """Create live budtender dashboard tab"""
        # Header with live indicator
        header_frame = tk.Frame(parent, bg=self.bg_color)
        header_frame.pack(fill=tk.X, pady=(10, 20))
        
        tk.Label(
            header_frame,
            text="🔴 LIVE - Last 30 Days Performance",
            font=("Arial", 16, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        self.live_status_label = tk.Label(
            header_frame,
            text="● LIVE",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg="#00ff00"
        )
        self.live_status_label.pack(side=tk.RIGHT, padx=10)
        
        self.last_update_label = tk.Label(
            header_frame,
            text="Last update: --:--",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.last_update_label.pack(side=tk.RIGHT, padx=10)
        
        # Budtender performance table
        table_frame = tk.Frame(parent, bg=self.dark_panel)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create treeview
        columns = ("budtender", "transactions", "avg_value", "items_per_trans", "mota_percent", "vs_store_avg", "shift_status")
        self.budtender_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Define headings
        self.budtender_tree.heading("budtender", text="BUDTENDER")
        self.budtender_tree.heading("transactions", text="TRANSACTIONS")
        self.budtender_tree.heading("avg_value", text="AVG $ VALUE")
        self.budtender_tree.heading("items_per_trans", text="ITEMS/TRANS")
        self.budtender_tree.heading("mota_percent", text="% MOTA")
        self.budtender_tree.heading("vs_store_avg", text="VS STORE AVG")
        self.budtender_tree.heading("shift_status", text="SHIFT STATUS")
        
        # Define column widths
        self.budtender_tree.column("budtender", width=200)
        self.budtender_tree.column("transactions", width=120, anchor=tk.CENTER)
        self.budtender_tree.column("avg_value", width=120, anchor=tk.CENTER)
        self.budtender_tree.column("items_per_trans", width=120, anchor=tk.CENTER)
        self.budtender_tree.column("mota_percent", width=100, anchor=tk.CENTER)
        self.budtender_tree.column("vs_store_avg", width=150, anchor=tk.CENTER)
        self.budtender_tree.column("shift_status", width=120, anchor=tk.CENTER)
        
        # Style - HIGH CONTRAST for better readability
        style = ttk.Style()
        style.configure("Treeview", 
            background=self.dark_panel, 
            foreground='#ffffff',  # Pure white for max contrast
            fieldbackground=self.dark_panel, 
            font=("Arial", 11),
            rowheight=28)  # Taller rows for easier reading
        style.configure("Treeview.Heading", 
            background=self.accent_color, 
            foreground="white", 
            font=("Arial", 11, "bold"))
        style.map('Treeview', 
            background=[('selected', '#1a5f7a')],  # Darker blue for selection
            foreground=[('selected', '#ffffff')])  # White text when selected
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.budtender_tree.yview)
        self.budtender_tree.configure(yscrollcommand=scrollbar.set)
        
        self.budtender_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Tags for color coding - HIGH CONTRAST for readability
        self.budtender_tree.tag_configure('above_avg', background='#0d3d1f', foreground='#00ff88')  # Dark green bg, bright green text
        self.budtender_tree.tag_configure('below_avg', background='#3d0d0d', foreground='#ff9999')  # Dark red bg, light red text
        self.budtender_tree.tag_configure('normal', background=self.dark_panel, foreground='#e0e0e0')  # Brighter text
        self.budtender_tree.tag_configure('active', background='#0d2d3d', foreground='#00ffff')  # Dark cyan bg, bright cyan text
        
        # Controls at bottom
        control_frame = tk.Frame(parent, bg=self.bg_color)
        control_frame.pack(fill=tk.X, pady=10)
        
        tk.Button(
            control_frame,
            text="🔄 REFRESH NOW",
            command=self._load_budtender_dashboard,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        self.auto_refresh_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            control_frame,
            text="Auto-refresh (60s)",
            variable=self.auto_refresh_var,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            font=("Arial", 11),
            command=self._toggle_auto_refresh
        ).pack(side=tk.LEFT, padx=10)
        
        # Stats summary
        stats_frame = tk.Frame(parent, bg=self.dark_panel)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.store_stats_label = tk.Label(
            stats_frame,
            text="Store Stats: Loading...",
            font=("Arial", 12, "bold"),
            bg='#333333',
            fg='#ffffff',
            anchor=tk.W,
            padx=20,
            pady=10
        )
        self.store_stats_label.pack(fill=tk.X)
    
    def _on_tab_changed(self, event):
        """Handle tab change - start/stop auto-refresh"""
        selected_tab = self.notebook.index(self.notebook.select())
        
        if selected_tab == 1:  # Budtender Dashboard tab
            self._load_budtender_dashboard()
            if self.auto_refresh_var.get():
                self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
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
        self.column_vars = {
            "customers": {},
            "transactions": {},
            "items": {}
        }
        
        # CUSTOMERS columns
        display_menu.add_command(label="─── CUSTOMERS ───", state="disabled")
        toggleable_customers = ["FirstName", "LastName", "DOB", "Phone", "Email", "TextOptIn", "EmailOptIn", "LastBudtender", "LastSpent"]
        for col in toggleable_customers:
            is_visible = col in self.config["visible_columns"]["customers"]
            self.column_vars["customers"][col] = tk.BooleanVar(value=is_visible)
            col_label = CUSTOMER_COLUMNS[col]["label"]
            display_menu.add_checkbutton(
                label=f"  {col_label}",
                variable=self.column_vars["customers"][col],
                command=lambda c=col: self._toggle_column("customers", c)
            )
        
        # TRANSACTIONS columns
        display_menu.add_separator()
        display_menu.add_command(label="─── TRANSACTIONS ───", state="disabled")
        toggleable_transactions = ["Date", "Amount", "Payment", "Budtender", "Status", "MOTAPercent"]
        for col in toggleable_transactions:
            is_visible = col in self.config["visible_columns"]["transactions"]
            self.column_vars["transactions"][col] = tk.BooleanVar(value=is_visible)
            col_label = TRANSACTION_COLUMNS[col]["label"]
            display_menu.add_checkbutton(
                label=f"  {col_label}",
                variable=self.column_vars["transactions"][col],
                command=lambda c=col: self._toggle_column("transactions", c)
            )
        
        # ITEMS columns
        display_menu.add_separator()
        display_menu.add_command(label="─── ITEMS ───", state="disabled")
        toggleable_items = ["Product", "Brand", "Qty", "TotalPrice"]
        for col in toggleable_items:
            is_visible = col in self.config["visible_columns"]["items"]
            self.column_vars["items"][col] = tk.BooleanVar(value=is_visible)
            col_label = ITEM_COLUMNS[col]["label"]
            display_menu.add_checkbutton(
                label=f"  {col_label}",
                variable=self.column_vars["items"][col],
                command=lambda c=col: self._toggle_column("items", c)
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
        """Create transactions panel - NARROW, stacked below Items"""
        self.trans_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.trans_frame)  # Height auto-adjusts
        
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
        """Create items panel - TOP of stack, smaller height"""
        self.items_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.items_frame, height=200)  # Small height (max ~10 rows)
        
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
        """Create details panel (Baseball Card) - WIDER!"""
        self.detail_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.detail_frame, width=700)  # MUCH WIDER!
        
        tk.Label(self.detail_frame, text="⚾ BASEBALL CARD", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        detail_scroll_frame = tk.Frame(self.detail_frame, bg=self.dark_panel)
        detail_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        detail_scroll = tk.Scrollbar(detail_scroll_frame)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(detail_scroll_frame, bg='#333333', fg='#ffffff', font=("Courier New", 10), yscrollcommand=detail_scroll.set, wrap=tk.WORD, insertbackground='white')
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.config(command=self.detail_text.yview)
    
    def _create_visit_frequency_panel(self, parent):
        """Create visit frequency visualization panel"""
        self.freq_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(self.freq_frame, width=400)
        
        tk.Label(self.freq_frame, text="📊 VISIT ANALYTICS", font=("Arial", 12, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(0, 5))
        
        freq_scroll_frame = tk.Frame(self.freq_frame, bg=self.dark_panel)
        freq_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        freq_scroll = tk.Scrollbar(freq_scroll_frame)
        freq_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.freq_text = tk.Text(freq_scroll_frame, wrap=tk.WORD, font=("Courier New", 12), 
                                 yscrollcommand=freq_scroll.set, bg='#333333', 
                                 fg='#ffffff', insertbackground='white', 
                                 padx=10, pady=10)
        self.freq_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        freq_scroll.config(command=self.freq_text.yview)
    
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
            
            # SIMPLE MODE: Just load last 100 visitors (fast & efficient!)
            # Search term for filtering
            search = self.search_var.get().strip() if self.search_var.get().strip() else None
            
            # Build query
            query = self.sb.table('customers_blaze').select('*')
            
            # Apply search filter if provided
            if search:
                # Search across multiple fields
                query = query.or_(f"first_name.ilike.%{search}%,last_name.ilike.%{search}%,phone.like.%{search}%,email.ilike.%{search}%")
            
            # Apply phone filter if checked
            if self.filter_phone.get():
                query = query.not_.is_('phone', 'null')
            
            # Apply email filter if checked
            if self.filter_email.get():
                query = query.not_.is_('email', 'null')
            
            # CRITICAL: Only show customers with actual visits (exclude NULL last_visited)
            query = query.not_.is_('last_visited', 'null')
            
            # Order by most recent visitors first
            query = query.order('last_visited', desc=True)
            
            # Limit to 100 (or 1000 if searching)
            limit = 1000 if search else 100
            query = query.limit(limit)
            
            result = query.execute()
            self.customers = result.data if result.data else []
            
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
                        val = cust.get('total_visits') or 0
                    elif col == "Lifetime":
                        val = f"${(cust.get('lifetime_value') or 0):.2f}"
                    elif col == "VIP":
                        val = cust.get('vip_status', 'N/A')
                    elif col == "LastVisit":
                        last_visit = cust.get('last_visited', 'N/A')
                        if last_visit and last_visit != 'N/A':
                            val = self._format_pst_time(last_visit)
                        else:
                            val = 'N/A'
                    elif col == "LastBudtender":
                        val = self._get_last_budtender(cust.get('member_id'))
                    elif col == "LastSpent":
                        val = self._get_last_spent(cust.get('member_id'))
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
                self._load_visit_frequency(member_id)
            
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
                        self._load_visit_frequency(customer_id)
                except:
                    pass

    def _existing_transaction_select(self, event):
        """Transaction selected"""
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        self._load_transaction_items(transaction_id)
    
    def _format_pst_time(self, date_str):
        """Format timestamp to PST in 11am/12pm format"""
        try:
            from datetime import datetime
            import pytz
            
            if not date_str or date_str == 'N/A':
                return 'N/A'
            
            # Check if this has a time component
            has_time = 'T' in str(date_str)
            
            # Parse the date
            if has_time:
                dt = datetime.fromisoformat(str(date_str).replace('Z', '+00:00'))
            else:
                # Date only - just return formatted date without time
                dt = datetime.fromisoformat(str(date_str))
                return dt.strftime('%m/%d/%y')
            
            # Convert to PST
            pst = pytz.timezone('America/Los_Angeles')
            dt_pst = dt.astimezone(pst)
            
            # Format as "11/09 3:45pm"
            month_day = dt_pst.strftime('%m/%d')
            hour = dt_pst.hour
            minute = dt_pst.strftime('%M')
            
            if hour == 0:
                time_str = f"12:{minute}am"
            elif hour < 12:
                time_str = f"{hour}:{minute}am"
            elif hour == 12:
                time_str = f"12:{minute}pm"
            else:
                time_str = f"{hour-12}:{minute}pm"
            
            return f"{month_day} {time_str}"
        except Exception as e:
            return str(date_str)[:10] if date_str else 'N/A'
    
    def _get_last_budtender(self, member_id):
        """Get last budtender name for customer"""
        try:
            result = self.sb.table('transactions_blaze').select('seller_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').order('date', desc=True).limit(1).execute()
            if result.data and result.data[0].get('seller_id'):
                return self._get_seller_name(result.data[0]['seller_id'])
            return 'N/A'
        except:
            return 'N/A'
    
    def _get_last_spent(self, member_id):
        """Get last transaction amount for customer"""
        try:
            result = self.sb.table('transactions_blaze').select('total_amount').eq('customer_id', member_id).eq('blaze_status', 'Completed').order('date', desc=True).limit(1).execute()
            if result.data:
                amount = result.data[0].get('total_amount') or 0
                return f"${amount:.2f}"
            return 'N/A'
        except:
            return 'N/A'
    
    def _calculate_mota_percent(self, transaction_id):
        """Calculate % MOTA products in transaction"""
        try:
            items_result = self.sb.table('transaction_items_blaze').select(
                'transaction_id, product_name, brand, category, total_price, unit_price, quantity'
            ).eq('transaction_id', transaction_id).execute()
            
            if not items_result.data:
                return "0%"
            
            # DEDUPE ITEMS!
            items = self._dedupe_items(items_result.data)
            
            total_revenue = 0
            mota_revenue = 0
            
            for item in items:
                # Skip recycling fees
                item_category = item.get('category') or ''
                if item_category == 'FEES':
                    continue
                
                # Calculate item price
                price = item.get('total_price')
                if price is None or price == 0:
                    unit_price = item.get('unit_price', 0) or 0
                    quantity = item.get('quantity', 1) or 1
                    price = unit_price * quantity
                
                total_revenue += price
                
                # Check if MOTA brand
                brand = item.get('brand', '').upper()
                if 'MOTA' in brand:
                    mota_revenue += price
            
            if total_revenue == 0:
                return "0%"
            
            mota_percent = (mota_revenue / total_revenue) * 100
            return f"{mota_percent:.0f}%"
        except Exception as e:
            print(f"Error calculating MOTA%: {e}")
            return "?"
    
    def _load_transactions(self, member_id):
        """Load transactions with % MOTA"""
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
                        val = self._format_pst_time(trans.get('date', 'N/A'))
                    elif col == "Amount":
                        val = f"${(trans.get('total_amount') or 0):.2f}"
                    elif col == "Tax":
                        val = f"${(trans.get('total_tax') or 0):.2f}"
                    elif col == "Payment":
                        val = trans.get('payment_type', 'N/A')
                    elif col == "Budtender":
                        val = self._get_seller_name(trans.get('seller_id'))
                    elif col == "Status":
                        val = trans.get('blaze_status', 'N/A')
                    elif col == "MOTAPercent":
                        val = self._calculate_mota_percent(trans['transaction_id'])
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

        # Activity stats - Handle None values
        # Get ACTUAL visit count from transactions (not cached value)
        actual_visits_result = self.sb.table('transactions_blaze').select('transaction_id', count='exact').eq('customer_id', member_id).eq('blaze_status', 'Completed').limit(1).execute()
        total_visits = actual_visits_result.count if actual_visits_result.count else 0
        
        lifetime_value = c.get('lifetime_value') or 0
        avg_transaction = lifetime_value / total_visits if total_visits > 0 else 0
        days_since_visit = c.get('days_since_last_visit') or 0

        # Calculate visit frequency (visits per ACTIVE month only)
        # Get actual transaction months to calculate properly
        visit_frequency = self._calculate_visits_per_month(member_id, total_visits)

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
   
💰 SPENDING BY CATEGORY
{self._format_product_categories(member_id)}

🏷️ TOP 5 BRANDS BY SPEND
{self._format_top_brands(member_id)}

🛍️ TOP 7 PURCHASED ITEMS
{self._format_top_items(member_id)}

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
                'transaction_id, product_name, brand, category, total_price, unit_price, quantity'
            ).eq('transaction_id', transaction_id).execute()

            if not items_result.data or len(items_result.data) == 0:
                return 0

            # DEDUPE ITEMS!
            items = self._dedupe_items(items_result.data)

            total_spend = 0
            mota_spend = 0

            for item in items:
                # Skip recycling fees
                item_category = item.get('category') or ''
                if item_category == 'FEES':
                    continue
                
                # Calculate price
                price = item.get('total_price', 0)
                if price is None or price == 0:
                    unit_price = item.get('unit_price', 0) or 0
                    quantity = item.get('quantity', 1) or 1
                    price = unit_price * quantity
                
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

    def _calculate_visits_per_month(self, member_id, total_visits):
        """Calculate visits per active month (months with visits > 0)"""
        try:
            from collections import defaultdict
            
            # Get all transaction dates
            trans_result = self.sb.table('transactions_blaze').select('date').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data or total_visits == 0:
                return 0
            
            # Count unique months with visits
            monthly_counts = defaultdict(int)
            for trans in trans_result.data:
                if trans.get('date'):
                    date_str = trans['date'][:7]  # "2025-11"
                    monthly_counts[date_str] += 1
            
            # Calculate average per active month
            active_months = len(monthly_counts)
            return total_visits / active_months if active_months > 0 else 0
            
        except Exception as e:
            print(f"Error calculating visits per month: {e}")
            return 0
    
    def _categorize_product(self, product_name, category_field=None):
        """Categorize product into Flower, Vapes, Edibles, Concentrates, or Other"""
        # Use category field if available
        if category_field:
            cat = category_field.lower()
            if 'flower' in cat or 'bud' in cat:
                return 'Flower'
            elif 'vape' in cat or 'cart' in cat or 'pen' in cat:
                return 'Vapes'
            elif 'edible' in cat or 'gumm' in cat or 'chocolate' in cat or 'candy' in cat:
                return 'Edibles'
            elif 'concentrate' in cat or 'wax' in cat or 'shatter' in cat or 'oil' in cat or 'dab' in cat:
                return 'Concentrates'
        
        # Fallback to product name
        if not product_name:
            return 'Other'
        
        name = product_name.lower()
        
        # Flower keywords
        if any(word in name for word in ['flower', 'bud', 'eighth', '1/8', 'quarter', '1/4', 'half', 'ounce', 'oz', 'gram', ' g ']):
            return 'Flower'
        
        # Vape keywords
        if any(word in name for word in ['vape', 'cart', 'cartridge', 'pen', 'pod', 'disposable']):
            return 'Vapes'
        
        # Edibles keywords
        if any(word in name for word in ['edible', 'gummy', 'gummies', 'chocolate', 'candy', 'mint', 'cookie', 'brownie']):
            return 'Edibles'
        
        # Concentrates keywords
        if any(word in name for word in ['concentrate', 'wax', 'shatter', 'oil', 'dab', 'rosin', 'resin', 'diamond', 'sauce']):
            return 'Concentrates'
        
        return 'Other'
    
    def _dedupe_items(self, items):
        """Deduplicate items by transaction_id + product + price + quantity"""
        seen = set()
        deduped = []
        
        for item in items:
            # Create unique key
            key = (
                item.get('transaction_id'),
                item.get('product_name'),
                item.get('brand'),
                item.get('unit_price'),
                item.get('quantity')
            )
            
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        
        return deduped
    
    def _format_product_categories(self, member_id):
        """Format spending by product category (Flower, Vapes, Edibles, Concentrates, Other)"""
        try:
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data:
                return "   No purchase data available"
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            category_data = {
                'Flower': {'revenue': 0, 'count': 0},
                'Vapes': {'revenue': 0, 'count': 0},
                'Edibles': {'revenue': 0, 'count': 0},
                'Concentrates': {'revenue': 0, 'count': 0},
                'Other': {'revenue': 0, 'count': 0}
            }
            
            # Batch query items
            all_items = []
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select(
                    'transaction_id, product_name, brand, category, total_price, unit_price, quantity'
                ).in_('transaction_id', batch_ids).execute()
                all_items.extend(items_result.data)
            
            # DEDUPE ITEMS!
            all_items = self._dedupe_items(all_items)
            
            for item in all_items:
                # Skip recycling fees (FEES category)
                item_category = item.get('category') or ''
                if item_category == 'FEES':
                    continue
                
                # Calculate price
                price = item.get('total_price')
                if price is None or price == 0:
                    unit_price = item.get('unit_price', 0) or 0
                    quantity = item.get('quantity', 1) or 1
                    price = unit_price * quantity
                
                # Categorize
                category = self._categorize_product(
                    item.get('product_name'),
                    item_category
                )
                
                category_data[category]['revenue'] += price
                category_data[category]['count'] += 1
            
            # Sort by revenue
            sorted_categories = sorted(category_data.items(), key=lambda x: x[1]['revenue'], reverse=True)
            
            # Format output
            output = []
            for category, data in sorted_categories:
                if data['revenue'] > 0:  # Only show categories with spending
                    output.append(f"   {category:<14} ${data['revenue']:>8,.2f}  ({data['count']} items)")
            
            return "\n".join(output) if output else "   No purchase data available"
            
        except Exception as e:
            return f"   Error loading category data: {str(e)}"
    
    def _format_top_brands(self, member_id):
        """Format top 5 brands by spending"""
        try:
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data:
                return "   No brand data available"
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            brand_data = {}
            
            # Batch query items
            all_items = []
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select(
                    'transaction_id, product_name, brand, category, total_price, unit_price, quantity'
                ).in_('transaction_id', batch_ids).execute()
                all_items.extend(items_result.data)
            
            # DEDUPE ITEMS!
            all_items = self._dedupe_items(all_items)
            
            for item in all_items:
                # Skip recycling fees
                item_category = item.get('category') or ''
                if item_category == 'FEES':
                    continue
                
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
                output.append(f"   {i}. {brand[:18]:<18} ${data['revenue']:>7,.2f} ({data['count']})")
            
            return "\n".join(output)
        except Exception as e:
            return f"   Error loading brand data: {str(e)}"
    
    def _format_top_items(self, member_id):
        """Format top 7 most purchased items"""
        try:
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            if not trans_result.data:
                return "   No item data available"
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            item_data = {}
            
            # Batch query items
            all_items = []
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select(
                    'transaction_id, product_name, brand, category, total_price, unit_price, quantity'
                ).in_('transaction_id', batch_ids).execute()
                all_items.extend(items_result.data)
            
            # DEDUPE ITEMS!
            all_items = self._dedupe_items(all_items)
            
            for item in all_items:
                # Skip recycling fees
                item_category = item.get('category') or ''
                if item_category == 'FEES':
                    continue
                
                # Create unique key: product_name + brand
                product = (item.get('product_name') or 'Unknown Product').strip()
                brand = (item.get('brand') or '').strip()
                
                # Skip if no meaningful product name
                if not product or product.lower() == 'unknown product':
                    continue
                
                # Key is product name (without brand since we show it separately)
                key = product
                
                # Calculate price
                price = item.get('total_price')
                if price is None or price == 0:
                    unit_price = item.get('unit_price', 0) or 0
                    quantity = item.get('quantity', 1) or 1
                    price = unit_price * quantity
                
                if key not in item_data:
                    item_data[key] = {'brand': brand, 'revenue': 0, 'count': 0}
                item_data[key]['revenue'] += price
                item_data[key]['count'] += 1
            
            sorted_items = sorted(item_data.items(), key=lambda x: x[1]['count'], reverse=True)[:7]
            
            if not sorted_items:
                return "   No item data available"
            
            # Format as compact list
            output = []
            for i, (product, data) in enumerate(sorted_items, 1):
                # Truncate product name if too long
                product_display = product[:30]
                brand_display = f"({data['brand'][:10]})" if data['brand'] else ""
                output.append(f"   {i}. {product_display} {brand_display}")
                output.append(f"      ${data['revenue']:>7,.2f} • {data['count']} purchases")
            
            return "\n".join(output)
        except Exception as e:
            return f"   Error loading item data: {str(e)}"

    def _load_visit_frequency(self, member_id):
        """Load visit frequency analytics"""
        try:
            self.freq_text.delete('1.0', tk.END)
            
            # Get all transactions for this customer
            trans_result = self.sb.table('transactions_blaze').select('date, total_amount').eq('customer_id', member_id).eq('blaze_status', 'Completed').order('date', desc=True).execute()
            
            if not trans_result.data:
                self.freq_text.insert('1.0', "No transaction data available")
                return
            
            transactions = trans_result.data
            total_visits = len(transactions)
            
            # Parse dates
            from datetime import datetime
            dates = []
            for trans in transactions:
                try:
                    if trans.get('date'):
                        date_obj = datetime.fromisoformat(trans['date'].replace('Z', '+00:00'))
                        dates.append(date_obj)
                except:
                    pass
            
            if not dates:
                self.freq_text.insert('1.0', "No valid date data")
                return
            
            dates.sort(reverse=True)
            
            # Calculate metrics
            first_visit = dates[-1]
            last_visit = dates[0]
            days_active = (last_visit - first_visit).days if len(dates) > 1 else 0
            
            # Monthly frequency
            from collections import defaultdict
            from datetime import timedelta
            
            monthly_counts = defaultdict(int)
            for date in dates:
                month_key = date.strftime('%Y-%m')
                monthly_counts[month_key] += 1
            
            # Generate ALL months from first visit to last visit
            all_months = []
            current = first_visit.replace(day=1)
            end = last_visit.replace(day=1)
            
            while current <= end:
                month_key = current.strftime('%Y-%m')
                all_months.append(month_key)
                # Move to next month (add 32 days then set to 1st of that month)
                current = (current + timedelta(days=32)).replace(day=1)
            
            # Reverse to show most recent first, limit to last 12
            all_months.reverse()
            display_months = all_months[:12]
            
            # Calculate avg visits per ACTIVE month (months with visits > 0)
            active_months = [m for m in monthly_counts.values() if m > 0]
            avg_per_active_month = sum(active_months) / len(active_months) if active_months else 0
            
            output = f"""
╔══════════════════════════════════════════╗
   VISIT FREQUENCY ANALYSIS
╚══════════════════════════════════════════╝

📊 OVERVIEW
   Total Visits:        {total_visits}
   Days Active:         {days_active} days
   Avg Visits/Month:    {avg_per_active_month:.1f} (active months only)
   First Visit:         {first_visit.strftime('%Y-%m-%d')}
   Last Visit:          {last_visit.strftime('%Y-%m-%d')}

📈 MONTHLY BREAKDOWN (All Months Since First Visit)
"""
            
            # Find max for scaling (ignore 0s)
            max_count = max(monthly_counts.values()) if monthly_counts else 1
            
            for month in display_months:
                count = monthly_counts.get(month, 0)  # Returns 0 if month not in counts
                
                # Format: "25-11" instead of "2025-11"
                year, mon = month.split('-')
                short_month = f"{year[-2:]}-{mon}"  # "25-11"
                
                # Larger, bolder formatting
                bar_length = int((count / max_count) * 25) if count > 0 else 0
                bar = '█' * bar_length if count > 0 else '·' * 3  # Show dots for 0 months
                
                # Format with more spacing and prominence
                if count > 0:
                    output += f"\n   {short_month}    {count:>2} visits   {bar}"
                else:
                    output += f"\n   {short_month}     0 visits   {bar}"
            
            self.freq_text.insert('1.0', output)
            
            # Add budtender breakdown
            budtender_breakdown = self._format_budtender_breakdown(member_id, total_visits)
            if budtender_breakdown:
                self.freq_text.insert(tk.END, "\n\n" + budtender_breakdown)
        
        except Exception as e:
            self.freq_text.insert('1.0', f"Error loading visit frequency: {str(e)}")
    
    def _format_budtender_breakdown(self, member_id, total_customer_visits):
        """Format budtender performance breakdown for this specific customer"""
        try:
            # Get all transactions with budtender info
            trans_result = self.sb.table('transactions_blaze').select(
                'transaction_id, seller_id, total_amount, date'
            ).eq('customer_id', member_id).eq('blaze_status', 'Completed').order('date', desc=True).execute()
            
            if not trans_result.data or total_customer_visits == 0:
                return None
            
            # Group by budtender
            budtender_stats = {}
            
            for trans in trans_result.data:
                seller_id = trans.get('seller_id')
                if not seller_id:
                    continue
                
                trans_id = trans['transaction_id']
                amount = trans.get('total_amount', 0) or 0
                
                if seller_id not in budtender_stats:
                    budtender_stats[seller_id] = {
                        'name': self._get_seller_name(seller_id),
                        'visit_count': 0,
                        'total_revenue': 0,
                        'transaction_ids': [],
                        'total_items': 0,
                        'mota_revenue': 0
                    }
                
                budtender_stats[seller_id]['visit_count'] += 1
                budtender_stats[seller_id]['total_revenue'] += amount
                budtender_stats[seller_id]['transaction_ids'].append(trans_id)
            
            # Get items for each budtender's transactions
            all_trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            # Batch query items
            items_by_trans = {}
            for i in range(0, len(all_trans_ids), 100):
                batch_ids = all_trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select(
                    'transaction_id, brand, category, total_price, unit_price, quantity, product_name'
                ).in_('transaction_id', batch_ids).execute()
                
                for item in items_result.data:
                    trans_id = item['transaction_id']
                    if trans_id not in items_by_trans:
                        items_by_trans[trans_id] = []
                    items_by_trans[trans_id].append(item)
            
            # DEDUPE items for each transaction and skip recycling fees!
            for trans_id in items_by_trans:
                items = items_by_trans[trans_id]
                # Dedupe
                items = self._dedupe_items(items)
                # Skip FEES category
                items = [item for item in items if (item.get('category') or '') != 'FEES']
                items_by_trans[trans_id] = items
            
            # Calculate detailed stats for each budtender
            for seller_id, stats in budtender_stats.items():
                total_items = 0
                mota_revenue = 0
                
                for trans_id in stats['transaction_ids']:
                    items = items_by_trans.get(trans_id, [])
                    
                    # Count unique products (SKUs)
                    unique_products = set()
                    for item in items:
                        product = item.get('product_name', 'Unknown')
                        unique_products.add(product)
                    
                    total_items += len(unique_products)
                    
                    # Calculate MOTA revenue
                    for item in items:
                        brand = (item.get('brand') or '').upper()
                        
                        # Calculate price
                        price = item.get('total_price')
                        if price is None or price == 0:
                            unit_price = item.get('unit_price') or 0
                            quantity = item.get('quantity') or 1
                            price = unit_price * quantity
                        
                        if 'MOTA' in brand:
                            mota_revenue += price
                
                stats['total_items'] = total_items
                stats['mota_revenue'] = mota_revenue
            
            # Sort by visit count (most visits first)
            sorted_budtenders = sorted(budtender_stats.items(), key=lambda x: x[1]['visit_count'], reverse=True)
            
            if not sorted_budtenders:
                return None
            
            # Format output
            output = """
╔══════════════════════════════════════════╗
   BUDTENDER BREAKDOWN
╚══════════════════════════════════════════╝

"""
            
            # Table header
            output += "Budtender        Visits  %    Items/Bkt  MOTA%  Avg$   MOTA$\n"
            output += "─────────────────────────────────────────────────────────\n"
            
            for seller_id, stats in sorted_budtenders[:10]:  # Top 10 budtenders
                name = stats['name'][:15]
                visits = stats['visit_count']
                pct_visits = (visits / total_customer_visits * 100) if total_customer_visits > 0 else 0
                items_per_basket = stats['total_items'] / visits if visits > 0 else 0
                mota_pct = (stats['mota_revenue'] / stats['total_revenue'] * 100) if stats['total_revenue'] > 0 else 0
                avg_basket = stats['total_revenue'] / visits if visits > 0 else 0
                mota_dollars = stats['mota_revenue']
                
                output += f"{name:<15} {visits:>3}/{total_customer_visits:<3} {pct_visits:>3.0f}%  {items_per_basket:>4.1f}     {mota_pct:>3.0f}%  ${avg_basket:>4.0f}  ${mota_dollars:>5.0f}\n"
            
            return output
            
        except Exception as e:
            print(f"Error calculating budtender breakdown: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _load_budtender_dashboard(self):
        """Load and display budtender performance metrics (last 30 days)"""
        try:
            from datetime import datetime, timedelta
            
            # Clear existing data
            for item in self.budtender_tree.get_children():
                self.budtender_tree.delete(item)
            
            self.status_label.config(text="Loading budtender metrics...")
            self.root.update()
            
            # Get transactions from last 30 days
            thirty_days_ago = (datetime.now() - timedelta(days=30)).isoformat()
            
            trans_result = self.sb.table('transactions_blaze').select(
                'transaction_id, seller_id, date, total_amount, customer_id'
            ).eq('blaze_status', 'Completed').gte('date', thirty_days_ago).execute()
            
            if not trans_result.data:
                self.store_stats_label.config(text="No transaction data in last 30 days")
                return
            
            # Group by budtender
            budtender_data = {}
            all_transaction_ids = []
            
            for trans in trans_result.data:
                seller_id = trans.get('seller_id')
                if not seller_id:
                    continue
                
                trans_id = trans['transaction_id']
                all_transaction_ids.append(trans_id)
                
                if seller_id not in budtender_data:
                    budtender_data[seller_id] = {
                        'transactions': [],
                        'total_amount': 0,
                        'transaction_ids': []
                    }
                
                budtender_data[seller_id]['transactions'].append(trans)
                budtender_data[seller_id]['total_amount'] += (trans.get('total_amount') or 0)
                budtender_data[seller_id]['transaction_ids'].append(trans_id)
            
            # Get items for all transactions (batch query)
            items_by_transaction = {}
            for i in range(0, len(all_transaction_ids), 500):
                batch_ids = all_transaction_ids[i:i+500]
                items_result = self.sb.table('transaction_items_blaze').select(
                    'transaction_id, brand, category, quantity, total_price, unit_price, product_name'
                ).in_('transaction_id', batch_ids).execute()
                
                for item in items_result.data:
                    trans_id = item['transaction_id']
                    if trans_id not in items_by_transaction:
                        items_by_transaction[trans_id] = []
                    items_by_transaction[trans_id].append(item)
            
            # DEDUPE items for each transaction and skip recycling fees!
            for trans_id in items_by_transaction:
                items = items_by_transaction[trans_id]
                # Dedupe
                items = self._dedupe_items(items)
                # Skip FEES category
                items = [item for item in items if (item.get('category') or '') != 'FEES']
                items_by_transaction[trans_id] = items
            
            # Calculate metrics for each budtender
            budtender_metrics = []
            
            for seller_id, data in budtender_data.items():
                metrics = self._calculate_budtender_metrics(
                    seller_id,
                    data['transactions'],
                    data['transaction_ids'],
                    items_by_transaction
                )
                if metrics:
                    budtender_metrics.append(metrics)
            
            # Calculate store averages
            if budtender_metrics:
                store_avg_value = sum(m['avg_value'] for m in budtender_metrics) / len(budtender_metrics)
                store_avg_items = sum(m['items_per_trans'] for m in budtender_metrics) / len(budtender_metrics)
                store_avg_mota = sum(m['mota_percent'] for m in budtender_metrics) / len(budtender_metrics)
                total_transactions = sum(m['transaction_count'] for m in budtender_metrics)
                total_revenue = sum(m['total_revenue'] for m in budtender_metrics)
            else:
                store_avg_value = 0
                store_avg_items = 0
                store_avg_mota = 0
                total_transactions = 0
                total_revenue = 0
            
            # Sort by transaction count (most active first)
            budtender_metrics.sort(key=lambda x: x['transaction_count'], reverse=True)
            
            # Display budtenders
            for metrics in budtender_metrics:
                # Determine performance tags
                tags = []
                
                # Check if active (transaction in last 30 mins)
                if metrics['is_active']:
                    tags.append('active')
                # Performance vs average
                elif metrics['items_per_trans'] >= store_avg_items and metrics['mota_percent'] >= store_avg_mota:
                    tags.append('above_avg')
                elif metrics['items_per_trans'] < store_avg_items or metrics['mota_percent'] < store_avg_mota:
                    tags.append('below_avg')
                else:
                    tags.append('normal')
                
                # Format values
                vs_store = f"Items: {metrics['items_per_trans'] - store_avg_items:+.1f} | MOTA: {metrics['mota_percent'] - store_avg_mota:+.0f}%"
                shift_status = "🟢 ACTIVE" if metrics['is_active'] else f"Idle ({metrics['minutes_since_last']:.0f}m)"
                
                values = (
                    metrics['budtender_name'],
                    metrics['transaction_count'],
                    f"${metrics['avg_value']:.2f}",
                    f"{metrics['items_per_trans']:.1f}",
                    f"{metrics['mota_percent']:.0f}%",
                    vs_store,
                    shift_status
                )
                
                self.budtender_tree.insert('', tk.END, values=values, tags=tags)
            
            # Update store stats
            self.store_stats_label.config(
                text=f"Store Totals (30d): {total_transactions} transactions | ${total_revenue:,.2f} revenue | "
                     f"Avg: ${store_avg_value:.2f} | Items/Trans: {store_avg_items:.1f} | MOTA: {store_avg_mota:.0f}%"
            )
            
            # Update last refresh time
            now = datetime.now()
            self.last_update_label.config(text=f"Last update: {now.strftime('%I:%M:%S %p')}")
            self.status_label.config(text=f"Loaded {len(budtender_metrics)} budtenders")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load budtender dashboard:\n{str(e)}")
            self.status_label.config(text="ERROR loading dashboard")
            print(f"Dashboard error: {e}")
            import traceback
            traceback.print_exc()
    
    def _calculate_budtender_metrics(self, seller_id, transactions, transaction_ids, items_by_transaction):
        """Calculate metrics for a single budtender"""
        try:
            from datetime import datetime
            
            budtender_name = self._get_seller_name(seller_id)
            
            if not transactions:
                return None
            
            # Basic stats
            transaction_count = len(transactions)
            total_revenue = sum((t.get('total_amount') or 0) for t in transactions)
            avg_value = total_revenue / transaction_count if transaction_count > 0 else 0
            
            # Items per transaction
            total_items = 0
            total_mota_revenue = 0
            
            for trans_id in transaction_ids:
                items = items_by_transaction.get(trans_id, [])
                
                # Count distinct products (SKUs)
                unique_products = set()
                for item in items:
                    product = item.get('product_name', 'Unknown')
                    unique_products.add(product)
                
                total_items += len(unique_products)
                
                # Calculate MOTA revenue
                for item in items:
                    brand = (item.get('brand') or '').upper()
                    
                    # Calculate price
                    price = item.get('total_price')
                    if price is None or price == 0:
                        unit_price = item.get('unit_price') or 0
                        quantity = item.get('quantity') or 1
                        price = unit_price * quantity
                    
                    if 'MOTA' in brand:
                        total_mota_revenue += price
            
            items_per_trans = total_items / transaction_count if transaction_count > 0 else 0
            mota_percent = (total_mota_revenue / total_revenue * 100) if total_revenue > 0 else 0
            
            # Check if active (last transaction in last 30 minutes)
            latest_trans = max(transactions, key=lambda t: t.get('date', ''))
            latest_date = latest_trans.get('date')
            
            is_active = False
            minutes_since_last = 9999
            
            if latest_date:
                try:
                    latest_dt = datetime.fromisoformat(latest_date.replace('Z', '+00:00'))
                    now = datetime.now(latest_dt.tzinfo)
                    minutes_since_last = (now - latest_dt).total_seconds() / 60
                    is_active = minutes_since_last <= 30
                except:
                    pass
            
            return {
                'seller_id': seller_id,
                'budtender_name': budtender_name,
                'transaction_count': transaction_count,
                'total_revenue': total_revenue,
                'avg_value': avg_value,
                'items_per_trans': items_per_trans,
                'mota_percent': mota_percent,
                'is_active': is_active,
                'minutes_since_last': minutes_since_last
            }
            
        except Exception as e:
            print(f"Error calculating metrics for {seller_id}: {e}")
            return None
    
    def _start_auto_refresh(self):
        """Start auto-refresh timer (60 seconds)"""
        self._stop_auto_refresh()  # Clear any existing timer
        
        if self.auto_refresh_var.get():
            self.auto_refresh_id = self.root.after(60000, self._auto_refresh_callback)
            self.live_status_label.config(text="● LIVE", fg="#00ff00")
    
    def _stop_auto_refresh(self):
        """Stop auto-refresh timer"""
        if self.auto_refresh_id:
            self.root.after_cancel(self.auto_refresh_id)
            self.auto_refresh_id = None
        self.live_status_label.config(text="● PAUSED", fg="#ff6b6b")
    
    def _toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        if self.auto_refresh_var.get():
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
    
    def _auto_refresh_callback(self):
        """Callback for auto-refresh timer"""
        self._load_budtender_dashboard()
        self._start_auto_refresh()  # Schedule next refresh

def main():
    root = tk.Tk()
    app = BlazeCustomerViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

