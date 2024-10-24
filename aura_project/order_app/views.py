from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from cart_app.models import *
from address_app.models import *
from authentication_app.models import *
from decimal import Decimal

# Create your views here.


@login_required
def confirm_order(request):
    
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.items.all()

    # Getting the address from the checkout page
    address_id = request.POST.get('address_id')
    print(address_id)
    address = user.addresses.get(id = address_id)
    print(address)
    
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

    context = {
        'cart_items': cart_items,
        'address': address,
        'cart_total': cart_total,
        'cart_total_with_discount': cart_total_with_discount,
        'payment_method': payment_method,
    }

    return render(request, 'order_app/order_confirmation.html', context)

# {% url 'order_app:place_order' %}