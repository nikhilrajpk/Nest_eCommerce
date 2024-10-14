from django.shortcuts import render,redirect
from authentication_app.models import CustomUser
from category_app.models import *
from django.db.models import Q

from django.contrib import messages
# Create your views here.

def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff: 
        return render(request,'admin_app/admin_home.html')
    else:
        return redirect('user_app:home')
    
def users(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            users = CustomUser.objects.all().exclude(is_staff = True).filter(Q(first_name__icontains = query) | Q(email__icontains = query))
        else:
            users = CustomUser.objects.all().exclude(is_staff = True)
        return render(request,'admin_app/users.html',{'users':users,'query':query})
    
    else:
        return redirect('user_app:home')
    

def user_block(request,id):
    if request.method == 'POST':
        user = CustomUser.objects.get(id = id)
        print(user)
        if user.is_block:
            print(user.is_block)
            user.is_block = False
            user.save()
        elif not user.is_block:
            user.is_block = True
            user.save()
    return redirect('admin_app:users')

def admin_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            category = Category.objects.all().filter(category_name__icontains = query)
        else:
            category = Category.objects.all()
        return render(request,'admin_app/category.html',{'category':category,'query':query})
    
    else:
        return redirect('user_app:home')
    
def category_listed(request,id):
    if request.method == 'POST':
        category = Category.objects.get(id = id)
        if category.is_listed:
            print(category.is_listed)
            category.is_listed = False
            category.save()
        elif not category.is_listed:
            category.is_listed = True
            category.save()
    return redirect('admin_app:admin_category')

def add_category(request):
    if request.method == 'POST':
        category_name = request.POST.get('category_name')
        category_image = request.POST.get('category_image')
        is_listed = request.POST.get('available')
        
        new_category = Category(category_name = category_name, cat_image = category_image, is_listed = is_listed)
        new_category.save()
        messages.success(request,f'New category {category_name} added.')
        return redirect('admin_app:admin_category')
    return render(request,'admin_app/add_category.html')