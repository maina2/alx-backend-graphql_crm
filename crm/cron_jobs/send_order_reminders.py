#!/usr/bin/env python3
"""
Send order reminders for pending orders from the last 7 days.
"""
import os
import sys
from datetime import datetime, timedelta
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

def setup_gql_client():
    """Set up and return a GraphQL client."""
    transport = RequestsHTTPTransport(
        url="http://localhost:8000/graphql",
        use_json=True,
    )
    return Client(transport=transport, fetch_schema_from_transport=True)

def get_recent_orders(client):
    """Fetch recent pending orders from the GraphQL API."""
    # Calculate date 7 days ago
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    
    query = gql("""
    query {
        orders(where: { 
            status: "pending",
            orderDate_gte: "%s"
        }) {
            id
            customer {
                email
            }
            orderDate
        }
    }
    """ % seven_days_ago)
    
    try:
        result = client.execute(query)
        return result.get('orders', [])
    except Exception as e:
        print(f"Error fetching orders: {e}", file=sys.stderr)
        return []

def log_reminders(orders):
    """Log order reminders to file."""
    log_file = "/tmp/order_reminders_log.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n=== Order Reminders - {timestamp} ===\n")
        if not orders:
            f.write("No pending orders found.\n")
            return
            
        for order in orders:
            order_id = order.get('id', 'N/A')
            customer_email = order.get('customer', {}).get('email', 'N/A')
            order_date = order.get('orderDate', 'N/A')
            f.write(f"Order ID: {order_id}, Customer Email: {customer_email}, Order Date: {order_date}\n")

def main():
    """Main function to process order reminders."""
    try:
        client = setup_gql_client()
        orders = get_recent_orders(client)
        log_reminders(orders)
        print("Order reminders processed!")
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())