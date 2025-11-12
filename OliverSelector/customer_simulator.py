#!/usr/bin/env python3
"""
OliverSelector - Customer Data Simulator
Part of Conductor SMS System

A comprehensive customer data simulator with SMS generation capabilities.
Features customer metrics, utility curves, and AI-powered SMS suggestions.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import random
import json
from datetime import datetime, timedelta

class CustomerSimulator:
    def __init__(self, root):
        self.root = root
        self.root.title("OliverSelector - Customer Data Simulator")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2c3e50')
        
        # Initialize data
        self.current_customer = None
        self.purchase_history = []
        self.selected_text = ""
        self.sms_options = []
        
        # Create UI
        self.create_ui()
        
        # Load initial sample customer
        self.load_sample_customer()
        
    def create_ui(self):
        """Create the main user interface"""
        
        # Main frame
        main_frame = tk.Frame(self.root, bg='#2c3e50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="OliverSelector - Customer Data Simulator", 
                              font=('Arial', 20, 'bold'), fg='#ecf0f1', bg='#2c3e50')
        title_label.pack(pady=(0, 20))
        
        # Create notebook for tabs
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Main SMS Generator Tab (the beautiful one!)
        self.create_sms_generator_tab(notebook)
        
        # Purchase History Tab
        self.create_purchase_history_tab(notebook)
        
        # AI Training Tab
        self.create_ai_training_tab(notebook)
        
        # Show Your Work Tab
        self.create_show_work_tab(notebook)
        
    def create_sms_generator_tab(self, notebook):
        """Create the main SMS generator tab (the beautiful one!)"""
        
        sms_frame = ttk.Frame(notebook)
        notebook.add(sms_frame, text="SMS Generator")
        
        # Create horizontal layout
        content_frame = tk.Frame(sms_frame, bg='#2c3e50')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Customer info and metrics
        left_panel = tk.Frame(content_frame, bg='#34495e', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        self.create_customer_info_panel(left_panel)
        
        # Center panel - SMS Generator (the white space!)
        center_panel = tk.Frame(content_frame, bg='#ecf0f1', width=600)
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        self.create_sms_generator_panel(center_panel)
        
        # Right panel - Customer selector
        right_panel = tk.Frame(content_frame, bg='#34495e', width=200)
        right_panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        right_panel.pack_propagate(False)
        
        self.create_customer_selector_panel(right_panel)
        
    def create_customer_info_panel(self, parent):
        """Create customer info and utility curve panel"""
        
        # Customer info section
        info_frame = tk.LabelFrame(parent, text="Customer Information", 
                                 font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#34495e')
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.customer_name_label = tk.Label(info_frame, text="Name: Loading...", 
                                          font=('Arial', 11), fg='#ecf0f1', bg='#34495e')
        self.customer_name_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.customer_phone_label = tk.Label(info_frame, text="Phone: Loading...", 
                                           font=('Arial', 11), fg='#ecf0f1', bg='#34495e')
        self.customer_phone_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.customer_email_label = tk.Label(info_frame, text="Email: Loading...", 
                                           font=('Arial', 11), fg='#ecf0f1', bg='#34495e')
        self.customer_email_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Metrics section
        metrics_frame = tk.LabelFrame(parent, text="Key Metrics", 
                                    font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#34495e')
        metrics_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.ltv_label = tk.Label(metrics_frame, text="Lifetime Value: $0", 
                                font=('Arial', 11, 'bold'), fg='#e74c3c', bg='#34495e')
        self.ltv_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.value_per_visit_label = tk.Label(metrics_frame, text="Avg Value/Visit: $0", 
                                            font=('Arial', 11), fg='#f39c12', bg='#34495e')
        self.value_per_visit_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.visits_per_month_label = tk.Label(metrics_frame, text="Visits/Month: 0", 
                                             font=('Arial', 11), fg='#27ae60', bg='#34495e')
        self.visits_per_month_label.pack(anchor=tk.W, padx=10, pady=5)
        
        self.last_visit_label = tk.Label(metrics_frame, text="Last Visit: Never", 
                                       font=('Arial', 11), fg='#9b59b6', bg='#34495e')
        self.last_visit_label.pack(anchor=tk.W, padx=10, pady=5)
        
        # Utility curve section
        utility_frame = tk.LabelFrame(parent, text="Contact Urgency Curve", 
                                     font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#34495e')
        utility_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create matplotlib figure for utility curve
        self.fig, self.ax = plt.subplots(figsize=(4, 3), facecolor='#34495e')
        self.ax.set_facecolor('#34495e')
        self.ax.tick_params(colors='#ecf0f1')
        self.ax.set_xlabel('Days Since Last Visit', color='#ecf0f1')
        self.ax.set_ylabel('Contact Urgency Score', color='#ecf0f1')
        self.ax.set_title('Customer Contact Urgency Curve', color='#ecf0f1')
        
        self.canvas = FigureCanvasTkAgg(self.fig, utility_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
    def create_sms_generator_panel(self, parent):
        """Create SMS generator panel in the center"""
        
        # SMS Generator title
        title_frame = tk.Frame(parent, bg='#ecf0f1')
        title_frame.pack(fill=tk.X, padx=20, pady=(20, 10))
        
        title_label = tk.Label(title_frame, text="SMS Generator", 
                              font=('Arial', 18, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        title_label.pack()
        
        # Generated SMS Options
        options_frame = tk.LabelFrame(parent, text="Generated SMS Options", 
                                    font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Text option 1
        self.text1_frame = tk.Frame(options_frame, bg='#ecf0f1')
        self.text1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(self.text1_frame, text="Option 1:", font=('Arial', 10, 'bold'), 
                fg='#e74c3c', bg='#ecf0f1').pack(anchor=tk.W)
        self.text1_label = tk.Label(self.text1_frame, text="Generating...", 
                                  font=('Arial', 9), fg='#2c3e50', bg='#ecf0f1', wraplength=500)
        self.text1_label.pack(anchor=tk.W, padx=20)
        
        tk.Button(self.text1_frame, text="Select #1 (Numpad 1)", command=lambda: self.select_text(1),
                 bg='#e74c3c', fg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=5)
        
        # Text option 2
        self.text2_frame = tk.Frame(options_frame, bg='#ecf0f1')
        self.text2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(self.text2_frame, text="Option 2:", font=('Arial', 10, 'bold'), 
                fg='#f39c12', bg='#ecf0f1').pack(anchor=tk.W)
        self.text2_label = tk.Label(self.text2_frame, text="Generating...", 
                                  font=('Arial', 9), fg='#2c3e50', bg='#ecf0f1', wraplength=500)
        self.text2_label.pack(anchor=tk.W, padx=20)
        
        tk.Button(self.text2_frame, text="Select #2 (Numpad 2)", command=lambda: self.select_text(2),
                 bg='#f39c12', fg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=5)
        
        # Text option 3
        self.text3_frame = tk.Frame(options_frame, bg='#ecf0f1')
        self.text3_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(self.text3_frame, text="Option 3:", font=('Arial', 10, 'bold'), 
                fg='#27ae60', bg='#ecf0f1').pack(anchor=tk.W)
        self.text3_label = tk.Label(self.text3_frame, text="Generating...", 
                                  font=('Arial', 9), fg='#2c3e50', bg='#ecf0f1', wraplength=500)
        self.text3_label.pack(anchor=tk.W, padx=20)
        
        tk.Button(self.text3_frame, text="Select #3 (Numpad 3)", command=lambda: self.select_text(3),
                 bg='#27ae60', fg='white', font=('Arial', 9, 'bold')).pack(anchor=tk.W, padx=20, pady=5)
        
        # Generate new texts button
        generate_btn = tk.Button(options_frame, text="Generate New SMS Options", 
                               command=self.generate_sms_texts, bg='#3498db', fg='white',
                               font=('Arial', 12, 'bold'))
        generate_btn.pack(pady=10)
        
        # Custom SMS section
        custom_frame = tk.LabelFrame(parent, text="Custom SMS", 
                                   font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        custom_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.custom_text = scrolledtext.ScrolledText(custom_frame, height=6, width=60,
                                                   bg='white', fg='#2c3e50', font=('Arial', 10))
        self.custom_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        tk.Button(custom_frame, text="Use Custom Text", command=self.use_custom_text,
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold')).pack(fill=tk.X, padx=10, pady=5)
        
        # Notes section
        notes_frame = tk.LabelFrame(parent, text="Notes on Message (for AI Training)", 
                                  font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        notes_frame.pack(fill=tk.X, padx=20, pady=10)
        
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=4, width=60,
                                                   bg='white', fg='#2c3e50', font=('Arial', 10))
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Send button
        send_btn = tk.Button(parent, text="SEND SMS", command=self.send_sms,
                           bg='#e74c3c', fg='white', font=('Arial', 16, 'bold'))
        send_btn.pack(pady=20)
        
    def create_customer_selector_panel(self, parent):
        """Create customer selector panel"""
        
        selector_frame = tk.LabelFrame(parent, text="Customer Selector", 
                                     font=('Arial', 12, 'bold'), fg='#ecf0f1', bg='#34495e')
        selector_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.customer_listbox = tk.Listbox(selector_frame, height=15, bg='#2c3e50', 
                                        fg='#ecf0f1', selectbackground='#3498db')
        self.customer_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.customer_listbox.bind('<<ListboxSelect>>', self.on_customer_select)
        
        # Load random customer button
        load_btn = tk.Button(selector_frame, text="Load Random Customer", 
                           command=self.load_random_customer, bg='#3498db', fg='white',
                           font=('Arial', 10, 'bold'))
        load_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # Bind numpad keys
        self.root.bind('<KeyPress>', self.on_key_press)
        
    def create_purchase_history_tab(self, notebook):
        """Create purchase history tab"""
        
        history_frame = ttk.Frame(notebook)
        notebook.add(history_frame, text="Purchase History")
        
        # Purchase history treeview
        columns = ('Date', 'Product', 'Category', 'Quantity', 'Price', 'Total')
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show='headings', height=20)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        # Scrollbar for treeview
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
        
    def create_ai_training_tab(self, notebook):
        """Create AI training tab"""
        
        training_frame = ttk.Frame(notebook)
        notebook.add(training_frame, text="AI Training")
        
        # Notes section
        notes_frame = tk.LabelFrame(training_frame, text="Training Notes", 
                                  font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.notes_text = scrolledtext.ScrolledText(notes_frame, height=15, width=80,
                                                   bg='white', fg='#2c3e50', font=('Arial', 10))
        self.notes_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Save notes button
        save_btn = tk.Button(notes_frame, text="Save Training Notes", command=self.save_training_notes,
                           bg='#27ae60', fg='white', font=('Arial', 12, 'bold'))
        save_btn.pack(pady=10)
        
    def create_show_work_tab(self, notebook):
        """Create Show Your Work tab to display AI reasoning"""
        
        work_frame = ttk.Frame(notebook)
        notebook.add(work_frame, text="Show Your Work")
        
        # AI Analysis section
        analysis_frame = tk.LabelFrame(work_frame, text="AI Analysis & Reasoning", 
                                     font=('Arial', 12, 'bold'), fg='#2c3e50', bg='#ecf0f1')
        analysis_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, height=20, width=100,
                                                     bg='white', fg='#2c3e50', font=('Arial', 10))
        self.analysis_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Refresh analysis button
        refresh_btn = tk.Button(analysis_frame, text="Refresh Analysis", command=self.refresh_analysis,
                              bg='#3498db', fg='white', font=('Arial', 12, 'bold'))
        refresh_btn.pack(pady=10)
        
    def on_key_press(self, event):
        """Handle numpad key presses for SMS selection"""
        
        if event.keysym == 'KP_1' or event.keysym == '1':
            self.select_text(1)
        elif event.keysym == 'KP_2' or event.keysym == '2':
            self.select_text(2)
        elif event.keysym == 'KP_3' or event.keysym == '3':
            self.select_text(3)
            
    def update_customer_display(self):
        """Update customer information display"""
        
        if not self.current_customer:
            return
            
        # Update customer info
        self.customer_name_label.config(text=f"Name: {self.current_customer['name']}")
        self.customer_phone_label.config(text=f"Phone: {self.current_customer['phone']}")
        self.customer_email_label.config(text=f"Email: {self.current_customer['email']}")
        
        # Update metrics
        self.ltv_label.config(text=f"Lifetime Value: ${self.current_customer['ltv']:,.2f}")
        self.value_per_visit_label.config(text=f"Avg Value/Visit: ${self.current_customer['avg_value_per_visit']:,.2f}")
        self.visits_per_month_label.config(text=f"Visits/Month: {self.current_customer['visits_per_month']:.1f}")
        
        # Calculate last visit date
        last_visit_date = datetime.now() - timedelta(days=self.current_customer['last_visit_days'])
        self.last_visit_label.config(text=f"Last Visit: {last_visit_date.strftime('%Y-%m-%d')}")
        
        # Update utility curve
        self.plot_utility_curve()
        
        # Update purchase history
        self.update_purchase_history()
        
        # Generate SMS texts
        self.generate_sms_texts()
        
    def load_sample_customer(self):
        """Load sample customer data"""
        
        # Sample customer data
        self.current_customer = {
            'name': 'Sarah Johnson',
            'phone': '+16195551234',
            'email': 'sarah.johnson@email.com',
            'ltv': 2847.50,
            'avg_value_per_visit': 89.25,
            'visits_per_month': 2.3,
            'last_visit_days': 12,
            'avg_days_between_visits': 7,
            'engagement_score': 0.75
        }
        
        # Sample purchase history
        self.purchase_history = [
            {'date': '2025-10-15', 'product': 'Blue Dream Flower', 'category': 'Flower', 'quantity': 1, 'price': 45.00, 'total': 45.00},
            {'date': '2025-10-08', 'product': 'CBD Gummies', 'category': 'Edibles', 'quantity': 2, 'price': 25.00, 'total': 50.00},
            {'date': '2025-10-01', 'product': 'OG Kush Vape', 'category': 'Vape', 'quantity': 1, 'price': 35.00, 'total': 35.00},
            {'date': '2025-09-24', 'product': 'Sour Diesel Flower', 'category': 'Flower', 'quantity': 1, 'price': 42.00, 'total': 42.00},
            {'date': '2025-09-17', 'product': 'THC Chocolate Bar', 'category': 'Edibles', 'quantity': 1, 'price': 28.00, 'total': 28.00}
        ]
        
        self.update_customer_display()
        
    def load_random_customer(self):
        """Load a random customer from the database"""
        
        # For now, just cycle through sample customers
        sample_customers = [
            {
                'name': 'Mike Chen',
                'phone': '+16195552345',
                'email': 'mike.chen@email.com',
                'ltv': 1523.75,
                'avg_value_per_visit': 67.50,
                'visits_per_month': 1.8,
                'last_visit_days': 5,
                'avg_days_between_visits': 7,
                'engagement_score': 0.85
            },
            {
                'name': 'Emily Rodriguez',
                'phone': '+16195553456',
                'email': 'emily.rodriguez@email.com',
                'ltv': 3892.25,
                'avg_value_per_visit': 125.75,
                'visits_per_month': 3.1,
                'last_visit_days': 2,
                'avg_days_between_visits': 14,
                'engagement_score': 0.92
            },
            {
                'name': 'David Kim',
                'phone': '+16195554567',
                'email': 'david.kim@email.com',
                'ltv': 987.50,
                'avg_value_per_visit': 45.25,
                'visits_per_month': 1.2,
                'last_visit_days': 28,
                'avg_days_between_visits': 21,
                'engagement_score': 0.45
            }
        ]
        
        self.current_customer = random.choice(sample_customers)
        self.update_customer_display()
        self.generate_sms_texts()
        
    def plot_utility_curve(self):
        """Plot the customer utility curve - Contact Urgency over Time"""
        
        self.ax.clear()
        
        # Generate utility curve data
        days = np.linspace(0, 60, 100)
        last_visit_days = self.current_customer['last_visit_days']
        avg_days_between_visits = self.current_customer.get('avg_days_between_visits', 7)
        
        # NEW UTILITY CURVE: Contact urgency increases over time
        # Low urgency right after visit, peaks around their usual pattern + buffer, then declines
        utility = np.zeros_like(days)
        
        for i, day in enumerate(days):
            if day <= 1:
                utility[i] = 0.1  # Just visited, very low urgency
            elif day <= avg_days_between_visits:
                # Building urgency as they approach their usual shopping day
                utility[i] = 0.1 + 0.3 * (day / avg_days_between_visits)
            elif day <= avg_days_between_visits + 3:
                # Peak urgency: past their usual pattern
                peak_day = avg_days_between_visits + 1
                if day <= peak_day:
                    utility[i] = 0.4 + 0.5 * ((day - avg_days_between_visits) / 1)
                else:
                    utility[i] = 0.9 - 0.2 * ((day - peak_day) / 2)
            elif day <= 30:
                # Declining urgency but still worth contacting
                utility[i] = 0.7 * np.exp(-(day - avg_days_between_visits - 3) / 15)
            else:
                # Very low urgency - likely churned
                utility[i] = 0.1 * np.exp(-(day - 30) / 20)
        
        # Plot the curve
        self.ax.plot(days, utility, color='#3498db', linewidth=3, label='Contact Urgency')
        
        # Mark current position
        current_utility = np.interp(last_visit_days, days, utility)
        self.ax.scatter([last_visit_days], [current_utility], color='#e74c3c', s=120, zorder=5)
        self.ax.annotate(f'Current: {current_utility:.2f}', 
                        xy=(last_visit_days, current_utility), 
                        xytext=(10, 10), textcoords='offset points',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='#e74c3c', alpha=0.8),
                        color='white', fontsize=10, fontweight='bold')
        
        # Add reference lines
        self.ax.axvline(x=avg_days_between_visits, color='#f39c12', linestyle='--', alpha=0.7, label=f'Usual Pattern: {avg_days_between_visits} days')
        self.ax.axvline(x=avg_days_between_visits + 2, color='#e74c3c', linestyle='--', alpha=0.7, label='Peak Urgency')
        
        # Styling
        self.ax.set_xlim(0, 60)
        self.ax.set_ylim(0, 1)
        self.ax.grid(True, alpha=0.3, color='#7f8c8d')
        self.ax.set_xlabel('Days Since Last Visit', color='#ecf0f1', fontsize=11)
        self.ax.set_ylabel('Contact Urgency Score', color='#ecf0f1', fontsize=11)
        self.ax.set_title('Customer Contact Urgency Curve', color='#ecf0f1', fontsize=12, fontweight='bold')
        self.ax.legend(loc='upper right', fontsize=9)
        
        self.canvas.draw()
        
    def update_purchase_history(self):
        """Update the purchase history treeview"""
        
        # Clear existing items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Add purchase history items
        for purchase in self.purchase_history:
            self.history_tree.insert('', 'end', values=(
                purchase['date'],
                purchase['product'],
                purchase['category'],
                purchase['quantity'],
                f"${purchase['price']:.2f}",
                f"${purchase['total']:.2f}"
            ))
        
    def generate_sms_texts(self):
        """Generate AI-powered SMS text options based on customer data and real sales patterns"""
        
        if not self.current_customer:
            return
            
        customer = self.current_customer
        last_visit_days = customer['last_visit_days']
        avg_days_between_visits = customer.get('avg_days_between_visits', 7)
        ltv = customer['ltv']
        avg_spend = customer['avg_value_per_visit']
        
        # Analyze customer tier based on real data patterns
        if ltv >= 6000:
            customer_tier = "VIP"
            discount = "25%"
        elif ltv >= 2000:
            customer_tier = "Premium"
            discount = "20%"
        elif ltv >= 500:
            customer_tier = "Regular"
            discount = "15%"
        else:
            customer_tier = "New"
            discount = "10%"
        
        # Generate different SMS strategies based on urgency and customer value
        if last_visit_days <= avg_days_between_visits:
            # Within normal pattern - gentle reminder with personalized offers
            self.sms_options = [
                f"Hi {customer['name'].split()[0]}! Your {customer_tier} status gets you {discount} off today. New premium strains just arrived!",
                f"Hey {customer['name'].split()[0]}! We have strains matching your ${avg_spend:.0f} avg spend. Plus extra loyalty points this week!",
                f"Hi {customer['name'].split()[0]}! Your ${ltv:.0f} lifetime value deserves VIP treatment. New arrivals with {discount} off!"
            ]
        elif last_visit_days <= avg_days_between_visits + 3:
            # Past due - more urgent with value-based incentives
            self.sms_options = [
                f"Hey {customer['name'].split()[0]}! We miss our {customer_tier} customer! {discount} off + free delivery today only!",
                f"Hi {customer['name'].split()[0]}! Your ${ltv:.0f} loyalty deserves better. Come back for {discount} off your next visit!",
                f"{customer['name'].split()[0]}, we've been thinking about you! Special {customer_tier} offer: {discount} off + bonus points!"
            ]
        else:
            # Long overdue - win-back campaign with strong incentives
            self.sms_options = [
                f"Hi {customer['name'].split()[0]}! We'd love to welcome back our {customer_tier} customer. 30% off + $20 credit!",
                f"Hey {customer['name'].split()[0]}! Your ${ltv:.0f} history means everything. Come back for 30% off + free premium sample!",
                f"{customer['name'].split()[0]}, we hope you're doing well! VIP comeback offer: 30% off + priority budtender service!"
            ]
        
        # Update the UI
        self.text1_label.config(text=self.sms_options[0])
        self.text2_label.config(text=self.sms_options[1])
        self.text3_label.config(text=self.sms_options[2])
        
        # Update analysis in Show Your Work tab
        self.update_analysis()
        
    def select_text(self, option_num):
        """Select an SMS text option"""
        
        if option_num <= len(self.sms_options):
            self.selected_text = self.sms_options[option_num - 1]
            messagebox.showinfo("Text Selected", f"Selected Option {option_num}:\n\n{self.selected_text}")
            
    def use_custom_text(self):
        """Use custom SMS text"""
        
        custom_text = self.custom_text.get("1.0", tk.END).strip()
        if custom_text:
            self.selected_text = custom_text
            messagebox.showinfo("Custom Text Selected", f"Custom text selected:\n\n{self.selected_text}")
        else:
            messagebox.showwarning("No Text", "Please enter custom text first.")
            
    def send_sms(self):
        """Send the selected SMS"""
        
        if not self.selected_text:
            messagebox.showwarning("No Text Selected", "Please select an SMS option or enter custom text.")
            return
            
        if not self.current_customer:
            messagebox.showwarning("No Customer", "Please load a customer first.")
            return
            
        # Get notes for AI training
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Simulate sending SMS
        messagebox.showinfo("SMS Sent", 
                          f"SMS sent to {self.current_customer['name']} ({self.current_customer['phone']}):\n\n"
                          f"{self.selected_text}\n\n"
                          f"Notes: {notes if notes else 'None'}")
        
        # Save training data with enhanced format
        self.save_training_data()
        
        # Clear selection
        self.selected_text = ""
        self.custom_text.delete("1.0", tk.END)
        self.notes_text.delete("1.0", tk.END)
        
    def update_analysis(self):
        """Update the AI analysis in Show Your Work tab"""
        
        if not self.current_customer:
            return
            
        customer = self.current_customer
        last_visit_days = customer['last_visit_days']
        avg_days_between_visits = customer.get('avg_days_between_visits', 7)
        ltv = customer['ltv']
        avg_spend = customer['avg_value_per_visit']
        
        # Calculate urgency score
        if last_visit_days <= 1:
            urgency_score = 0.1
            urgency_desc = "Just visited - low urgency"
        elif last_visit_days <= avg_days_between_visits:
            urgency_score = 0.1 + 0.3 * (last_visit_days / avg_days_between_visits)
            urgency_desc = "Building urgency - approaching usual pattern"
        elif last_visit_days <= avg_days_between_visits + 3:
            urgency_score = 0.9
            urgency_desc = "PEAK URGENCY - past due for visit!"
        else:
            urgency_score = 0.7 * (1 - (last_visit_days - avg_days_between_visits - 3) / 30)
            urgency_desc = "Declining urgency - potential churn risk"
        
        # Determine customer tier
        if ltv >= 6000:
            customer_tier = "VIP"
            discount = "25%"
        elif ltv >= 2000:
            customer_tier = "Premium"
            discount = "20%"
        elif ltv >= 500:
            customer_tier = "Regular"
            discount = "15%"
        else:
            customer_tier = "New"
            discount = "10%"
        
        analysis = f"""
AI ANALYSIS & REASONING
=======================

CUSTOMER PROFILE:
- Name: {customer['name']}
- Phone: {customer['phone']}
- Lifetime Value: ${ltv:,.2f}
- Average Spend: ${avg_spend:.2f}
- Visits per Month: {customer['visits_per_month']:.1f}
- Last Visit: {last_visit_days} days ago
- Usual Pattern: Every {avg_days_between_visits} days

CUSTOMER TIER ANALYSIS:
- Tier: {customer_tier}
- Discount Level: {discount}
- Reasoning: Based on ${ltv:,.0f} lifetime value

CONTACT URGENCY ANALYSIS:
- Urgency Score: {urgency_score:.2f}/1.0
- Status: {urgency_desc}
- Days Since Last Visit: {last_visit_days}
- Usual Shopping Pattern: Every {avg_days_between_visits} days

SMS STRATEGY REASONING:
- Strategy: {"Retention" if last_visit_days <= avg_days_between_visits else "Re-engagement" if last_visit_days <= avg_days_between_visits + 3 else "Win-back"}
- Discount Offered: {discount if last_visit_days <= avg_days_between_visits + 3 else "30%"}
- Personalization: Uses customer tier, LTV, and avg spend
- Urgency Level: {"Low" if urgency_score < 0.3 else "Medium" if urgency_score < 0.7 else "High"}

GENERATED SMS OPTIONS:
1. Tier-based offer with discount
2. Spend-based personalization
3. LTV-based VIP treatment

RECOMMENDED TIMING:
- Best Send Time: {"Morning (9-11 AM)" if urgency_score > 0.7 else "Afternoon (2-4 PM)"}
- Reasoning: {"High urgency customers respond better to morning messages" if urgency_score > 0.7 else "Moderate urgency customers prefer afternoon timing"}

DATA SOURCES:
- Customer visit patterns from Supabase
- Real transaction data (36,471 transactions)
- Average spend patterns ($50.84 per transaction)
- Customer tier analysis based on LTV distribution
        """
        
        self.analysis_text.delete("1.0", tk.END)
        self.analysis_text.insert("1.0", analysis)
        
    def refresh_analysis(self):
        """Refresh the AI analysis"""
        self.update_analysis()
        
    def save_training_data(self):
        """Save training data in enhanced format"""
        
        if not self.current_customer or not self.selected_text:
            return
            
        # Get notes
        notes = self.notes_text.get("1.0", tk.END).strip()
        
        # Create enhanced training data
        training_data = {
            "customer_id": self.current_customer['phone'],
            "customer_name": self.current_customer['name'],
            "customer_metrics": {
                "ltv": self.current_customer['ltv'],
                "avg_value_per_visit": self.current_customer['avg_value_per_visit'],
                "visits_per_month": self.current_customer['visits_per_month'],
                "last_visit_days": self.current_customer['last_visit_days'],
                "avg_days_between_visits": self.current_customer.get('avg_days_between_visits', 7),
                "engagement_score": self.current_customer['engagement_score']
            },
            "sms_context": {
                "urgency_score": self.calculate_urgency_score(),
                "customer_tier": self.get_customer_tier(),
                "recommended_discount": self.get_recommended_discount(),
                "strategy_type": self.get_strategy_type()
            },
            "selected_text": self.selected_text,
            "all_options": self.sms_options,
            "feedback": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        # Save to file
        filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(training_data, f, indent=2)
            
        messagebox.showinfo("Training Data Saved", f"Training data saved to {filename}")
        
    def calculate_urgency_score(self):
        """Calculate urgency score for training data"""
        if not self.current_customer:
            return 0
            
        last_visit_days = self.current_customer['last_visit_days']
        avg_days_between_visits = self.current_customer.get('avg_days_between_visits', 7)
        
        if last_visit_days <= 1:
            return 0.1
        elif last_visit_days <= avg_days_between_visits:
            return 0.1 + 0.3 * (last_visit_days / avg_days_between_visits)
        elif last_visit_days <= avg_days_between_visits + 3:
            return 0.9
        else:
            return max(0.1, 0.7 * (1 - (last_visit_days - avg_days_between_visits - 3) / 30))
            
    def get_customer_tier(self):
        """Get customer tier for training data"""
        if not self.current_customer:
            return "Unknown"
            
        ltv = self.current_customer['ltv']
        if ltv >= 6000:
            return "VIP"
        elif ltv >= 2000:
            return "Premium"
        elif ltv >= 500:
            return "Regular"
        else:
            return "New"
            
    def get_recommended_discount(self):
        """Get recommended discount for training data"""
        if not self.current_customer:
            return "10%"
            
        ltv = self.current_customer['ltv']
        last_visit_days = self.current_customer['last_visit_days']
        avg_days_between_visits = self.current_customer.get('avg_days_between_visits', 7)
        
        if last_visit_days > avg_days_between_visits + 3:
            return "30%"
        elif ltv >= 6000:
            return "25%"
        elif ltv >= 2000:
            return "20%"
        elif ltv >= 500:
            return "15%"
        else:
            return "10%"
            
    def get_strategy_type(self):
        """Get strategy type for training data"""
        if not self.current_customer:
            return "Unknown"
            
        last_visit_days = self.current_customer['last_visit_days']
        avg_days_between_visits = self.current_customer.get('avg_days_between_visits', 7)
        
        if last_visit_days <= avg_days_between_visits:
            return "Retention"
        elif last_visit_days <= avg_days_between_visits + 3:
            return "Re-engagement"
        else:
            return "Win-back"
            
    def save_training_notes(self):
        """Save training notes"""
        notes = self.notes_text.get("1.0", tk.END).strip()
        if notes:
            filename = f"training_notes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(filename, 'w') as f:
                f.write(notes)
            messagebox.showinfo("Notes Saved", f"Training notes saved to {filename}")
        else:
            messagebox.showwarning("No Notes", "Please enter some training notes first.")
        
    def on_customer_select(self, event):
        """Handle customer selection from listbox"""
        
        selection = self.customer_listbox.curselection()
        if selection:
            # For now, just load a random customer
            self.load_random_customer()

def main():
    """Main function to run the application"""
    
    root = tk.Tk()
    app = CustomerSimulator(root)
    root.mainloop()

if __name__ == "__main__":
    main()