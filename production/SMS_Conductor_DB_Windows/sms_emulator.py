#!/usr/bin/env python3
"""
SMS Conductor Emulator - Supabase Edition
Tests chatbot workflows by interacting with real Supabase database
"""

import os
import json
from datetime import datetime
from supabase import create_client, Client
import hashlib
import time

class SMSEmulatorSupabase:
    """Supabase-connected SMS emulator for testing chatbot workflows"""
    
    def __init__(self):
        """Initialize Supabase connection"""
        config_path = os.path.join(os.path.dirname(__file__), "config.json")
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.supabase_url = config['database']['supabase_url']
        self.supabase_key = config['database']['supabase_key']
        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        self.table_name = "messages_test"
        
        print(f"[INIT] Connected to Supabase")
        print(f"[INIT] Using table: {self.table_name}")
    
    def create_inbound_message(self, phone_number, content, sender_name="Customer"):
        """Create an inbound message (from customer)"""
        try:
            response = self.supabase.table(self.table_name).insert({
                "phone_number": phone_number,
                "content": content,
                "direction": "inbound",
                "status": "unread",
                "timestamp": datetime.now().isoformat()
            }).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to create inbound message: {e}")
            return False
    
    def get_queued_messages(self):
        """Get all queued messages"""
        try:
            response = self.supabase.table(self.table_name).select("*").eq("status", "queued").execute()
            return response.data if response.data else []
        except Exception as e:
            print(f"[ERROR] Failed to get queued messages: {e}")
            return []
    
    def mark_message_as_sent(self, message_id):
        """Mark a queued message as sent"""
        try:
            self.supabase.table(self.table_name).update(
                {"status": "sent"}
            ).eq("id", message_id).execute()
        except Exception as e:
            print(f"[ERROR] Failed to mark message as sent: {e}")
    
    def delete_message(self, message_id):
        """Delete a message from the database"""
        try:
            response = self.supabase.table(self.table_name).delete().eq("id", message_id).execute()
            return True
        except Exception as e:
            print(f"[ERROR] Failed to delete message: {e}")
            return False
    
    def get_conversation_history(self, phone_number, limit=20):
        """Get conversation history with a specific number"""
        try:
            response = self.supabase.table(self.table_name).select(
                "id, timestamp, direction, content, status"
            ).eq("phone_number", phone_number).order(
                "timestamp", desc=True
            ).limit(limit).execute()
            
            messages = response.data if response.data else []
            return list(reversed(messages))  # Return in chronological order
        
        except Exception as e:
            print(f"[ERROR] Failed to get history: {e}")
            return []
    
    def get_stats(self):
        """Get system statistics"""
        try:
            response = self.supabase.table(self.table_name).select(
                "id, direction, status"
            ).execute()
            
            messages = response.data if response.data else []
            
            total = len(messages)
            inbound = sum(1 for m in messages if m['direction'] == 'inbound')
            outbound = sum(1 for m in messages if m['direction'] == 'outbound')
            unread = sum(1 for m in messages if m['status'] == 'unread')
            queued = sum(1 for m in messages if m['status'] == 'queued')
            sent = sum(1 for m in messages if m['status'] == 'sent')
            
            return {
                'total_messages': total,
                'inbound': inbound,
                'outbound': outbound,
                'unread': unread,
                'queued': queued,
                'sent': sent
            }
        except Exception as e:
            print(f"[ERROR] Failed to get stats: {e}")
            return {}

def main():
    """Main function for testing"""
    emulator = SMSEmulatorSupabase()
    
    while True:
        print("\n=== SMS Conductor Emulator ===")
        print("1. Create inbound message")
        print("2. View queued messages")
        print("3. Process queued messages")
        print("4. View conversation history")
        print("5. View statistics")
        print("6. Exit")
        
        choice = input("\nChoice (1-6): ").strip()
        
        if choice == "1":
            phone = input("Phone number: ").strip()
            content = input("Message: ").strip()
            if phone and content:
                emulator.create_inbound_message(phone, content)
        
        elif choice == "2":
            queued = emulator.get_queued_messages()
            print(f"\nQueued messages ({len(queued)}):")
            for msg in queued:
                print(f"ID {msg['id']}: {msg['content']}")
        
        elif choice == "3":
            queued = emulator.get_queued_messages()
            if queued:
                for msg in queued:
                    emulator.mark_message_as_sent(msg['id'])
                print(f"Processed {len(queued)} messages")
            else:
                print("No queued messages")
        
        elif choice == "4":
            phone = input("Phone number: ").strip()
            if phone:
                history = emulator.get_conversation_history(phone)
                print(f"\nHistory ({len(history)} messages):")
                for msg in history:
                    print(f"{msg['direction']}: {msg['content']}")
        
        elif choice == "5":
            stats = emulator.get_stats()
            print(f"\nStatistics:")
            for key, value in stats.items():
                print(f"{key}: {value}")
        
        elif choice == "6":
            break
        
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
