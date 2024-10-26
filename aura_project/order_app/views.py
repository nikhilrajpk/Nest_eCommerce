from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from cart_app.models import *
from address_app.models import *
from authentication_app.models import *
from order_app.models import *
from product_app.models import *
from decimal import Decimal
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.db.models import F

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
    request.session['address_id'] = address_id
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
            coupon.used_limit = F('used_limit') - 1
            coupon.save()
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

@login_required
def order_view(request):
    if request.method == 'POST':
        user_id = request.user.id
        user = CustomUser.objects.get(id = user_id)
        cart = Cart.objects.get(user = user) # Getting the cart for the user
        cart_item = cart.items.all()    # Getting all cart items for the cart
        
        delivery_date = timezone.now() + timedelta(days=7)
        
        address_id = request.session.get('address_id')
        address = Address.objects.get(id = address_id)
        # Creating and saving the order
        order = Order(
            user = user,
            order_status = 'confirmed',
            delivery_date = delivery_date,
            address = address
        )
        
        order.save()
        
        # Creating order items for the items from cart.
        for item in cart_item:
            OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.quantity * Decimal(item.product.price)
            )
            # Reducing the available stock
            item.product.available_stock = F('available_stock') - item.quantity
            item.product.save()
            
            # Unlist the product if stock becomes 0
            if item.product.available_stock == 0:
                item.product.is_listed = False
                item.product.save()
            
        cart_item.delete()
        return redirect('order_app:order_view')
            
            
    orders = request.user.orders.all().order_by('-id')
    context = {
        'orders':orders,
    }
    return render(request,'order_app/orders.html',context)

# {% url 'order_details' order.id %}


@login_required
def order_details(request,order_id):
    order = Order.objects.get(id = order_id)
    request.session['order_id'] = order_id
    order_items = order.items.all()
    total_price = 0
    for item in order_items:
        if item.product.offer:
            total_price += item.product.discount_price
        else:
            total_price += item.price
        
    context = {
        'order':order,
        'total_price':total_price,
    }
    
    return render(request,'order_app/order_details.html',context)

@login_required
def submit_review(request, product_id):
    order_id = request.session.get('order_id')
    if request.method == 'POST':
        rating = int(request.POST.get('rating'))
        comment = request.POST.get('review')
        
        product = get_object_or_404(Product, id=product_id)
        
        # Save the review
        review = ProductReview(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )
        review.save()

        
        messages.success(request, "Thank you for your review!")
        return redirect('order_app:order_details', order_id=order_id)

    order_items = OrderItems.objects.filter(product_id=product_id, order__user=request.user)[:1]
    
    if not order_items.exists():
        messages.error(request, "Order item does not exist.")
        return redirect('order_app:order_details', order_id=order_id)
    
    return render(request,'order_app/add_review.html',{'order_items':order_items})

# {% url 'return_item' item.id %}
# {% url 'cancel_order' order.id %}
# {% url 'submit_review' order.id %}


@login_required
def cancel_order(request, order_id):
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        
        # Get cancellation reason from form
        cancel_reason = request.POST.get('cancel_reason')
        
        if cancel_reason:
            order.order_status = 'canceled'
            order.cancellation_reason = cancel_reason 
            
            # If order canceled then available stock is recalculated
            order_items = order.items.all()
            for item in order_items:
                item.product.available_stock = F('available_stock') + item.quantity
                item.product.save()
            order.save()

            messages.success(request, "Order canceled successfully.")
        else:
            messages.error(request, "Cancellation reason is required.")
    
    return redirect('order_app:order_details', order_id=order_id)
