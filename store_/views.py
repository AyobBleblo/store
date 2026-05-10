from rest_framework import status
from store_.serializers import StoreSumAvgMacPriceSerializer
from django.db.models import Avg, Sum, Max, Count
from store_.serializers import StoreWithCollectionsAndProductsSerializer
from store_.serializers import StoreSerializer
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import ProductSerializer, CollectionSerializer, CustomerSerializer, \
    StoreProductsSerializer
from .models import Product, Collection, Customer, Order, OrderItem, Store


# Create your views here.
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.select_related(
            'collection__store',
            'store__owner'
        ).all()
        serializer = ProductSerializer(
            products, many=True, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = ProductSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET' ,'PUT', 'DELETE'])
def product_details(request, pk):
    
    product = get_object_or_404(Product, pk=pk)
    if request.method == "GET":
        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = ProductSerializer(product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == "DELETE":
        if product.orderitem_set.count() > 0:
            return Response({"error": "Product has order items"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

        
    


@api_view(['GET'])
def collection_list(request):
    collections = Collection.objects.\
        select_related(
            'store'
        ).prefetch_related(
            Prefetch(
                'product_set',
                queryset=Product.objects.select_related(
                    'store',
                    'collection__store'
                )
            )
        )
    serializer = CollectionSerializer(collections, many=True , context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def collection_details(request, pk):

    collection = get_object_or_404(
        Collection.objects.prefetch_related(
            Prefetch(
                'product_set',
                queryset=Product.objects.all()
            )
        ).select_related('store'),
        pk=pk
    )

    serializer = CollectionSerializer(collection, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
def customer_orders(request):

    customers = Customer.objects.filter(order__isnull=False).prefetch_related(
        'order_set'
    ).distinct()

    serializer = CustomerSerializer(customers, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def customer_stores(request, id):
    stores = Store.objects.select_related('owner').filter(owner_id=id)
    serializer = StoreSerializer(stores, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def store_products(request, store_id):
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


@api_view(['GET'])
def store_with_collection(request, id):
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


@api_view(['GET'])
def store_sum_avg_max_price(request, pk):
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
