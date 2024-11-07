from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product_app.models import *
from coupen_app.models import *
from wallet_app.models import *
from order_app.models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from decimal import Decimal

# Create your views here.
from django.http import JsonResponse

@login_required
def add_to_cart(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse({'redirect_url': 'admin_app:admin_home'})
    if request.user.is_authenticated and request.user.is_block:
        return JsonResponse({'redirect_url': 'authentication_app:logout'})

    user = request.user
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=user)
    cart_item, item_created = Cart_item.objects.get_or_create(cart=cart, product=product, defaults={'quantity': 1})

    if not item_created:
        cart_item.quantity += 1
    cart_item.total_price = cart_item.quantity * (product.discount_price if product.offer else product.price)
    cart_item.save()
    
    return JsonResponse({
        'status': 'success',
        'message': 'Product added to cart',
        'quantity': cart_item.quantity
    })

    


@login_required
def cart_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    
    # List to hold the items that should stay in the cart
    filtered_cart_items = []
    
    # Loop through cart items and remove those that are not listed
    for item in cart_items:
        if not item.product.is_listed or not item.product.category.is_listed:
            item.delete()
        else:
            # Check if quantity exceeds available stock
            if item.quantity > item.product.available_stock:
                item.quantity = item.product.available_stock
                item.save()
                messages.warning(request, f'Quantity for {item.product.product_name} has been adjusted to match available stock ({item.product.stock}).')
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
    
    return render(request, 'cart_app/cart.html', {
        'cart': cart,
        'cart_items': filtered_cart_items,
        'cart_total': cart_total,
    })

@login_required
def update_cart_item_quantity(request, product_id, action):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user=user)
    
    # Get the cart item for the specified product
    cart_item = get_object_or_404(Cart_item, cart=cart, product=product)
    
    # Update quantity based on action
    if action == 'increment':
        # Check if incrementing would exceed available stock
        if cart_item.quantity >= product.available_stock:
            messages.error(request, f'Cannot add more {product.product_name}. Maximum available stock ({product.available_stock}) reached.')
            return redirect('cart_app:cart')
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
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    cart_item = Cart_item.objects.get(id = cart_id)
    cart_item.delete()
    
    return redirect('cart_app:cart')


def checkout(request,cart_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
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
    cart_total_with_discount = float(cart_total) - float(discount)

    
    request.session['cart_total'] = float(cart_total_with_discount)

    coupon_code = request.session.get('coupon_code', '')
    
     # Wallet payment
    wallet,created = Wallet.objects.get_or_create(user = user)
    wallet_balance = wallet.balance
        
    
    context = {
        'user':user,
        'cart_items':cart_items,
        'cart_total':cart_total,
        'cart_total_with_discount':cart_total_with_discount,
        'coupon_code':coupon_code,
        'wallet_balance':wallet_balance,
    }
    return render(request,'cart_app/checkout.html',context)

# {% url 'checkout_app:process_order' %}

def check_coupon(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    cart_total = Decimal(request.session.get('cart_total', 0))

    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        coupon_applied = request.session.get('coupon_applied', False)
        cart_id = request.session.get('cart_id')
        cart = Cart.objects.get(id=cart_id)
        checkout = Checkout.objects.filter(cart=cart)
        
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
                
                for c in checkout:
                    if coupon == c.coupons:
                        messages.error(request,'You already applied this coupon ones. Cannot use again!')
                        return redirect('cart_app:checkout', cart_id=cart_id)
                
                if coupon.used_limit < 0:
                    coupon.update(used_limit=0)
                if coupon.used_limit > 0 and coupon.expiry_date > timezone.now():
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