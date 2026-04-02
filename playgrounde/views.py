from django.shortcuts import render
from django.http import HttpResponse


def say_hello(request): # --> return an http response
    return render(request, "hi.html", {'name':'hello'})
