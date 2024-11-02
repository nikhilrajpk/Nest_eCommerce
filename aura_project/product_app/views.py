from django.shortcuts import render,redirect
from category_app.models import Category
from product_app.models import *
from django.core.paginator import Paginator
from django.db.models import Count,Sum
# Create your views here.

def display_products(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
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
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    product = Product.objects.get(id = id)
    
    # getting the review data
    review_data = Product.objects.filter(id=id).aggregate(
        total_reviews=Count('productreview'),
        total_stars=Sum('productreview__rating')
    )

    #  total reviews and total stars from the aggregated data
    total_reviews = review_data['total_reviews'] or 0
    total_stars = review_data['total_stars'] or 0
    
    print(total_reviews)

    # Calculating the average rating
    if total_reviews > 0:
        average_rating = total_stars / total_reviews
    else:
        average_rating = 0
    
    context = {
        'product':product,
        'total_review':total_reviews,
        'average_rating':average_rating,
    }
    
    return render(request,'product_app/single_product.html',context)