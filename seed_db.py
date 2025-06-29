#!/usr/bin/env python
"""
Database seeding script for the CRM system.
Run this script to populate the database with sample data.

Usage:
    python seed_db.py
"""

import os
import sys
import django
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_backend_graphql_crm.settings')
django.setup()

from crm.models import Customer, Product, Order


def seed_customers():
    """Create sample customers"""
    customers_data = [
        {'name': 'Alice Johnson', 'email': 'alice@example.com', 'phone': '+1234567890'},
        {'name': 'Bob Smith', 'email': 'bob@example.com', 'phone': '123-456-7890'},
        {'name': 'Carol Williams', 'email': 'carol@example.com', 'phone': '+1987654321'},
        {'name': 'David Brown', 'email': 'david@example.com', 'phone': None},
        {'name': 'Eve Davis', 'email': 'eve@example.com', 'phone': '555-123-4567'},
        {'name': 'Frank Miller', 'email': 'frank@example.com', 'phone': '+1555987654'},
        {'name': 'Grace Wilson', 'email': 'grace@example.com', 'phone': None},
        {'name': 'Henry Taylor', 'email': 'henry@example.com', 'phone': '777-888-9999'},
    ]
    
    customers = []
    for data in customers_data:
        customer, created = Customer.objects.get_or_create(
            email=data['email'],
            defaults=data
        )
        if created:
            customers.append(customer)
            print(f"Created customer: {customer.name}")
        else:
            print(f"Customer already exists: {customer.name}")
    
    return Customer.objects.all()


def seed_products():
    """Create sample products"""
    products_data = [
        {'name': 'Laptop', 'price': Decimal('999.99'), 'stock': 15},
        {'name': 'Desktop Computer', 'price': Decimal('799.99'), 'stock': 8},
        {'name': 'Smartphone', 'price': Decimal('599.99'), 'stock': 25},
        {'name': 'Tablet', 'price': Decimal('399.99'), 'stock': 12},
        {'name': 'Headphones', 'price': Decimal('149.99'), 'stock': 30},
        {'name': 'Keyboard', 'price': Decimal('79.99'), 'stock': 20},
        {'name': 'Mouse', 'price': Decimal('49.99'), 'stock': 35},
        {'name': 'Monitor', 'price': Decimal('299.99'), 'stock': 10},
        {'name': 'Webcam', 'price': Decimal('89.99'), 'stock': 18},
        {'name': 'Speaker', 'price': Decimal('199.99'), 'stock': 5},
    ]
    
    products = []
    for data in products_data:
        product, created = Product.objects.get_or_create(
            name=data['name'],
            defaults=data
        )
        if created:
            products.append(product)
            print(f"Created product: {product.name}")
        else:
            print(f"Product already exists: {product.name}")
    
    return Product.objects.all()


def seed_orders():
    """Create sample orders"""
    customers = list(Customer.objects.all())
    products = list(Product.objects.all())
    
    if not customers or not products:
        print("No customers or products found. Please seed customers and products first.")
        return
    
    # Create 15 sample orders
    orders_created = 0
    for i in range(15):
        # Random customer
        customer = random.choice(customers)
        
        # Random 1-4 products
        order_products = random.sample(products, random.randint(1, 4))
        
        # Random order date (last 30 days)
        order_date = timezone.now() - timedelta(days=random.randint(0, 30))
        
        # Create order
        order = Order.objects.create(
            customer=customer,
            order_date=order_date
        )
        
        # Add products and calculate total
        order.products.set(order_products)
        total_amount = sum(product.price for product in order_products)
        order.total_amount = total_amount
        order.save()
        
        orders_created += 1
        print(f"Created order {order.id} for {customer.name} - Total: ${total_amount}")
    
    print(f"Created {orders_created} orders")
    return Order.objects.all()


def main():
    """Main seeding function"""
    print("Starting database seeding...")
    
    # Clear existing data (optional)
    # Uncomment the lines below if you want to start fresh
    # Order.objects.all().delete()
    # Customer.objects.all().delete()
    # Product.objects.all().delete()
    # print("Cleared existing data")
    
    # Seed data
    print("\n--- Seeding Customers ---")
    customers = seed_customers()
    
    print("\n--- Seeding Products ---")
    products = seed_products()
    
    print("\n--- Seeding Orders ---")
    orders = seed_orders()
    
    print(f"\n--- Seeding Complete ---")
    print(f"Total Customers: {Customer.objects.count()}")
    print(f"Total Products: {Product.objects.count()}")
    print(f"Total Orders: {Order.objects.count()}")
    print("\nYou can now test the GraphQL API at http://localhost:8000/graphql/")


if __name__ == '__main__':
    main()