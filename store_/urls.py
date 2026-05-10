from django.urls import path
from . import views


urlpatterns = [
    path('products/',views.product_list),
    path('product_details/<int:pk>/',views.product_details),
    path('collection/',views.collection_list),
    path('collection_details/<int:pk>/',views.collection_details, name='collection_details'),
    path('customer-orders/',views.customer_orders),
    path('customer-stores/<int:id>/',views.customer_stores),
    path('store-products/<int:store_id>/',views.store_products),
    path('store-with-collection/<int:id>/',views.store_with_collection),
    path('store-sum-avg-max-price/<int:pk>/',views.store_sum_avg_max_price , name='store-sum-avg-max-price')
]