#!/usr/bin/env python3
"""
MoTa Transaction Viewer - ENHANCED VERSION
View ALL transactions without artificial limits
"""

import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from datetime import datetime, timedelta
import webbrowser
from supabase_helpers import fetch_all_records

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class TransactionViewerEnhanced:
    def __init__(self, root):
        self.root = root
        self.root.title("MoTa Transaction Viewer - ENHANCED")
        self.root.geometry("1600x900")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Configure colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        
        self.root.configure(bg=self.bg_color)
        
        # Data storage
        self.transactions = []
        self.all_transactions = []
        self.current_transaction = None
        
        self._create_ui()
        self._load_all_transactions()
    
    def _create_ui(self):
        """Create the enhanced user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            title_frame,
            text="MOTA TRANSACTION VIEWER - ENTERPRISE",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title.pack(side=tk.LEFT)
        
        # Stats
        self.stats_label = tk.Label(
            title_frame,
            text="Loading...",
            font=("Arial", 12),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.stats_label.pack(side=tk.RIGHT)
        
        # Search and filters
        controls_frame = tk.Frame(main_frame, bg=self.bg_color)
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Search
        tk.Label(controls_frame, text="Search Customer:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_transactions)
        search_entry = tk.Entry(controls_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Date range
        tk.Label(controls_frame, text="Date Range:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.date_var = tk.StringVar(value="All Time")
        date_combo = ttk.Combobox(controls_frame, textvariable=self.date_var, width=15)
        date_combo['values'] = ['All Time', 'Last 7 Days', 'Last 30 Days', 'Last 90 Days', 'This Year', 'Last Year']
        date_combo.pack(side=tk.LEFT, padx=(5, 20))
        date_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_transactions())
        
        # Location
        tk.Label(controls_frame, text="Location:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.location_var = tk.StringVar(value="All")
        location_combo = ttk.Combobox(controls_frame, textvariable=self.location_var, width=15)
        location_combo.pack(side=tk.LEFT, padx=(5, 20))
        location_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_transactions())
        
        # Staff
        tk.Label(controls_frame, text="Staff:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.staff_var = tk.StringVar(value="All")
        staff_combo = ttk.Combobox(controls_frame, textvariable=self.staff_var, width=15)
        staff_combo.pack(side=tk.LEFT, padx=(5, 20))
        staff_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_transactions())
        
        # Load controls
        load_frame = tk.Frame(controls_frame, bg=self.bg_color)
        load_frame.pack(side=tk.RIGHT)
        
        tk.Button(
            load_frame,
            text="Load All",
            command=self._load_all_transactions,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            load_frame,
            text="Load 10K",
            command=lambda: self._load_transactions(10000),
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        tk.Button(
            load_frame,
            text="Load 5K",
            command=lambda: self._load_transactions(5000),
            bg="#444444",
            fg="white",
            font=("Arial", 10),
            padx=10
        ).pack(side=tk.LEFT, padx=2)
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Transaction list
        left_frame = tk.Frame(content_frame, bg=self.bg_color, width=1000)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(
            left_frame,
            text="ALL TRANSACTIONS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Transaction tree
        tree_frame = tk.Frame(left_frame, bg=self.bg_color)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Trans ID", "Date", "Customer", "Location", "Staff", "Amount", "Payment")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="browse")
        
        # Column headers
        self.tree.heading("Trans ID", text="Trans ID")
        self.tree.heading("Date", text="Date")
        self.tree.heading("Customer", text="Customer")
        self.tree.heading("Location", text="Location")
        self.tree.heading("Staff", text="Staff")
        self.tree.heading("Amount", text="Amount")
        self.tree.heading("Payment", text="Payment")
        
        # Column widths
        self.tree.column("Trans ID", width=80)
        self.tree.column("Date", width=100)
        self.tree.column("Customer", width=150)
        self.tree.column("Location", width=120)
        self.tree.column("Staff", width=120)
        self.tree.column("Amount", width=100)
        self.tree.column("Payment", width=80)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection
        self.tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        
        # Right panel - Transaction details
        right_frame = tk.Frame(content_frame, bg=self.bg_color, width=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        
        # Transaction details header
        details_header = tk.Frame(right_frame, bg=self.bg_color)
        details_header.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            details_header,
            text="TRANSACTION DETAILS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(side=tk.LEFT)
        
        # Action buttons
        buttons_frame = tk.Frame(details_header, bg=self.bg_color)
        buttons_frame.pack(side=tk.RIGHT)
        
        self.view_items_btn = tk.Button(
            buttons_frame,
            text="View Items",
            command=self._view_transaction_items,
            bg="#444444",
            fg="white",
            font=("Arial", 9),
            padx=10,
            state=tk.DISABLED
        )
        self.view_items_btn.pack(side=tk.LEFT, padx=2)
        
        self.export_btn = tk.Button(
            buttons_frame,
            text="Export",
            command=self._export_transaction_data,
            bg="#444444",
            fg="white",
            font=("Arial", 9),
            padx=10,
            state=tk.DISABLED
        )
        self.export_btn.pack(side=tk.LEFT, padx=2)
        
        # Details text
        self.detail_text = tk.Text(
            right_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="#2d2d2d",
            fg=self.fg_color
        )
        detail_scroll = ttk.Scrollbar(right_frame, orient="vertical", command=self.detail_text.yview)
        self.detail_text.config(yscrollcommand=detail_scroll.set)
        
        self.detail_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        detail_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Ready",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.status_label.pack(pady=(10, 0))
    
    def _load_all_transactions(self):
        """Load ALL transactions from Supabase"""
        try:
            self.status_label.config(text="Loading ALL transactions (this may take a moment)...")
            self.root.update()
            
            # Get ALL transactions using pagination
            self.all_transactions = fetch_all_records(self.sb, 'transactions', order_by='date', order_desc=True)
            
            # Update filter options
            self._update_filter_options()
            
            # Apply current filters
            self._filter_transactions()
            
            self.status_label.config(text=f"Loaded ALL {len(self.all_transactions):,} transactions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")
            self.status_label.config(text="Error loading transactions")
    
    def _load_transactions(self, limit):
        """Load limited number of transactions"""
        try:
            self.status_label.config(text=f"Loading {limit:,} transactions...")
            self.root.update()
            
            # Get limited transactions
            response = self.sb.table('transactions').select('*').order('date', desc=True).limit(limit).execute()
            self.all_transactions = response.data
            
            # Update filter options
            self._update_filter_options()
            
            # Apply current filters
            self._filter_transactions()
            
            self.status_label.config(text=f"Loaded {len(self.all_transactions):,} transactions (limited to {limit:,})")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")
            self.status_label.config(text="Error loading transactions")
    
    def _update_filter_options(self):
        """Update filter dropdown options"""
        if not self.all_transactions:
            return
        
        # Get unique locations
        locations = sorted(set(t.get('shop_location', 'Unknown') for t in self.all_transactions if t.get('shop_location')))
        self.location_combo = ttk.Combobox(self.root.nametowidget(str(self.location_var).split('.')[0]), values=['All'] + locations)
        
        # Get unique staff
        staff = sorted(set(t.get('staff_name', 'Unknown') for t in self.all_transactions if t.get('staff_name')))
        self.staff_combo = ttk.Combobox(self.root.nametowidget(str(self.staff_var).split('.')[0]), values=['All'] + staff)
    
    def _populate_tree(self, transactions):
        """Populate transaction tree"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert transactions
        for trans in transactions:
            date = trans.get('date', 'N/A')
            if date != 'N/A':
                try:
                    dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                    date = dt.strftime('%Y-%m-%d')
                except:
                    pass
            
            self.tree.insert('', 'end', values=(
                trans.get('transaction_id', 'N/A'),
                date,
                trans.get('customer_id', 'N/A'),  # Show customer_id instead of customer_name
                trans.get('shop_location', 'N/A'),
                trans.get('staff_name', 'N/A'),
                f"${float(trans.get('total_amount', 0)):.2f}",
                trans.get('payment_type', 'N/A')
            ))
    
    def _filter_transactions(self):
        """Filter transactions based on search and filters"""
        if not self.all_transactions:
            return
        
        search_term = self.search_var.get().lower()
        date_filter = self.date_var.get()
        location_filter = self.location_var.get()
        staff_filter = self.staff_var.get()
        
        filtered = []
        for trans in self.all_transactions:
            # Search filter
            if search_term:
                customer_id = trans.get('customer_id', '').lower()
                if search_term not in customer_id:
                    continue
            
            # Date filter
            if date_filter != "All Time":
                trans_date = trans.get('date')
                if trans_date:
                    try:
                        dt = datetime.fromisoformat(trans_date.replace('Z', '+00:00'))
                        if date_filter == "Last 7 Days":
                            if dt < datetime.now() - timedelta(days=7):
                                continue
                        elif date_filter == "Last 30 Days":
                            if dt < datetime.now() - timedelta(days=30):
                                continue
                        elif date_filter == "Last 90 Days":
                            if dt < datetime.now() - timedelta(days=90):
                                continue
                        elif date_filter == "This Year":
                            if dt.year != datetime.now().year:
                                continue
                        elif date_filter == "Last Year":
                            if dt.year != datetime.now().year - 1:
                                continue
                    except:
                        pass
            
            # Location filter
            if location_filter != "All":
                if trans.get('shop_location') != location_filter:
                    continue
            
            # Staff filter
            if staff_filter != "All":
                if trans.get('staff_name') != staff_filter:
                    continue
            
            filtered.append(trans)
        
        self.transactions = filtered
        self._populate_tree(filtered)
        
        # Calculate totals
        total_amount = sum(float(t.get('total_amount', 0)) for t in filtered)
        self.stats_label.config(text=f"Showing {len(filtered):,} of {len(self.all_transactions):,} transactions | Total: ${total_amount:,.2f}")
    
    def _on_transaction_select(self, event):
        """Handle transaction selection"""
        selection = self.tree.selection()
        if not selection:
            self.current_transaction = None
            self.view_items_btn.config(state=tk.DISABLED)
            self.export_btn.config(state=tk.DISABLED)
            return
        
        item = self.tree.item(selection[0])
        trans_id = item['values'][0]
        
        # Find transaction
        self.current_transaction = next((t for t in self.transactions if t.get('transaction_id') == trans_id), None)
        
        if self.current_transaction:
            self.view_items_btn.config(state=tk.NORMAL)
            self.export_btn.config(state=tk.NORMAL)
            self._display_transaction_details()
    
    def _display_transaction_details(self):
        """Display transaction details"""
        if not self.current_transaction:
            return
        
        self.detail_text.delete(1.0, tk.END)
        
        trans = self.current_transaction
        details = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      TRANSACTION DETAILS                        ║
╚══════════════════════════════════════════════════════════════════╝

TRANSACTION INFO
  Transaction ID:  {trans.get('transaction_id', 'N/A')}
  Date:            {trans.get('date', 'N/A')}
  Customer ID:     {trans.get('customer_id', 'N/A')}

LOCATION & STAFF
  Shop Location:   {trans.get('shop_location', 'N/A')}
  Staff Member:    {trans.get('staff_name', 'N/A')}
  Assigned Emp:    {trans.get('assigned_employee', 'N/A')}
  Terminal:        {trans.get('terminal', 'N/A')}

FINANCIAL DETAILS
  Total Amount:    ${float(trans.get('total_amount', 0)):.2f}
  Gross Sales:     ${float(trans.get('gross_sales', 0)):.2f}
  Net Sales:       ${float(trans.get('net_sales', 0)):.2f}
  Total Tax:       ${float(trans.get('total_tax', 0)):.2f}
  COGS:            ${float(trans.get('cogs', 0)):.2f}

PAYMENT & ORDER
  Payment Type:    {trans.get('payment_type', 'N/A')}
  Order Source:    {trans.get('order_source', 'N/A')}
  Queue Type:      {trans.get('queue_type', 'N/A')}
  Transaction Type: {trans.get('transaction_type', 'N/A')}

CUSTOMER INFO
  Marketing Source: {trans.get('marketing_source', 'N/A')}
  Member Group:    {trans.get('member_group', 'N/A')}

METADATA
  Created:         {trans.get('created_at', 'N/A')}
  Updated:         {trans.get('updated_at', 'N/A')}
"""
        
        self.detail_text.insert(1.0, details)
    
    def _view_transaction_items(self):
        """View transaction items"""
        if not self.current_transaction:
            return
        
        # Create popup window
        popup = tk.Toplevel(self.root)
        popup.title(f"Transaction Items - {self.current_transaction.get('transaction_id', 'N/A')}")
        popup.geometry("1000x600")
        
        # Create tree
        tree_frame = tk.Frame(popup)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("Product", "Brand", "Category", "Quantity", "Price", "Total")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Load data
        try:
            response = self.sb.table('transaction_items').select(
                'product_name, brand, category, quantity, unit_price, total_price'
            ).eq('transaction_id', self.current_transaction.get('transaction_id')).execute()
            
            for item in response.data:
                tree.insert('', 'end', values=(
                    item.get('product_name', 'N/A'),
                    item.get('brand', 'N/A'),
                    item.get('category', 'N/A'),
                    item.get('quantity', 1),
                    f"${float(item.get('unit_price', 0)):.2f}",
                    f"${float(item.get('total_price', 0)):.2f}"
                ))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transaction items: {str(e)}")
    
    def _export_transaction_data(self):
        """Export transaction data to CSV"""
        if not self.current_transaction:
            return
        
        # TODO: Implement CSV export
        messagebox.showinfo("Export", "CSV export functionality coming soon!")

def main():
    """Main function"""
    root = tk.Tk()
    app = TransactionViewerEnhanced(root)
    root.mainloop()

if __name__ == "__main__":
    main()
