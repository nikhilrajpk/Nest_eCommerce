from django.shortcuts import render,redirect
from product_app.models import *

from django.core.paginator import Paginator

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    latest_products = Product.objects.all().order_by('-id')[:4]
    best_sellers = Product.objects.all().order_by('-sold_count')[:8]
    
    # Paginator for the products
    page = 1
    if request.GET:
        page = request.GET.get('page',1)
    products = Product.objects.all()
    product_paginator = Paginator(products,8)
    products = product_paginator.get_page(page)
        
    context = {
        'latest_products':latest_products,
        'products':products,
        'best_sellers':best_sellers,
    }
    return render(request,'user_app/index.html',context)