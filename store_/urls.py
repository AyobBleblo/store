from django.urls import path
from . import views


urlpatterns = [
    path('products/',views.ProductList.as_view()),
    path('product_details/<int:pk>/',views.ProductDetail.as_view()),
    path('collection/',views.CollectionList.as_view()),
    path('collection_details/<int:pk>/',views.CollectionDetail.as_view(), name='collection_details'),
    path('customer-orders/',views.CustomerOrderList.as_view()),
    path('customer-stores/<int:id>/',views.CustomerStoreList.as_view()),
    path('store-products/<int:store_id>/',views.StoreProductList.as_view()),
    path('store-with-collection/<int:id>/',views.StoreWithCollection.as_view()),
    path('store-sum-avg-max-price/<int:pk>/',views.StoreSumAvgMaxPrice.as_view() , name='store-sum-avg-max-price')
]