from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Order, OrderItem, Product, Collection, Store, Customer, Review , Cart , CartItem


class ProductSerializerWithExtraDetails(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'inventory', 'unit_price',
                  'price_with_tax', 'collection', 'store']

    price_with_tax = serializers.SerializerMethodField(
        method_name='get_price_with_tax')
    collection = serializers.HyperlinkedRelatedField(
        queryset=Collection.objects.all(),
        view_name='collection-detail',
    )
    store = serializers.HyperlinkedRelatedField(
        queryset=Store.objects.all(),
        view_name='store-sum-avg-max-price',
    )

    def get_price_with_tax(self, product: Product):
        return product.unit_price * Decimal('1.1')


class CollectionSerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField(
        method_name='get_products_count')
    store = serializers.StringRelatedField()

    class Meta:
        model = Collection
        fields = ['id', 'title', 'store', 'products_count']

    def get_products_count(self, collection: Collection):
        return collection.product_set.count()


class CustomerSerializer(serializers.ModelSerializer):

    orders_count = serializers.SerializerMethodField(
        method_name='get_orders_count'
    )
    orders = serializers.StringRelatedField(
        many=True,
        source='order_set'
    )

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name', 'email',
                  'phone', 'created_at', 'membership', 'orders', 'orders_count']
    def get_orders_count(self, customer: Customer):
        return customer.order_set.count()


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = ['id', 'name', 'owner', 'created_at']


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
    def get_collections_count(self, store: Store):
        return store.collection_set.count()

    def get_products_count(self, store: Store):
        return store.product_set.count()


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


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'rating', 'description', 'created_at']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(**validated_data, product_id=product_id)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    total_product_price = serializers.SerializerMethodField(method_name='get_total_product_price')

    product = SimpleProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity' , 'total_product_price']

    def get_total_product_price(self, cartitem: CartItem):
        return cartitem.product.unit_price * cartitem.quantity

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True , read_only=True)
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    class Meta:
        model = Cart
        fields = ['id' , 'items' , 'total_price']

    def get_total_price(self, cart: Cart):
        return sum(item.product.unit_price * item.quantity for item in cart.items.all())


class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product with the given id was found.')
        return value

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id'] = self.validated_data['product_id']
        quantity = self.validated_data['quantity'] = self.validated_data['quantity']
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class CustomerSerializer(serializers.ModelSerializer):

    user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id','user_id','phone', 'membership' , 'birth_date' ]
    def get_orders_count(self, customer: Customer):
        return customer.order_set.count()
    
class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.select_related('customer__user').all()
    )

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True , source='items')
    customer = serializers.PrimaryKeyRelatedField(
        queryset=Customer.objects.select_related('user').all()
    )

    class Meta:
        model = Order
        fields = ['id', 'customer', 'placed_at', 'payment_status' , 'order_items']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()


    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer, created = Customer.objects.get_or_create(user_id=self.context['user_id'])
            order = Order.objects.create(customer=customer)
            cart_items = CartItem.objects.\
                    select_related('product').\
                    filter(cart_id=cart_id)
            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.unit_price
                ) for item in cart_items
            ]
            OrderItem.objects.bulk_create(order_items)
            CartItem.objects.filter(pk=cart_id).delete()





    

