#!/usr/bin/env python3
"""
Dispensary & Budtender Viewer - Supabase Version
Part of Conductor SMS System

Usage: python dispensary_viewer.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timezone
from supabase import create_client, Client
import sys

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class DispensaryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("Dispensary & Budtender Viewer - Supabase")
        self.root.geometry("1400x800")
        
        # Configure colors (matching your existing viewers)
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize Supabase client
        try:
            self.sb: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect to Supabase: {e}")
            sys.exit(1)
        
        # Data storage
        self.budtenders = []
        self.filtered_budtenders = []
        self.dispensaries = set()
        self.current_dispensary = None
        
        self._create_ui()
        self._load_data()
    
    def _create_ui(self):
        """Create the user interface"""
        
        # Main container
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        title = tk.Label(
            title_frame,
            text="DISPENSARY & BUDTENDER VIEWER - SUPABASE",
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
        tk.Label(controls_frame, text="Search:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._live_search)
        search_entry = tk.Entry(controls_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Removed sort toggle - always sort by budtender count
        
        # Points filter
        tk.Label(controls_frame, text="Min Points:", bg=self.bg_color, fg=self.fg_color).pack(side=tk.LEFT)
        self.points_var = tk.StringVar(value="0")
        points_entry = tk.Entry(controls_frame, textvariable=self.points_var, width=10)
        points_entry.pack(side=tk.LEFT, padx=(5, 20))
        self.points_var.trace('w', self._live_search)
        
        # Refresh button
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh Data",
            command=self._refresh_data,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        )
        refresh_btn.pack(side=tk.RIGHT)
        
        # Bind F5 key for refresh
        self.root.bind('<F5>', lambda e: self._refresh_data())
        
        # Main content area
        content_frame = tk.Frame(main_frame, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Dispensary list
        left_frame = tk.Frame(content_frame, bg=self.bg_color, width=600)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.pack_propagate(False)
        
        tk.Label(
            left_frame,
            text="DISPENSARIES",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Dispensary listbox with scrollbar
        list_frame = tk.Frame(left_frame, bg=self.bg_color)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.dispensary_listbox = tk.Listbox(
            list_frame,
            bg="#2d2d2d",
            fg=self.fg_color,
            selectbackground=self.accent_color,
            font=("Arial", 10),
            height=20
        )
        self.dispensary_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.dispensary_listbox.bind('<<ListboxSelect>>', self._on_dispensary_select)
        
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.dispensary_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dispensary_listbox.config(yscrollcommand=scrollbar.set)
        
        # Right panel - Budtender details
        right_frame = tk.Frame(content_frame, bg=self.bg_color, width=600)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        right_frame.pack_propagate(False)
        
        tk.Label(
            right_frame,
            text="BUDTENDERS",
            font=("Arial", 14, "bold"),
            bg=self.bg_color,
            fg=self.accent_color
        ).pack(pady=(0, 10))
        
        # Budtender details frame
        details_frame = tk.Frame(right_frame, bg=self.bg_color)
        details_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for budtenders
        columns = ('Dispensary', 'Name', 'Email', 'Phone', 'Points')
        self.budtender_tree = ttk.Treeview(details_frame, columns=columns, show='headings', height=20)
        
        # Configure columns
        self.budtender_tree.heading('Dispensary', text='Dispensary')
        self.budtender_tree.heading('Name', text='Name')
        self.budtender_tree.heading('Email', text='Email')
        self.budtender_tree.heading('Phone', text='Phone')
        self.budtender_tree.heading('Points', text='Points')
        
        self.budtender_tree.column('Dispensary', width=150)
        self.budtender_tree.column('Name', width=150)
        self.budtender_tree.column('Email', width=180)
        self.budtender_tree.column('Phone', width=100)
        self.budtender_tree.column('Points', width=80)
        
        # Style the treeview
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Treeview', 
                       background='#2d2d2d',
                       foreground='white',
                       fieldbackground='#2d2d2d')
        style.configure('Treeview.Heading',
                       background='#444444',
                       foreground='white')
        
        self.budtender_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for treeview
        tree_scrollbar = tk.Scrollbar(details_frame, orient=tk.VERTICAL, command=self.budtender_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.budtender_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Add right-click context menu for editing
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="✏️ Edit All Fields", command=self._edit_budtender)
        self.context_menu.add_command(label="🎯 Quick Edit Points", command=self._quick_edit_points)
        self.context_menu.add_command(label="🏆 Award Points + SMS", command=self._award_points_and_notify)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🔄 Refresh", command=self._refresh_data)
        self.budtender_tree.bind("<Button-3>", self._show_context_menu)
        self.budtender_tree.bind("<Double-Button-1>", lambda e: self._edit_budtender())
    
    def _load_data(self):
        """Load budtender data from Supabase"""
        try:
            # Load all budtenders
            result = self.sb.table('budtenders').select('*').execute()
            self.budtenders = result.data
            
            # Extract unique dispensaries
            self.dispensaries = set(budtender['dispensary_name'] for budtender in self.budtenders)
            
            self.filtered_budtenders = self.budtenders.copy()
            self._update_stats()
            self._populate_dispensary_list()
            self._populate_all_matching_budtenders()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data from Supabase: {e}")
    
    def _refresh_data(self):
        """Refresh data from Supabase with visual feedback"""
        self.stats_label.config(text="Refreshing data...")
        self.root.update()  # Force GUI update
        
        try:
            # Load all budtenders
            result = self.sb.table('budtenders').select('*').execute()
            self.budtenders = result.data
            
            # Extract unique dispensaries
            self.dispensaries = set(budtender['dispensary_name'] for budtender in self.budtenders)
            
            self.filtered_budtenders = self.budtenders.copy()
            self._update_stats()
            self._populate_dispensary_list()
            self._populate_all_matching_budtenders()
            
            print(f"Data refreshed: {len(self.budtenders)} budtenders loaded")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh data from Supabase: {e}")
            self.stats_label.config(text="Refresh failed")
    
    def _update_stats(self):
        """Update statistics display"""
        total_budtenders = len(self.budtenders)
        total_dispensaries = len(self.dispensaries)
        filtered_count = len(self.filtered_budtenders)
        
        stats_text = f"Dispensaries: {total_dispensaries} | Budtenders: {filtered_count}/{total_budtenders}"
        self.stats_label.config(text=stats_text)
    
    def _populate_dispensary_list(self):
        """Populate the dispensary listbox - always sorted by budtender count (highest first)"""
        self.dispensary_listbox.delete(0, tk.END)
        
        # Count budtenders per dispensary from ALL budtenders (not filtered)
        dispensary_counts = {}
        for budtender in self.budtenders:
            disp_name = budtender['dispensary_name']
            dispensary_counts[disp_name] = dispensary_counts.get(disp_name, 0) + 1
        
        # Always sort by budtender count (highest first)
        sorted_dispensaries = sorted(dispensary_counts.items(), key=lambda x: x[1], reverse=True)
        
        for dispensary_name, count in sorted_dispensaries:
            display_text = f"{dispensary_name} ({count} budtenders)"
            self.dispensary_listbox.insert(tk.END, display_text)
    
    def _live_search(self, *args):
        """Live search - updates as user types"""
        query = self.search_var.get().lower()
        min_points = 0
        
        try:
            min_points = int(self.points_var.get())
        except ValueError:
            min_points = 0
        
        self.filtered_budtenders = []
        
        for budtender in self.budtenders:
            # Check points filter
            if budtender['points'] < min_points:
                continue
            
            # Check search query
            if not query:
                self.filtered_budtenders.append(budtender)
            else:
                # Search only budtender details, not dispensary names
                first_name = budtender['first_name'].lower()
                last_name = budtender['last_name'].lower()
                full_name = f"{first_name} {last_name}"
                email = (budtender['email'] or '').lower()
                phone = (budtender['phone'] or '')
                
                # Check if query matches any budtender field
                if (query in first_name or
                    query in last_name or
                    query in full_name or
                    query in email or
                    query in phone):
                    self.filtered_budtenders.append(budtender)
        
        self._update_stats()
        self._populate_dispensary_list()
        self._populate_all_matching_budtenders()
        
        # Debug: print search results
        print(f"Search query: '{query}'")
        print(f"Filtered budtenders count: {len(self.filtered_budtenders)}")
        if self.filtered_budtenders:
            results = [f"{b['first_name']} {b['last_name']}" for b in self.filtered_budtenders[:3]]
            print(f"First few results: {results}")
            # Check if Sophia is in the results
            sophia_results = [f"{b['first_name']} {b['last_name']}" for b in self.filtered_budtenders if 'sophia' in f"{b['first_name']} {b['last_name']}".lower()]
            if sophia_results:
                print(f"Sophia found: {sophia_results}")
            else:
                print("Sophia NOT found in results")
    
    def _on_dispensary_select(self, event):
        """Handle dispensary selection - only works when no search is active"""
        # Only show dispensary-specific budtenders if no search is active
        if not self.search_var.get().strip():
            selection = self.dispensary_listbox.curselection()
            if not selection:
                return
            
            # Get the dispensary name from the display text
            display_text = self.dispensary_listbox.get(selection[0])
            dispensary_name = display_text.split(' (')[0]  # Remove the budtender count part
            
            self.current_dispensary = dispensary_name
            self._populate_budtender_details(dispensary_name)
    
    def _populate_all_matching_budtenders(self):
        """Populate all matching budtenders in the right panel (for search results)"""
        # Clear existing items
        for item in self.budtender_tree.get_children():
            self.budtender_tree.delete(item)
        
        # Sort by points (highest first), then by name
        sorted_budtenders = sorted(self.filtered_budtenders, 
                                 key=lambda x: (x['points'], x['first_name'], x['last_name']), 
                                 reverse=True)
        
        print(f"About to insert {len(sorted_budtenders)} budtenders into tree")
        sophia_found = False
        for i, budtender in enumerate(sorted_budtenders):
            dispensary = budtender['dispensary_name']
            name = f"{budtender['first_name']} {budtender['last_name']}"
            email = budtender['email'] or ""
            phone = budtender['phone'] or ""
            points = budtender['points']
            
            self.budtender_tree.insert('', 'end', iid=str(budtender['id']), values=(dispensary, name, email, phone, points))
            if 'sophia' in name.lower():
                print(f"*** FOUND SOPHIA AT INDEX {i}: {name} ***")
                sophia_found = True
        
        print(f"Tree now has {len(self.budtender_tree.get_children())} items")
        if not sophia_found:
            print("*** SOPHIA NOT FOUND IN SORTED BUDTENDERS ***")
    
    def _populate_budtender_details(self, dispensary_name):
        """Populate budtender details for selected dispensary (when no search is active)"""
        # Clear existing items
        for item in self.budtender_tree.get_children():
            self.budtender_tree.delete(item)
        
        # Only show dispensary-specific budtenders if no search is active
        if not self.search_var.get().strip():
            # Filter budtenders for this dispensary
            dispensary_budtenders = [b for b in self.filtered_budtenders if b['dispensary_name'] == dispensary_name]
            
            # Sort by points (highest first)
            dispensary_budtenders.sort(key=lambda x: x['points'], reverse=True)
            
            for budtender in dispensary_budtenders:
                dispensary = budtender['dispensary_name']
                name = f"{budtender['first_name']} {budtender['last_name']}"
                email = budtender['email'] or ""
                phone = budtender['phone'] or ""
                points = budtender['points']
                
                self.budtender_tree.insert('', 'end', iid=str(budtender['id']), values=(dispensary, name, email, phone, points))
    
    def _clear_budtender_details(self):
        """Clear budtender details"""
        for item in self.budtender_tree.get_children():
            self.budtender_tree.delete(item)
    
    def _show_context_menu(self, event):
        """Show right-click context menu"""
        selection = self.budtender_tree.selection()
        if selection:
            item = selection[0]
        else:
            item = self.budtender_tree.identify_row(event.y)
            if item:
                self.budtender_tree.selection_set(item)
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def _edit_budtender(self):
        """Edit all fields for selected budtender"""
        selection = self.budtender_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.budtender_tree.item(item, 'values')
        dispensary, name, email, phone, points = values
        
        # Find the budtender in our data
        budtender = next((b for b in self.budtenders if str(b['id']) == item), None)
        
        if not budtender:
            return
        
        # Show comprehensive edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Edit Budtender - {name}")
        dialog.geometry("500x600")
        dialog.configure(bg=self.bg_color)
        
        # Store scroll position and selection state
        scroll_pos = self.budtender_tree.yview()[0]
        selected_item = item
        
        # Create form
        form_frame = tk.Frame(dialog, bg=self.bg_color)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        fields = []
        
        def create_field(label, value, row):
            tk.Label(form_frame, text=label, bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold")).grid(row=row, column=0, sticky="w", pady=5)
            var = tk.StringVar(value=str(value) if value is not None else "")
            entry = tk.Entry(form_frame, textvariable=var, width=40, font=("Arial", 10))
            entry.grid(row=row, column=1, pady=5, padx=(10, 0))
            return var
        
        tk.Label(form_frame, text=f"Editing: {name}", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color).grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        first_name_var = create_field("First Name:", budtender['first_name'], 1)
        last_name_var = create_field("Last Name:", budtender['last_name'], 2)
        dispensary_var = create_field("Dispensary:", budtender['dispensary_name'], 3)
        email_var = create_field("Email:", budtender['email'] or "", 4)
        phone_var = create_field("Phone:", budtender['phone'] or "", 5)
        points_var = create_field("Points:", budtender['points'], 6)
        title_var = create_field("Title:", budtender.get('title', ''), 7)
        
        def save_changes():
            try:
                # Prepare update data
                update_data = {
                    'first_name': first_name_var.get().strip(),
                    'last_name': last_name_var.get().strip(),
                    'dispensary_name': dispensary_var.get().strip(),
                    'email': email_var.get().strip() or None,
                    'phone': phone_var.get().strip() or None,
                    'points': int(points_var.get()),
                    'title': title_var.get().strip() or None
                }
                
                # Update in Supabase
                self.sb.table('budtenders').update(update_data).eq('id', budtender['id']).execute()
                
                # Update local data
                budtender.update(update_data)
                
                # Refresh display WITHOUT losing position
                self._refresh_display_preserve_state(scroll_pos, selected_item)
                
                dialog.destroy()
                # Don't show messagebox - just update silently
                
            except ValueError as e:
                messagebox.showerror("Error", f"Invalid data: {e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to update: {e}")
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="💾 Save Changes", command=save_changes, bg=self.accent_color, fg="white", font=("Arial", 11, "bold"), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="❌ Cancel", command=dialog.destroy, bg="#666666", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
    
    def _quick_edit_points(self):
        """Quick edit just points"""
        selection = self.budtender_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.budtender_tree.item(item, 'values')
        dispensary, name, email, phone, points = values
        
        # Find the budtender in our data
        budtender = next((b for b in self.budtenders if str(b['id']) == item), None)
        
        if not budtender:
            return
        
        # Store scroll position and selection state
        scroll_pos = self.budtender_tree.yview()[0]
        selected_item = item
        
        # Show edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Quick Edit Points")
        dialog.geometry("350x180")
        dialog.configure(bg=self.bg_color)
        
        tk.Label(dialog, text=f"Edit points for {name}:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 11, "bold")).pack(pady=15)
        
        points_var = tk.StringVar(value=str(budtender['points']))
        points_entry = tk.Entry(dialog, textvariable=points_var, width=20, font=("Arial", 12))
        points_entry.pack(pady=10)
        points_entry.select_range(0, tk.END)
        points_entry.focus()
        
        def save_points():
            try:
                new_points = int(points_var.get())
                
                # Update in Supabase
                self.sb.table('budtenders').update({'points': new_points}).eq('id', budtender['id']).execute()
                
                # Update local data
                budtender['points'] = new_points
                
                # Refresh display WITHOUT losing position
                self._refresh_display_preserve_state(scroll_pos, selected_item)
                
                dialog.destroy()
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        # Bind Enter key to save
        points_entry.bind('<Return>', lambda e: save_points())
        
        tk.Button(dialog, text="💾 Save", command=save_points, bg=self.accent_color, fg="white", font=("Arial", 10, "bold"), padx=20, pady=5).pack(pady=15)
    
    def _award_points_and_notify(self):
        """Increment points via RPC and queue an outbound SMS"""
        selection = self.budtender_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.budtender_tree.item(item, 'values')
        dispensary, name, email, phone, points = values
        
        budtender = next((b for b in self.budtenders if str(b['id']) == item), None)
        if not budtender:
            messagebox.showerror("Error", "Unable to locate budtender record.")
            return
        
        if not budtender.get('phone'):
            messagebox.showerror("Missing Phone", "This budtender does not have a phone number on file. Add a phone number before sending a reward message.")
            return
        
        current_points = budtender.get('points', 0) or 0
        scroll_pos = self.budtender_tree.yview()[0]
        selected_item = item
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Award Points & Send SMS")
        dialog.geometry("500x380")
        dialog.configure(bg=self.bg_color)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"{name} @ {dispensary}", font=("Arial", 14, "bold"), bg=self.bg_color, fg=self.accent_color).pack(pady=(15, 5))
        tk.Label(dialog, text=f"Current Points: {current_points}", font=("Arial", 11), bg=self.bg_color, fg=self.fg_color).pack()
        
        form_frame = tk.Frame(dialog, bg=self.bg_color)
        form_frame.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(form_frame, text="Points to Award:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w")
        points_var = tk.StringVar(value="100")
        points_entry = tk.Entry(form_frame, textvariable=points_var, width=12, font=("Arial", 11))
        points_entry.grid(row=0, column=1, padx=(10, 0))
        
        tk.Label(form_frame, text="Optional Note:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="nw", pady=(15, 0))
        note_text = tk.Text(form_frame, width=32, height=4, font=("Arial", 10), bg="#2d2d2d", fg="white")
        note_text.grid(row=1, column=1, pady=(15, 0), padx=(10, 0))
        
        preview_var = tk.StringVar()
        
        def update_preview(*args):
            try:
                add_points = int(points_var.get())
                if add_points < 0:
                    raise ValueError
                new_total = current_points + add_points
                preview_var.set(
                    f"Great job {budtender['first_name']}! You earned {add_points} points helping customers today. "
                    f"Keep up the great work! Your balance is {new_total} points."
                )
            except ValueError:
                preview_var.set("Enter a non-negative whole number for points.")
        
        points_var.trace_add('write', update_preview)
        update_preview()
        
        preview_frame = tk.Frame(dialog, bg=self.bg_color)
        preview_frame.pack(fill=tk.X, padx=20)
        tk.Label(preview_frame, text="Message Preview:", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10, "bold")).pack(anchor="w")
        tk.Label(preview_frame, textvariable=preview_var, wraplength=440, justify="left", bg=self.bg_color, fg=self.fg_color, font=("Arial", 10)).pack(anchor="w", pady=(5, 0))
        
        def award_and_send():
            try:
                add_points = int(points_var.get())
            except ValueError:
                messagebox.showerror("Invalid Points", "Please enter a valid whole number of points to award.")
                return
            
            if add_points < 0:
                messagebox.showerror("Invalid Points", "Points to award must be zero or greater.")
                return
            
            if add_points == 0:
                confirm = messagebox.askyesno("Confirm Zero Points", "Are you sure you want to queue a message without awarding points?")
                if not confirm:
                    return
            
            note_value = note_text.get("1.0", tk.END).strip() or None
            
            try:
                rpc_result = self.sb.rpc('increment_budtender_points', {
                    'budtender_id': budtender['id'],
                    'points_to_add': add_points
                }).execute()
            except Exception as e:
                messagebox.showerror("Supabase Error", f"Failed to award points: {e}")
                return
            
            if not rpc_result.data:
                messagebox.showerror("Supabase Error", "Did not receive updated budtender data.")
                return
            
            updated_record = rpc_result.data[0]
            new_points = updated_record.get('points', current_points + add_points)
            timestamp = datetime.now(timezone.utc).isoformat()
            message_content = preview_var.get()
            
            message_error = None
            try:
                self.sb.table('messages').insert({
                    'phone_number': budtender['phone'],
                    'content': message_content,
                    'status': 'queued',
                    'direction': 'outbound',
                    'timestamp': timestamp
                }).execute()
            except Exception as e:
                message_error = e
            
            try:
                self.sb.table('budtender_points_history').insert({
                    'budtender_id': budtender['id'],
                    'points_awarded': add_points,
                    'previous_points': current_points,
                    'new_points': new_points,
                    'note': note_value,
                    'awarded_by': 'dispensary_viewer',
                    'created_at': timestamp
                }).execute()
            except Exception:
                pass
            
            budtender.update(updated_record)
            self._refresh_display_preserve_state(scroll_pos, selected_item)
            
            if message_error:
                messagebox.showwarning("Partial Success", f"Points updated, but SMS could not be queued:\n{message_error}")
            else:
                messagebox.showinfo("Success", f"Awarded {add_points} points and queued SMS.\nNew balance: {new_points} points.")
            
            dialog.destroy()
        
        button_frame = tk.Frame(dialog, bg=self.bg_color)
        button_frame.pack(pady=20)
        tk.Button(button_frame, text="🏆 Award & Send", command=award_and_send, bg=self.accent_color, fg="black", font=("Arial", 11, "bold"), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Cancel", command=dialog.destroy, bg="#666666", fg="white", font=("Arial", 11), padx=20, pady=5).pack(side=tk.LEFT, padx=5)
        
        points_entry.focus()
    
    def _refresh_display_preserve_state(self, scroll_pos, selected_item):
        """Refresh display while preserving scroll position and selection"""
        # Refresh display
        if self.search_var.get().strip():
            self._populate_all_matching_budtenders()
        else:
            if self.current_dispensary:
                self._populate_budtender_details(self.current_dispensary)
            else:
                self._populate_all_matching_budtenders()
        
        # Restore scroll position
        try:
            self.budtender_tree.yview_moveto(scroll_pos)
            # Try to restore selection
            if selected_item:
                self.budtender_tree.selection_set(selected_item)
        except:
            pass  # If item no longer exists, just skip

def main():
    """Main function"""
    root = tk.Tk()
    app = DispensaryViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()