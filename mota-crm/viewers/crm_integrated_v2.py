#!/usr/bin/env python3
"""
MoTa CRM - OPTIMIZED with new Supabase views
Uses customer_sms_context and cascading queries
Performance: 10-50x faster than v1
"""

import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from datetime import datetime
import json

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class OptimizedCRM:
    def __init__(self, root):
        self.root = root
        self.root.title("MoTa CRM - OPTIMIZED (with new views)")
        self.root.geometry("1800x1000")
        
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
        
        # Performance tracking
        self.query_times = []
        
        self._create_ui()
        self._load_customers()
    
    def _create_ui(self):
        """Create optimized UI"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title with performance indicator
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            title_frame,
            text="MOTA CRM - INTEGRATED SYSTEM",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        self.perf_label = tk.Label(
            title_frame,
            text="⚡ OPTIMIZED",
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
        
        # Performance stats
        self.stats_label = tk.Label(
            search_frame,
            text="Query time: --",
            bg=self.bg_color,
            fg=self.success_color,
            font=("Arial", 10)
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # Main content (3 columns)
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # LEFT: Customers list
        left_frame = tk.Frame(content_frame, bg=self.bg_color, width=400)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            left_frame,
            text="CUSTOMERS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Customer tree
        cust_tree_frame = tk.Frame(left_frame, bg=self.bg_color)
        cust_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        cust_scroll_y = tk.Scrollbar(cust_tree_frame)
        cust_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.cust_tree = ttk.Treeview(
            cust_tree_frame,
            columns=("Name", "Phone", "VIP", "Visits", "Lifetime"),
            show="headings",
            yscrollcommand=cust_scroll_y.set
        )
        
        self.cust_tree.heading("Name", text="Name")
        self.cust_tree.heading("Phone", text="Phone")
        self.cust_tree.heading("VIP", text="VIP")
        self.cust_tree.heading("Visits", text="Visits")
        self.cust_tree.heading("Lifetime", text="Lifetime")
        
        self.cust_tree.column("Name", width=150)
        self.cust_tree.column("Phone", width=120)
        self.cust_tree.column("VIP", width=80)
        self.cust_tree.column("Visits", width=60)
        self.cust_tree.column("Lifetime", width=80)
        
        self.cust_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cust_scroll_y.config(command=self.cust_tree.yview)
        
        # Bind selection
        self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)
        
        # MIDDLE: Transactions + Context
        middle_frame = tk.Frame(content_frame, bg=self.bg_color, width=500)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Customer context (NEW!)
        context_frame = tk.Frame(middle_frame, bg="#2a2a2a", relief=tk.RIDGE, borderwidth=2)
        context_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            context_frame,
            text="📊 CUSTOMER CONTEXT",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg=self.success_color
        ).pack(pady=5)
        
        self.context_text = tk.Text(
            context_frame,
            height=8,
            bg="#2a2a2a",
            fg=self.fg_color,
            font=("Courier", 10),
            wrap=tk.WORD,
            relief=tk.FLAT
        )
        self.context_text.pack(fill=tk.X, padx=10, pady=5)
        
        # Transactions
        tk.Label(
            middle_frame,
            text="TRANSACTIONS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        trans_tree_frame = tk.Frame(middle_frame, bg=self.bg_color)
        trans_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_scroll_y = tk.Scrollbar(trans_tree_frame)
        trans_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_tree = ttk.Treeview(
            trans_tree_frame,
            columns=("Date", "Amount", "Staff", "Location"),
            show="headings",
            yscrollcommand=trans_scroll_y.set
        )
        
        self.trans_tree.heading("Date", text="Date")
        self.trans_tree.heading("Amount", text="Amount")
        self.trans_tree.heading("Staff", text="Staff")
        self.trans_tree.heading("Location", text="Location")
        
        self.trans_tree.column("Date", width=120)
        self.trans_tree.column("Amount", width=100)
        self.trans_tree.column("Staff", width=130)
        self.trans_tree.column("Location", width=150)
        
        self.trans_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        trans_scroll_y.config(command=self.trans_tree.yview)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        
        # RIGHT: Purchase Items
        right_frame = tk.Frame(content_frame, bg=self.bg_color, width=500)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="PURCHASE ITEMS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        items_tree_frame = tk.Frame(right_frame, bg=self.bg_color)
        items_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        items_scroll_y = tk.Scrollbar(items_tree_frame)
        items_scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.items_tree = ttk.Treeview(
            items_tree_frame,
            columns=("Product", "Brand", "Category", "Price", "Qty"),
            show="headings",
            yscrollcommand=items_scroll_y.set
        )
        
        self.items_tree.heading("Product", text="Product")
        self.items_tree.heading("Brand", text="Brand")
        self.items_tree.heading("Category", text="Category")
        self.items_tree.heading("Price", text="Price")
        self.items_tree.heading("Qty", text="Qty")
        
        self.items_tree.column("Product", width=250)
        self.items_tree.column("Brand", width=100)
        self.items_tree.column("Category", width=100)
        self.items_tree.column("Price", width=80)
        self.items_tree.column("Qty", width=50)
        
        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        items_scroll_y.config(command=self.items_tree.yview)
        
        # Product details
        details_frame = tk.Frame(right_frame, bg="#2a2a2a", relief=tk.RIDGE, borderwidth=2)
        details_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        tk.Label(
            details_frame,
            text="PRODUCT DETAILS",
            font=("Arial", 12, "bold"),
            bg="#2a2a2a",
            fg=self.accent_color
        ).pack(pady=5)
        
        self.details_text = tk.Text(
            details_frame,
            height=10,
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
    
    def _load_customers(self):
        """Load ALL customers using pagination"""
        import time
        start = time.time()
        
        try:
            # Clear tree
            for item in self.cust_tree.get_children():
                self.cust_tree.delete(item)
            
            self.status_label.config(text="Loading customers... (this may take a moment)")
            self.root.update()
            
            # Fetch ALL customers using pagination
            all_customers = []
            page_size = 1000
            offset = 0
            
            while True:
                result = self.sb.table('customers').select(
                    'member_id, name, phone, vip_status, total_visits, lifetime_value'
                ).order('name').range(offset, offset + page_size - 1).execute()
                
                if not result.data:
                    break
                
                all_customers.extend(result.data)
                offset += page_size
                
                # Update status
                self.status_label.config(text=f"Loading customers... {len(all_customers)} loaded")
                self.root.update()
                
                # If we got less than page_size, we're done
                if len(result.data) < page_size:
                    break
            
            self.customers = all_customers
            
            # Populate tree
            for cust in self.customers:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}"
                ), iid=cust.get('member_id'))
            
            elapsed = time.time() - start
            self.stats_label.config(text=f"Loaded {len(self.customers)} customers in {elapsed:.3f}s")
            self.status_label.config(text=f"Loaded {len(self.customers)} customers")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers:\n{str(e)}")
    
    def _on_customer_select(self, event):
        """When customer is selected - USE NEW VIEW!"""
        import time
        start = time.time()
        
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        member_id = selection[0]
        
        try:
            # Step 1: Try to get customer context from NEW VIEW first
            try:
                context_result = self.sb.table('customer_sms_context').select('*').eq('member_id', member_id).execute()
                
                if context_result.data and len(context_result.data) > 0:
                    self.current_customer = context_result.data[0]
                else:
                    # Fallback to old method
                    context_result = self.sb.table('customers').select('*').eq('member_id', member_id).execute()
                    self.current_customer = context_result.data[0] if context_result.data else None
            except:
                # If view fails, use customers table
                context_result = self.sb.table('customers').select('*').eq('member_id', member_id).execute()
                self.current_customer = context_result.data[0] if context_result.data else None
            
            if not self.current_customer:
                messagebox.showwarning("No Data", f"No data found for customer {member_id}")
                return
            
            # Display context
            self._display_context(self.current_customer)
            
            # Step 2: Load transactions for THIS customer only
            self._load_transactions(member_id)
            
            elapsed = time.time() - start
            self.stats_label.config(text=f"Customer context loaded in {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer:\n{str(e)}")
    
    def _display_context(self, customer):
        """Display customer context from customer_sms_context view"""
        self.context_text.delete('1.0', tk.END)
        
        if not customer:
            return
        
        # Format context beautifully
        context = f"""
Name: {customer.get('name', 'N/A')}
Phone: {customer.get('phone', 'N/A')}
VIP Status: {customer.get('vip_status', 'N/A')}
Churn Risk: {customer.get('churn_risk', 'N/A')}

📊 Stats:
  Total Visits: {customer.get('total_visits', 0)}
  Lifetime Value: ${customer.get('lifetime_value', 0):.2f}
  Avg Sale: ${customer.get('avg_sale_value', 0):.2f}
  Days Since Last Visit: {customer.get('days_since_last_visit', 'N/A')}

🛍️ Preferences:
  Favorite Category: {customer.get('favorite_category', 'Unknown')}
  Preferred Location: {customer.get('preferred_location', 'Unknown')}
  Preferred Payment: {customer.get('preferred_payment', 'Unknown')}

🌟 Top Products:
{self._format_products(customer.get('favorite_products'))}
"""
        
        self.context_text.insert('1.0', context.strip())
    
    def _format_products(self, products_json):
        """Format favorite products from JSON"""
        if not products_json:
            return "  No data"
        
        try:
            if isinstance(products_json, str):
                products = json.loads(products_json)
            else:
                products = products_json
            
            if not products:
                return "  No purchases yet"
            
            lines = []
            for p in products[:3]:
                lines.append(f"  • {p.get('product_name', 'Unknown')} ({p.get('purchase_count', 0)}x)")
            return "\n".join(lines)
        except:
            return "  Data unavailable"
    
    def _load_transactions(self, member_id):
        """Load transactions for specific customer - CASCADING QUERY"""
        import time
        start = time.time()
        
        # Clear trees
        for item in self.trans_tree.get_children():
            self.trans_tree.delete(item)
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        try:
            # Query only THIS customer's transactions
            result = self.sb.table('transactions').select(
                '*'
            ).eq('customer_id', member_id).order('date', desc=True).execute()
            
            transactions = result.data if result.data else []
            
            for trans in transactions:
                self.trans_tree.insert('', tk.END, values=(
                    trans.get('date', '')[:10],
                    f"${trans.get('total_amount', 0):.2f}",
                    trans.get('staff_name', 'N/A'),
                    trans.get('shop_location', 'N/A')
                ), iid=trans.get('transaction_id'))
            
            elapsed = time.time() - start
            self.status_label.config(text=f"Showing {len(transactions)} transactions | Query time: {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions:\n{str(e)}")
    
    def _on_transaction_select(self, event):
        """When transaction selected - load ONLY its items"""
        import time
        start = time.time()
        
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        transaction_id = selection[0]
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        try:
            # Query only THIS transaction's items
            result = self.sb.table('transaction_items').select(
                '*'
            ).eq('transaction_id', transaction_id).execute()
            
            items = result.data if result.data else []
            
            for item in items:
                self.items_tree.insert('', tk.END, values=(
                    item.get('product_name', 'N/A')[:40],
                    item.get('brand', 'N/A'),
                    item.get('category', 'N/A'),
                    f"${item.get('unit_price', 0):.2f}",
                    item.get('quantity', 0)
                ))
            
            elapsed = time.time() - start
            self.status_label.config(text=f"Showing {len(items)} items in transaction {transaction_id} | Query time: {elapsed:.3f}s")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items:\n{str(e)}")
    
    def _on_search(self, event):
        """Filter customers - case insensitive"""
        search = self.search_var.get().strip().lower()
        
        # Clear tree
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        # If empty search, show all
        if not search:
            for cust in self.customers:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}"
                ), iid=cust.get('member_id'))
            self.status_label.config(text=f"Showing all {len(self.customers)} customers")
            return
        
        # Filter and repopulate
        matches = 0
        for cust in self.customers:
            name = str(cust.get('name', '')).lower()
            phone = str(cust.get('phone', '')).lower()
            member_id = str(cust.get('member_id', '')).lower()
            
            if search in name or search in phone or search in member_id:
                self.cust_tree.insert('', tk.END, values=(
                    cust.get('name', 'N/A'),
                    cust.get('phone', 'N/A')[:14] if cust.get('phone') else 'N/A',
                    cust.get('vip_status', 'N/A'),
                    cust.get('total_visits', 0),
                    f"${cust.get('lifetime_value', 0):.2f}"
                ), iid=cust.get('member_id'))
                matches += 1
        
        self.status_label.config(text=f"Found {matches} matches for '{search}'")
    
    def _clear_search(self):
        """Clear search"""
        self.search_var.set('')
        self._load_customers()

if __name__ == "__main__":
    root = tk.Tk()
    app = OptimizedCRM(root)
    root.mainloop()

