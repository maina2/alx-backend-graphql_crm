from django.db import models
from django.core.validators import RegexValidator
from decimal import Decimal
from django.utils import timezone

class Customer(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message="Phone number must be entered in the format: '+999999999' or '999-999-9999'. Up to 15 digits allowed."
            )
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

    def clean(self):
        if self.price <= 0:
            raise ValueError("Price must be positive")
        if self.stock < 0:
            raise ValueError("Stock cannot be negative")


class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    order_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} - {self.customer.name}"

    class Meta:
        ordering = ['-order_date']

    def calculate_total(self):
        """Calculate total amount based on associated products"""
        total = sum(product.price for product in self.products.all())
        self.total_amount = total
        return total

    def save(self, *args, **kwargs):
        # Save first to get an ID
        super().save(*args, **kwargs)
        # Then calculate total if products exist
        if self.products.exists():
            self.calculate_total()
            super().save(update_fields=['total_amount'])