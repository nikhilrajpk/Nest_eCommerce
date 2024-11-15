from django.shortcuts import render,redirect,get_object_or_404
from authentication_app.models import CustomUser
from category_app.models import *
from product_app.models import *
from coupen_app.models import *
from order_app.models import *
from django.db.models import Q
from django.views.decorators.cache import never_cache
from django.contrib import messages
from django.db.models import F
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import re

#For dashboard chart
import calendar
from django.db.models import Count
from django.db.models.functions import ExtractMonth,ExtractDay,ExtractYear,ExtractWeekDay

# Create your views here.

@never_cache
def admin_home(request):
    if request.user.is_authenticated and request.user.is_staff: 
        # Getting the orders
        orders = Order.objects.exclude(order_status='canceled')
        
        # Initializing count array (0=Monday to 6=Sunday as per Python's weekday())
        days_count = [0] * 7
        
        # Count orders by weekday using Python's date.weekday()
        for order in orders:
            # Convert UTC to local time
            local_date = timezone.localtime(order.order_date)
            weekday = local_date.weekday()  # Monday = 0, Sunday = 6
            days_count[weekday] += 1
        
        # Create day names starting with Monday
        day_names = [calendar.day_name[i] for i in range(7)]  # Monday to Sunday

        # Debug information
        print("Raw order counts by day:", days_count)
        print("Day names:", day_names)
        print("Total orders:", sum(days_count))
        
        # Process monthly data
        orders_monthly = Order.objects.annotate(
            month=ExtractMonth('order_date', tzinfo=timezone.get_current_timezone())
        ).values('month').annotate(
            count_month=Count('id')
        ).values('month', 'count_month').exclude(
            order_status='canceled'
        )
        
        # Process yearly data
        orders_yearly = Order.objects.annotate(
            year=ExtractYear('order_date', tzinfo=timezone.get_current_timezone())
        ).values('year').annotate(
            count_year=Count('id')
        ).values('year', 'count_year').exclude(
            order_status='canceled'
        )

        # Process monthly and yearly data
        month = []
        year = []
        total_order_month = []
        total_order_year = []
        
        for i in orders_monthly:
            month.append(calendar.month_name[i['month']])
            total_order_month.append(i['count_month'])
            
        for i in orders_yearly:
            year.append(str(i['year']))
            total_order_year.append(i['count_year'])

        # Let's also print a detailed breakdown
        weekday_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        print("\nDetailed daily breakdown:")
        for i, count in enumerate(days_count):
            print(f"{weekday_names[i]}: {count} orders")

        context = {
            'total_order_day': days_count,
            'day': day_names,
            'total_order_month': total_order_month,
            'month': month,
            'total_order_year': total_order_year,
            'year': year,
        }
        return render(request,'admin_app/admin_home.html',context)
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
@require_POST
def user_block(request, id):
    user = CustomUser.objects.get(id=id)
    if user.is_block:
        user.is_block = False
    else:
        user.is_block = True
    user.save()
    return JsonResponse({"is_block": user.is_block})
  

# Category Details

@never_cache
def admin_category(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            category = Category.objects.all().filter(category_name__icontains = query)
        else:
            category = Category.objects.all().order_by('category_name')
        for i in category:
            if i.offer and i.offer.end_date < timezone.now():
                i.offer = None
                i.product.all().update(offer=None)
                i.save()
            
        return render(request,'admin_app/category.html',{'category':category,'query':query})
    
    else:
        return redirect('user_app:home')
    
@never_cache
def top_selling_category(request):
    categories = Category.objects.all().annotate(total_sold = Sum('product__sold_count')).order_by('-total_sold')[:10]
    return render(request,'admin_app/top_selling_category.html',{'categories':categories})

@require_POST
def category_listed(request, id):
    category = Category.objects.get(id=id)
    category.is_listed = not category.is_listed  # Toggle the listed status
    category.save()
    return JsonResponse({"is_listed": category.is_listed})


@never_cache

def add_category(request):
    if request.user.is_authenticated and request.user.is_staff:

        if request.method == 'POST':

            category_name = request.POST.get('category_name')

            category_exist = Category.objects.filter(category_name__iexact = category_name).exists()

            print('Category already exist or not : ',category_exist)

            if category_exist:
                messages.error(request,'This category already exist!')

            else:
                category_image = request.FILES.get('category_image')

                is_listed = request.POST.get('available')

                offer = None

                new_category = Category(

                    category_name = category_name,
                    offer = offer,
                    cat_image = category_image,
                    is_listed = is_listed

                )

                new_category.save() 

                messages.success(request,f'New category {category_name} added.')

                return redirect('admin_app:admin_category')

        offers = Offer.objects.exclude(end_date__lt = timezone.now())

        return render(request,'admin_app/add_category.html',{'offers':offers})

    else:

        return redirect('user_app:home')


@never_cache

def edit_category(request,id):

    if request.user.is_authenticated and request.user.is_staff:

        category = Category.objects.get(id = id)# Retrive data of the catgory

        if request.method == 'POST':

            category_name = request.POST.get('category_name')

            offer_id = request.POST.get('offer')
            print('offer_id : ',offer_id)
            category_image = request.FILES.get('category_image')
            is_listed = request.POST.get('available')

            if offer_id == '0' or not offer_id:
                offer = None  # No offer selected
            else:
                offer = get_object_or_404(Offer, id=offer_id)

            print('offer object:', offer)
            category.offer = offer 


            category.category_name = category_name

            category.is_listed = is_listed

            if category_image:
                category.cat_image = category_image

            category.save()

           

            # Update products without an individual offer
            if offer is None:  
                products = category.product.all()  
                for product in products:
                    product.offer = None 
                    product.save()

            else:
                products = category.product.filter(offer__isnull=True)  # products with no offer
                for product in products:
                    product.offer = offer  
                    product.save()
                

            messages.success(request,f'Category {category_name} edited.')

            return redirect('admin_app:admin_category')

        if category.offer:
            offers = Offer.objects.exclude(id = category.offer.id)
            offers = offers.exclude( end_date__lt = timezone.now())
        else:
            offers = Offer.objects.exclude(end_date__lt = timezone.now())

        return render(request,'admin_app/edit_category.html',{'category':category,'offers':offers})

    else:

        return redirect('user_app:home')


@never_cache
def admin_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            products = Product.objects.all().filter(Q(product_name__icontains = query)| Q(category__category_name__icontains = query))
        else:
            products = Product.objects.all().order_by('category__category_name')
            
        for i in products:
            if i.offer and i.offer.end_date < timezone.now():
                i.offer = None
                i.category.offer = None
                i.save()
                
        return render(request,'admin_app/product.html',{'products':products,'query':query})
    
    else:
        return redirect('user_app:home')

@never_cache
def top_selling_products(request):
    products = Product.objects.all().order_by('-sold_count')[:10]
    return render(request,'admin_app/top_selling_product.html',{'products':products})

@require_POST
def product_listed(request, id):
    product = Product.objects.get(id=id)
    product.is_listed = not product.is_listed  # Toggle the listed status
    product.save()
    return JsonResponse({"is_listed": product.is_listed})

@never_cache
def add_product(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            product_name = request.POST.get('product_name')
            product_exist = Product.objects.filter(product_name__iexact = product_name).exists()
            if product_exist:
                messages.error(request,'Product name already exist.')
            else:
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
                width = request.POST.get('width')
                height = request.POST.get('height')
                length = request.POST.get('length')
                    
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
                    color = color,
                    length = length,
                    width = width,
                    height = height,
                )
                if offer_id:
                    offer = Offer.objects.get(id = offer_id)
                    new_product.offer = offer
                
                new_product.save()
                messages.success(request,f'New product {product_name} added.')
                return redirect('admin_app:admin_product')
        categories = Category.objects.all()
        offers = Offer.objects.exclude(end_date__lt = timezone.now())
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
            print('Edited stock : ',available_stock)
            image_1 = request.FILES.get('image_1')
            image_2 = request.FILES.get('image_2')
            image_3 = request.FILES.get('image_3')
            is_listed = request.POST.get('is_listed')
            in_stock = request.POST.get('in_stock')
            material = request.POST.get('material')
            color = request.POST.get('color')
            width = request.POST.get('width')
            height = request.POST.get('height')
            length = request.POST.get('length')
            
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
            product.width = width
            product.length = length
            product.height = height
            
            product.save()
            
            messages.success(request,f'Product {product_name} edited.')
            return redirect('admin_app:admin_product')
        categories = Category.objects.all().exclude(id = product.category.id)
        if product.offer:
            offers = Offer.objects.all().exclude(id = product.offer.id)
            offers = offers.exclude(end_date__lt=timezone.now())
        else:
            offers = Offer.objects.exclude(end_date__lt=timezone.now())
        context = {
            'product':product,
            'categories' : categories,
            'offers' : offers
        }
        return render(request,'admin_app/edit_product.html',context)
    else:
        return redirect('user_app:home')
    
def add_stock(request,product_id):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            product = Product.objects.get(id = product_id)
            new_stock = request.POST.get('new_stock')
            
            if new_stock and new_stock.isdigit():
                new_stock = int(new_stock)
                
                product.available_stock = F('available_stock') + new_stock
                product.save()
                
                messages.success(request,f'{product.product_name} added {new_stock} stock ')
            else:
                messages.error(request,'Invalid stock value')
        return redirect('admin_app:admin_product')
    
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
        offer = Offer.objects.get(id = id)    # Retrive data of the offer
        if request.method == 'POST':
            offer_title = offer.offer_title
            offer.delete()
            
            messages.success(request,f'Offer {offer_title} removed.')
            return redirect('admin_app:admin_offer')
        return redirect('admin_app:admin_offer')
    else:
        return redirect('user_app:home')
    
    
@never_cache
def admin_banner(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            banners = Banner.objects.all().filter(banner_name__icontains = query)
        else:
            banners = Banner.objects.all()
            
        return render(request,'admin_app/banner.html',{'banners':banners,'query':query})
    
    else:
        return redirect('user_app:home')
    
def add_banner(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            banner_name = request.POST.get('banner_name')
            description = request.POST.get('description')
            product_id = request.POST.get('product_id')
            price = request.POST.get('price')
            deal_price = request.POST.get('deal_price')
            banner_image = request.FILES.get('banner_image')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            print(product_id)
            product = Product.objects.get(id = product_id)
            
            new_banner = Banner(
                banner_name = banner_name,
                banner_description = description,
                product = product,
                price = price,
                deal_price = deal_price,
                banner_image = banner_image,
                start_date = start_date,
                end_date = end_date,
            )
            
            new_banner.save()
            messages.success(request,f'New banner {banner_name} added.')
            return redirect('admin_app:admin_banner')
        
        products = Product.objects.all()
        
        context = {
            'products':products,
        }
        
        return render(request,'admin_app/add_banner.html',context)
    else:
        return redirect('user_app:home')


def edit_banner(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        banner = Banner.objects.get(id = id)
        if request.method == 'POST':
            banner_name = request.POST.get('banner_name')
            description = request.POST.get('description')
            product_id = request.POST.get('product_id')
            price = request.POST.get('price')
            deal_price = request.POST.get('deal_price')
            banner_image = request.FILES.get('banner_image')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            
            product = Product.objects.get(id = product_id)
            
            banner.banner_name = banner_name
            banner.banner_description = description
            banner.product = product
            banner.price = price
            banner.deal_price = deal_price
            banner.start_date = start_date
            banner.end_date = end_date
            
            if banner_image:
                banner.banner_image = banner_image
                
            banner.save()
            
            messages.success(request,f' banner {banner_name} edited.')
            return redirect('admin_app:admin_banner')
        
        products = Product.objects.exclude(id = banner.product.id)
        
        context = {
            'banner':banner,
            'products':products,
        }
        
        return render(request,'admin_app/edit_banner.html',context)
    else:
        return redirect('user_app:home')
    
def remove_banner(request,id):
    if request.user.is_authenticated and request.user.is_staff:
        banner = Banner.objects.get(id = id)    # Retrive Banner
        if request.method == 'POST':
            banner_name = banner.banner_name
            banner.delete()
            
            messages.success(request,f'Banner {banner_name} removed.')
            return redirect('admin_app:admin_banner')
        return redirect('admin_app:admin_banner')
    else:
        return redirect('user_app:home')
    
    
def admin_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            coupons = Coupons.objects.all().filter(code__icontains = query)
        else:
            coupons = Coupons.objects.all()
            
        return render(request,'admin_app/coupon.html',{'coupons':coupons,'query':query})
    
    else:
        return redirect('user_app:home')
    
def add_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        if request.method == 'POST':
            code = request.POST.get('code')
            
            code_regex = r'^[a-zA-Z0-9]+$'
            
            if re.match(code_regex,code):
                minimum_order_amount = float(request.POST.get('minimum_order_amount'))
                maximum_order_amount = float(request.POST.get('maximum_order_amount'))
                used_limit = int(request.POST.get('used_limit'))
                expiry_date_str = request.POST.get('expiry_date')
                discount_amount = float(request.POST.get('discount_amount'))
                
                
                # Converting string expiry date to datetime object.
                expiry_date_naive = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
                
                # Converting naive datetime to timezone-aware datetime
                expiry_date = timezone.make_aware(expiry_date_naive, timezone.get_current_timezone())
                
                context = {
                    'code':code,
                    'minimum_order_amount':minimum_order_amount,
                    'maximum_order_amount':maximum_order_amount,
                    'used_limit':used_limit,
                    'expiry_date':expiry_date,
                    'discount_amount':discount_amount,
                }
                if maximum_order_amount <= minimum_order_amount:
                    messages.error(request,'minimum order amount cannot be greater than maximum order amount!')
                    return render(request,'admin_app/add_coupon.html',context)
                elif minimum_order_amount <= discount_amount:
                    messages.error(request,'Discount amount cannot be greater than minimum order amount!')
                    return render(request,'admin_app/add_coupon.html',context)
                elif expiry_date < timezone.now():
                    messages.error(request,'Expiry date cannot be a past time!')
                    return render(request,'admin_app/add_coupon.html',context)
                else:
                    coupon = Coupons(
                        code = code,
                        minimum_order_amount = minimum_order_amount,
                        maximum_order_amount = maximum_order_amount,
                        used_limit = used_limit,
                        expiry_date = expiry_date,
                        discount_amount = discount_amount,
                    )
                    coupon.save()
                    
                    messages.success(request,f'New coupon {code} has added.')
                    return redirect('admin_app:admin_coupon')
            else:
                messages.error(request,'Coupon code should only be numbers and letters!')
         
        return render(request,'admin_app/add_coupon.html')
    
    else:
        return redirect('user_app:home')
    
    
def edit_coupon(request,coupon_id):
    if request.user.is_authenticated and request.user.is_staff:
        coupon = Coupons.objects.get(id = coupon_id)
        
        if request.method == 'POST':
            code = request.POST.get('code')
            
            code_regex = r'^[a-zA-Z0-9]+$'
            
            if re.match(code_regex,code):
                minimum_order_amount = float(request.POST.get('minimum_order_amount'))
                maximum_order_amount = float(request.POST.get('maximum_order_amount'))
                used_limit = int(request.POST.get('used_limit'))
                expiry_date_str = request.POST.get('expiry_date')
                discount_amount = float(request.POST.get('discount_amount'))
                
                # Converting string expiry date to datetime object.
                expiry_date_naive = datetime.strptime(expiry_date_str, '%Y-%m-%dT%H:%M')
                
                # Converting naive datetime to timezone-aware datetime
                expiry_date = timezone.make_aware(expiry_date_naive, timezone.get_current_timezone())
                
                if maximum_order_amount <= minimum_order_amount:
                    messages.error(request,'minimum order amount cannot be greater than maximum order amount!')
                elif minimum_order_amount <= discount_amount:
                    messages.error(request,'Discount amount cannot be greater than minimum order amount!')
                elif expiry_date < timezone.now():
                    messages.error(request,'Expiry date cannot be a past time!')
                else:
                    coupon.code = code
                    coupon.minimum_order_amount = minimum_order_amount
                    coupon.maximum_order_amount = maximum_order_amount
                    coupon.used_limit = used_limit
                    coupon.expiry_date = expiry_date
                    coupon.discount_amount = discount_amount
                    
                    coupon.save()
                    
                    messages.success(request,f'Coupon {code} edited.')
                    return redirect('admin_app:admin_coupon')
            else:
                messages.error(request,'Coupon code should only be numbers and letters!')
        
        context = {
            'coupon':coupon
        }
        return render(request,'admin_app/edit_coupon.html',context)
    
    else:
        return redirect('user_app:home')
    
    
def remove_coupon(request,coupon_id):
    if request.user.is_authenticated and request.user.is_staff:
        
        coupon = Coupons.objects.get(id = coupon_id)
        
        if request.method == 'POST':
            coupon.delete()
            messages.success(request,f'Coupon {coupon.code} removed.')
            return redirect('admin_app:admin_coupon')
    
    else:
        return redirect('user_app:home')
    
    
def admin_orders(request):
    if request.user.is_authenticated and request.user.is_staff:
        query = request.GET.get('search_query')
        if query:
            orders = Order.objects.filter(id__icontains = query)        
        else:
            orders = Order.objects.all().order_by('-id')
        context = {
            'orders':orders,
            'query':query,
        }
        return render(request,'admin_app/orders.html',context)
    
    else:
        return redirect('user_app:home')

def show_order(request,order_id):
    if request.user.is_authenticated and request.user.is_staff:
        order = Order.objects.get(id = order_id)
        order_items = order.items.all()
        
        # Handling the form submission to change order status
        if request.method == "POST":
            new_status = request.POST.get('order_status')
            if new_status in dict(STATUS):  # Ensure the status is valid
                order.order_status = new_status
                order.save()
                messages.success(request, "Order status updated successfully.")
            else:
                messages.error(request, "Invalid order status.")
        
        
        # Calculating total price
        total_price = 0
        item_total_prices = []
        
        for item in order_items:
            # Check if product has an offer and calculate the item total
            if item.product.offer:
                item_total = item.quantity * item.product.discount_price
            else:
                item_total = item.quantity * item.product.price
                
            # Add item total to total order price
            total_price += item_total
            item_total_prices.append(item_total)  # Store each item's total price

        context = {
            'order': order,
            'order_items': zip(order_items, item_total_prices),  # Pass both items and their individual total prices
            'total_price': total_price,
            'status_choices': STATUS,
            'items':order_items,
        }
        return render(request,'admin_app/show_order.html',context)
    
    else:
        return redirect('user_app:home')
    
    # {% url 'admin_app:edit_order' order.id %}
    
    
    
from django.views.generic import TemplateView
from django.http import HttpResponse
from django.db.models import Sum, Count, F
from django.db.models.functions import TruncDate, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
from django.db.models.functions import Coalesce
from django.db.models import DecimalField
import pandas as pd
from io import BytesIO
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import logging
import pytz

logger = logging.getLogger(__name__)
class SalesReportView(TemplateView):
    template_name = 'admin_app/sales_report.html'
    timezone = pytz.timezone('Asia/Kolkata')

    def get(self, request, *args, **kwargs):
        download_format = request.GET.get('download_format')
        if download_format:
            start_date, end_date = self.get_date_range()
            sales_data = self.get_sales_data(start_date, end_date)
            
            if download_format == 'excel':
                return self.download_excel(sales_data)
            elif download_format == 'pdf':
                return self.download_pdf(sales_data)
        
        return super().get(request, *args, **kwargs)
    def download_excel(self, sales_data):
        try:
            # Prepare data for Excel
            excel_data = self.prepare_data_for_excel(sales_data)
            
            # Create DataFrame
            df = pd.DataFrame(excel_data)
            
            # Rename columns to be more readable
            column_mapping = {
                'period': 'Date',
                'orders': 'Total Orders',
                'total_amount': 'Total Amount',
                'discount': 'Discount',
                'net_amount': 'Net Amount',
                'orders_delivered': 'Delivered Orders',
                'orders_confirmed': 'Confirmed Orders',
                'orders_canceled': 'Canceled Orders'
            }
            df = df.rename(columns=column_mapping)
            
            # Reorder columns
            column_order = [
                'Date', 'Total Orders', 'Delivered Orders', 'Confirmed Orders', 
                'Canceled Orders', 'Total Amount', 'Discount', 'Net Amount'
            ]
            df = df.reindex(columns=[col for col in column_order if col in df.columns])
            
            # Create Excel file in memory
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sales Report')
                
                # Auto-adjust columns' width
                worksheet = writer.sheets['Sales Report']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)
            
            # Prepare response
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="sales_report.xlsx"'
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating Excel file: {str(e)}", exc_info=True)
            return HttpResponse(
                "Error generating Excel file",
                content_type='text/plain',
                status=500
            )

    def download_pdf(self, sales_data):
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        elements.append(Paragraph("Sales Report", styles['Heading1']))
        elements.append(Spacer(1, 20))
        
        # Convert data to table format
        table_data = [['Period', 'Orders', 'Total Amount', 'Discount', 'Net Amount']]
        for item in sales_data:
            table_data.append([
                item['period'].strftime('%Y-%m-%d'),
                str(item['orders']),
                f"₹{item['total_amount']}",
                f"₹{item['discount']}",
                f"₹{item['net_amount']}"
            ])
        
        # Create table
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
        
        doc.build(elements)
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=sales_report.pdf'
        response.write(pdf)
        return response
    
    def dispatch(self, request, *args, **kwargs):
        logger.info(f"Request Method: {request.method}")
        logger.info(f"GET Parameters: {request.GET}")
        
        # Handle download requests
        download_format = request.GET.get('download')
        if download_format:
            start_date, end_date = self.get_date_range()
            sales_data = self.get_sales_data(start_date, end_date)
            
            if download_format == 'excel':
                return self.download_excel(sales_data)
        
        return super().dispatch(request, *args, **kwargs)
    def prepare_data_for_excel(self, sales_data):
        """Prepare sales data for Excel export by converting timezone-aware dates."""
        excel_data = []
        
        for item in sales_data:
            # Create a new dict for each row
            row = item.copy()
            
            # Convert period to timezone-naive datetime
            if isinstance(row['period'], datetime):
                # If it's a timezone-aware datetime, convert to naive
                row['period'] = row['period'].astimezone(self.timezone).replace(tzinfo=None)
            
            # Convert orders_by_status dict to separate columns
            if 'orders_by_status' in row:
                for status, count in row['orders_by_status'].items():
                    row[f'orders_{status}'] = count
                del row['orders_by_status']
            
            # Ensure all decimal values are converted to float
            for key in ['total_amount', 'discount', 'net_amount']:
                if key in row and isinstance(row[key], Decimal):
                    row[key] = float(row[key])
            
            excel_data.append(row)
        
        return excel_data

    def validate_order_data(self):
        """Check if OrderItems table has data and correct structure"""
        try:
            # Check if OrderItems model exists and has data
            sample_order = OrderItems.objects.first()
            if sample_order is None:
                logger.error("OrderItems table is empty")
                return False
            
            # Validate required fields exist
            required_fields = ['order', 'price', 'quantity']
            for field in required_fields:
                if not hasattr(sample_order, field):
                    logger.error(f"Missing required field in OrderItems: {field}")
                    return False
            
            logger.info("OrderItems data structure validated successfully")
            return True
        except Exception as e:
            logger.error(f"Error validating OrderItems data: {str(e)}")
            return False

    def get_date_range(self):
        report_type = self.request.GET.get('report_type', 'daily')
        
        # Get current time in Asia/Kolkata
        current_time = timezone.localtime(timezone.now(), self.timezone)
        today = current_time.date()
        
        logger.info(f"Current time in IST: {current_time}")
        logger.info(f"Getting date range for report type: {report_type}")
        
        try:
            if report_type == 'custom':
                start_date = self.request.GET.get('start_date')
                end_date = self.request.GET.get('end_date')
                if start_date and end_date:
                    start = datetime.strptime(start_date, '%Y-%m-%d').date()
                    end = datetime.strptime(end_date, '%Y-%m-%d').date() + timedelta(days=1)
                    return start, end
            
            # Calculate date range based on report type
            date_ranges = {
                'daily': (today - timedelta(days=1), today + timedelta(days=1)),
                'weekly': (today - timedelta(days=7), today + timedelta(days=1)),
                'monthly': (today.replace(day=1), (today + timedelta(days=1))),
                'yearly': (today.replace(month=1, day=1), today + timedelta(days=1))
            }
            
            date_range = date_ranges.get(report_type, (today, today + timedelta(days=1)))
            logger.info(f"Calculated date range: {date_range[0]} to {date_range[1]}")
            return date_range

        except Exception as e:
            logger.error(f"Error in get_date_range: {str(e)}")
            return today, today + timedelta(days=1)

    def get_sales_data(self, start_date, end_date):
        
        # Debug queries
        test_order = OrderItems.objects.first()
        if test_order:
            logger.info(f"Sample order date: {test_order.order.order_date}")
            logger.info(f"Sample order status: {test_order.order.order_status}")
        
        all_statuses = OrderItems.objects.values_list(
            'order__order_status', flat=True).distinct()
        logger.info(f"All order statuses in DB: {list(all_statuses)}")
        
        logger.info(f"Fetching sales data from {start_date} to {end_date}")
        
        try:
            # Convert dates to timezone-aware datetimes in IST
            start_datetime = timezone.make_aware(
                datetime.combine(start_date, datetime.min.time()),
                self.timezone
            )
            end_datetime = timezone.make_aware(
                datetime.combine(end_date, datetime.min.time()),
                self.timezone
            )
            
            logger.info(f"Query parameters - Start: {start_datetime}, End: {end_datetime}")
            
            # Base queryset with proper timezone handling
            base_queryset = OrderItems.objects.filter(
                order__order_date__gte=start_datetime,
                order__order_date__lt=end_datetime,
                order__order_status='delivered' 
            )
            
            # Get the appropriate truncation function
            trunc_func = self.get_trunc_function()
            
            # Aggregate sales data
            sales_data = base_queryset.annotate(
                period=trunc_func('order__order_date', tzinfo=self.timezone)
            ).values('period').annotate(
                orders=Count('order', distinct=True),
                total_amount=Coalesce(
                    Sum(F('price') * F('quantity')),
                    Decimal('0.00'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                ),
            ).order_by('period')
            
            # Get discount data
            discount_data = Checkout.objects.filter(
                updated_at__gte=start_datetime,
                updated_at__lt=end_datetime,
                checkout_status='completed'
            ).annotate(
                period=trunc_func('updated_at', tzinfo=self.timezone)
            ).values('period').annotate(
                total_discount=Coalesce(
                    Sum(F('coupons__discount_amount')),
                    Decimal('0.00'),
                    output_field=DecimalField(max_digits=10, decimal_places=2)
                )
            ).order_by('period')
            #printing discount amount
            for i in discount_data:
                print('############')
                print(i['total_discount'])
                print('############')
            # Combine sales and discount data
            discount_dict = {item['period']: item['total_discount'] for item in discount_data}
            processed_data = []
            
            for item in sales_data:
                period = item['period']
                period_discount = discount_dict.get(period, Decimal('0.00'))
                print(f' discount is = {period_discount}')
                processed_item = {
                    'period': period,
                    'orders': item['orders'],
                    'total_amount': item['total_amount'],
                    'discount': period_discount,
                    'net_amount': item['total_amount'] - period_discount
                }
                processed_data.append(processed_item)
                
                logger.debug(f"Processed record for {period}: {processed_item}")
            
            return processed_data

        except Exception as e:
            logger.error(f"Error in get_sales_data: {str(e)}", exc_info=True)
            return []

    def get_trunc_function(self):
        report_type = self.request.GET.get('report_type', 'daily')
        trunc_functions = {
            'daily': TruncDate,
            'weekly': TruncWeek,
            'monthly': TruncMonth,
            'yearly': TruncYear
        }
        return trunc_functions.get(report_type, TruncDate)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            start_date, end_date = self.get_date_range()
            sales_data = self.get_sales_data(start_date, end_date)
            
            context.update({
                'sales_data': sales_data,
                'report_type': self.request.GET.get('report_type', 'daily'),
                'start_date': start_date,
                'end_date': end_date - timedelta(days=1),
                'overall_stats': {
                    'total_orders': sum(item['orders'] for item in sales_data) if sales_data else 0,
                    'total_amount': sum(item['total_amount'] for item in sales_data) if sales_data else Decimal('0.00'),
                    'total_discount': sum(item['discount'] for item in sales_data) if sales_data else Decimal('0.00'),
                    'net_amount': sum(item['net_amount'] for item in sales_data) if sales_data else Decimal('0.00')
                }
            })
            
            return context
            
        except Exception as e:
            logger.error(f"Error in get_context_data: {str(e)}", exc_info=True)
            context.update({
                'error_message': 'An error occurred while generating the report.',
                'sales_data': [],
                'overall_stats': {
                    'total_orders': 0,
                    'total_amount': Decimal('0.00'),
                    'total_discount': Decimal('0.00'),
                    'net_amount': Decimal('0.00')
                }
            })
            return context
