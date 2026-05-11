from rest_framework.generics import ListCreateAPIView
from .venv.Lib.site-packages.rest_framework.generics import ListCreateAPIView
from rest_framework import status
from store_.serializers import StoreSumAvgMacPriceSerializer
from django.db.models import Avg, Sum, Max, Count
from store_.serializers import StoreWithCollectionsAndProductsSerializer
from store_.serializers import StoreSerializer
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import ProductSerializerWithExtraDetails, CollectionSerializer, CustomerSerializer, \
    StoreProductsSerializer
from .models import Product, Collection, Customer, Order, OrderItem, Store


class ProductList(ListCreateAPIView):  

    def get(self, request):
        products = Product.objects.select_related(
            'collection__store',
            'store__owner'
        ).all()
        serializer = ProductSerializerWithExtraDetails(
            products, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializerWithExtraDetails(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ProductDetail(APIView):
    def get(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializerWithExtraDetails(
            product, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        serializer = ProductSerializerWithExtraDetails(
            product, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.orderitem_set.count() > 0:
            return Response({"error": "Product has order items"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CollectionList(APIView):
    def get(self, request):
        collections = Collection.objects.select_related('store').\
            annotate(
            products_count=Count('product'))
        
        serializer = CollectionSerializer(collections, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):

        serializer = CollectionSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CollectionDetail(APIView):
    def get(self, request, pk):
        collection = get_object_or_404(
            Collection.objects.prefetch_related(
                Prefetch(
                    'product_set',
                    queryset=Product.objects.all()
                )
            ).select_related('store').annotate(
                products_count=Count('product')),
            pk=pk
        )
        serializer = CollectionSerializer(
            collection, context={'request': request})
        return Response(serializer.data)

    def put(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        serializer = CollectionSerializer(
            collection, data=request.data, partial=True, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.product_set.count() > 0:
            return Response({"error": "Collection has products"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CustomerOrderList(APIView):
    def get(self, request):
        customers = Customer.objects.filter(order__isnull=False).prefetch_related(
            'order_set'
        ).distinct()
        serializer = CustomerSerializer(customers, many=True)
        return Response(serializer.data)


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
