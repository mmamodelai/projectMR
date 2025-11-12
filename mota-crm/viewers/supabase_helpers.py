#!/usr/bin/env python3
"""
Supabase helper functions for fetching all data
"""

def fetch_all_records(supabase_client, table_name, order_by=None, order_desc=True):
    """
    Fetch all records from a Supabase table using pagination
    
    Args:
        supabase_client: Supabase client instance
        table_name: Name of the table
        order_by: Column to order by (optional)
        order_desc: Order descending (default True)
    
    Returns:
        List of all records
    """
    all_records = []
    batch_size = 1000
    offset = 0
    
    while True:
        # Build query
        query = supabase_client.table(table_name).select('*')
        
        if order_by:
            query = query.order(order_by, desc=order_desc)
        
        # Fetch batch
        response = query.range(offset, offset + batch_size - 1).execute()
        
        if not response.data:
            break
        
        all_records.extend(response.data)
        
        # If we got less than batch_size, we're done
        if len(response.data) < batch_size:
            break
        
        offset += batch_size
    
    return all_records

