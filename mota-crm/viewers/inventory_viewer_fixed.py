#!/usr/bin/env python3
"""
MoTa Inventory & Products Database Viewer - FIXED VERSION
View and analyze product catalog from Supabase
"""

import tkinter as tk
from tkinter import ttk, messagebox
from supabase import create_client, Client
from datetime import datetime
import random
from supabase_helpers import fetch_all_records

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class InventoryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("MoTa Inventory & Products Viewer - FIXED")
        self.root.geometry("1400x800")
        
        # Supabase client
        self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Configure colors
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        
        self.root.configure(bg=self.bg_color)
        
        # Data storage
        self.all_products = []
        self.displayed_products = []
        self.current_limit = 1000
        
        self._create_ui()
        self._load_products()
    
    def _create_ui(self):
        """Create the user interface"""
        
        # Title
        title_frame = tk.Frame(self.root, bg=self.bg_color)
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title = tk.Label(
            title_frame,
            text="MOTA INVENTORY & PRODUCTS",
            font=("Arial", 18, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        )
        title.pack(side=tk.LEFT)
        
        # Stats and controls
        stats_frame = tk.Frame(title_frame, bg=self.bg_color)
        stats_frame.pack(side=tk.RIGHT)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="Total Products: 0",
            font=("Arial", 10),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.stats_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Refresh button
        refresh_btn = tk.Button(
            stats_frame,
            text="Refresh",
            command=self._load_products,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Controls frame
        controls_frame = tk.Frame(self.root, bg=self.bg_color)
        controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Search
        tk.Label(controls_frame, text="Search:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._filter_products)
        search_entry = tk.Entry(controls_frame, textvariable=self.search_var, width=20)
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Category filter
        tk.Label(controls_frame, text="Category:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(controls_frame, textvariable=self.category_var, width=15)
        self.category_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_products())
        
        # Brand filter
        tk.Label(controls_frame, text="Brand:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.brand_var = tk.StringVar(value="All")
        self.brand_combo = ttk.Combobox(controls_frame, textvariable=self.brand_var, width=15)
        self.brand_combo.pack(side=tk.LEFT, padx=(5, 20))
        self.brand_combo.bind('<<ComboboxSelected>>', lambda e: self._filter_products())
        
        # Load controls
        load_frame = tk.Frame(controls_frame, bg=self.bg_color)
        load_frame.pack(side=tk.RIGHT)
        
        tk.Label(load_frame, text="Load:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        
        # Load buttons
        load_1k_btn = tk.Button(
            load_frame,
            text="1K",
            command=lambda: self._set_limit(1000),
            bg="#444444",
            fg="white",
            font=("Arial", 9),
            padx=8
        )
        load_1k_btn.pack(side=tk.LEFT, padx=2)
        
        load_5k_btn = tk.Button(
            load_frame,
            text="5K",
            command=lambda: self._set_limit(5000),
            bg="#444444",
            fg="white",
            font=("Arial", 9),
            padx=8
        )
        load_5k_btn.pack(side=tk.LEFT, padx=2)
        
        load_all_btn = tk.Button(
            load_frame,
            text="ALL",
            command=lambda: self._set_limit(0),
            bg="#444444",
            fg="white",
            font=("Arial", 9),
            padx=8
        )
        load_all_btn.pack(side=tk.LEFT, padx=2)
        
        # Randomize button
        random_btn = tk.Button(
            load_frame,
            text="RANDOM",
            command=self._randomize_products,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 9, "bold"),
            padx=8
        )
        random_btn.pack(side=tk.LEFT, padx=(10, 0))
        
        # Content frame
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Products tree
        tree_frame = tk.Frame(content_frame, bg=self.bg_color)
        tree_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        columns = ("SKU", "Product", "Brand", "Category", "Type", "THC%", "CBD%")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", selectmode="extended")
        
        # Column configuration
        self.tree.heading("SKU", text="SKU")
        self.tree.heading("Product", text="Product Name")
        self.tree.heading("Brand", text="Brand")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Type", text="Flower Type")
        self.tree.heading("THC%", text="THC %")
        self.tree.heading("CBD%", text="CBD %")
        
        self.tree.column("SKU", width=100)
        self.tree.column("Product", width=350)
        self.tree.column("Brand", width=150)
        self.tree.column("Category", width=150)
        self.tree.column("Type", width=100)
        self.tree.column("THC%", width=80)
        self.tree.column("CBD%", width=80)
        
        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Details panel
        details_frame = tk.Frame(content_frame, bg=self.bg_color, width=400)
        details_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        details_frame.pack_propagate(False)
        
        tk.Label(
            details_frame,
            text="PRODUCT DETAILS",
            font=("Arial", 12, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Details text widget
        self.detail_text = tk.Text(
            details_frame,
            height=20,
            width=50,
            bg="#2d2d2d",
            fg=self.fg_color,
            font=("Courier", 9),
            wrap=tk.WORD
        )
        self.detail_text.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.bg_color)
        status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_label = tk.Label(
            status_frame,
            text="Ready",
            font=("Arial", 9),
            bg=self.bg_color,
            fg=self.fg_color
        )
        self.status_label.pack(side=tk.LEFT)
    
    def _set_limit(self, limit):
        """Set the display limit"""
        self.current_limit = limit
        self._filter_products()
    
    def _randomize_products(self):
        """Show random 1000 products"""
        if not self.all_products:
            return
        
        # Shuffle and take first 1000
        random.shuffle(self.all_products)
        self.displayed_products = self.all_products[:1000]
        self._populate_tree(self.displayed_products)
        self.status_label.config(text=f"Showing random 1,000 products from {len(self.all_products):,} total")
    
    def _load_products(self):
        """Load products from Supabase"""
        try:
            self.status_label.config(text="Loading ALL products (this may take a moment)...")
            self.root.update()
            
            # Get ALL products using pagination
            self.all_products = fetch_all_records(self.sb, 'products')
            
            # Get categories and brands for filters
            categories = set(p.get('category', 'Unknown') for p in self.all_products if p.get('category'))
            brands = set(p.get('brand', 'Unknown') for p in self.all_products if p.get('brand'))
            
            self.category_combo['values'] = ['All'] + sorted(categories)
            self.brand_combo['values'] = ['All'] + sorted(brands)
            
            # Update stats
            self.stats_label.config(text=f"Total Products: {len(self.all_products):,}")
            
            # Apply current limit and filters
            self._filter_products()
            self.status_label.config(text=f"Loaded {len(self.all_products):,} products")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load products: {str(e)}")
            self.status_label.config(text="Error loading products")
    
    def _populate_tree(self, products):
        """Populate tree with products"""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Insert products
        for product in products:
            sku = product.get('product_id', 'N/A')
            name = product.get('name', 'Unknown')  # FIXED: Use 'name' not 'product_name'
            brand = product.get('brand', 'Unknown')
            category = product.get('category', 'Unknown')
            flower_type = product.get('flower_type', '')
            thc = f"{float(product.get('thc_content', 0)):.1f}" if product.get('thc_content') else ''  # FIXED: Use 'thc_content'
            cbd = f"{float(product.get('cbd_content', 0)):.1f}" if product.get('cbd_content') else ''  # FIXED: Use 'cbd_content'
            
            self.tree.insert('', 'end', values=(sku, name, brand, category, flower_type, thc, cbd))
    
    def _filter_products(self):
        """Filter products based on search and dropdowns"""
        if not self.all_products:
            return
        
        search_term = self.search_var.get().lower()
        category = self.category_var.get()
        brand = self.brand_var.get()
        
        # Filter products
        filtered = []
        for product in self.all_products:
            # Search filter
            if search_term:
                name = product.get('name', '').lower()
                sku = product.get('product_id', '').lower()
                if search_term not in name and search_term not in sku:
                    continue
            
            # Category filter
            if category != "All":
                if product.get('category') != category:
                    continue
            
            # Brand filter
            if brand != "All":
                if product.get('brand') != brand:
                    continue
            
            filtered.append(product)
        
        # Apply limit
        if self.current_limit > 0:
            self.displayed_products = filtered[:self.current_limit]
        else:
            self.displayed_products = filtered
        
        self._populate_tree(self.displayed_products)
        self.status_label.config(text=f"Showing {len(self.displayed_products):,} of {len(filtered):,} filtered products")
    
    def _on_select(self, event):
        """Handle product selection"""
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        sku = item['values'][0]
        
        # Find product details
        product = None
        for p in self.displayed_products:
            if p.get('product_id') == sku:
                product = p
                break
        
        if product:
            self._display_product_details(product)
    
    def _display_product_details(self, product):
        """Display product details in text widget"""
        self.detail_text.delete(1.0, tk.END)
        
        details = f"""
╔══════════════════════════════════════════════════════════════════╗
║                      PRODUCT DETAILS                             ║
╚══════════════════════════════════════════════════════════════════╝

IDENTIFICATION
  Product ID:     {product.get('product_id', 'N/A')}
  Product Name:   {product.get('name', 'N/A')}
  Brand:          {product.get('brand', 'N/A')}
  Vendor:         {product.get('vendor', 'N/A')}

CATEGORY
  Category:       {product.get('category', 'N/A')}
  Type:           {product.get('flower_type', 'N/A')}
  Flower Type:    {product.get('flower_type', 'N/A')}

CANNABINOID CONTENT
  Total THC:      {f"{float(product.get('thc_content', 0)):.2f}%" if product.get('thc_content') else "N/A"}
  Total CBD:      {f"{float(product.get('cbd_content', 0)):.2f}%" if product.get('cbd_content') else "N/A"}

METADATA
  Created:        {product.get('created_at', 'N/A')}
  Updated:        {product.get('updated_at', 'N/A')}
  Active:         {product.get('is_active', 'N/A')}
"""
        
        self.detail_text.insert(1.0, details)

def main():
    """Main function"""
    root = tk.Tk()
    app = InventoryViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
