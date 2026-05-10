from decimal import Decimal
from rest_framework import serializers
from .models import Product ,Collection , Store , Customer

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'inventory','unit_price','price_with_tax' , 'collection','store']

    price_with_tax = serializers.SerializerMethodField(method_name='get_price_with_tax')
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection_details',
    )
    store= serializers.HyperlinkedRelatedField(
        queryset=Store.objects.all(),
        view_name='store-sum-avg-max-price',
    )

    def get_price_with_tax(self, product: Product):
        return product.unit_price * Decimal('1.1')





class CollectionSerializer(serializers.ModelSerializer):
    products = ProductSerializer(
    many=True,
    source='product_set'
    )

    title = serializers.CharField()
    store = serializers.StringRelatedField()

    class Meta:
        model = Collection
        fields = ['title' , 'store' , 'products']

class CustomerSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField()
    created_at = serializers.DateTimeField()
    membership = serializers.CharField()

    orders = serializers.StringRelatedField(
    many=True,
    source='order_set'
)
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name','email','phone','created_at','membership' , 'orders']

class StoreSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    owner = serializers.StringRelatedField()
    created_at = serializers.DateTimeField()
    class Meta:
        model = Store
        fields = ['id', 'name', 'owner','created_at']

class StoreProductsSerializer(serializers.ModelSerializer):
    owner_name = serializers.StringRelatedField(
        source='owner'
    )
    products_number = serializers.IntegerField()

    class Meta:
        model = Store
        fields = [
            'id',
            'name',
            'owner_name',
            'products_number'
        ]

class StoreWithCollectionsAndProductsSerializer(serializers.ModelSerializer):

    collections_count = serializers.IntegerField()

    products_count = serializers.IntegerField()

    class Meta:
        model = Store
        fields = [
            'name',
            'products_count',
            'collections_count'
        ]
class StoreSumAvgMacPriceSerializer(serializers.ModelSerializer):

    total_inventory = serializers.IntegerField()
    average_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    max_price = serializers.DecimalField(max_digits=10, decimal_places=2)


    class Meta:
        model = Store
        fields = [
            'name',
            'total_inventory',
            'average_price',
            'max_price'
        ]