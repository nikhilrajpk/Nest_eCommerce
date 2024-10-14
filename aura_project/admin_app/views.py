from django.shortcuts import render,redirect
from authentication_app.models import CustomUser
from category_app.models import *
from product_app.models import *
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.contrib import messages
# Create your views here.

@never_cache
def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff: 
        return render(request,'admin_app/admin_home.html')
    else:
        return redirect('user_app:home')

@never_cache    
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
    
@never_cache
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

@never_cache
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

@never_cache
def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category_image = request.FILES.get('category_image')
            is_listed = request.POST.get('available')
            
            new_category = Category(
                category_name = category_name,
                cat_image = category_image,
                is_listed = is_listed
            )
            new_category.save()
            messages.success(request,f'New category {category_name} added.')
            return redirect('admin_app:admin_category')
        return render(request,'admin_app/add_category.html')
    else:
        return redirect('user_app:home')
    
@never_cache
def edit_category(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        category = Category.objects.get(id = id)    # Retrive data of the catgory
        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            category_image = request.FILES.get('category_image')
            is_listed = request.POST.get('available')
            
            category.category_name = category_name
            category.is_listed = is_listed
            
            if category_image:
                category.cat_image = category_image
            
            category.save()
            
            messages.success(request,f'Category {category_name} edited.')
            return redirect('admin_app:admin_category')
        return render(request,'admin_app/edit_category.html',{'category':category})
    else:
        return redirect('user_app:home')
    
    
@never_cache
def admin_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            product = Product.objects.all().filter(Q(product_name__icontains = query)) #| Q(category.category_name__icontains = query)
        else:
            # product = Product.objects.all()
            products = {'product_name':'Rocking chair','category_name':'Chair','price': 400,'is_listed':True}
        return render(request,'admin_app/product.html',{'products':products,'query':query})
    
    else:
        return redirect('user_app:home')
    
def product_listed(request,id):
    if request.method == 'POST':
        product = Product.objects.get(id = id)
        if product.is_listed:
            print(product.is_listed)
            product.is_listed = False
            product.save()
        elif not product.is_listed:
            product.is_listed = True
            product.save()
    return redirect('admin_app:admin_product')

# @never_cache
# def add_product(request):
#     if request.user.is_authenticated and request.user.is_staff:
#         if request.method == 'POST':
#             product_name = request.POST.get('product_name')
#             category_image = request.FILES.get('product_image')
#             is_listed = request.POST.get('available')
            
#             new_category = Category(
#                 category_name = category_name,
#                 cat_image = category_image,
#                 is_listed = is_listed
#             )
#             new_category.save()
#             messages.success(request,f'New category {category_name} added.')
#             return redirect('admin_app:admin_category')
#         return render(request,'admin_app/add_category.html')
#     else:
#         return redirect('user_app:home')
    
# @never_cache
# def edit_product(request,id):
#     if request.user.is_authenticated and request.user.is_staff:
#         category = Category.objects.get(id = id)    # Retrive data of the catgory
#         if request.method == 'POST':
#             category_name = request.POST.get('category_name')
#             category_image = request.FILES.get('category_image')
#             is_listed = request.POST.get('available')
            
#             category.category_name = category_name
#             category.is_listed = is_listed
            
#             if category_image:
#                 category.cat_image = category_image
            
#             category.save()
            
#             messages.success(request,f'Category {category_name} edited.')
#             return redirect('admin_app:admin_category')
#         return render(request,'admin_app/edit_category.html',{'category':category})
#     else:
#         return redirect('user_app:home')