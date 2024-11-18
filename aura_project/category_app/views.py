from django.shortcuts import render,redirect
from category_app.models import *
from django.db.models import *
from django.utils import timezone
from django.core.paginator import Paginator
# Create your views here.

def category_view(request):
    # If admin then return to the admin page
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    query = request.GET.get('search_query','')
    page = request.GET.get('page',1)
    
    if query:
        categories = Category.objects.all().filter(category_name__icontains = query).annotate(count_of_product = Count('product'))
    else:
        categories = Category.objects.annotate(count_of_product = Count('product'))
        
    # removing offers if it expires 
    for category in categories:
        if category.offer and category.offer.end_date < timezone.now():
            category.offer = None
            category.product.all().update(offer=None)
            category.save()
    
    
    # Paginator
    category_paginator = Paginator(categories,9)
    categories = category_paginator.get_page(page)
    
    total = Category.objects.count()
    
    context = {
        'categories':categories,
        'total':total,
        'query':query
    }
    return render(request,'category_app/category.html',context)