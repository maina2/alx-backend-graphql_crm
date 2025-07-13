import graphene
from graphene_django import DjangoObjectType
from django.db.models import F
from .models import Product

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = ("id", "name", "stock", "price")

class UpdateLowStockProducts(graphene.Mutation):
    class Arguments:
        restockAmount = graphene.Int(required=True)
    
    success = graphene.Boolean()
    message = graphene.String()
    updated_products = graphene.List(ProductType)

    def mutate(self, info, restockAmount):
        # Trouver les produits avec un stock inférieur à 10
        products_to_update = Product.objects.filter(stock__lt=10)
        
        if not products_to_update.exists():
            return UpdateLowStockProducts(
                success=True,
                message="No products with low stock found.",
                updated_products=[]
            )
        
        # Mettre à jour le stock des produits
        updated_products = []
        for product in products_to_update:
            # Utiliser F() pour éviter les conditions de course
            Product.objects.filter(pk=product.pk).update(stock=F('stock') + restockAmount)
            # Rafraîchir l'objet pour obtenir les valeurs mises à jour
            product.refresh_from_db()
            updated_products.append(product)
        
        return UpdateLowStockProducts(
            success=True,
            message=f"Successfully restocked {len(updated_products)} products.",
            updated_products=updated_products
        )

class Mutation(graphene.ObjectType):
    update_low_stock_products = UpdateLowStockProducts.Field()

class Query(graphene.ObjectType):
    hello = graphene.String()
    
    def resolve_hello(self, info):
        return "Hello!"

schema = graphene.Schema(query=Query, mutation=Mutation)