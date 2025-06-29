# seed_db.py
import os
import django
import random
from datetime import datetime

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alx_backend_graphql_crm.settings")
django.setup()

from crm.models import Customer, Product, Order

# Seed customers
customers = [
    {"name": "Alice", "email": "alice@example.com", "phone": "+1234567890"},
    {"name": "Bob", "email": "bob@example.com", "phone": "123-456-7890"},
    {"name": "Carol", "email": "carol@example.com", "phone": None},
]

for c in customers:
    Customer.objects.get_or_create(email=c["email"], defaults=c)

# Seed products
products = [
    {"name": "Laptop", "price": 999.99, "stock": 10},
    {"name": "Mouse", "price": 25.50, "stock": 50},
    {"name": "Keyboard", "price": 45.00, "stock": 30},
]

for p in products:
    Product.objects.get_or_create(name=p["name"], defaults=p)

# Create sample order
all_customers = Customer.objects.all()
all_products = list(Product.objects.all())

if all_customers and all_products:
    customer = random.choice(all_customers)
    selected_products = random.sample(all_products, 2)
    total = sum(p.price for p in selected_products)
    order = Order.objects.create(customer=customer, total_amount=total)
    order.products.set(selected_products)

print("Database seeded successfully.")