from django.shortcuts import render,redirect
from category_app.models import Category
from product_app.models import *
from django.core.paginator import Paginator
# Create your views here.

def display_products(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    
    category = Category.objects.get(id = id)
    
    page = request.GET.get('page',1)
    query = request.GET.get('search_query','')
    
    if query:
        products = category.product.filter(product_name__icontains = query)
    else:
        # getting all the products in the specified category
        products = category.product.all()
    
    product_paginator = Paginator(products,1)
    products = product_paginator.get_page(page)
    
    context = {
        'category':category,
        'products':products,
        'query':query,
    }
    return render(request,'product_app/product.html',context)


def single_product_view(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    
    product = Product.objects.get(id = id)
    
    context = {
        'product':product,
    }
    
    return render(request,'product_app/single_product.html',context)