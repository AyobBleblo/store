from django.urls import include
from django.urls import path
from . import views
from rest_framework_nested import routers
from pprint import pprint

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet)
router.register('collections', views.CollectionViewSet)
router.register('customer-orders', views.CustomerOrderList, basename='customer-orders')
router.register('carts', views.CartViewSet, basename='carts')
router.register('cart-items', views.CartItemViewSet, basename='cart-items')
router.register('customer', views.CustomerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router , "products",  lookup='product')
product_router.register('reviews' , views.ReviewViewSet , 'product-reviews')

cart_item_router = routers.NestedDefaultRouter(router, "carts", lookup='cart')
cart_item_router.register('items', views.CartItemViewSet, basename='cart-items')



# pprint(router.urls)


urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_item_router.urls)),
    # path('products/',views.ProductList.as_view()),
    # path('product_details/<int:pk>/',views.ProductDetail.as_view()),
    # path('collection/',views.CollectionList.as_view()),
    # path('collection_details/<int:pk>/',views.CollectionDetail.as_view(), name='collection_details'),
    # path('customer-orders/',views.CustomerOrderList.as_view()),
    path('customer-stores/<int:id>/',views.CustomerStoreList.as_view()),
    path('store-products/<int:store_id>/',views.StoreProductList.as_view()),
    path('store-with-collection/<int:id>/',views.StoreWithCollection.as_view()),
    path('store-sum-avg-max-price/<int:pk>/',views.StoreSumAvgMaxPrice.as_view() , name='store-sum-avg-max-price')
]