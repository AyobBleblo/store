from django.db.models import Avg, Sum, Max, Count
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.viewsets import ModelViewSet , CreateDeleteViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView
from rest_framework.filters import SearchFilter , OrderingFilter
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from store_.filter import ProductFilter
from .permations import IsAdminOrReadOnly , ViewCustomerHistoryPermission
from .serializers import CreateOrderSerializer, OrderItemSerializer, OrderSerializer, ProductSerializerWithExtraDetails, CollectionSerializer, CustomerSerializer, \
    StoreProductsSerializer , ReviewSerializer , StoreSumAvgMacPriceSerializer,\
    StoreWithCollectionsAndProductsSerializer ,StoreSerializer,CartSerializer,CartItemSerializer ,AddCartItemSerializer
from .models import Product, Collection, Customer, Order, OrderItem, Store , Review,Cart,CartItem
from .pagination import StandardResultsSetPagination


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.select_related(
        'collection__store', 'store__owner').all()
    serializer_class = ProductSerializerWithExtraDetails
    filter_backends = [DjangoFilterBackend , SearchFilter , OrderingFilter]
    pagination_class = StandardResultsSetPagination
    permission_classes = [IsAdminOrReadOnly]
    filterset_class = ProductFilter
    search_fields = ['title' , 'description']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self,request, *args, **kwargs):

        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({"error": "Product has order items"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)

class CollectionViewSet(ModelViewSet):

    queryset = Collection.objects.prefetch_related(
        Prefetch('product_set')).select_related('store').\
        annotate(products_count=Count('product'))

    serializer_class = CollectionSerializer

    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self,request, *args, **kwargs):
        collection = get_object_or_404(Collection, pk=kwargs['pk'])
        if collection.product_set.count() > 0:
            return Response({"error": "Collection has products"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class CustomerOrderList(ModelViewSet):
    queryset = Customer.objects.filter(order__isnull=False).distinct().prefetch_related(
        'order_set')
    serializer_class = CustomerSerializer
    http_method_names = ['get']

class CustomerStoreList(APIView):
    def get(self, request, id):
        stores = Store.objects.select_related('owner').filter(owner_id=id)
        serializer = StoreSerializer(stores, many=True)
        return Response(serializer.data)


class StoreProductList(APIView):
    def get(self, request, store_id):
        store = get_object_or_404(
            Store.objects.select_related(
                'owner'
            ).annotate(
                products_number=Count('product')
            ),
            pk=store_id
        )
        serializer = StoreProductsSerializer(store)
        return Response(serializer.data)


class StoreWithCollection(APIView):
    def get(self, request, id):
        store = get_object_or_404(
            Store.objects.annotate(
                collections_count=Count(
                    'collection',
                    distinct=True
                ),
                products_count=Count(
                    'product',
                    distinct=True
                )
            ),
            pk=id
        )
        serializer = StoreWithCollectionsAndProductsSerializer(store)
        return Response(serializer.data)


class StoreSumAvgMaxPrice(APIView):
    def get(self, request, pk):
        store = get_object_or_404(
            Store.objects.annotate(
                total_inventory=Sum('product__inventory'),
                average_price=Avg('product__unit_price'),
                max_price=Max('product__unit_price')
            ),
            pk=pk
        )
        serializer = StoreSumAvgMacPriceSerializer(store)
        return Response(serializer.data)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id' : self.kwargs['product_pk']}

class CartViewSet(CreateDeleteViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    queryset = CartItem.objects.select_related('product').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}
    

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.select_related('user').all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        customer = get_object_or_404(Customer, pk=pk)
        serializer = CustomerSerializer(customer)
        return Response(serializer.data)

        

    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer , created = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = self.get_serializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.select_related('customer__user').prefetch_related('items__product').all()
        
        customer_id,created = Customer.objects.only('id').get_or_create(user_id=self.request.user.id)
        return Order.objects.filter(customer_id=customer_id)
    

    
