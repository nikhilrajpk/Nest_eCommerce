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

# Category Details

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
    
    
 # Product Details 
    
@never_cache
def admin_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            products = Product.objects.all().filter(Q(product_name__icontains = query)| Q(category__category_name__icontains = query))
        else:
            products = Product.objects.all()
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

@never_cache
def add_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            product_description = request.POST.get('description')
            price = request.POST.get('price')
            offer_id = request.POST.get('offer')
            category_id = request.POST.get('category')
            available_stock = request.POST.get('available_stock')
            image_1 = request.FILES.get('image_1')
            image_2 = request.FILES.get('image_2')
            image_3 = request.FILES.get('image_3')
            is_listed = request.POST.get('is_listed')
            in_stock = request.POST.get('in_stock')
            material = request.POST.get('material')
            color = request.POST.get('color')
                
            category = Category.objects.get(id = category_id)
            
            new_product = Product(
                product_name = product_name,
                description = product_description,
                price = price,
                category = category,
                available_stock = available_stock,
                image_1 = image_1,
                image_2 = image_2,
                image_3 = image_3,
                is_listed = is_listed,
                in_stock = in_stock,
                material = material,
                color = color
            )
            if offer_id:
                offer = Offer.objects.get(id = offer_id)
                new_product = Product(offer = offer)
            
            new_product.save()
            messages.success(request,f'New product {product_name} added.')
            return redirect('admin_app:admin_product')
        categories = Category.objects.all()
        offers = Offer.objects.all()
        context = {
            'categories' : categories,
            'offers' : offers
        }
        return render(request,'admin_app/add_product.html',context)
    else:
        return redirect('user_app:home')
    
@never_cache
def edit_product(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        product = Product.objects.get(id = id)    # Retrive data of the product
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            product_description = request.POST.get('description')
            price = request.POST.get('price')
            offer_id = request.POST.get('offer')
            category_id = request.POST.get('category')
            available_stock = request.POST.get('available_stock')
            image_1 = request.FILES.get('image_1')
            image_2 = request.FILES.get('image_2')
            image_3 = request.FILES.get('image_3')
            is_listed = request.POST.get('is_listed')
            in_stock = request.POST.get('in_stock')
            material = request.POST.get('material')
            color = request.POST.get('color')
            
            product.product_name = product_name
            product.description = product_description
            product.price = price
            
            if offer_id == '0':
                product.offer = None
            elif offer_id:
                offer = Offer.objects.get(id = offer_id)
                product.offer = offer
            
            category = Category.objects.get(id = category_id)
            product.category = category
            
            product.available_stock = available_stock
            
            if image_1:
                product.image_1 = image_1
            if image_2:
                product.image_2 = image_2
            if image_3:
                product.image_3 = image_3
                
            product.is_listed = is_listed
            product.in_stock = in_stock
            product.material = material
            product.color = color
            
            product.save()
            
            messages.success(request,f'Product {product_name} edited.')
            return redirect('admin_app:admin_product')
        categories = Category.objects.all().exclude(id = product.category.id)
        if product.offer:
            offers = Offer.objects.all().exclude(id = product.offer.id)
        else:
            offers = Offer.objects.all()
        context = {
            'product':product,
            'categories' : categories,
            'offers' : offers
        }
        return render(request,'admin_app/edit_product.html',context)
    else:
        return redirect('user_app:home')
    
    
# Offer Details

def admin_offer(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            offers = Offer.objects.all().filter(offer_title__icontains = query)
        else:
            offers = Offer.objects.all()
            
        return render(request,'admin_app/offer.html',{'offers':offers,'query':query})
    
    else:
        return redirect('user_app:home')
    
def add_offer(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            offer_title = request.POST.get('offer_title')
            offer_description = request.POST.get('offer_description')
            offer_percentage = request.POST.get('offer_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            offer = Offer(
                offer_title = offer_title,
                offer_description = offer_description,
                offer_percentage = offer_percentage,
                start_date = start_date,
                end_date = end_date
            )
            
            offer.save()
            messages.success(request,f'New offer {offer_title} added.')
            return redirect('admin_app:admin_offer')
            
        return render(request,'admin_app/add_offer.html')
    else:
        return redirect('user_app:home')
    
@never_cache
def edit_offer(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        offer = Offer.objects.get(id = id)    # Retrive data of the offer
        if request.method == 'POST':
            offer_title = request.POST.get('offer_title')
            offer_description = request.POST.get('offer_description')
            offer_percentage = request.POST.get('offer_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            offer.offer_title = offer_title
            offer.offer_description = offer_description
            offer.offer_percentage = offer_percentage
            offer.start_date = start_date
            offer.end_date = end_date
            
            
            offer.save()
            
            messages.success(request,f'Offer {offer_title} edited.')
            return redirect('admin_app:admin_offer')
        return render(request,'admin_app/edit_offer.html',{'offer':offer})
    else:
        return redirect('user_app:home')
    
@never_cache
def edit_offer(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        offer = Offer.objects.get(id = id)    # Retrive data of the offer
        if request.method == 'POST':
            offer_title = request.POST.get('offer_title')
            offer_description = request.POST.get('offer_description')
            offer_percentage = request.POST.get('offer_percentage')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            offer.offer_title = offer_title
            offer.offer_description = offer_description
            offer.offer_percentage = offer_percentage
            offer.start_date = start_date
            offer.end_date = end_date
            
            
            offer.save()
            
            messages.success(request,f'Offer {offer_title} edited.')
            return redirect('admin_app:admin_offer')
        return render(request,'admin_app/edit_offer.html',{'offer':offer})
    else:
        return redirect('user_app:home')
    
@never_cache
def remove_offer(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        print('hai')
        offer = Offer.objects.get(id = id)    # Retrive data of the offer
        if request.method == 'POST':
            print('hello')
            offer_title = offer.offer_title
            offer.delete()
            
            messages.success(request,f'Offer {offer_title} removed.')
            return redirect('admin_app:admin_offer')
        return redirect('admin_app:admin_offer')
    else:
        return redirect('user_app:home')
    