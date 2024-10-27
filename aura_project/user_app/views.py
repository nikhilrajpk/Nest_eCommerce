from django.shortcuts import render,redirect
from product_app.models import *
from authentication_app.models import *
from address_app.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from authentication_app.validators import Authentication_check

from django.core.paginator import Paginator

def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    
    banners = Banner.objects.all()
    
    latest_products = Product.objects.all().order_by('-id')[:4]
    
    best_sellers = Product.objects.all().order_by('-sold_count')[:8]
    
    # Paginator for the products
    page = 1
    if request.GET:
        page = request.GET.get('page',1)
    
    query = request.GET.get('search_query')
    
    if query:
        products = Product.objects.filter(product_name__icontains = query)
    
    else:    
        # Sorting with price or name
        sort_with = 'product_name'
        if request.method == 'POST':
            sort_with = request.POST.get('sort_with')
            request.session['sort_with'] = sort_with
            print(sort_with)
        sort_with = request.session.get('sort_with','product_name')
        products = Product.objects.all().order_by(sort_with)
        print(sort_with,'hai')
        
    # products = Product.objects.all()
    product_paginator = Paginator(products,8)
    products = product_paginator.get_page(page)
        
    context = {
        'banners':banners,
        'latest_products':latest_products,
        'products':products,
        'best_sellers':best_sellers,
        'query':query,
    }
    return render(request,'user_app/index.html',context)

@login_required
def account(request):
    user_logged = request.user
    user = CustomUser.objects.get(email = user_logged.email)
    
    context = {
        'user':user,
    }
    return render(request,'user_app/account.html',context)

@login_required
def add_address(request):
    user = request.user
    user_details = CustomUser.objects.get(email = user.email)
    if request.method == 'POST':
        address_type = request.POST.get('address_type')
        street_address = request.POST.get('street_address')
        landmark = request.POST.get('landmark')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        alternative_phone = request.POST.get('alternative_phone')
        address = request.POST.get('address')
        
        print(user_details.email)
        
        new_address = Address(
            user = user_details,
            address_type = address_type,
            street_address = street_address,
            landmark = landmark,
            state = state,
            country = country,
            postal_code = postal_code,
            phone = phone,
            alternative_phone = alternative_phone,
            address = address
        )
        new_address.save()
        messages.success(request,'New address added.')
        
        return redirect('user_app:account')
        
    return render(request,'user_app/add_address.html')


@login_required
def edit_profile(request):
    logged_user = request.user
    user = CustomUser.objects.get(email = logged_user.email)
    
    # Validation object
    user_validation = Authentication_check()
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        errors = {}
            
        #first_name validation
        first_name_valid = user_validation.first_name_validator(first_name)
        if first_name_valid:
            errors['first_name_error'] = first_name_valid
            messages.error(request,'first name should not contain number or spaces!')
        
        #last_name validation
        last_name_valid = user_validation.last_name_validator(last_name)
        if last_name_valid:
            errors['last_name_error'] = last_name_valid
            messages.error(request,'last name should not contain number or spaces!')
        
        if not errors:    
        
            user.first_name = first_name
            user.last_name = last_name
        
            user.save()
            messages.success(request,'Changes have been saved.')
        else:
        
            context = {user : {
                'first_name':first_name,
                'last_name':last_name
            }
            }
        
            return render(request,'user_app/edit_profile.html',context)
    
    context = {
        'user':user,
    }
    return render(request,'user_app/edit_profile.html',context)


@login_required
def edit_address(request,address_id):
    address = Address.objects.get(id=address_id)
    
    if request.method == 'POST':
        address_type = request.POST.get('address_type')
        street_address = request.POST.get('street_address')
        landmark = request.POST.get('landmark')
        state = request.POST.get('state')
        country = request.POST.get('country')
        postal_code = request.POST.get('postal_code')
        phone = request.POST.get('phone')
        alternative_phone = request.POST.get('alternative_phone')
        address_inp = request.POST.get('address')
        
        # Updating the address details
        address.address_type = address_type
        address.street_address = street_address
        
        if landmark:
            address.landmark = landmark
            
        address.state = state
        address.country = country
        address.postal_code = postal_code
        address.phone = phone
        
        if alternative_phone:
            address.alternative_phone = alternative_phone
        
        address.address = address_inp
        
        address.save()
        
        messages.success(request,'Address have been updated.')
        return redirect('user_app:edit_profile')
    
    context = {
        'address':address,
    }
    return render(request,'user_app/edit_address.html',context)


@login_required
def delete_address(request,address_id):
    if request.method == 'POST':
        address = Address.objects.get(id = address_id)
        address.delete()
    
        return redirect('user_app:edit_profile')