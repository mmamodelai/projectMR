#!/usr/bin/env python3
"""
Get Customer's Favorite Budtender
Analyzes transaction history to find the budtender a customer interacts with most
Part of: MoTa CRM System
"""

from supabase import create_client, Client
import sys

# Supabase credentials (matching CRM database)
SUPABASE_URL = "https://kiwmwoqrguyrcpjytgte.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imtpd213b3FyZ3V5cmNwanl0Z3RlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk4NDUwNTEsImV4cCI6MjA3NTQyMTA1MX0.3YhobdFv0ZV6PzExcr88l-zNN3vZeEsM_Du9kVEmdV0"

def get_customer_favorite_budtender(phone_number: str) -> dict:
    """
    Get the budtender a customer interacts with most frequently.
    
    Args:
        phone_number: Customer's phone number (E.164 format, e.g., +16199773020)
        
    Returns:
        dict with budtender info or None if not found
    """
    try:
        # Initialize Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # First, find customer by phone
        customer_result = supabase.table("customers").select("member_id, name").eq("phone", phone_number).execute()
        
        if not customer_result.data or len(customer_result.data) == 0:
            return {
                "success": False,
                "error": "Customer not found",
                "phone_number": phone_number
            }
        
        customer = customer_result.data[0]
        member_id = customer["member_id"]
        customer_name = customer["name"]
        
        # Get all transactions for this customer with staff info
        transactions_result = supabase.table("transactions").select(
            "staff_name, total_amount"
        ).eq("customer_id", member_id).execute()
        
        if not transactions_result.data or len(transactions_result.data) == 0:
            return {
                "success": False,
                "error": "No transaction history found",
                "customer_name": customer_name,
                "phone_number": phone_number
            }
        
        # Count interactions with each budtender
        budtender_stats = {}
        for txn in transactions_result.data:
            staff_name = txn.get("staff_name")
            if not staff_name or staff_name == "Unknown" or staff_name == "":
                continue
            
            if staff_name not in budtender_stats:
                budtender_stats[staff_name] = {
                    "name": staff_name,
                    "transaction_count": 0,
                    "total_sales": 0.0
                }
            
            budtender_stats[staff_name]["transaction_count"] += 1
            budtender_stats[staff_name]["total_sales"] += float(txn.get("total_amount", 0) or 0)
        
        if not budtender_stats:
            return {
                "success": False,
                "error": "No budtender information found in transaction history",
                "customer_name": customer_name,
                "phone_number": phone_number
            }
        
        # Find the budtender with the most interactions
        favorite_budtender = max(budtender_stats.values(), key=lambda x: x["transaction_count"])
        
        # Calculate percentage of transactions
        total_transactions = len(transactions_result.data)
        percentage = (favorite_budtender["transaction_count"] / total_transactions) * 100
        
        return {
            "success": True,
            "customer_name": customer_name,
            "phone_number": phone_number,
            "member_id": member_id,
            "total_transactions": total_transactions,
            "favorite_budtender": {
                "name": favorite_budtender["name"],
                "transaction_count": favorite_budtender["transaction_count"],
                "percentage": round(percentage, 1),
                "total_sales": round(favorite_budtender["total_sales"], 2)
            },
            "all_budtenders": sorted(budtender_stats.values(), key=lambda x: x["transaction_count"], reverse=True)
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "phone_number": phone_number
        }


def main():
    """Main function for CLI usage"""
    if len(sys.argv) < 2:
        print("Usage: python get_customer_budtender.py <phone_number>")
        print("Example: python get_customer_budtender.py +16199773020")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    result = get_customer_favorite_budtender(phone_number)
    
    if result["success"]:
        print(f"\nSUCCESS - Customer: {result['customer_name']}")
        print(f"Phone: {result['phone_number']}")
        print(f"Total Transactions: {result['total_transactions']}")
        print(f"\nFavorite Budtender:")
        fav = result["favorite_budtender"]
        print(f"   Name: {fav['name']}")
        print(f"   Transactions: {fav['transaction_count']} ({fav['percentage']}%)")
        print(f"   Total Sales: ${fav['total_sales']}")
        
        if len(result["all_budtenders"]) > 1:
            print(f"\nAll Budtenders:")
            for i, bt in enumerate(result["all_budtenders"][:5], 1):
                pct = (bt["transaction_count"] / result["total_transactions"]) * 100
                print(f"   {i}. {bt['name']} - {bt['transaction_count']} txns ({pct:.1f}%)")
    else:
        print(f"\nERROR: {result['error']}")
        print(f"Phone: {result['phone_number']}")


if __name__ == "__main__":
    main()

