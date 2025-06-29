
import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django.filter import DjangoFilterConnectionField
from django.core.exceptions import ValidationError
from django.db import transaction
from decimal import Decimal
import re
from .models import Customer, Product, Order
from .filters import CustomerFilter, ProductFilter, OrderFilter


# GraphQL Types
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = "__all__"


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = "__all__"


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = "__all__"


# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutation Response Types
class CustomerMutationResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)


class BulkCustomerMutationResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


class ProductMutationResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    message = graphene.String()
    errors = graphene.List(graphene.String)


class OrderMutationResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    message = graphene.String()
    errors = graphene.List(graphene.String)


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CustomerMutationResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
        
        # Validate phone format
        if input.phone:
            phone_pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
            if not re.match(phone_pattern, input.phone):
                errors.append("Invalid phone format")
        
        if errors:
            return CustomerMutationResponse(errors=errors)
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            return CustomerMutationResponse(
                customer=customer,
                message="Customer created successfully"
            )
        except Exception as e:
            return CustomerMutationResponse(errors=[str(e)])


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCustomerMutationResponse

    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for i, customer_data in enumerate(input):
                try:
                    # Check for duplicate email
                    if Customer.objects.filter(email=customer_data.email).exists():
                        errors.append(f"Customer {i+1}: Email already exists")
                        continue
                    
                    # Validate phone format
                    if customer_data.phone:
                        phone_pattern = r'^\+?1?\d{9,15}$|^\d{3}-\d{3}-\d{4}$'
                        if not re.match(phone_pattern, customer_data.phone):
                            errors.append(f"Customer {i+1}: Invalid phone format")
                            continue
                    
                    customer = Customer.objects.create(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customers.append(customer)
                    
                except Exception as e:
                    errors.append(f"Customer {i+1}: {str(e)}")
        
        return BulkCustomerMutationResponse(
            customers=customers,
            errors=errors
        )


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = ProductMutationResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate price
        if input.price <= 0:
            errors.append("Price must be positive")
        
        # Validate stock
        stock = input.stock if input.stock is not None else 0
        if stock < 0:
            errors.append("Stock cannot be negative")
        
        if errors:
            return ProductMutationResponse(errors=errors)
        
        try:
            product = Product.objects.create(
                name=input.name,
                price=input.price,
                stock=stock
            )
            return ProductMutationResponse(
                product=product,
                message="Product created successfully"
            )
        except Exception as e:
            return ProductMutationResponse(errors=[str(e)])


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = OrderMutationResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate customer exists
        try:
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Customer not found")
            return OrderMutationResponse(errors=errors)
        
        # Validate products exist
        if not input.product_ids:
            errors.append("At least one product must be selected")
            return OrderMutationResponse(errors=errors)
        
        products = Product.objects.filter(id__in=input.product_ids)
        if len(products) != len(input.product_ids):
            errors.append("One or more products not found")
            return OrderMutationResponse(errors=errors)
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    order_date=input.order_date
                )
                
                # Add products
                order.products.set(products)
                
                # Calculate total amount
                total_amount = sum(product.price for product in products)
                order.total_amount = total_amount
                order.save()
                
                return OrderMutationResponse(
                    order=order,
                    message="Order created successfully"
                )
        except Exception as e:
            return OrderMutationResponse(errors=[str(e)])


# Queries
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    # Basic queries
    all_customers = DjangoFilterConnectionField(CustomerType, filterset_class=CustomerFilter)
    all_products = DjangoFilterConnectionField(ProductType, filterset_class=ProductFilter)
    all_orders = DjangoFilterConnectionField(OrderType, filterset_class=OrderFilter)
    
    # Single object queries
    customer = graphene.Field(CustomerType, id=graphene.ID())
    product = graphene.Field(ProductType, id=graphene.ID())
    order = graphene.Field(OrderType, id=graphene.ID())

    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(pk=id)
        except Customer.DoesNotExist:
            return None

    def resolve_product(self, info, id):
        try:
            return Product.objects.get(pk=id)
        except Product.DoesNotExist:
            return None

    def resolve_order(self, info, id):
        try:
            return Order.objects.get(pk=id)
        except Order.DoesNotExist:
            return None


# Mutations
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
