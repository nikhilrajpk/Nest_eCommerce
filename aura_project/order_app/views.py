from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from cart_app.models import *
from address_app.models import *
from authentication_app.models import *
from order_app.models import *
from decimal import Decimal
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone

# Create your views here.


# @login_required
# def confirm_order(request):
    
#     user = request.user
#     cart = Cart.objects.get(user=user)
#     cart_items = cart.items.all()

#     # Getting the address from the checkout page
#     address_id = request.POST.get('address_id')
#     print(address_id)
#     address = user.addresses.get(id = address_id)
#     print(address)
    
#     payment_method = request.POST.get('payment_method')
    
    
#     cart_items_with_prices = []
#     # Calculate the total price for each item
#     for item in cart_items:
#         if item.product.offer:
#             item.total_price = item.product.discount_price * item.quantity
#         else:
#             item.total_price = item.product.price * item.quantity
    
#         cart_items_with_prices.append(item)

#     # Get cart totals
#     cart_total = sum(item.total_price for item in cart_items)
#     discount = Decimal(request.session.get('discount_amount', 0))
#     cart_total_with_discount = cart_total - discount

#     coupon_code = request.POST.get('coupon_code', None)
#     print(coupon_code)
#     coupon = None
#     if coupon_code:
#         coupon = get_object_or_404(Coupons, code=coupon_code)

#     # Checking if the checkout already exist
#     checkout_exist = Checkout.objects.get(cart = cart)
    
#     if checkout_exist is None:
#         # Adding data of checkout to checkout database
#         checkout = Checkout(
#             cart = cart,
#             total_amount = cart_total_with_discount,
#             coupons = coupon,
#             address = address,
#             checkout_status = 'completed',
#         )
#         checkout.save()
#     else:
#         checkout_exist.cart = cart
#         checkout_exist.total_amount = cart_total_with_discount
#         checkout_exist.coupons = coupon
#         checkout_exist.address = address
        
#         checkout_exist.save()
    
#     context = {
#         'cart_items': cart_items,
#         'address': address,
#         'cart_total': cart_total,
#         'cart_total_with_discount': cart_total_with_discount,
#         'payment_method': payment_method,
#     }

#     return render(request, 'order_app/order_confirmation.html', context)

# {% url 'order_app:place_order' %}


@login_required
def confirm_order(request):
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.items.all()

    # Getting the address from the checkout page
    address_id = request.POST.get('address_id')
    address = get_object_or_404(Address, id=address_id, user=user)

    payment_method = request.POST.get('payment_method')

    cart_items_with_prices = []
    # Calculate the total price for each item
    for item in cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
            item.total_price = item.product.price * item.quantity
    
        cart_items_with_prices.append(item)

    # Get cart totals
    cart_total = sum(item.total_price for item in cart_items)
    discount = Decimal(request.session.get('discount_amount', 0))
    cart_total_with_discount = cart_total - discount

    # Get the coupon code from the request
    coupon_code = request.session.get('coupon_code', '')
    print(coupon_code)
    coupon = None
    if coupon_code:
        try:
            coupon = Coupons.objects.get(code=coupon_code)
        except Coupons.DoesNotExist:
            coupon = None
            messages.error(request, "Coupon not found or expired.")
    
    # Check if a Checkout already exists
    checkout_exist = Checkout.objects.filter(cart=cart).first()
    
    if not checkout_exist:
        # Adding data to checkout if it doesn't exist
        checkout = Checkout(
            cart=cart,
            total_amount=cart_total_with_discount,
            coupons=coupon,  # Assign the coupon object
            address=address,
            checkout_status='completed',
        )
        checkout.save()
    else:
        # Update the existing checkout
        checkout_exist.cart = cart
        checkout_exist.total_amount = cart_total_with_discount
        checkout_exist.coupons = coupon  # Assign the coupon object
        checkout_exist.address = address
        checkout_exist.checkout_status = 'completed'
        checkout_exist.save()

    context = {
        'cart_items': cart_items,
        'address': address,
        'cart_total': cart_total,
        'cart_total_with_discount': cart_total_with_discount,
        'payment_method': payment_method,
    }

    return render(request, 'order_app/order_confirmation.html', context)


def order_view(request):
    if request.method == 'POST':
        user_id = request.user.id
        user = CustomUser.objects.get(id = user_id)
        cart = Cart.objects.get(user = user) # Getting the cart for the user
        cart_item = cart.items.all()    # Getting all cart items for the cart
        
        delivery_date = timezone.now() + timedelta(days=7)
        
        # Creating and saving the order
        order = Order(
            user = user,
            order_status = 'confirmed',
            delivery_date = delivery_date
        )
        
        order.save()
        
        for item in cart_item:
            OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.quantity * Decimal(item.product.price)
            )
    user_id = request.user.id
    user = CustomUser.objects.get(id = user_id)
    orders = user.orders.all()
    context = {
        'orders':orders,
    }
    return render(request,'order_app/orders.html',context)

# {% url 'order_details' order.id %}