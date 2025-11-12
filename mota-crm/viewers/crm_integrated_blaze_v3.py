#!/usr/bin/env python3
"""
IC Viewer - BLAZE v3
PROPER 3-PANEL LAYOUT with live-calculated fields and full transaction drill-down
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

# ALL AVAILABLE COLUMNS with calculated fields
CUSTOMER_COLUMNS = {
    "FirstName": {"label": "First Name", "width": 100, "db_field": "first_name"},
    "LastName": {"label": "Last Name", "width": 120, "db_field": "last_name"},
    "MiddleName": {"label": "Middle", "width": 80, "db_field": "middle_name"},
    "DOB": {"label": "Date of Birth", "width": 90, "db_field": "date_of_birth"},
    "Phone": {"label": "Phone", "width": 110, "db_field": "phone"},
    "Email": {"label": "Email", "width": 150, "db_field": "email"},
    "Medical": {"label": "Medical", "width": 60, "db_field": "is_medical"},
    "TextOptIn": {"label": "SMS Opt-In", "width": 70, "db_field": "text_opt_in"},
    "EmailOptIn": {"label": "Email Opt-In", "width": 80, "db_field": "email_opt_in"},
    "EmailVerified": {"label": "Email Verified", "width": 90, "db_field": "email_verified"},
    "Loyalty": {"label": "Loyalty Pts", "width": 80, "db_field": "loyalty_points"},
    "Visits": {"label": "Visits", "width": 50, "db_field": "total_visits", "calculated": True},
    "Lifetime": {"label": "Lifetime $", "width": 80, "db_field": "lifetime_value", "calculated": True},
    "VIP": {"label": "VIP Status", "width": 70, "db_field": "vip_status"},
    "LastVisit": {"label": "Last Visit", "width": 100, "db_field": "last_visited"},
    "DateJoined": {"label": "Date Joined", "width": 100, "db_field": "date_joined"},
    "MemberStatus": {"label": "Status", "width": 70, "db_field": "member_status"},
    "MemberGroup": {"label": "Member Group", "width": 100, "db_field": "member_group_name"},
    "ConsumerType": {"label": "Consumer Type", "width": 100, "db_field": "consumer_type"},
    "ReferralCode": {"label": "Referral Code", "width": 100, "db_field": "referral_code"},
    "MarketingSource": {"label": "Mktg Source", "width": 100, "db_field": "marketing_source"},
    "City": {"label": "City", "width": 100, "db_field": "city"},
    "State": {"label": "State", "width": 50, "db_field": "state"},
    "ZipCode": {"label": "Zip", "width": 70, "db_field": "zip_code"},
}

class BlazeCustomerViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("IC Viewer - BLAZE v3 (Fixed)")
        self.root.geometry("2600x1200")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        self.dark_panel = "#2a2a2a"
        
        self.root.configure(bg=self.bg_color)
        
        # Data
        self.customers = []
        self.current_customer = None
        self.calculated_fields = {}  # Cache for calculated fields
        
        # Load config
        self.config = self._load_config()
        
        self._create_ui()
        self._load_customers()
    
    def _load_config(self):
        """Load viewer configuration"""
        default_config = {
            "filters": {
                "has_email": True,
                "has_phone": True,
                "last_visited": True,
                "days": 180
            },
            "visible_columns": {
                "customers": ["FirstName", "LastName", "DOB", "Phone", "Email", "TextOptIn", "Visits", "Lifetime", "VIP", "LastVisit"]
            },
            "column_widths": {}
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
        """Save viewer configuration"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def _create_ui(self):
        """Create 3-panel layout UI"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            title_frame,
            text="IC VIEWER - BLAZE v3 (PROPER LAYOUT)",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        # Filters
        filter_frame = tk.Frame(main_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.filter_email = tk.BooleanVar(value=self.config["filters"]["has_email"])
        self.filter_phone = tk.BooleanVar(value=self.config["filters"]["has_phone"])
        self.filter_recent = tk.BooleanVar(value=self.config["filters"]["last_visited"])
        
        tk.Checkbutton(
            filter_frame,
            text="Has Email",
            variable=self.filter_email,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            font=("Arial", 11),
            command=self._save_filter_state
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Checkbutton(
            filter_frame,
            text="Has Phone",
            variable=self.filter_phone,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            font=("Arial", 11),
            command=self._save_filter_state
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Checkbutton(
            filter_frame,
            text="Last Visited Within:",
            variable=self.filter_recent,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            font=("Arial", 11),
            command=self._save_filter_state
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.days_var = tk.StringVar(value=str(self.config["filters"]["days"]))
        days_entry = tk.Entry(filter_frame, textvariable=self.days_var, width=5, font=("Arial", 11))
        days_entry.pack(side=tk.LEFT, padx=(0, 5))
        days_entry.bind('<Return>', lambda e: self._apply_filters())
        days_entry.bind('<FocusOut>', lambda e: self._save_filter_state())
        
        tk.Label(filter_frame, text="days", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Button(
            filter_frame,
            text="Apply Filters",
            command=self._apply_filters,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            filter_frame,
            text="Select Columns",
            command=self._show_column_selector,
            bg="#444444",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        tk.Button(
            filter_frame,
            text="Save Layout",
            command=self._save_layout,
            bg="#666666",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        self.stats_label = tk.Label(
            filter_frame,
            text="Loading...",
            bg=self.bg_color,
            fg="#00ff00",
            font=("Arial", 11, "bold")
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # Search
        search_frame = tk.Frame(main_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 11))
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_search)
        
        # 3-PANEL LAYOUT: Left | (Right Top / Right Bottom)
        content_paned = tk.PanedWindow(main_frame, orient=tk.HORIZONTAL, bg=self.bg_color, sashwidth=5)
        content_paned.pack(fill=tk.BOTH, expand=True)
        
        # LEFT PANEL: Customers
        self._create_customers_panel(content_paned)
        
        # RIGHT PANEL: (Transactions / Details+Items+Brand)
        right_paned = tk.PanedWindow(content_paned, orient=tk.VERTICAL, bg=self.bg_color, sashwidth=5)
        content_paned.add(right_paned)
        
        # RIGHT TOP: Transactions
        self._create_transactions_panel(right_paned)
        
        # RIGHT BOTTOM: (Items + Details + Brand) - 3 columns
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
    
    def _create_customers_panel(self, parent):
        """Create customers panel"""
        left_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(left_frame, width=900)
        
        tk.Label(
            left_frame,
            text="CUSTOMERS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        cust_tree_frame = tk.Frame(left_frame, bg=self.bg_color)
        cust_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cust_scroll_y = tk.Scrollbar(cust_tree_frame)
        cust_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        cust_scroll_x = tk.Scrollbar(cust_tree_frame, orient=tk.HORIZONTAL)
        cust_scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        
        visible_cols = self.config["visible_columns"]["customers"]
        self.cust_tree = ttk.Treeview(
            cust_tree_frame,
            columns=tuple(visible_cols),
            show="headings",
            yscrollcommand=cust_scroll_y.set,
            xscrollcommand=cust_scroll_x.set
        )
        
        for col in visible_cols:
            col_info = CUSTOMER_COLUMNS[col]
            self.cust_tree.heading(col, text=col_info["label"], command=lambda c=col: self._sort_column(c))
            width = self.config["column_widths"].get("customers", {}).get(col, col_info["width"])
            self.cust_tree.column(col, width=width)
        
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_scroll_y.config(command=self.cust_tree.yview)
        cust_scroll_x.config(command=self.cust_tree.xview)
        
        self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)
    
    def _create_transactions_panel(self, parent):
        """Create transactions panel"""
        trans_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(trans_frame, height=350)
        
        tk.Label(
            trans_frame,
            text="TRANSACTIONS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        trans_tree_frame = tk.Frame(trans_frame, bg=self.bg_color)
        trans_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll = tk.Scrollbar(trans_tree_frame)
        trans_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_tree = ttk.Treeview(
            trans_tree_frame,
            columns=("Date", "Amount", "Tax", "Payment", "Budtender", "Status"),
            show="headings",
            yscrollcommand=trans_scroll.set
        )
        
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Tax", text="Tax")
        self.trans_tree.heading("Payment", text="Payment")
        self.trans_tree.heading("Budtender", text="Budtender")
        self.trans_tree.heading("Status", text="Status")
        
        self.trans_tree.column("Date", width=100)
        self.trans_tree.column("Amount", width=80)
        self.trans_tree.column("Tax", width=70)
        self.trans_tree.column("Payment", width=90)
        self.trans_tree.column("Budtender", width=120)
        self.trans_tree.column("Status", width=90)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll.config(command=self.trans_tree.yview)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
    
    def _create_items_panel(self, parent):
        """Create transaction items panel"""
        items_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(items_frame, width=400)
        
        tk.Label(
            items_frame,
            text="TRANSACTION ITEMS",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        items_tree_frame = tk.Frame(items_frame, bg=self.bg_color)
        items_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        items_scroll = tk.Scrollbar(items_tree_frame)
        items_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree = ttk.Treeview(
            items_tree_frame,
            columns=("Product", "Brand", "Qty", "Price"),
            show="headings",
            yscrollcommand=items_scroll.set
        )
        
        self.items_tree.heading("Product", text="Product")
        self.items_tree.heading("Brand", text="Brand")
        self.items_tree.heading("Qty", text="Qty")
        self.items_tree.heading("Price", text="Price")
        
        self.items_tree.column("Product", width=180)
        self.items_tree.column("Brand", width=100)
        self.items_tree.column("Qty", width=50)
        self.items_tree.column("Price", width=70)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scroll.config(command=self.items_tree.yview)
    
    def _create_details_panel(self, parent):
        """Create customer details panel"""
        detail_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(detail_frame, width=400)
        
        tk.Label(
            detail_frame,
            text="CUSTOMER DETAILS",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        detail_scroll_frame = tk.Frame(detail_frame, bg=self.dark_panel)
        detail_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        detail_scroll = tk.Scrollbar(detail_scroll_frame)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(
            detail_scroll_frame,
            bg=self.dark_panel,
            fg=self.fg_color,
            font=("Courier New", 9),
            yscrollcommand=detail_scroll.set,
            wrap=tk.WORD
        )
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.config(command=self.detail_text.yview)
    
    def _create_brand_panel(self, parent):
        """Create revenue by brand panel"""
        brand_frame = tk.Frame(parent, bg=self.bg_color)
        parent.add(brand_frame, width=400)
        
        tk.Label(
            brand_frame,
            text="REVENUE BY BRAND",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        brand_scroll_frame = tk.Frame(brand_frame, bg=self.dark_panel)
        brand_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        brand_scroll = tk.Scrollbar(brand_scroll_frame)
        brand_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.brand_tree = ttk.Treeview(
            brand_scroll_frame,
            columns=("Brand", "Revenue", "Count", "Avg"),
            show="headings",
            yscrollcommand=brand_scroll.set
        )
        
        self.brand_tree.heading("Brand", text="Brand")
        self.brand_tree.heading("Revenue", text="Revenue")
        self.brand_tree.heading("Count", text="Count")
        self.brand_tree.heading("Avg", text="Avg Sale")
        
        self.brand_tree.column("Brand", width=150)
        self.brand_tree.column("Revenue", width=90)
        self.brand_tree.column("Count", width=60)
        self.brand_tree.column("Avg", width=80)
        
        # Dark theme for treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", background=self.dark_panel, foreground=self.fg_color, fieldbackground=self.dark_panel)
        
        self.brand_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        brand_scroll.config(command=self.brand_tree.yview)
    
    def _show_column_selector(self):
        """Show column selector dialog"""
        dialog = Toplevel(self.root)
        dialog.title("Select Columns")
        dialog.geometry("400x600")
        dialog.configure(bg=self.bg_color)
        
        tk.Label(
            dialog,
            text="Select columns to display:",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=10)
        
        canvas = tk.Canvas(dialog, bg=self.bg_color)
        scrollbar = tk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        col_vars = {}
        visible = self.config["visible_columns"]["customers"]
        
        for col_id, col_info in CUSTOMER_COLUMNS.items():
            var = tk.BooleanVar(value=col_id in visible)
            col_vars[col_id] = var
            
            label_text = col_info["label"]
            if col_info.get("calculated"):
                label_text += " (LIVE)"
            
            tk.Checkbutton(
                scrollable_frame,
                text=label_text,
                variable=var,
                bg=self.bg_color,
                fg=self.fg_color,
                selectcolor=self.bg_color,
                font=("Arial", 11)
            ).pack(anchor=tk.W, padx=20, pady=2)
        
        canvas.pack(side="left", fill="both", expand=True, padx=10)
        scrollbar.pack(side="right", fill="y")
        
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        def apply_columns():
            new_visible = [col_id for col_id, var in col_vars.items() if var.get()]
            self.config["visible_columns"]["customers"] = new_visible
            self._save_config()
            dialog.destroy()
            messagebox.showinfo("Success", "Columns updated! Reloading...")
            self._reload_ui()
        
        tk.Button(
            button_frame,
            text="Apply",
            command=apply_columns,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 11, "bold"),
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#666666",
            fg="white",
            font=("Arial", 11),
            padx=20
        ).pack(side=tk.LEFT, padx=5)
    
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
    
    def _save_layout(self):
        """Save column widths"""
        widths = {}
        for col in self.config["visible_columns"]["customers"]:
            widths[col] = self.cust_tree.column(col, "width")
        
        if "customers" not in self.config["column_widths"]:
            self.config["column_widths"] = {}
        self.config["column_widths"]["customers"] = widths
        
        self._save_config()
        messagebox.showinfo("Saved", "Layout saved successfully!")
    
    def _reload_ui(self):
        """Reload UI after column changes"""
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        visible_cols = self.config["visible_columns"]["customers"]
        self.cust_tree["columns"] = tuple(visible_cols)
        
        for col in visible_cols:
            col_info = CUSTOMER_COLUMNS[col]
            self.cust_tree.heading(col, text=col_info["label"], command=lambda c=col: self._sort_column(c))
            width = self.config["column_widths"].get("customers", {}).get(col, col_info["width"])
            self.cust_tree.column(col, width=width)
        
        self._load_customers()
    
    def _apply_filters(self):
        """Apply filters"""
        self._save_filter_state()
        self._load_customers()
    
    def _calculate_customer_fields(self, member_id):
        """Calculate visits and lifetime value from transactions"""
        if member_id in self.calculated_fields:
            return self.calculated_fields[member_id]
        
        try:
            result = self.sb.table('transactions_blaze').select('total_amount', count='exact').eq('customer_id', member_id).eq('blaze_status', 'Completed').execute()
            
            visits = result.count or 0
            lifetime = sum([t.get('total_amount', 0) or 0 for t in result.data])
            
            self.calculated_fields[member_id] = {"visits": visits, "lifetime": lifetime}
            return self.calculated_fields[member_id]
        except:
            return {"visits": 0, "lifetime": 0}
    
    def _load_customers(self):
        """Load customers with live-calculated fields"""
        import time
        from datetime import datetime, timedelta
        start = time.time()
        
        try:
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            self.calculated_fields = {}  # Clear cache
            self.status_label.config(text="Loading...")
            self.root.update()
            
            visible_cols = self.config["visible_columns"]["customers"]
            db_fields = set()
            db_fields.add("member_id")
            
            for col in visible_cols:
                db_fields.add(CUSTOMER_COLUMNS[col]["db_field"])
            
            query = self.sb.table('customers_blaze').select(','.join(db_fields))
            
            if self.filter_email.get():
                query = query.neq('email', None).neq('email', '')
            
            if self.filter_phone.get():
                query = query.neq('phone', None).neq('phone', '')
            
            if self.filter_recent.get():
                try:
                    days = int(self.days_var.get())
                    cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
                    query = query.gte('last_visited', cutoff_date)
                except:
                    pass
            
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = query.order('last_name').range(offset, offset + page_size - 1).execute()
                if not result.data:
                    break
                all_customers.extend(result.data)
                offset += page_size
                self.status_label.config(text=f"Loading... {len(all_customers)}")
                self.root.update()
                if len(result.data) < page_size:
                    break
            
            self.customers = all_customers
            
            # Display with calculated fields
            for cust in self.customers:
                member_id = cust.get('member_id')
                calc = self._calculate_customer_fields(member_id)
                
                values = []
                for col in visible_cols:
                    col_info = CUSTOMER_COLUMNS[col]
                    
                    # Use calculated fields if available
                    if col == "Visits":
                        val = calc["visits"]
                    elif col == "Lifetime":
                        val = f"${calc['lifetime']:.2f}"
                    else:
                        db_field = col_info["db_field"]
                        val = cust.get(db_field)
                        
                        if val is None:
                            val = "N/A"
                        elif col in ["Medical", "TextOptIn", "EmailOptIn", "EmailVerified"]:
                            val = "Yes" if val else "No"
                        elif col == "Loyalty":
                            val = f"{val:.0f}"
                        elif col == "Phone" and len(str(val)) > 14:
                            val = str(val)[:14]
                        else:
                            val = str(val)
                    
                    values.append(val)
                
                self.cust_tree.insert('', tk.END, values=tuple(values), iid=member_id)
            
            elapsed = time.time() - start
            
            filters = []
            if self.filter_email.get(): filters.append("Email")
            if self.filter_phone.get(): filters.append("Phone")
            if self.filter_recent.get(): filters.append(f"<{self.days_var.get()}d")
            
            filter_text = " + ".join(filters) if filters else "No filters"
            self.stats_label.config(text=f"{len(self.customers)} customers ({filter_text}) - {elapsed:.2f}s")
            self.status_label.config(text="Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
            self.status_label.config(text="ERROR")
    
    def _sort_column(self, col):
        """Sort column"""
        items = [(self.cust_tree.set(item, col), item) for item in self.cust_tree.get_children('')]
        
        try:
            items.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '').replace('N/A', '0')))
        except:
            items.sort(key=lambda x: x[0].lower())
        
        for index, (val, item) in enumerate(items):
            self.cust_tree.move(item, '', index)
    
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
        """Transaction selected - load items"""
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        self._load_transaction_items(transaction_id)
    
    def _load_transactions(self, member_id):
        """Load transactions with budtender info"""
        try:
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            result = self.sb.table('transactions_blaze').select(
                'transaction_id, date, total_amount, total_tax, payment_type, blaze_status, seller_id'
            ).eq('customer_id', member_id).order('date', desc=True).limit(100).execute()
            
            for trans in result.data:
                # Get budtender name from seller_id (for now show ID)
                seller_id = trans.get('seller_id', 'Unknown')
                
                self.trans_tree.insert('', tk.END, values=(
                    trans.get('date', 'N/A')[:10],
                    f"${trans.get('total_amount', 0):.2f}",
                    f"${trans.get('total_tax', 0):.2f}",
                    trans.get('payment_type', 'N/A'),
                    seller_id,
                    trans.get('blaze_status', 'N/A')
                ), iid=trans['transaction_id'])
        
        except Exception as e:
            print(f"Failed to load transactions: {e}")
    
    def _load_transaction_items(self, transaction_id):
        """Load items for selected transaction"""
        try:
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            result = self.sb.table('transaction_items_blaze').select(
                'product_name, brand, quantity, total_price'
            ).eq('transaction_id', transaction_id).execute()
            
            for item in result.data:
                self.items_tree.insert('', tk.END, values=(
                    item.get('product_name', 'N/A'),
                    item.get('brand', 'N/A'),
                    f"{item.get('quantity', 0):.1f}",
                    f"${item.get('total_price', 0):.2f}"
                ))
        
        except Exception as e:
            print(f"Failed to load items: {e}")
    
    def _display_customer_details(self):
        """Display customer details"""
        self.detail_text.delete('1.0', tk.END)
        
        if not self.current_customer:
            return
        
        c = self.current_customer
        calc = self.calculated_fields.get(c.get('member_id'), {"visits": 0, "lifetime": 0})
        
        details = f"""
═══════════════════════════════════════
        CUSTOMER PROFILE (BLAZE)
═══════════════════════════════════════

📝 BASIC:
   Name: {c.get('first_name', '')} {c.get('last_name', '')}
   DOB: {c.get('date_of_birth', 'N/A')}
   Phone: {c.get('phone', 'N/A')}
   Email: {c.get('email', 'N/A')}

📍 ADDRESS:
   {c.get('street_address', 'N/A')}
   {c.get('city', 'N/A')}, {c.get('state', 'N/A')} {c.get('zip_code', 'N/A')}

🏥 STATUS:
   Medical: {'Yes' if c.get('is_medical') else 'No'}
   Status: {c.get('member_status', 'N/A')}

📱 PREFS:
   SMS: {'Yes' if c.get('text_opt_in') else 'No'}
   Email: {'Yes' if c.get('email_opt_in') else 'No'}

⭐ STATS (LIVE):
   Visits: {calc['visits']}
   Lifetime: ${calc['lifetime']:.2f}
   VIP: {c.get('vip_status', 'N/A')}

📅 DATES:
   Joined: {c.get('date_joined', 'N/A')}
   Last Visit: {c.get('last_visited', 'N/A')}
═══════════════════════════════════════
"""
        
        self.detail_text.insert('1.0', details)
    
    def _load_brand_analysis(self, member_id):
        """Load revenue by brand"""
        try:
            for item in self.brand_tree.get_children():
                self.brand_tree.delete(item)
            
            trans_result = self.sb.table('transactions_blaze').select('transaction_id').eq('customer_id', member_id).execute()
            
            if not trans_result.data:
                return
            
            trans_ids = [t['transaction_id'] for t in trans_result.data]
            
            brand_data = {}
            for i in range(0, len(trans_ids), 100):
                batch_ids = trans_ids[i:i+100]
                items_result = self.sb.table('transaction_items_blaze').select('brand, total_price').in_('transaction_id', batch_ids).execute()
                
                for item in items_result.data:
                    brand = item.get('brand') or 'Unknown'
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
    
    def _on_search(self, event):
        """Live search"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self._load_customers()
            return
        
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        visible_cols = self.config["visible_columns"]["customers"]
        matches = 0
        
        for cust in self.customers:
            search_fields = [
                str(cust.get('first_name', '')).lower(),
                str(cust.get('last_name', '')).lower(),
                str(cust.get('phone', '')).lower(),
                str(cust.get('email', '')).lower()
            ]
            
            if any(search_term in field for field in search_fields):
                member_id = cust.get('member_id')
                calc = self.calculated_fields.get(member_id, {"visits": 0, "lifetime": 0})
                
                values = []
                for col in visible_cols:
                    if col == "Visits":
                        val = calc["visits"]
                    elif col == "Lifetime":
                        val = f"${calc['lifetime']:.2f}"
                    else:
                        db_field = CUSTOMER_COLUMNS[col]["db_field"]
                        val = cust.get(db_field)
                        
                        if val is None:
                            val = "N/A"
                        elif col in ["Medical", "TextOptIn", "EmailOptIn"]:
                            val = "Yes" if val else "No"
                        elif col == "Loyalty":
                            val = f"{val:.0f}"
                        else:
                            val = str(val)
                        
                        values.append(val)
                
                self.cust_tree.insert('', tk.END, values=tuple(values), iid=member_id)
                matches += 1
        
        self.status_label.config(text=f"Found {matches} matches")

def main():
    root = tk.Tk()
    app = BlazeCustomerViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

