#!/usr/bin/env python3
"""
MoTa CRM - FULLY INTEGRATED
Customer → Transactions → Purchase Items - All in one view
"""

import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from datetime import datetime
from supabase_helpers import fetch_all_records

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class IntegratedCRM:
    def __init__(self, root):
        self.root = root
        self.root.title("MoTa CRM - INTEGRATED")
        self.root.geometry("1800x1000")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        
        # Sort tracking
        self.sort_column = None
        self.sort_reverse = False
        
        self.root.configure(bg=self.bg_color)
        
        # Data
        self.customers = []
        self.current_customer = None
        
        self._create_ui()
        self._load_customers()
    
    def _create_ui(self):
        """Create integrated UI"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title = tk.Label(
            main_frame,
            text="MOTA CRM - INTEGRATED SYSTEM",
            font=("Arial", 20, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title.pack(pady=(0, 10))
        
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
        
        cust_columns = ("Name", "Phone", "VIP", "Visits", "Lifetime")
        self.cust_tree = ttk.Treeview(cust_tree_frame, columns=cust_columns, show="headings", selectmode="browse")
        
        # Make columns sortable
        for col in cust_columns:
            self.cust_tree.heading(col, text=col, command=lambda c=col: self._sort_customers(c))
        
        self.cust_tree.column("Name", width=150)
        self.cust_tree.column("Phone", width=100)
        self.cust_tree.column("VIP", width=60)
        self.cust_tree.column("Visits", width=50)
        self.cust_tree.column("Lifetime", width=80)
        
        cust_vsb = ttk.Scrollbar(cust_tree_frame, orient="vertical", command=self.cust_tree.yview)
        self.cust_tree.configure(yscrollcommand=cust_vsb.set)
        
        self.cust_tree.grid(row=0, column=0, sticky="nsew")
        cust_vsb.grid(row=0, column=1, sticky="ns")
        
        cust_tree_frame.grid_rowconfigure(0, weight=1)
        cust_tree_frame.grid_columnconfigure(0, weight=1)
        
        self.cust_tree.bind('<<TreeviewSelect>>', self._on_customer_select)
        self.cust_tree.bind('<Button-3>', self._on_customer_right_click)  # Right-click
        
        # MIDDLE: Transactions
        middle_frame = tk.Frame(content_frame, bg=self.bg_color, width=600)
        middle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            middle_frame,
            text="TRANSACTIONS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Transaction tree
        trans_tree_frame = tk.Frame(middle_frame, bg=self.bg_color)
        trans_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        trans_columns = ("Date", "Amount", "Staff", "Location")
        self.trans_tree = ttk.Treeview(trans_tree_frame, columns=trans_columns, show="headings", selectmode="browse")
        
        for col in trans_columns:
            self.trans_tree.heading(col, text=col)
        
        self.trans_tree.column("Date", width=100)
        self.trans_tree.column("Amount", width=80)
        self.trans_tree.column("Staff", width=120)
        self.trans_tree.column("Location", width=150)
        
        trans_vsb = ttk.Scrollbar(trans_tree_frame, orient="vertical", command=self.trans_tree.yview)
        self.trans_tree.configure(yscrollcommand=trans_vsb.set)
        
        self.trans_tree.grid(row=0, column=0, sticky="nsew")
        trans_vsb.grid(row=0, column=1, sticky="ns")
        
        trans_tree_frame.grid_rowconfigure(0, weight=1)
        trans_tree_frame.grid_columnconfigure(0, weight=1)
        
        self.trans_tree.bind('<<TreeviewSelect>>', self._on_transaction_select)
        
        # RIGHT: Purchase Items
        right_frame = tk.Frame(content_frame, bg=self.bg_color, width=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            right_frame,
            text="PURCHASE ITEMS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Items tree
        items_tree_frame = tk.Frame(right_frame, bg=self.bg_color)
        items_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        items_columns = ("Product", "Brand", "Category", "Price", "Qty")
        self.items_tree = ttk.Treeview(items_tree_frame, columns=items_columns, show="headings")
        
        for col in items_columns:
            self.items_tree.heading(col, text=col)
        
        self.items_tree.column("Product", width=200)
        self.items_tree.column("Brand", width=100)
        self.items_tree.column("Category", width=100)
        self.items_tree.column("Price", width=80)
        self.items_tree.column("Qty", width=50)
        
        items_vsb = ttk.Scrollbar(items_tree_frame, orient="vertical", command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=items_vsb.set)
        
        self.items_tree.grid(row=0, column=0, sticky="nsew")
        items_vsb.grid(row=0, column=1, sticky="ns")
        
        items_tree_frame.grid_rowconfigure(0, weight=1)
        items_tree_frame.grid_columnconfigure(0, weight=1)
        
        self.items_tree.bind('<<TreeviewSelect>>', self._on_item_select)
        
        # Product details text below items
        tk.Label(
            right_frame,
            text="PRODUCT DETAILS",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(10, 5))
        
        product_text_frame = tk.Frame(right_frame, bg=self.bg_color)
        product_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.product_text = tk.Text(
            product_text_frame,
            wrap=tk.WORD,
            font=("Courier", 9),
            bg="#2d2d2d",
            fg=self.fg_color,
            height=10,
            padx=10,
            pady=10
        )
        product_scroll = ttk.Scrollbar(product_text_frame, orient="vertical", command=self.product_text.yview)
        self.product_text.config(yscrollcommand=product_scroll.set)
        
        self.product_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        product_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_label = tk.Label(
            main_frame,
            text="Loading customers...",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.status_label.pack(pady=(10, 0))
    
    def _load_customers(self):
        """Load all customers"""
        try:
            self.status_label.config(text="Loading customers...")
            self.root.update()
            
            # Get all customers
            self.customers = fetch_all_records(self.sb, 'customers', order_by='id', order_desc=True)
            
            self._populate_customers(self.customers)
            self.status_label.config(text=f"Loaded {len(self.customers):,} customers - Select a customer to view their transactions")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _populate_customers(self, customers):
        """Populate customer tree"""
        for item in self.cust_tree.get_children():
            self.cust_tree.delete(item)
        
        for customer in customers:
            self.cust_tree.insert('', 'end', values=(
                customer.get('name', 'N/A'),
                customer.get('phone', 'N/A'),
                customer.get('vip_status', 'N/A'),
                customer.get('total_visits', 0),
                f"${float(customer.get('lifetime_value', 0)):.0f}"
            ), tags=(customer.get('member_id'),))
    
    def _on_search(self, event=None):
        """Filter customers by search"""
        search_term = self.search_var.get().lower()
        
        if not search_term:
            self._populate_customers(self.customers)
            self.status_label.config(text=f"Showing all {len(self.customers):,} customers")
            return
        
        filtered = []
        for c in self.customers:
            name = str(c.get('name', '')).lower()
            phone = str(c.get('phone', '')).lower()
            if search_term in name or search_term in phone:
                filtered.append(c)
        
        self._populate_customers(filtered)
        self.status_label.config(text=f"Showing {len(filtered):,} of {len(self.customers):,} customers")
    
    def _clear_search(self):
        """Clear search"""
        self.search_var.set('')
        self._populate_customers(self.customers)
        self.status_label.config(text=f"Showing all {len(self.customers):,} customers")
    
    def _on_customer_select(self, event):
        """Load customer transactions"""
        selection = self.cust_tree.selection()
        if not selection:
            return
        
        # Get member_id from tags
        member_id = self.cust_tree.item(selection[0])['tags'][0]
        
        # Find customer
        self.current_customer = next((c for c in self.customers if c.get('member_id') == member_id), None)
        
        if not self.current_customer:
            return
        
        # Clear items
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        # Load transactions
        self._load_customer_transactions(member_id)
    
    def _load_customer_transactions(self, member_id):
        """Load transactions for customer"""
        try:
            self.status_label.config(text=f"Loading transactions for {self.current_customer.get('name')}...")
            self.root.update()
            
            # Clear transactions
            for item in self.trans_tree.get_children():
                self.trans_tree.delete(item)
            
            # Get transactions
            response = self.sb.table('transactions').select('*').eq('customer_id', member_id).order('date', desc=True).execute()
            transactions = response.data
            
            # Populate transactions
            for trans in transactions:
                date = trans.get('date', 'N/A')
                if date != 'N/A':
                    try:
                        dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
                        date = dt.strftime('%Y-%m-%d')
                    except:
                        pass
                
                self.trans_tree.insert('', 'end', values=(
                    date,
                    f"${float(trans.get('total_amount', 0)):.2f}",
                    trans.get('staff_name', 'Unknown'),
                    trans.get('shop_location', 'Unknown')
                ), tags=(trans.get('transaction_id'),))
            
            self.status_label.config(text=f"Showing {len(transactions)} transactions for {self.current_customer.get('name')} - Click a transaction to see items")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load transactions: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _on_transaction_select(self, event):
        """Load transaction items"""
        selection = self.trans_tree.selection()
        if not selection:
            return
        
        # Get transaction_id from tags
        transaction_id = self.trans_tree.item(selection[0])['tags'][0]
        
        # Load items
        self._load_transaction_items(transaction_id)
    
    def _load_transaction_items(self, transaction_id):
        """Load items for transaction"""
        try:
            self.status_label.config(text=f"Loading items for transaction {transaction_id}...")
            self.root.update()
            
            # Clear items
            for item in self.items_tree.get_children():
                self.items_tree.delete(item)
            
            # Get items
            response = self.sb.table('transaction_items').select('*').eq('transaction_id', transaction_id).execute()
            items = response.data
            
            # Populate items
            for item in items:
                self.items_tree.insert('', 'end', values=(
                    item.get('product_name', 'N/A'),
                    item.get('brand', 'N/A'),
                    item.get('category', 'N/A'),
                    f"${float(item.get('total_price', 0)):.2f}",
                    item.get('quantity', 1)
                ))
            
            self.status_label.config(text=f"Showing {len(items)} items in transaction {transaction_id} - Click an item to see product details")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load items: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _on_item_select(self, event):
        """Show product details when item is selected"""
        selection = self.items_tree.selection()
        if not selection:
            return
        
        item_values = self.items_tree.item(selection[0])['values']
        product_name = item_values[0]
        
        self._load_product_details(product_name)
    
    def _load_product_details(self, product_name):
        """Load and display product details"""
        try:
            self.status_label.config(text=f"Loading product details for {product_name}...")
            self.root.update()
            
            self.product_text.delete(1.0, tk.END)
            
            # Get product from database
            response = self.sb.table('products').select('*').ilike('name', f'%{product_name}%').limit(1).execute()
            
            if not response.data:
                self.product_text.insert(1.0, f"Product: {product_name}\n\nNot found in product database.")
                return
            
            product = response.data[0]
            
            # Build product details display
            details = f"""
PRODUCT: {product.get('name', 'N/A')}
SKU: {product.get('product_id', 'N/A')}
Brand: {product.get('brand', 'N/A')}
Category: {product.get('category', 'N/A')}

CANNABIS PROFILE:
  Type: {product.get('flower_type', 'N/A')}
  Strain: {product.get('strain', 'N/A')}
  THC: {product.get('thc_content', 'N/A')}%
  CBD: {product.get('cbd_content', 'N/A')}%

PRICING:
  Retail: ${float(product.get('retail_price', 0)):.2f}
  Cost: ${float(product.get('cost', 0)):.2f if product.get('cost') else 'N/A'}

INVENTORY:
  Status: {'Active' if product.get('is_active') else 'Inactive'}
  Vendor: {product.get('vendor', 'N/A')}

EFFECTS:
  {self._get_effects(product)}
"""
            
            self.product_text.insert(1.0, details)
            self.status_label.config(text=f"Showing product details for {product_name}")
            
        except Exception as e:
            self.product_text.delete(1.0, tk.END)
            self.product_text.insert(1.0, f"Error loading product: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}")
    
    def _get_effects(self, product):
        """Get effects description based on strain type"""
        flower_type = str(product.get('flower_type', '')).lower()
        category = str(product.get('category', '')).lower()
        
        if 'sativa' in flower_type:
            return "High Energy • Uplifting • Creative • Daytime Use"
        elif 'indica' in flower_type:
            return "Relaxing • Calming • Sleep Aid • Evening Use"
        elif 'hybrid' in flower_type:
            return "Balanced • Versatile • All-Day Use"
        elif 'vape' in category or 'cartridge' in category:
            return "Fast-Acting • Discreet • Portable"
        elif 'edible' in category:
            return "Long-Lasting • Precise Dosing • Smoke-Free"
        else:
            return "See budtender for specific effects"
    
    def _sort_customers(self, column):
        """Sort customers by column"""
        # Toggle sort direction if same column, else ascending
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
        
        # Map display columns to data keys
        column_map = {
            "Name": "name",
            "Phone": "phone",
            "VIP": "vip_status",
            "Visits": "total_visits",
            "Lifetime": "lifetime_value"
        }
        
        sort_key = column_map.get(column, "name")
        
        # Sort customers
        try:
            self.customers.sort(
                key=lambda x: x.get(sort_key) if x.get(sort_key) is not None else ("" if isinstance(x.get(sort_key, ""), str) else 0),
                reverse=self.sort_reverse
            )
            
            # Repopulate
            self._populate_customers(self.customers)
            
            # Update status
            direction = "descending" if self.sort_reverse else "ascending"
            self.status_label.config(text=f"Sorted by {column} ({direction})")
            
        except Exception as e:
            messagebox.showerror("Sort Error", f"Failed to sort: {str(e)}")
    
    def _on_customer_right_click(self, event):
        """Handle right-click on customer"""
        # Get clicked item
        item_id = self.cust_tree.identify_row(event.y)
        if not item_id:
            return
        
        self.cust_tree.selection_set(item_id)
        
        # Get member_id
        member_id = self.cust_tree.item(item_id)['tags'][0]
        customer = next((c for c in self.customers if c.get('member_id') == member_id), None)
        
        if not customer:
            return
        
        # Create context menu
        menu = tk.Menu(self.root, tearoff=0, bg=self.bg_color, fg=self.fg_color)
        menu.add_command(label="Edit Name", command=lambda: self._edit_field(customer, 'name'))
        menu.add_command(label="Edit Phone", command=lambda: self._edit_field(customer, 'phone'))
        menu.add_command(label="Edit VIP Status", command=lambda: self._edit_field(customer, 'vip_status'))
        menu.add_separator()
        menu.add_command(label="View Full Profile", command=lambda: self._view_profile(customer))
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
    
    def _edit_field(self, customer, field_name):
        """Edit a customer field"""
        # Field display names
        field_labels = {
            'name': 'Name',
            'phone': 'Phone Number',
            'vip_status': 'VIP Status'
        }
        
        label = field_labels.get(field_name, field_name)
        current_value = customer.get(field_name, '')
        
        # Create dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit {label}")
        dialog.geometry("400x150")
        dialog.configure(bg=self.bg_color)
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(
            dialog,
            text=f"Edit {label} for {customer.get('name', 'Unknown')}:",
            bg=self.bg_color,
            fg=self.fg_color,
            font=("Arial", 10)
        ).pack(pady=10)
        
        entry_var = tk.StringVar(value=current_value)
        entry = tk.Entry(dialog, textvariable=entry_var, font=("Arial", 12), width=30)
        entry.pack(pady=10)
        entry.focus()
        entry.select_range(0, tk.END)
        
        def save():
            new_value = entry_var.get().strip()
            
            if not new_value and field_name == 'name':
                messagebox.showerror("Error", "Name cannot be empty")
                return
            
            try:
                # Update in Supabase
                self.sb.table('customers').update({
                    field_name: new_value
                }).eq('member_id', customer['member_id']).execute()
                
                # Update local data
                customer[field_name] = new_value
                self._populate_customers(self.customers)
                
                self.status_label.config(text=f"Updated {label} for {customer.get('name')}")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {str(e)}")
        
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Save",
            command=save,
            bg=self.accent_color,
            fg="#000000",
            font=("Arial", 10, "bold"),
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#555555",
            fg=self.fg_color,
            font=("Arial", 10),
            padx=20
        ).pack(side=tk.LEFT, padx=5)
        
        entry.bind('<Return>', lambda e: save())
        entry.bind('<Escape>', lambda e: dialog.destroy())
    
    def _view_profile(self, customer):
        """View full customer profile"""
        profile_text = f"""
CUSTOMER PROFILE
{'=' * 60}

Name: {customer.get('name', 'N/A')}
Phone: {customer.get('phone', 'N/A')}
Email: {customer.get('email', 'N/A')}

VIP Status: {customer.get('vip_status', 'N/A')}
Member ID: {customer.get('member_id', 'N/A')}

Total Visits: {customer.get('total_visits', 0)}
Lifetime Value: ${float(customer.get('lifetime_value', 0)):.2f}
Last Visit: {customer.get('last_visit_date', 'N/A')}

Churn Risk: {customer.get('churn_risk', 'N/A')}
Member Since: {customer.get('member_since', 'N/A')}

Gender: {customer.get('gender', 'N/A')}
Age: {customer.get('age', 'N/A')}
City: {customer.get('city', 'N/A')}
State: {customer.get('state', 'N/A')}
Zip: {customer.get('zip_code', 'N/A')}

Loyalty Points Balance: {customer.get('loyalty_points_balance', 0)}
"""
        
        messagebox.showinfo("Customer Profile", profile_text)

def main():
    """Main function"""
    root = tk.Tk()
    app = IntegratedCRM(root)
    root.mainloop()

if __name__ == "__main__":
    main()

