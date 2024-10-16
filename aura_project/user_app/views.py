from django.shortcuts import render,redirect
from product_app.models import *

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    latest_products = Product.objects.all().order_by('-id')[:4]
    products = Product.objects.all()
    best_sellers = Product.objects.all().order_by('-sold_count')[:8]
    context = {
        'latest_products':latest_products,
        'products':products,
        'best_sellers':best_sellers,
    }
    return render(request,'user_app/index.html',context)