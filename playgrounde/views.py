from django.shortcuts import render
from django.db.models import Q , Count
from django.db import transaction
from store_.models import Product , OrderItem , Order , Customer, Collection





def say_hello(request): # --> return an http response

    gg = Order.objects.prefetch_related('orderitem_set__product')


    return render(request, "hi.html", {'name':'Ayoub','collection':gg})
