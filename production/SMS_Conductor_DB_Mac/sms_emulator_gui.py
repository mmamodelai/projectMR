#!/usr/bin/env python3
"""
SMS Conductor Emulator - GUI Edition
Beautiful chat interface for testing chatbot workflows
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os
from sms_emulator import SMSEmulatorSupabase

class SMSEmulatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SMS Conductor Emulator - Chatbot Testing")
        self.root.geometry("900x750")
        self.root.configure(bg="#f0f0f0")
        
        self.emulator = None
        self.current_phone = None
        self.label_to_msg_id = {}
        
        # Try to connect to Supabase
        try:
            self.emulator = SMSEmulatorSupabase()
            self.connected = True
        except Exception as e:
            self.connected = False
            messagebox.showerror("Connection Error", f"Failed to connect to Supabase:\n{e}")
        
        # Create notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Dashboard tab
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.setup_dashboard()
        
        # Chat tab
        self.chat_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.chat_frame, text="Chat")
        self.setup_chat()
    
    def setup_dashboard(self):
        """Setup dashboard with all contacts"""
        header = tk.Label(
            self.dashboard_frame,
            text="Conversations Dashboard",
            font=("Arial", 16, "bold"),
            bg="#075E54",
            fg="white",
            pady=10
        )
        header.pack(fill=tk.X)
        
        info = tk.Label(
            self.dashboard_frame,
            text="Click any number to load conversation",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#666666"
        )
        info.pack(pady=5)
        
        list_frame = tk.Frame(self.dashboard_frame, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.contact_canvas = tk.Canvas(list_frame, bg="white", highlightthickness=0)
        self.contact_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.contact_frame = tk.Frame(self.contact_canvas, bg="white")
        self.canvas_window = self.contact_canvas.create_window((0, 0), window=self.contact_frame, anchor="nw")
        
        self.contact_frame.bind(
            "<Configure>",
            lambda e: self.contact_canvas.configure(scrollregion=self.contact_canvas.bbox("all"))
        )
        
        scrollbar.config(command=self.contact_canvas.yview)
        self.contact_canvas.config(yscrollcommand=scrollbar.set)
        
        self.load_all_contacts()
    
    def load_all_contacts(self):
        """Load all contacts from database"""
        try:
            response = self.emulator.supabase.table("messages_test").select(
                "phone_number"
            ).order("timestamp", desc=True).execute()
            
            phones = {}
            if response.data:
                for msg in response.data:
                    phone = msg.get('phone_number')
                    if phone and phone.strip():
                        if phone not in phones:
                            phones[phone] = 0
                        phones[phone] += 1
            
            self.display_contacts(phones)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load contacts: {e}")
    
    def display_contacts(self, phones):
        """Display all contacts as clickable buttons"""
        for widget in self.contact_frame.winfo_children():
            widget.destroy()
        
        if not phones:
            label = tk.Label(
                self.contact_frame,
                text="No conversations found",
                font=("Arial", 11),
                bg="white",
                fg="#999999"
            )
            label.pack(pady=20)
            return
        
        sorted_contacts = sorted(phones.items(), key=lambda x: x[1], reverse=True)
        
        for phone, count in sorted_contacts:
            btn_frame = tk.Frame(self.contact_frame, bg="white", relief=tk.RAISED, bd=1)
            btn_frame.pack(fill=tk.X, padx=5, pady=5)
            
            btn_frame.bind("<Button-1>", lambda e, p=phone: self.load_contact(p))
            
            phone_label = tk.Label(
                btn_frame,
                text=phone,
                font=("Arial", 12, "bold"),
                bg="white",
                fg="#075E54"
            )
            phone_label.pack(anchor=tk.W, padx=10, pady=5)
            phone_label.bind("<Button-1>", lambda e, p=phone: self.load_contact(p))
            
            count_label = tk.Label(
                btn_frame,
                text=f"{count} messages",
                font=("Arial", 10),
                bg="white",
                fg="#999999"
            )
            count_label.pack(anchor=tk.W, padx=10, pady=2)
            count_label.bind("<Button-1>", lambda e, p=phone: self.load_contact(p))
    
    def load_contact(self, phone):
        """Load a contact conversation"""
        self.current_phone = phone
        self.current_name = "Customer"
        
        self.clear_chat()
        self.load_conversation_history()
        self.notebook.select(self.chat_frame)
        
        self.add_message(None, f"Loaded conversation from {phone}", "system")
        self.message_input.focus()
    
    def setup_chat(self):
        """Setup the GUI layout for chat"""
        header_frame = tk.Frame(self.chat_frame, bg="#075E54", height=60)
        header_frame.pack(side=tk.TOP, fill=tk.X, padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        header_label = tk.Label(
            header_frame,
            text="SMS Conductor Emulator",
            font=("Arial", 16, "bold"),
            bg="#075E54",
            fg="white"
        )
        header_label.pack(side=tk.LEFT, padx=15, pady=15)
        
        status_text = "Connected to Supabase" if self.connected else "Disconnected"
        status_color = "#00C853" if self.connected else "#D32F2F"
        status_label = tk.Label(
            header_frame,
            text=status_text,
            font=("Arial", 10),
            bg="#075E54",
            fg=status_color
        )
        status_label.pack(side=tk.RIGHT, padx=15, pady=15)
        
        phone_frame = tk.Frame(self.chat_frame, bg="white", height=70)
        phone_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        phone_frame.pack_propagate(False)
        
        tk.Label(phone_frame, text="Phone Number:", font=("Arial", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.phone_entry = tk.Entry(phone_frame, font=("Arial", 11), width=20)
        self.phone_entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.phone_entry.insert(0, "+16199773020")
        
        tk.Label(phone_frame, text="Name:", font=("Arial", 10, "bold"), bg="white").pack(side=tk.LEFT, padx=10, pady=10)
        
        self.name_entry = tk.Entry(phone_frame, font=("Arial", 11), width=20)
        self.name_entry.pack(side=tk.LEFT, padx=5, pady=10)
        self.name_entry.insert(0, "TestCustomer")
        
        connect_btn = tk.Button(
            phone_frame,
            text="Connect",
            command=self.connect_phone,
            bg="#075E54",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=5
        )
        connect_btn.pack(side=tk.LEFT, padx=10, pady=10)
        
        chat_frame = tk.Frame(self.chat_frame, bg="white")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(chat_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.canvas = tk.Canvas(chat_frame, bg="white", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.scrollable_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        scrollbar.config(command=self.canvas.yview)
        self.canvas.config(yscrollcommand=scrollbar.set)
        
        control_frame = tk.Frame(self.chat_frame, bg="#f0f0f0")
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            control_frame,
            text="Refresh Dashboard",
            command=self.refresh_dashboard,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="View Queued",
            command=self.view_queued,
            bg="#2196F3",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Process Queued",
            command=self.process_queued,
            bg="#00C853",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="View Stats",
            command=self.view_stats,
            bg="#FF9800",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_frame,
            text="Clear Chat",
            command=self.clear_chat,
            bg="#9C27B0",
            fg="white",
            font=("Arial", 9),
            padx=10,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        input_frame = tk.Frame(self.chat_frame, bg="#f0f0f0")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.message_input = tk.Entry(input_frame, font=("Arial", 11))
        self.message_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        self.message_input.bind("<Return>", lambda e: self.send_message())
        
        send_btn = tk.Button(
            input_frame,
            text="Send",
            command=self.send_message,
            bg="#075E54",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        )
        send_btn.pack(side=tk.RIGHT, padx=5)
    
    def refresh_dashboard(self):
        """Refresh the dashboard with latest data"""
        self.load_all_contacts()
        self.notebook.select(self.dashboard_frame)
        messagebox.showinfo("Dashboard", "Contacts refreshed!")
    
    def connect_phone(self):
        """Connect to a phone number"""
        phone = self.phone_entry.get().strip()
        name = self.name_entry.get().strip()
        
        if not phone:
            messagebox.showwarning("Input Error", "Please enter a phone number")
            return
        
        if not phone.startswith("+"):
            phone = "+" + phone
        
        self.current_phone = phone
        self.current_name = name or "Customer"
        
        self.clear_chat()
        self.load_conversation_history()
        self.add_message(None, f"Connected as {self.current_name} ({phone})", "system")
        self.message_input.focus()
    
    def load_conversation_history(self):
        """Load all existing messages for this phone number"""
        if not self.current_phone:
            return
        
        try:
            response = self.emulator.supabase.table("messages_test").select(
                "id, timestamp, direction, content, status"
            ).eq("phone_number", self.current_phone).order("timestamp").execute()
            
            messages = response.data if response.data else []
            
            if not messages:
                self.add_message(None, "No previous messages", "system")
                return
            
            self.add_message(None, f"--- Conversation History ({len(messages)} messages) ---", "system")
            
            self.label_to_msg_id = {}
            
            for msg in messages:
                msg_id = msg.get('id')
                direction = msg['direction']
                content = msg['content']
                status = msg['status']
                
                if direction == 'inbound':
                    label = self.add_message(self.current_name, f"{content}\n[{status}]", "outgoing")
                    if label and msg_id:
                        self.label_to_msg_id[id(label)] = msg_id
                else:
                    label = self.add_message(f"Chatbot [{status}]", content, "incoming")
                    if label and msg_id:
                        self.label_to_msg_id[id(label)] = msg_id
        
        except Exception as e:
            self.add_message(None, f"Error loading history: {e}", "system")
    
    def send_message(self):
        """Send a message as customer"""
        if not self.current_phone:
            messagebox.showwarning("Not Connected", "Please connect to a phone number first")
            return
        
        message_text = self.message_input.get().strip()
        if not message_text:
            return
        
        try:
            self.emulator.create_inbound_message(
                self.current_phone,
                message_text,
                self.current_name
            )
            self.add_message(self.current_name, message_text, "outgoing")
            self.message_input.delete(0, tk.END)
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
    
    def add_message(self, sender, text, msg_type="incoming"):
        """Add a message to the display and return the label widget"""
        msg_frame = tk.Frame(self.scrollable_frame, bg="white")
        msg_frame.pack(fill=tk.X, padx=10, pady=8)
        
        label = None
        
        if msg_type == "system":
            label = tk.Label(
                msg_frame,
                text=text,
                font=("Arial", 9, "italic"),
                bg="#E0E0E0",
                fg="#666666",
                wraplength=600,
                justify=tk.CENTER,
                padx=10,
                pady=5
            )
            label.pack(anchor=tk.CENTER)
        
        elif msg_type == "outgoing":
            header_frame = tk.Frame(msg_frame, bg="white")
            header_frame.pack(anchor=tk.E, padx=5)
            
            header_label = tk.Label(
                header_frame,
                text="YOU (sent):",
                font=("Arial", 8, "bold"),
                bg="white",
                fg="#003D33"
            )
            header_label.pack(anchor=tk.E)
            
            bubble_frame = tk.Frame(msg_frame, bg="#075E54")
            bubble_frame.pack(anchor=tk.E, padx=20, pady=3)
            
            label = tk.Label(
                bubble_frame,
                text=text,
                font=("Arial", 10),
                bg="#075E54",
                fg="white",
                wraplength=400,
                justify=tk.LEFT,
                padx=12,
                pady=8
            )
            label.pack()
            label.bind("<Button-3>", lambda e: self.show_context_menu(e, label))
            bubble_frame.bind("<Button-3>", lambda e: self.show_context_menu(e, label))
        
        else:
            header_frame = tk.Frame(msg_frame, bg="white")
            header_frame.pack(anchor=tk.W, padx=5)
            
            header_label = tk.Label(
                header_frame,
                text=f"CHATBOT ({sender if sender else 'incoming'}):",
                font=("Arial", 8, "bold"),
                bg="white",
                fg="#00796B"
            )
            header_label.pack(anchor=tk.W)
            
            bubble_frame = tk.Frame(msg_frame, bg="#E8F5E9")
            bubble_frame.pack(anchor=tk.W, padx=20, pady=3)
            
            label = tk.Label(
                bubble_frame,
                text=text,
                font=("Arial", 10),
                bg="#E8F5E9",
                fg="#1B5E20",
                wraplength=500,
                justify=tk.LEFT,
                padx=12,
                pady=8
            )
            label.pack()
            label.bind("<Button-3>", lambda e: self.show_context_menu(e, label))
            bubble_frame.bind("<Button-3>", lambda e: self.show_context_menu(e, label))
        
        self.canvas.yview_moveto(1)
        return label
    
    def show_context_menu(self, event, label):
        """Show right-click context menu for message editing"""
        menu = tk.Menu(self.root, tearoff=0)
        
        msg_text = label.cget("text")
        
        menu.add_command(
            label="Edit",
            command=lambda: self.edit_message_dialog(label, msg_text)
        )
        menu.add_command(
            label="Delete",
            command=lambda: self.delete_message_dialog(label)
        )
        menu.add_separator()
        menu.add_command(label="Close", command=menu.quit)
        
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.update_idletasks()
    
    def edit_message_dialog(self, label, current_text):
        """Show dialog to edit message"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Message")
        dialog.geometry("400x150")
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Edit message:", font=("Arial", 10)).pack(pady=5)
        
        text_input = tk.Text(dialog, height=3, width=40, font=("Arial", 10))
        text_input.pack(padx=10, pady=5)
        text_input.insert("1.0", current_text)
        
        def save_edit():
            new_text = text_input.get("1.0", tk.END).strip()
            if new_text:
                label.config(text=new_text)
                messagebox.showinfo("Success", "Message updated!")
                dialog.destroy()
        
        def cancel():
            dialog.destroy()
        
        button_frame = tk.Frame(dialog)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Save",
            command=save_edit,
            bg="#075E54",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=cancel,
            bg="#999999",
            fg="white",
            padx=15,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
    
    def delete_message_dialog(self, label):
        """Show confirmation dialog to delete message"""
        if messagebox.askyesno("Delete Message", "Are you sure you want to delete this message?\n\n(This will remove it from the database!)"):
            try:
                label_id = id(label)
                msg_id = self.label_to_msg_id.get(label_id)
                
                if msg_id:
                    success = self.emulator.delete_message(msg_id)
                    if success:
                        label.master.destroy()
                        messagebox.showinfo("Success", "Message deleted from database!")
                    else:
                        messagebox.showerror("Error", "Failed to delete message from database")
                else:
                    label.master.destroy()
                    messagebox.showinfo("Info", "Message removed from display (no database ID tracked)")
            
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete message: {e}")
    
    def view_queued(self):
        """View queued messages"""
        try:
            queued = self.emulator.get_queued_messages()
            self.add_message(None, f"QUEUED MESSAGES ({len(queued)})", "system")
            
            if not queued:
                self.add_message(None, "No queued messages", "system")
            else:
                for msg in queued:
                    self.add_message(
                        f"ID {msg['id']} - {msg['phone_number']}",
                        msg['content'],
                        "incoming"
                    )
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get queued messages: {e}")
    
    def process_queued(self):
        """Process all queued messages"""
        try:
            queued = self.emulator.get_queued_messages()
            
            if not queued:
                self.add_message(None, "No queued messages to process", "system")
                return
            
            self.add_message(None, f"PROCESSING {len(queued)} QUEUED MESSAGE(S)", "system")
            
            for msg in queued:
                self.emulator.mark_message_as_sent(msg['id'])
                self.add_message(
                    f"SENT ID {msg['id']}",
                    msg['content'],
                    "outgoing"
                )
            
            self.add_message(None, f"DONE: {len(queued)} messages sent", "system")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process queued: {e}")
    
    def view_stats(self):
        """View system statistics"""
        try:
            stats = self.emulator.get_stats()
            
            stats_text = (
                f"Total Messages: {stats.get('total_messages', 0)}\n"
                f"Inbound: {stats.get('inbound', 0)}\n"
                f"Outbound: {stats.get('outbound', 0)}\n"
                f"Unread: {stats.get('unread', 0)}\n"
                f"Queued: {stats.get('queued', 0)}\n"
                f"Sent: {stats.get('sent', 0)}"
            )
            
            self.add_message(None, f"SYSTEM STATISTICS:\n{stats_text}", "system")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get stats: {e}")
    
    def clear_chat(self):
        """Clear the chat display"""
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

def main():
    root = tk.Tk()
    gui = SMSEmulatorGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
