#!/usr/bin/env python3
"""
IC Viewer - BLAZE API EDITION
Connected to: customers_blaze (131K+ customers with FULL DATA)
NEW FIELDS: DOB, First/Last Name, Actual Loyalty Points, Tags, Preferences, Notes
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from supabase import create_client, Client
from datetime import datetime
import json

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class BlazeCustomerViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("IC Viewer - BLAZE API EDITION (131K+ Customers)")
        self.root.geometry("2400x1200")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        self.success_color = "#00ff00"
        
        self.root.configure(bg=self.bg_color)
        
        # Data
        self.customers = []
        self.current_customer = None
        
        self._create_ui()
        self._load_customers()
    
    def _create_ui(self):
        """Create reorganized UI"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            title_frame,
            text="IC VIEWER - BLAZE API EDITION (131K+ CUSTOMERS)",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        self.perf_label = tk.Label(
            title_frame,
            text="🔥 BLAZE POWERED",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.success_color
        )
        self.perf_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Filters
        filter_frame = tk.Frame(main_frame, bg=self.bg_color)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Checkboxes
        self.filter_email = tk.BooleanVar(value=True)
        self.filter_phone = tk.BooleanVar(value=True)
        self.filter_recent = tk.BooleanVar(value=True)
        
        tk.Checkbutton(
            filter_frame,
            text="Has Email",
            variable=self.filter_email,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color,
            font=("Arial", 11),
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Checkbutton(
            filter_frame,
            text="Has Phone",
            variable=self.filter_phone,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color,
            font=("Arial", 11),
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=(0, 15))
        
        tk.Checkbutton(
            filter_frame,
            text="Last Visited Within:",
            variable=self.filter_recent,
            bg=self.bg_color,
            fg=self.fg_color,
            selectcolor=self.bg_color,
            activebackground=self.bg_color,
            activeforeground=self.accent_color,
            font=("Arial", 11),
            command=self._apply_filters
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.days_var = tk.StringVar(value="180")
        days_entry = tk.Entry(filter_frame, textvariable=self.days_var, width=5, font=("Arial", 11))
        days_entry.pack(side=tk.LEFT, padx=(0, 5))
        days_entry.bind('<Return>', lambda e: self._apply_filters())
        
        tk.Label(filter_frame, text="days", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11)).pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Button(
            filter_frame,
            text="Apply Filters",
            command=self._apply_filters,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=(0, 20))
        
        self.stats_label = tk.Label(
            filter_frame,
            text="Loading...",
            bg=self.bg_color,
            fg=self.success_color,
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
        
        tk.Button(
            search_frame,
            text="Clear Search",
            command=self._clear_search,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT)
        
        # === TOP SECTION: Customers | Transactions | Items ===
        top_frame = tk.Frame(main_frame, bg=self.bg_color, height=400)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # LEFT: Customers (40% width) - MORE COLUMNS!
        left_frame = tk.Frame(top_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="CUSTOMERS (BLAZE DATA)",
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
        
        self.cust_tree = ttk.Treeview(
            cust_tree_frame,
            columns=("FirstName", "LastName", "DOB", "Phone", "Email", "Medical", "Loyalty", "Visits", "Lifetime", "VIP", "LastVisit"),
            show="headings",
            yscrollcommand=cust_scroll_y.set,
            xscrollcommand=cust_scroll_x.set
        )

        self.cust_tree.heading("FirstName", text="First Name")
        self.cust_tree.heading("LastName", text="Last Name")
        self.cust_tree.heading("DOB", text="Date of Birth")
        self.cust_tree.heading("Phone", text="Phone")
        self.cust_tree.heading("Email", text="Email")
        self.cust_tree.heading("Medical", text="Medical")
        self.cust_tree.heading("Loyalty", text="Loyalty Pts")
        self.cust_tree.heading("Visits", text="Visits")
        self.cust_tree.heading("Lifetime", text="Lifetime $")
        self.cust_tree.heading("VIP", text="VIP Status")
        self.cust_tree.heading("LastVisit", text="Last Visit")

        self.cust_tree.column("FirstName", width=100)
        self.cust_tree.column("LastName", width=120)
        self.cust_tree.column("DOB", width=90)
        self.cust_tree.column("Phone", width=110)
        self.cust_tree.column("Email", width=150)
        self.cust_tree.column("Medical", width=60)
        self.cust_tree.column("Loyalty", width=80)
        self.cust_tree.column("Visits", width=50)
        self.cust_tree.column("Lifetime", width=80)
        self.cust_tree.column("VIP", width=70)
        self.cust_tree.column("LastVisit", width=100)
        
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_scroll_y.config(command=self.cust_tree.yview)
        cust_scroll_x.config(command=self.cust_tree.xview)
        
        # Bind selection and right-click
        self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)
        self.cust_tree.bind('<Button-3>', self._customer_right_click)
        
        # Make columns sortable
        for col in ("FirstName", "LastName", "DOB", "Phone", "Email", "Medical", "Loyalty", "Visits", "Lifetime", "VIP", "LastVisit"):
            self.cust_tree.heading(col, command=lambda c=col: self._sort_column(c))
        
        # MIDDLE: Transactions (30% width)
        middle_frame = tk.Frame(top_frame, bg=self.bg_color)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            middle_frame,
            text="TRANSACTIONS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        trans_tree_frame = tk.Frame(middle_frame, bg=self.bg_color)
        trans_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll_y = tk.Scrollbar(trans_tree_frame)
        trans_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_tree = ttk.Treeview(
            trans_tree_frame,
            columns=("Date", "Amount", "Payment", "Status"),
            show="headings",
            yscrollcommand=trans_scroll_y.set
        )

        self.trans_tree.heading("Date", text="Date/Time")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Payment", text="Payment")
        self.trans_tree.heading("Status", text="Status")

        self.trans_tree.column("Date", width=140)
        self.trans_tree.column("Amount", width=80)
        self.trans_tree.column("Payment", width=80)
        self.trans_tree.column("Status", width=80)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll_y.config(command=self.trans_tree.yview)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        
        # RIGHT: Transaction Items (30% width)
        right_frame = tk.Frame(top_frame, bg=self.bg_color)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="ITEMS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        items_tree_frame = tk.Frame(right_frame, bg=self.bg_color)
        items_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        items_scroll_y = tk.Scrollbar(items_tree_frame)
        items_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree = ttk.Treeview(
            items_tree_frame,
            columns=("Product", "Qty", "Price"),
            show="headings",
            yscrollcommand=items_scroll_y.set
        )

        self.items_tree.heading("Product", text="Product")
        self.items_tree.heading("Qty", text="Qty")
        self.items_tree.heading("Price", text="Price")

        self.items_tree.column("Product", width=200)
        self.items_tree.column("Qty", width=50)
        self.items_tree.column("Price", width=70)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scroll_y.config(command=self.items_tree.yview)
        
        # === BOTTOM SECTION: Customer Details ===
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            bottom_frame,
            text="CUSTOMER DETAILS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 5))
        
        detail_scroll_frame = tk.Frame(bottom_frame, bg=self.bg_color)
        detail_scroll_frame.pack(fill=tk.BOTH, expand=True)
        
        detail_scroll = tk.Scrollbar(detail_scroll_frame)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.detail_text = tk.Text(
            detail_scroll_frame,
            bg="#2a2a2a",
            fg=self.fg_color,
            font=("Courier New", 10),
            height=15,
            yscrollcommand=detail_scroll.set,
            wrap=tk.WORD
        )
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.config(command=self.detail_text.yview)
        
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
    
    def _customer_right_click(self, event):
        """Show context menu for customer"""
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="View Full Details", command=self._view_full_customer)
        menu.add_command(label="Edit Phone", command=lambda: self._edit_customer_field("phone"))
        menu.add_command(label="Edit Email", command=lambda: self._edit_customer_field("email"))
        
        menu.post(event.x_root, event.y_root)
    
    def _view_full_customer(self):
        """Show full customer data in a dialog"""
        selection = self.cust_tree.selection()
        if not selection or not self.current_customer:
            return
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Full Customer Data")
        dialog.geometry("800x600")
        dialog.configure(bg=self.bg_color)
        
        text = tk.Text(dialog, bg="#2a2a2a", fg=self.fg_color, font=("Courier New", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Show formatted JSON
        text.insert('1.0', json.dumps(self.current_customer, indent=2, default=str))
        text.config(state=tk.DISABLED)
    
    def _edit_customer_field(self, field):
        """Edit a customer field"""
        selection = self.cust_tree.selection()
        if not selection or not self.current_customer:
            return
        
        member_id = self.current_customer.get('member_id')
        current_value = self.current_customer.get(field, '')
        
        new_value = simpledialog.askstring(
            f"Edit {field.title()}",
            f"Current {field}: {current_value}\n\nEnter new value:",
            initialvalue=current_value
        )
        
        if new_value is not None and new_value != current_value:
            self._save_customer_field(member_id, field, new_value)
    
    def _save_customer_field(self, member_id, field, new_value):
        """Save customer field to Supabase"""
        try:
            result = self.sb.table('customers_blaze').update({
                field: new_value
            }).eq('member_id', member_id).execute()
            
            # Update local cache
            for cust in self.customers:
                if cust.get('member_id') == member_id:
                    cust[field] = new_value
                    break
            
            # Refresh customer list
            self._load_customers()
            
            messagebox.showinfo("Success", f"{field.replace('_', ' ').title()} updated successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update {field}:\n{str(e)}")
    
    def _apply_filters(self):
        """Apply filters and reload customers"""
        self._load_customers()
    
    def _load_customers(self):
        """Load customers from customers_blaze with filters"""
        import time
        from datetime import datetime, timedelta
        start = time.time()
        
        try:
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            self.status_label.config(text="Loading...")
            self.root.update()
            
            # Build query with filters
            query = self.sb.table('customers_blaze').select(
                'member_id, first_name, last_name, date_of_birth, phone, email, is_medical, loyalty_points, total_visits, lifetime_value, vip_status, last_visited, member_status'
            )
            
            # Apply filters
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
                    pass  # Invalid days input, skip filter
            
            # Execute query with pagination
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

            for cust in self.customers:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('first_name', 'N/A') or 'N/A',
                    cust.get('last_name', 'N/A') or 'N/A',
                    cust.get('date_of_birth', 'N/A') or 'N/A',
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('email', 'N/A') or 'N/A',
                    'Yes' if cust.get('is_medical') else 'No',
                    f"{cust.get('loyalty_points', 0):.0f}",
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}",
                    cust.get('vip_status', 'N/A') or 'N/A',
                    cust.get('last_visited', 'N/A') or 'N/A'
                ), iid=cust.get('member_id'))

            elapsed = time.time() - start
            
            # Show filter summary
            filters = []
            if self.filter_email.get():
                filters.append("Email")
            if self.filter_phone.get():
                filters.append("Phone")
            if self.filter_recent.get():
                filters.append(f"<{self.days_var.get()}d")
            
            filter_text = " + ".join(filters) if filters else "No filters"
            self.stats_label.config(text=f"{len(self.customers)} customers ({filter_text}) - {elapsed:.2f}s")
            self.status_label.config(text=f"Ready")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
            self.status_label.config(text="ERROR loading customers")
    
    def _sort_column(self, col):
        """Sort treeview by column"""
        # Get all items
        items = [(self.cust_tree.set(item, col), item) for item in self.cust_tree.get_children('')]
        
        # Sort items
        try:
            # Try numeric sort first
            items.sort(key=lambda x: float(x[0].replace('$', '').replace(',', '').replace('N/A', '0')))
        except:
            # Fall back to string sort
            items.sort(key=lambda x: x[0].lower())
        
        # Rearrange items
        for index, (val, item) in enumerate(items):
            self.cust_tree.move(item, '', index)
    
    def _on_customer_select(self, event):
        """When customer is selected"""
        import time
        start = time.time()
        
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        member_id = selection[0]
        
        try:
            # Get full customer data
            result = self.sb.table('customers_blaze').select('*').eq('member_id', member_id).execute()
            self.current_customer = result.data[0] if result.data else None
            
            if self.current_customer:
                self._display_customer_details()
                self._load_transactions(member_id)
            
            elapsed = time.time() - start
            self.stats_label.config(text=f"Loaded customer in {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer:\n{str(e)}")
    
    def _display_customer_details(self):
        """Display customer details in text area"""
        self.detail_text.delete('1.0', tk.END)
        
        if not self.current_customer:
            return
        
        c = self.current_customer
        
        details = f"""
═══════════════════════════════════════════════════════════════
                    CUSTOMER PROFILE (BLAZE API)
═══════════════════════════════════════════════════════════════

📝 BASIC INFO:
   Name: {c.get('first_name', '')} {c.get('middle_name', '')} {c.get('last_name', '')}
   Date of Birth: {c.get('date_of_birth', 'N/A')}
   Member ID: {c.get('member_id', 'N/A')}
   Phone: {c.get('phone', 'N/A')}
   Email: {c.get('email', 'N/A')}

📍 ADDRESS:
   Street: {c.get('street_address', 'N/A')}
   City: {c.get('city', 'N/A')}
   State: {c.get('state', 'N/A')}
   Zip: {c.get('zip_code', 'N/A')}

🏥 STATUS:
   Medical: {'Yes' if c.get('is_medical') else 'No'}
   Member Status: {c.get('member_status', 'N/A')}
   Member Group: {c.get('member_group_name', 'N/A')}
   Consumer Type: {c.get('consumer_type', 'N/A')}

📱 PREFERENCES:
   Text Opt-In: {'Yes' if c.get('text_opt_in') else 'No'}
   Email Opt-In: {'Yes' if c.get('email_opt_in') else 'No'}
   Email Verified: {'Yes' if c.get('email_verified') else 'No'}

⭐ LOYALTY & ANALYTICS:
   Loyalty Points: {c.get('loyalty_points', 0):.0f}
   VIP Status: {c.get('vip_status', 'N/A')}
   Total Visits: {c.get('total_visits', 0)}
   Lifetime Value: ${c.get('lifetime_value', 0):.2f}
   Churn Risk: {c.get('churn_risk', 'N/A')}

📅 DATES:
   Date Joined: {c.get('date_joined', 'N/A')}
   Last Visited: {c.get('last_visited', 'N/A')}
   Days Since Last Visit: {c.get('days_since_last_visit', 'N/A')}

🔖 TAGS:
   {', '.join(c.get('tags', [])) if c.get('tags') else 'None'}

🔗 REFERRAL:
   Referral Code: {c.get('referral_code', 'N/A')}
   Marketing Source: {c.get('marketing_source', 'N/A')}

═══════════════════════════════════════════════════════════════
"""
        
        self.detail_text.insert('1.0', details)
    
    def _load_transactions(self, member_id):
        """Load transactions for selected customer"""
        try:
            # Clear existing items
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            self.status_label.config(text=f"Loading transactions for customer...")
            self.root.update()
            
            # Query transactions_blaze
            result = self.sb.table('transactions_blaze').select(
                'transaction_id, date, total_amount, payment_type, blaze_status'
            ).eq('customer_id', member_id).order('date', desc=True).limit(100).execute()
            
            for trans in result.data:
                self.trans_tree.insert('', tk.END, values=(
                    trans.get('date', 'N/A')[:19] if trans.get('date') else 'N/A',
                    f"${trans.get('total_amount', 0):.2f}",
                    trans.get('payment_type', 'N/A') or 'N/A',
                    trans.get('blaze_status', 'N/A') or 'N/A'
                ), iid=trans.get('transaction_id'))
            
            self.status_label.config(text=f"Loaded {len(result.data)} transactions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions:\n{str(e)}")
    
    def _on_transaction_select(self, event):
        """When transaction is selected"""
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        self._load_transaction_items(transaction_id)
    
    def _load_transaction_items(self, transaction_id):
        """Load items for selected transaction"""
        try:
            # Clear existing items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            self.status_label.config(text=f"Loading transaction items...")
            self.root.update()
            
            # Query transaction_items_blaze
            result = self.sb.table('transaction_items_blaze').select(
                'product_name, quantity, total_price'
            ).eq('transaction_id', transaction_id).execute()
            
            for item in result.data:
                self.items_tree.insert('', tk.END, values=(
                    item.get('product_name', 'N/A') or 'N/A',
                    f"{item.get('quantity', 0):.1f}",
                    f"${item.get('total_price', 0):.2f}"
                ))
            
            self.status_label.config(text=f"Loaded {len(result.data)} items")
            
        except Exception as e:
            self.status_label.config(text=f"No items found (transaction_items_blaze may be empty)")
    
    def _on_search(self, event):
        """Live search customers"""
        search_term = self.search_var.get().strip().lower()
        
        if not search_term:
            self._load_customers()
            return
        
        # Filter local cache
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        matches = 0
        for cust in self.customers:
            first = (cust.get('first_name') or '').lower()
            last = (cust.get('last_name') or '').lower()
            phone = (cust.get('phone') or '').lower()
            email = (cust.get('email') or '').lower()
            
            if search_term in first or search_term in last or search_term in phone or search_term in email:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('first_name', 'N/A') or 'N/A',
                    cust.get('last_name', 'N/A') or 'N/A',
                    cust.get('date_of_birth', 'N/A') or 'N/A',
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('email', 'N/A') or 'N/A',
                    'Yes' if cust.get('is_medical') else 'No',
                    f"{cust.get('loyalty_points', 0):.0f}",
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}",
                    cust.get('vip_status', 'N/A') or 'N/A',
                    cust.get('last_visited', 'N/A') or 'N/A'
                ), iid=cust.get('member_id'))
                matches += 1
        
        self.status_label.config(text=f"Found {matches} matching customers")
    
    def _clear_search(self):
        """Clear search"""
        self.search_var.set('')
        self._load_customers()

def main():
    root = tk.Tk()
    app = BlazeCustomerViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()

