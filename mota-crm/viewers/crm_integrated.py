#!/usr/bin/env python3
"""
IC Viewer - Enhanced Customer Analytics v4
EXPANDED DATA VIEW:
- Customers: ID, Name, Phone, VIP, Visits, Lifetime, Avg Sale, Churn Risk, Days Since Last Visit
- Transactions: Transaction ID, Full DateTime, Amount, Payment Type, Staff, Location, Discount, Tax
- Purchase Items: Item ID, Product, Brand, Category, Unit/Total Price, Qty, Weight, Discount, Tax
- Customer Context: Full profile with preferences and behavior analysis
- Revenue by Brand: Detailed breakdown with category analysis
+ Right-click editing for customer fields
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from supabase import create_client, Client
from datetime import datetime
from collections import Counter, defaultdict

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class EnhancedCustomerAnalytics:
    def __init__(self, root):
        self.root = root
        self.root.title("IC Viewer - Enhanced Customer Analytics v4")
        self.root.geometry("2200x1200")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        self.staff_cache = {}
        
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
            text="IC VIEWER - INTERNAL CUSTOMER SYSTEM",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        self.perf_label = tk.Label(
            title_frame,
            text="⚡ OPTIMIZED v3",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.success_color
        )
        self.perf_label.pack(side=tk.RIGHT, padx=(10, 0))
        
        # Search
        search_frame = tk.Frame(main_frame, bg=self.bg_color)
        search_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(search_frame, text="Search Customer:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 12)).pack(side=tk.LEFT, padx=(0, 10))
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30, font=("Arial", 12))
        search_entry.pack(side=tk.LEFT, padx=(0, 10))
        search_entry.bind('<KeyRelease>', self._on_search)
        
        tk.Button(
            search_frame,
            text="Clear",
            command=self._clear_search,
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(
            search_frame,
            text="Query time: --",
            bg=self.bg_color,
            fg=self.success_color,
            font=("Arial", 10)
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # === TOP SECTION: Customers | Transactions | Items ===
        top_frame = tk.Frame(main_frame, bg=self.bg_color, height=400)
        top_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # LEFT: Customers (1/3 width)
        left_frame = tk.Frame(top_frame, bg=self.bg_color)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
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
        
        self.cust_tree = ttk.Treeview(
            cust_tree_frame,
            columns=("ID", "Name", "Phone", "VIP", "Visits", "Lifetime", "AvgSale", "ChurnRisk", "LastVisit"),
            show="headings",
            yscrollcommand=cust_scroll_y.set
        )

        self.cust_tree.heading("ID", text="Customer ID")
        self.cust_tree.heading("Name", text="Name")
        self.cust_tree.heading("Phone", text="Phone")
        self.cust_tree.heading("VIP", text="VIP")
        self.cust_tree.heading("Visits", text="Visits")
        self.cust_tree.heading("Lifetime", text="Lifetime")
        self.cust_tree.heading("AvgSale", text="Avg Sale")
        self.cust_tree.heading("ChurnRisk", text="Churn Risk")
        self.cust_tree.heading("LastVisit", text="Days Since Last")

        self.cust_tree.column("ID", width=100)
        self.cust_tree.column("Name", width=120)
        self.cust_tree.column("Phone", width=100)
        self.cust_tree.column("VIP", width=60)
        self.cust_tree.column("Visits", width=50)
        self.cust_tree.column("Lifetime", width=70)
        self.cust_tree.column("AvgSale", width=70)
        self.cust_tree.column("ChurnRisk", width=80)
        self.cust_tree.column("LastVisit", width=90)
        
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_scroll_y.config(command=self.cust_tree.yview)
        
        # Bind selection and right-click
        self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)
        self.cust_tree.bind('<Button-3>', self._customer_right_click)
        
        # MIDDLE: Transactions (1/3 width)
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
            columns=("TransID", "DateTime", "Amount", "Payment", "Staff", "Location", "Discount", "Tax"),
            show="headings",
            yscrollcommand=trans_scroll_y.set
        )

        self.trans_tree.heading("TransID", text="Transaction ID")
        self.trans_tree.heading("DateTime", text="Date/Time")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Payment", text="Payment Type")
        self.trans_tree.heading("Staff", text="Staff")
        self.trans_tree.heading("Location", text="Location")
        self.trans_tree.heading("Discount", text="Discount")
        self.trans_tree.heading("Tax", text="Tax")

        self.trans_tree.column("TransID", width=120)
        self.trans_tree.column("DateTime", width=140)
        self.trans_tree.column("Amount", width=80)
        self.trans_tree.column("Payment", width=100)
        self.trans_tree.column("Staff", width=100)
        self.trans_tree.column("Location", width=120)
        self.trans_tree.column("Discount", width=80)
        self.trans_tree.column("Tax", width=70)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll_y.config(command=self.trans_tree.yview)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        
        # RIGHT: Purchase Items (1/3 width)
        right_frame = tk.Frame(top_frame, bg=self.bg_color)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="PURCHASE ITEMS",
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
            columns=("ItemID", "Product", "Brand", "Category", "UnitPrice", "TotalPrice", "Qty", "Weight", "Discount", "Tax"),
            show="headings",
            yscrollcommand=items_scroll_y.set
        )

        self.items_tree.heading("ItemID", text="Item ID")
        self.items_tree.heading("Product", text="Product")
        self.items_tree.heading("Brand", text="Brand")
        self.items_tree.heading("Category", text="Category")
        self.items_tree.heading("UnitPrice", text="Unit Price")
        self.items_tree.heading("TotalPrice", text="Total Price")
        self.items_tree.heading("Qty", text="Qty")
        self.items_tree.heading("Weight", text="Weight")
        self.items_tree.heading("Discount", text="Discount")
        self.items_tree.heading("Tax", text="Tax")

        self.items_tree.column("ItemID", width=80)
        self.items_tree.column("Product", width=200)
        self.items_tree.column("Brand", width=80)
        self.items_tree.column("Category", width=90)
        self.items_tree.column("UnitPrice", width=80)
        self.items_tree.column("TotalPrice", width=90)
        self.items_tree.column("Qty", width=50)
        self.items_tree.column("Weight", width=70)
        self.items_tree.column("Discount", width=80)
        self.items_tree.column("Tax", width=70)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scroll_y.config(command=self.items_tree.yview)
        
        # === BOTTOM SECTION: Customer Context | Product Details ===
        bottom_frame = tk.Frame(main_frame, bg=self.bg_color, height=250)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT: Customer Context (2/3 width)
        context_frame = tk.Frame(bottom_frame, bg="#2a2a2a", relief=tk.RIDGE, borderwidth=2)
        context_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            context_frame,
            text="📊 CUSTOMER CONTEXT",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg=self.success_color
        ).pack(pady=5)
        
        self.context_text = tk.Text(
            context_frame,
            bg="#2a2a2a",
            fg=self.fg_color,
            font=("Courier", 10),
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.context_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # RIGHT: Product Details (1/3 width)
        details_frame = tk.Frame(bottom_frame, bg="#2a2a2a", relief=tk.RIDGE, borderwidth=2)
        details_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            details_frame,
            text="💰 REVENUE BY BRAND",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg=self.accent_color
        ).pack(pady=5)
        
        self.details_text = tk.Text(
            details_frame,
            bg="#2a2a2a",
            fg=self.fg_color,
            font=("Courier", 9),
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Status bar
        self.status_label = tk.Label(
            self.root,
            text="Ready",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10),
            anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _customer_right_click(self, event):
        """Right-click menu for customers"""
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        member_id = selection[0]
        customer = next((c for c in self.customers if c.get('member_id') == member_id), None)
        if not customer:
            return
        
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Name", command=lambda: self._edit_customer_field(member_id, 'name'))
        menu.add_command(label="Edit Phone", command=lambda: self._edit_customer_field(member_id, 'phone'))
        menu.add_command(label="Change VIP Status", command=lambda: self._edit_customer_field(member_id, 'vip_status'))
        
        menu.post(event.x_root, event.y_root)
    
    def _edit_customer_field(self, member_id, field):
        """Edit a customer field"""
        customer = next((c for c in self.customers if c.get('member_id') == member_id), None)
        if not customer:
            return
        
        field_names = {
            'name': 'Customer Name',
            'phone': 'Phone Number',
            'vip_status': 'VIP Status'
        }
        
        current_value = customer.get(field, '')
        
        if field == 'vip_status':
            # Show options for VIP status
            options = ['VIP', 'Casual', 'New', 'Regular']
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Change VIP Status")
            dialog.geometry("300x200")
            dialog.configure(bg=self.bg_color)
            
            tk.Label(dialog, text=f"Select VIP Status for {customer.get('name')}:", bg=self.bg_color, fg=self.fg_color).pack(pady=10)
            
            selected = tk.StringVar(value=current_value)
            for opt in options:
                tk.Radiobutton(dialog, text=opt, variable=selected, value=opt, bg=self.bg_color, fg=self.fg_color, selectcolor=self.accent_color).pack(anchor=tk.W, padx=20)
            
            def save():
                new_value = selected.get()
                self._save_customer_field(member_id, field, new_value)
                dialog.destroy()
            
            tk.Button(dialog, text="Save", command=save, bg=self.accent_color, fg="black").pack(pady=10)
        else:
            new_value = simpledialog.askstring(
                f"Edit {field_names[field]}",
                f"Enter new {field_names[field]} for {customer.get('name')}:",
                initialvalue=current_value
            )
            
            if new_value is not None and new_value != current_value:
                self._save_customer_field(member_id, field, new_value)
    
    def _save_customer_field(self, member_id, field, new_value):
        """Save customer field to Supabase"""
        try:
            result = self.sb.table('customers').update({
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
    
    def _load_customers(self):
        """Load ALL customers using pagination"""
        import time
        start = time.time()
        
        try:
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            self.status_label.config(text="Loading customers...")
            self.root.update()
            
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = self.sb.table('customers').select(
                    'member_id, name, phone, vip_status, total_visits, lifetime_value, avg_sale_value, churn_risk, days_since_last_visit'
                ).order('name').range(offset, offset + page_size - 1).execute()

                if not result.data:
                    break

                all_customers.extend(result.data)
                offset += page_size

                self.status_label.config(text=f"Loading customers... {len(all_customers)} loaded")
                self.root.update()

                if len(result.data) < page_size:
                    break
            
            self.customers = all_customers

            for cust in self.customers:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('member_id', 'N/A'),
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}",
                    f"${cust.get('avg_sale_value', 0):.2f}",
                    cust.get('churn_risk', 'N/A'),
                    cust.get('days_since_last_visit', 'N/A')
                ), iid=cust.get('member_id'))

            elapsed = time.time() - start
            self.stats_label.config(text=f"Loaded {len(self.customers)} customers in {elapsed:.3f}s")
            self.status_label.config(text=f"Loaded {len(self.customers)} customers")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
    
    def _on_customer_select(self, event):
        """When customer is selected"""
        import time
        start = time.time()
        
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        member_id = selection[0]
        
        try:
            # Get customer context
            try:
                context_result = self.sb.table('customer_sms_context').select('*').eq('member_id', member_id).execute()
                
                if context_result.data and len(context_result.data) > 0:
                    self.current_customer = context_result.data[0]
                else:
                    context_result = self.sb.table('customers').select('*').eq('member_id', member_id).execute()
                    self.current_customer = context_result.data[0] if context_result.data else None
            except:
                context_result = self.sb.table('customers').select('*').eq('member_id', member_id).execute()
                self.current_customer = context_result.data[0] if context_result.data else None
            
            if not self.current_customer:
                return
            
            metrics = self._calculate_customer_metrics(member_id)

            self._display_context(self.current_customer, metrics)
            self._load_transactions(member_id, metrics.get('staff_lookup'))
            self._load_revenue_by_brand(member_id, metrics)
            
            elapsed = time.time() - start
            self.stats_label.config(text=f"Context loaded in {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer:\n{str(e)}")
    
    def _display_context(self, customer, metrics=None):
        """Display customer context"""
        self.context_text.delete('1.0', tk.END)
        
        if not customer:
            return

        metrics = metrics or {}

        total_visits = metrics.get('total_visits', customer.get('total_visits', 0))
        lifetime_value = metrics.get('total_revenue', customer.get('lifetime_value', 0))
        avg_revenue_per_visit = metrics.get('avg_revenue_per_visit', customer.get('avg_sale_value', 0))
        avg_days_between = metrics.get('avg_days_between_visits')
        visits_per_month = metrics.get('visits_per_month')

        visit_frequency = f"Every {avg_days_between:.1f} days" if avg_days_between else "N/A"
        visit_velocity = f"{visits_per_month:.2f}/month" if visits_per_month else "N/A"

        favorite_category = metrics.get('favorite_category', customer.get('favorite_category', 'Unknown'))
        preferred_location = metrics.get('preferred_location', customer.get('preferred_location', 'Unknown'))
        preferred_payment = metrics.get('preferred_payment', customer.get('preferred_payment', 'Unknown'))

        top_categories = metrics.get('top_categories', [])
        category_lines = [f"  • {name} ({count} visits)" for name, count in top_categories[:3]] or ['  No category data']

        top_brands = metrics.get('favorite_brands', [])
        brand_lines = [f"  • {name} (${revenue:.2f})" for name, revenue in top_brands[:3]] or ['  No brand data']

        top_products = metrics.get('top_products')
        if top_products:
            product_lines = [
                f"  • {prod['name']} ({prod['count']}x | ${prod['revenue']:.2f})"
                for prod in top_products[:3]
            ]
        else:
            product_lines = ["  No purchase data"]

        context = f"""
Name: {customer.get('name', 'N/A')}
Phone: {customer.get('phone', 'N/A')}
VIP Status: {customer.get('vip_status', 'N/A')}
Churn Risk: {customer.get('churn_risk', 'N/A')}

📊 Stats:
  Total Visits: {total_visits}
  Lifetime Value: ${lifetime_value:.2f}
  Avg Revenue / Visit: ${avg_revenue_per_visit:.2f}
  Visit Frequency: {visit_frequency}
  Visit Velocity: {visit_velocity}
  Days Since Last Visit: {customer.get('days_since_last_visit', 'N/A')}

🛍️ Preferences:
  Favorite Category: {favorite_category}
  Preferred Location: {preferred_location}
  Preferred Payment: {preferred_payment}

📈 What They Like:
  Top Categories:
{chr(10).join(category_lines)}

  Top Brands:
{chr(10).join(brand_lines)}

🌟 Top Products:
{chr(10).join(product_lines)}
"""
        
        self.context_text.insert('1.0', context.strip())
    
    def _load_transactions(self, member_id, staff_lookup=None):
        """Load transactions for customer"""
        import time
        start = time.time()
        
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        staff_lookup = staff_lookup or {}
        
        try:
            result = self.sb.table('transactions').select(
                '*'
            ).eq('customer_id', member_id).order('date', desc=True).execute()
            
            transactions = result.data if result.data else []
            
            for trans in transactions:
                staff_display = staff_lookup.get(trans.get('transaction_id'))
                if not staff_display:
                    staff_display = self._resolve_staff_name(trans)
                
                self.trans_tree.insert('', tk.END, values=(
                    trans.get('transaction_id', 'N/A'),
                    trans.get('date', '')[:19] if trans.get('date') else 'N/A',  # Full datetime
                    f"${trans.get('total_amount', 0):.2f}",
                    trans.get('payment_type', 'N/A'),
                    staff_display,
                    trans.get('shop_location', 'N/A'),
                    f"${trans.get('discount_amount', 0):.2f}",
                    f"${trans.get('tax_amount', 0):.2f}"
                ), iid=trans.get('transaction_id'))
            
            elapsed = time.time() - start
            self.status_label.config(text=f"Showing {len(transactions)} transactions | Query: {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions:\n{str(e)}")
    
    def _on_transaction_select(self, event):
        """When transaction selected"""
        import time
        start = time.time()
        
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        try:
            result = self.sb.table('transaction_items').select(
                '*'
            ).eq('transaction_id', transaction_id).execute()
            
            items = result.data if result.data else []
            
            for item in items:
                self.items_tree.insert('', tk.END, values=(
                    item.get('item_id', 'N/A'),
                    item.get('product_name', 'N/A')[:35],
                    item.get('brand', 'N/A'),
                    item.get('category', 'N/A'),
                    f"${item.get('unit_price', 0):.2f}",
                    f"${item.get('total_price', 0):.2f}",
                    item.get('quantity', 0),
                    f"{item.get('weight', 0):.1f}g" if item.get('weight') else 'N/A',
                    f"${item.get('discount_amount', 0):.2f}",
                    f"${item.get('tax_amount', 0):.2f}"
                ))
            
            elapsed = time.time() - start
            self.status_label.config(text=f"Showing {len(items)} items | Query: {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items:\n{str(e)}")
    
    def _load_revenue_by_brand(self, member_id, metrics=None):
        """Calculate and display revenue by brand for the customer"""
        import time
        start = time.time()

        self.details_text.delete('1.0', tk.END)

        try:
            brand_revenue = {}
            brand_category_revenue = {}
            total_revenue = 0.0

            if metrics and metrics.get('brand_breakdown'):
                brand_revenue = metrics.get('brand_breakdown', {})
                brand_category_revenue = metrics.get('brand_category_breakdown', {})
                total_revenue = sum(data['revenue'] for data in brand_revenue.values())
            else:
                result = self.sb.table('transaction_items').select(
                    'brand, total_price, category, transaction_id'
                ).execute()

                if not result.data:
                    self.details_text.insert('1.0', "No purchase data available")
                    return

                trans_result = self.sb.table('transactions').select('transaction_id').eq('customer_id', member_id).execute()
                customer_transaction_ids = {t['transaction_id'] for t in trans_result.data} if trans_result.data else set()

                if not customer_transaction_ids:
                    self.details_text.insert('1.0', "No transactions found for this customer")
                    return

                customer_items = [item for item in result.data if item['transaction_id'] in customer_transaction_ids]

                for item in customer_items:
                    brand = item.get('brand', 'Unknown')
                    category = item.get('category', 'Unknown')
                    item_revenue = float(item.get('total_price', 0))

                    if brand.upper() == 'MOTA' or category.upper() == 'FEES':
                        brand_key = 'MOTA (includes recycling)'
                    else:
                        brand_key = brand

                    if brand_key not in brand_category_revenue:
                        brand_category_revenue[brand_key] = {}
                        brand_revenue[brand_key] = {
                            'revenue': 0.0,
                            'count': 0
                        }

                    if category not in brand_category_revenue[brand_key]:
                        brand_category_revenue[brand_key][category] = 0

                    brand_category_revenue[brand_key][category] += item_revenue
                    brand_revenue[brand_key]['revenue'] += item_revenue
                    brand_revenue[brand_key]['count'] += 1
                    total_revenue += item_revenue

            if not brand_revenue:
                self.details_text.insert('1.0', "No revenue data available")
                return

            sorted_brands = sorted(
                brand_revenue.items(),
                key=lambda x: x[1]['revenue'],
                reverse=True
            )

            display_text = f"Total Customer Revenue: ${total_revenue:.2f}\n\n"
            display_text += "Revenue by Brand & Category:\n"
            display_text += "=" * 40 + "\n"

            for brand, data in sorted_brands:
                revenue = data['revenue']
                percentage = (revenue / total_revenue * 100) if total_revenue > 0 else 0
                display_text += f"{brand:<25} ${revenue:>8.2f} ({percentage:>5.1f}%)\n"

                categories = brand_category_revenue.get(brand, {})
                sorted_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)

                for category, cat_revenue in sorted_categories:
                    cat_percentage = (cat_revenue / revenue * 100) if revenue > 0 else 0
                    display_text += f"  └─ {category:<20} ${cat_revenue:>6.2f} ({cat_percentage:>4.1f}%)\n"

                display_text += "\n"

            if len(sorted_brands) >= 3:
                display_text += "🏆 Top 3 Brands:\n"
                for i, (brand, data) in enumerate(sorted_brands[:3], 1):
                    display_text += f"  {i}. {brand}: ${data['revenue']:.2f}\n"

            self.details_text.insert('1.0', display_text)

            elapsed = time.time() - start
            self.status_label.config(text=f"Revenue analysis loaded in {elapsed:.3f}s")

        except Exception as e:
            self.details_text.insert('1.0', f"Error loading revenue data:\n{str(e)}")
    
    def _calculate_customer_metrics(self, member_id):
        """Gather visit, preference, and purchase metrics for a customer"""
        metrics = {
            'total_visits': 0,
            'total_revenue': 0.0,
            'avg_revenue_per_visit': 0.0,
            'avg_days_between_visits': None,
            'visits_per_month': None,
            'favorite_category': 'Unknown',
            'preferred_location': 'Unknown',
            'preferred_payment': 'Unknown',
            'top_categories': [],
            'favorite_brands': [],
            'top_products': [],
            'brand_breakdown': {},
            'brand_category_breakdown': {},
            'staff_lookup': {}
        }

        try:
            trans_result = self.sb.table('transactions').select(
                'transaction_id, date, total_amount, staff_id, staff_name, shop_location, payment_type'
            ).eq('customer_id', member_id).order('date', desc=True).execute()

            transactions = trans_result.data or []
            metrics['total_visits'] = len(transactions)

            if not transactions:
                return metrics

            total_revenue = 0.0
            location_counter = Counter()
            payment_counter = Counter()
            date_values = []
            staff_lookup = {}

            for trans in transactions:
                staff_lookup[trans.get('transaction_id')] = self._resolve_staff_name(trans)
                total_revenue += float(trans.get('total_amount', 0) or 0)
                location_counter[trans.get('shop_location', 'Unknown')] += 1
                payment_counter[trans.get('payment_type', 'Unknown')] += 1

                parsed_date = self._parse_datetime(trans.get('date'))
                if parsed_date:
                    date_values.append(parsed_date)

            metrics['total_revenue'] = total_revenue
            if metrics['total_visits'] > 0:
                metrics['avg_revenue_per_visit'] = total_revenue / metrics['total_visits']

            if location_counter:
                metrics['preferred_location'] = location_counter.most_common(1)[0][0]
            if payment_counter:
                metrics['preferred_payment'] = payment_counter.most_common(1)[0][0]

            if len(date_values) >= 2:
                sorted_dates = sorted(date_values)
                span_days = (sorted_dates[-1] - sorted_dates[0]).days
                span_days = span_days if span_days > 0 else 1
                metrics['avg_days_between_visits'] = span_days / (len(sorted_dates) - 1)
                metrics['visits_per_month'] = (len(sorted_dates) / span_days) * 30.437 if span_days else None

            metrics['staff_lookup'] = staff_lookup

            transaction_ids = [t['transaction_id'] for t in transactions if t.get('transaction_id')]
            if not transaction_ids:
                return metrics

            items_result = self.sb.table('transaction_items').select(
                'transaction_id, category, brand, product_name, total_price'
            ).in_('transaction_id', transaction_ids).execute()

            items = items_result.data or []

            category_counter = Counter()
            brand_revenue = defaultdict(lambda: {'revenue': 0.0, 'count': 0})
            brand_category_breakdown = defaultdict(lambda: defaultdict(float))
            product_stats = {}

            for item in items:
                category = item.get('category', 'Unknown')
                brand = item.get('brand', 'Unknown')
                product_name = item.get('product_name', 'Unknown')
                revenue = float(item.get('total_price', 0) or 0)

                if brand.upper() == 'MOTA' or category.upper() == 'FEES':
                    brand_key = 'MOTA (includes recycling)'
                else:
                    brand_key = brand

                category_counter[category] += 1
                brand_revenue[brand_key]['revenue'] += revenue
                brand_revenue[brand_key]['count'] += 1
                brand_category_breakdown[brand_key][category] += revenue

                if product_name not in product_stats:
                    product_stats[product_name] = {'name': product_name, 'count': 0, 'revenue': 0.0}
                product_stats[product_name]['count'] += 1
                product_stats[product_name]['revenue'] += revenue

            if category_counter:
                metrics['favorite_category'] = category_counter.most_common(1)[0][0]
                metrics['top_categories'] = category_counter.most_common(5)

            if brand_revenue:
                metrics['favorite_brands'] = sorted(
                    ((brand, data['revenue']) for brand, data in brand_revenue.items()),
                    key=lambda x: x[1],
                    reverse=True
                )

            metrics['brand_breakdown'] = {
                brand: {'revenue': data['revenue'], 'count': data['count']}
                for brand, data in brand_revenue.items()
            }
            metrics['brand_category_breakdown'] = {
                brand: dict(categories) for brand, categories in brand_category_breakdown.items()
            }

            if product_stats:
                metrics['top_products'] = sorted(
                    product_stats.values(),
                    key=lambda p: (p['count'], p['revenue']),
                    reverse=True
                )

        except Exception as e:
            print(f"Error calculating customer metrics for {member_id}: {e}")

        return metrics

    def _resolve_staff_name(self, transaction):
        """Resolve budtender/staff name, falling back to the staff table when needed"""
        raw_name = (transaction.get('staff_name') or '').strip()

        try:
            if raw_name and not raw_name.lower().startswith(('seller #', 'staff #')) and raw_name.lower() != 'unknown':
                return raw_name

            staff_id = transaction.get('staff_id')

            if not staff_id and raw_name and '#' in raw_name:
                candidate = raw_name.split('#', 1)[-1].strip()
                candidate = candidate.split()[0]
                if candidate:
                    staff_id = candidate

            if staff_id:
                if staff_id in self.staff_cache:
                    return self.staff_cache[staff_id]

                result = self.sb.table('staff').select('staff_name').eq('staff_id', staff_id).execute()
                if result.data:
                    resolved = (result.data[0].get('staff_name') or raw_name or 'Unknown').strip()
                    self.staff_cache[staff_id] = resolved
                    return resolved

                self.staff_cache[staff_id] = raw_name or 'Unknown'
                return self.staff_cache[staff_id]

            return raw_name or 'Unknown'

        except Exception as e:
            print(f"Error resolving staff name: {e}")
            return raw_name or 'Unknown'

    @staticmethod
    def _parse_datetime(value):
        """Parse Supabase/ISO datetime strings safely"""
        if not value:
            return None
        if isinstance(value, datetime):
            return value
        try:
            text = str(value)
            if text.endswith('Z'):
                text = text[:-1] + '+00:00'
            return datetime.fromisoformat(text)
        except Exception:
            for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
                try:
                    return datetime.strptime(text, fmt)
                except Exception:
                    continue
        return None
    
    def _on_search(self, event):
        """Filter customers"""
        search = self.search_var.get().strip().lower()
        
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        if not search:
            for cust in self.customers:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('member_id', 'N/A'),
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}",
                    f"${cust.get('avg_sale_value', 0):.2f}",
                    cust.get('churn_risk', 'N/A'),
                    cust.get('days_since_last_visit', 'N/A')
                ), iid=cust.get('member_id'))
            self.status_label.config(text=f"Showing all {len(self.customers)} customers")
            return
        
        matches = 0
        for cust in self.customers:
            name = str(cust.get('name', '')).lower()
            phone = str(cust.get('phone', '')).lower()
            member_id = str(cust.get('member_id', '')).lower()
            
            if search in name or search in phone or search in member_id:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('member_id', 'N/A'),
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}",
                    f"${cust.get('avg_sale_value', 0):.2f}",
                    cust.get('churn_risk', 'N/A'),
                    cust.get('days_since_last_visit', 'N/A')
                ), iid=cust.get('member_id'))
                matches += 1
        
        self.status_label.config(text=f"Found {matches} matches for '{search}'")
    
    def _clear_search(self):
        """Clear search"""
        self.search_var.set('')
        self._load_customers()

if __name__ == "__main__":
    root = tk.Tk()
    app = EnhancedCustomerAnalytics(root)
    root.mainloop()

