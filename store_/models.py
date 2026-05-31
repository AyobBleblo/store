import uuid
from django.db import models
from django.core.validators import MinValueValidator
from django.conf import settings
from django.contrib import admin

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.DecimalField(max_digits=10, decimal_places=2)
    class Meta:
        db_table = 'store_promotion'
    


class Customer(models.Model):
    MEMBERSHIP_BRONZE = 'B'
    MEMBERSHIP_SILVER = 'S'
    MEMBERSHIP_GOLD = 'G'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]

    birth_date = models.DateField(null=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    membership = models.CharField(
        max_length=1, choices=MEMBERSHIP_CHOICES, default=MEMBERSHIP_BRONZE)
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = 'store_customers'
        ordering = ['user__first_name', 'user__last_name']
        permissions = [(
            'view_history', 'Can view history'
        )]
        

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name

class Store(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='stores')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_store'

    def __str__(self):
        return self.name


class Collection(models.Model):
    title = models.CharField(max_length=255)
    store = models.ForeignKey(
        Store, on_delete=models.CASCADE, null=True, blank=True)
    featured_product = models.ForeignKey(
        'Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='+')

    class Meta:
        ordering = ['title']
        db_table = 'store_collection'

    def __str__(self):
        return f"{self.title}"
        
class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    is_featured = models.BooleanField(default=False)
    promotions = models.ManyToManyField(Promotion, blank=True)
    
    def __str__(self):
        return  f"{self.title}"
    

    class Meta:
        ordering = ['title']
        db_table = 'store_product'


class Order(models.Model):
    PAYMENT_STATUS_PENDING = 'P'
    PAYMENT_STATUS_COMPLETE = 'C'
    PAYMENT_STATUS_FAILED = 'F'

    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_STATUS_PENDING, 'Pending'),
        (PAYMENT_STATUS_COMPLETE, 'Complete'),
        (PAYMENT_STATUS_FAILED, 'Failed'),
    ]

    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(
        max_length=1, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)

    class Meta:
        permissions = [
            ('cancel_order', 'Can cancel order')
            ]
        db_table = 'store_order'

    def __str__(self):
        return f"Order {self.id} - {self.customer.first_name} {self.customer.last_name} payment_status: {self.payment_status}"



class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.PROTECT , related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveSmallIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'store_orderitem'


class Address(models.Model):
    user = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=50)
    zip_code = models.CharField(max_length=255, null=True)
    is_default = models.BooleanField(default=False)

    class Meta:
        db_table = 'store_address'


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.OneToOneField(
        Customer, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'store_cart'

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = 'store_cartitem'
        unique_together = [['cart', 'product']]


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_review'
