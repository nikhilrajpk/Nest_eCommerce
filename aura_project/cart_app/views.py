from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product_app.models import *
from coupen_app.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

# Create your views here.

@login_required
def add_to_cart(request,product_id):
    # Getting the user and the product
    user = request.user
    product = get_object_or_404(Product, id = product_id)
    
    # Check the user has already a cart or create new cart
    cart, created = Cart.objects.get_or_create(user = user)
    
    # Check the products is already in the cart
    cart_item, item_created = Cart_item.objects.get_or_create(cart = cart, product = product, defaults={'quantity': 1})
    
    if not item_created:
        # If the product already exists, increment the quantity
        cart_item.quantity += 1

    cart_item.save()
    print(f"Cart item saved: {cart_item.product.product_name} with quantity {cart_item.quantity}")
        
    # request.session['coupon_applied'] = False  # Reset coupon status to recalculate discount
    # request.session['discount_amount'] = 0 
    
    return redirect('cart_app:cart')
    
@login_required
def cart_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user = request.user)
    cart_items = cart.items.all()  # Related name from Cart_item
    
    # List to hold the items that should stay in the cart
    filtered_cart_items = []
    
    # Loop through cart items and remove those that are not listed
    for item in cart_items:
        if not item.product.is_listed or not item.product.category.is_listed:
            item.delete()
        else:
            filtered_cart_items.append(item)
    
    
    cart_items_with_prices = []
    
    # Calculate the total price for each item
    for item in filtered_cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
            item.total_price = item.product.price * item.quantity
    
        cart_items_with_prices.append(item)
    
    # Calculate total cart value
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    request.session['cart_total'] = float(cart_total)

    # cart_total_with_discount = cart_total  

    # If a discount was already applied, recalculate the total with the discount
    # if request.session.get('coupon_applied', False):
    #     discount = request.session.get('discount_amount', 0)
    #     cart_total_with_discount = cart_total - Decimal(discount)
    #     request.session['cart_total'] = float(cart_total_with_discount)

      
    return render(request,'cart_app/cart.html',{
        'cart': cart,
        'cart_items': filtered_cart_items,
        'cart_total':cart_total,
    })

# def check_coupon(request):
#     cart_total = Decimal(request.session.get('cart_total',0))
    
#     if request.method == 'POST':
#         coupon_code = request.POST.get('coupon_code')
#         coupon_applied = request.session.get('coupon_applied')
#         if not coupon_applied:
#             print(coupon_code)
            
#             if coupon_code:
#                 coupon = get_object_or_404(Coupons, code = coupon_code)
#                 print(coupon)
                
#                 if coupon.used_limit > 0:
#                     print(coupon.used_limit)
#                     cart_total_discount = cart_total - coupon.discount_amount
                    
#                     print(cart_total_discount)
                    
#                     request.session['cart_total'] = float(cart_total_discount)
                    
#                     request.session['coupon_applied'] = True
#                     request.session['discount_amount'] = float(coupon.discount_amount)
                    
#                     messages.success(request,f'{coupon.code} applied successfully')
#                     return redirect('cart_app:cart')
#                 else:
#                     messages.error(request,f'{coupon.code} is no longer available or expired')
#                     return redirect('cart_app:cart')
        
                    
#     messages.error(request, 'Invalid coupon code.')
#     return redirect('cart_app:cart')


    

@login_required
def update_cart_item_quantity(request, product_id, action):
    # Getting the user and the product
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=user)

    # Get the cart item for the specified product
    cart_item = get_object_or_404(Cart_item, cart=cart, product=product)

    # Update quantity based on action
    if action == 'increment':
        cart_item.quantity += 1
    elif action == 'decrement':
        if cart_item.quantity > 1:  
            cart_item.quantity -= 1
        else:
            cart_item.delete()
            return redirect('cart_app:cart')
    
    cart_item.save()

    return redirect('cart_app:cart')

def remove_cart_item(request,cart_id):
    cart_item = Cart_item.objects.get(id = cart_id)
    cart_item.delete()
    
    return redirect('cart_app:cart')


def checkout(request,cart_id):
    user_email = request.user.email
    user = CustomUser.objects.get(email = user_email)
    cart = Cart.objects.get(id = cart_id)
    cart_items = cart.items.all()
    request.session['cart_id'] = cart_id
    
    cart_items_with_prices = []
    # Calculate the total price for each item
    for item in cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
            item.total_price = item.product.price * item.quantity
    
        cart_items_with_prices.append(item)
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    # Apply coupon discount if applicable
    discount = Decimal(request.session.get('discount_amount', 0))
    cart_total_with_discount = cart_total - discount

    
    request.session['cart_total'] = float(cart_total_with_discount)

    coupon_code = request.session.get('coupon_code', '')

    context = {
        'user':user,
        'cart_items':cart_items,
        'cart_total':cart_total,
        'cart_total_with_discount':cart_total_with_discount,
        'coupon_code':coupon_code,
    }
    return render(request,'cart_app/checkout.html',context)

# {% url 'checkout_app:process_order' %}

def check_coupon(request):
    cart_total = Decimal(request.session.get('cart_total', 0))

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        coupon_applied = request.session.get('coupon_applied', False)
        cart_id = request.session.get('cart_id')

        #  coupon removal
        if coupon_code == 'remove':
            request.session['coupon_applied'] = False
            request.session['discount_amount'] = 0
            request.session['coupon_code'] = ''
            messages.success(request, 'Coupon removed successfully.')
            return redirect('cart_app:checkout', cart_id=cart_id)

        # Apply coupon if not already applied
        if not coupon_applied:
            if coupon_code:
                coupon = get_object_or_404(Coupons, code=coupon_code)
                if coupon.used_limit > 0:
                    discount = Decimal(coupon.discount_amount)
                    cart_total_discount = cart_total - discount

                    request.session['cart_total'] = float(cart_total_discount)
                    request.session['coupon_applied'] = True
                    request.session['discount_amount'] = float(coupon.discount_amount)
                    request.session['coupon_code'] = coupon_code

                    messages.success(request, f'{coupon.code} applied successfully.')
                    return redirect('cart_app:checkout', cart_id=cart_id)
                else:
                    messages.error(request, f'{coupon.code} is no longer available or expired.')
                    return redirect('cart_app:checkout', cart_id=cart_id)

    messages.error(request, 'Invalid coupon code.')
    return redirect('cart_app:checkout', cart_id=cart_id)
