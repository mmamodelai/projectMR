#!/usr/bin/env python3
"""
X-Viewer Portable - External Budtender Management System
Part of Conductor SMS System

Usage: python x_viewer_portable.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Try to import supabase, show helpful error if not available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# Supabase credentials
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

class DispensaryViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("X-Viewer Portable - External Budtender Management")
        self.root.geometry("1400x800")
        
        # Configure colors (matching your existing viewers)
        self.bg_color = "#1e1e1e"
        self.fg_color = "#ffffff"
        self.accent_color = "#00d4aa"
        
        self.root.configure(bg=self.bg_color)
        
        # Initialize Supabase client
        if not SUPABASE_AVAILABLE:
            self._show_install_instructions()
            return
            
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
    
    def _show_install_instructions(self):
        """Show instructions for installing required packages"""
        instructions = """
REQUIRED PACKAGE MISSING

The 'supabase' package is not installed.

To install it, run this command in your terminal/command prompt:

pip install supabase

Then restart this application.

Alternatively, if you don't have pip, you can:
1. Install Python from python.org
2. Open Command Prompt or Terminal
3. Run: pip install supabase
4. Restart this application

This viewer connects to a cloud database and requires the supabase package to work.
        """
        
        # Create a simple window with instructions
        instructions_window = tk.Toplevel(self.root)
        instructions_window.title("Installation Required")
        instructions_window.geometry("600x400")
        instructions_window.configure(bg=self.bg_color)
        
        # Make it modal
        instructions_window.transient(self.root)
        instructions_window.grab_set()
        
        # Center the window
        instructions_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 50,
            self.root.winfo_rooty() + 50
        ))
        
        # Add text widget with instructions
        text_widget = tk.Text(
            instructions_window,
            wrap=tk.WORD,
            bg="#2d2d2d",
            fg=self.fg_color,
            font=("Arial", 12),
            padx=20,
            pady=20
        )
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        text_widget.insert(tk.END, instructions)
        text_widget.config(state=tk.DISABLED)
        
        # Add close button
        close_button = tk.Button(
            instructions_window,
            text="Close",
            command=instructions_window.destroy,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20
        )
        close_button.pack(pady=20)
    
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
            text="DISPENSARY & BUDTENDER VIEWER - PORTABLE",
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
        tk.Button(
            controls_frame,
            text="Refresh",
            command=self._load_data,
            bg=self.accent_color,
            fg="white",
            font=("Arial", 10, "bold"),
            padx=10
        ).pack(side=tk.RIGHT)
        
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
        
        # Add right-click context menu for editing points
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Edit Points", command=self._edit_points)
        self.budtender_tree.bind("<Button-3>", self._show_context_menu)
    
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
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data from Supabase: {e}")
    
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
        
        # Count budtenders per dispensary
        dispensary_counts = {}
        for budtender in self.filtered_budtenders:
            disp_name = budtender['dispensary_name']
            dispensary_counts[disp_name] = dispensary_counts.get(disp_name, 0) + 1
        
        # Always sort by budtender count (highest first)
        sorted_dispensaries = sorted(dispensary_counts.items(), key=lambda x: x[1], reverse=True)
        
        for dispensary_name, count in sorted_dispensaries:
            display_text = f"{dispensary_name} ({count} budtenders)"
            self.dispensary_listbox.insert(tk.END, display_text)
    
    def _normalize_phone(self, phone):
        """Normalize phone number for searching - remove all non-digits"""
        if not phone:
            return ""
        return ''.join(filter(str.isdigit, str(phone)))
    
    def _live_search(self, *args):
        """Live search - updates as user types"""
        query = self.search_var.get().lower().strip()
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
            
            # Check search query - EXCLUDE dispensary names from search
            if not query:
                self.filtered_budtenders.append(budtender)
            else:
                # Search only budtender details, not dispensary names
                first_name = budtender['first_name'].lower()
                last_name = budtender['last_name'].lower()
                email = (budtender['email'] or '').lower()
                phone = self._normalize_phone(budtender['phone'])
                query_normalized = self._normalize_phone(query)
                
                # Check if query matches any budtender field
                if (query in first_name or
                    query in last_name or
                    query in email or
                    query_normalized in phone):
                    self.filtered_budtenders.append(budtender)
        
        self._update_stats()
        self._populate_dispensary_list()
        self._populate_all_matching_budtenders()
    
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
        
        for budtender in sorted_budtenders:
            dispensary = budtender['dispensary_name']
            name = f"{budtender['first_name']} {budtender['last_name']}"
            email = budtender['email'] or ""
            phone = budtender['phone'] or ""
            points = budtender['points']
            
            self.budtender_tree.insert('', 'end', values=(dispensary, name, email, phone, points))
    
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
                
                self.budtender_tree.insert('', 'end', values=(dispensary, name, email, phone, points))
    
    def _clear_budtender_details(self):
        """Clear budtender details"""
        for item in self.budtender_tree.get_children():
            self.budtender_tree.delete(item)
    
    def _show_context_menu(self, event):
        """Show right-click context menu"""
        item = self.budtender_tree.selection()[0] if self.budtender_tree.selection() else None
        if item:
            self.context_menu.post(event.x_root, event.y_root)
    
    def _edit_points(self):
        """Edit points for selected budtender"""
        selection = self.budtender_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        values = self.budtender_tree.item(item, 'values')
        name = values[1]  # Name is now in column 1 (after Dispensary)
        
        # Find the budtender in our data
        budtender = None
        for b in self.budtenders:
            if f"{b['first_name']} {b['last_name']}" == name:
                budtender = b
                break
        
        if not budtender:
            return
        
        # Show edit dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Points")
        dialog.geometry("300x150")
        dialog.configure(bg=self.bg_color)
        
        tk.Label(dialog, text=f"Edit points for {name}:", bg=self.bg_color, fg=self.fg_color).pack(pady=10)
        
        points_var = tk.StringVar(value=str(budtender['points']))
        points_entry = tk.Entry(dialog, textvariable=points_var, width=20)
        points_entry.pack(pady=10)
        
        def save_points():
            try:
                new_points = int(points_var.get())
                
                # Update in Supabase
                self.sb.table('budtenders').update({'points': new_points}).eq('id', budtender['id']).execute()
                
                # Update local data
                budtender['points'] = new_points
                
                # Refresh display
                if self.search_var.get().strip():
                    self._populate_all_matching_budtenders()
                else:
                    self._populate_budtender_details(self.current_dispensary)
                
                dialog.destroy()
                messagebox.showinfo("Success", f"Points updated for {name}")
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number")
        
        tk.Button(dialog, text="Save", command=save_points, bg=self.accent_color, fg="white").pack(pady=10)

def main():
    """Main function"""
    root = tk.Tk()
    app = DispensaryViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()
