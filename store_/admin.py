from django.urls import reverse
from django.db.models import Count
from django.db.models.fields import related
from django.contrib import admin
from django.utils.html import format_html , urlencode
from store_.models import Product,Collection , Customer , Order
# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','unit_price','inventory_status' , 'collection' ]
    list_editable = ['unit_price']
    list_per_page = 10
    list_select_related = ['collection__store']

    @admin.display(ordering='inventory')
    def inventory_status(self,product):
        if product.inventory < 10:
            return 'Low'
        return 'High'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name','last_name','email','membership','order_count']
    list_editable = ['membership']
    list_per_page = 10
    search_fields = ['first_name__istartswith','last_name__istartswith']
    def order_count(self,customer):
        return customer.order_count
    
    @admin.display(ordering='order_count')
    def get_queryset(self,request):
        return super().get_queryset(request).annotate(
            order_count=Count('order')
        )
    

    
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['placed_at','payment_status','customer','ordering_customer']
    list_per_page = 10
    list_filter = ['payment_status']

    def ordering_customer(self,order):
        return order.ordering_customer
        
    @admin.display(ordering='ordering_customer')
    def get_queryset(self,request):
        return super().get_queryset(request).annotate(
            ordering_customer=Count('customer')
        )

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title' ,'products_count']
    list_select_related = ['store']
    list_per_page = 10

    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url = (reverse('admin:store__product_changelist') 
        + '?'
        + urlencode({
            'collection__id': str(collection.id)
        }))
        return format_html('<a href="{}">{}</a>',url,collection.products_count)
        

    def get_queryset(self,request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

    
    