from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from cart_app.models import *
from address_app.models import *
from authentication_app.models import *
from order_app.models import *
from product_app.models import *
from wallet_app.models import *
from decimal import Decimal
from django.contrib import messages
from datetime import timedelta
from django.utils import timezone
from django.db.models import F
import razorpay
from django.conf import settings

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
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    user = request.user
    cart = Cart.objects.get(user=user)
    cart_items = cart.items.all()

    if request.method == 'POST':
        # Getting the address from the checkout page
        address_id = request.POST.get('address_id')
        request.session['address_id'] = address_id
        address = get_object_or_404(Address, id=address_id, user=user)

        payment_method = request.POST.get('payment_method')
        request.session['payment_method'] = payment_method
    
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
    cart_total_with_discount = float(cart_total) - float(discount)
    request.session['cart_total_with_discount'] = cart_total_with_discount
    
    print(request.session['cart_total_with_discount'])
    
    # # Get the coupon code from the request
    # coupon_code = request.session.get('coupon_code', '')
    # print(coupon_code)
    # coupon = None
    # if coupon_code:
    #     try:
    #         coupon = Coupons.objects.get(code=coupon_code)
    #         coupon.used_limit = F('used_limit') - 1
    #         cart_total_with_discount -= float(coupon.discount_amount)
    #         coupon.save()
    #     except Coupons.DoesNotExist:
    #         coupon = None
    #         messages.error(request, "Coupon not found or expired.")
    
    # # Check if a Checkout already exists
    # checkout_exist = Checkout.objects.filter(cart=cart).first()
    
    # if not checkout_exist:
    #     # Adding data to checkout if it doesn't exist
    #     checkout = Checkout(
    #         cart=cart,
    #         total_amount=cart_total_with_discount,
    #         coupons=coupon,  # Assign the coupon object
    #         address=address,
    #         checkout_status='completed',
    #     )
    #     checkout.save()
    # else:
    #     # Update the existing checkout
    #     checkout_exist.cart = cart
    #     checkout_exist.total_amount = cart_total_with_discount
    #     checkout_exist.coupons = coupon  # Assign the coupon object
    #     checkout_exist.address = address
    #     checkout_exist.checkout_status = 'completed'
    #     checkout_exist.save()

    context = {
        'cart_id':cart.id,
        'cart_items': cart_items,
        'address': address,
        'cart_total': float(cart_total),
        'cart_total_with_discount': cart_total_with_discount,
        'payment_method': payment_method,
    }    
    
    # Wallet payment
    wallet,created = Wallet.objects.get_or_create(user=user)
    wallet_balance = float(wallet.balance)
    
    if payment_method == 'wallet':
        
        if cart_total_with_discount > wallet_balance:
            messages.error(request,'Insufficient balance in wallet!')
            return redirect('cart_app:checkout',cart_id=cart.id)
    
    # Razor pay ******************************
    elif payment_method == 'razorpay':
    
        client = razorpay.Client(auth=(settings.KEY, settings.SECRET))

        data = { "amount": cart_total_with_discount * 100, "currency": "INR", "payment_capture": 1, "receipt": "order_rcptid_11" }
        payment = client.order.create(data=data)        
        request.session['razor_payment'] = payment
        # ***************
        print(payment)
        #****************
        context['payment'] = payment
    else:
        pass
        
    return render(request, 'order_app/order_confirmation.html', context)

@login_required
def order_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
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
            # product price if it has offer or not.
            item_price = 0
            if item.product.offer:
                item_price = item.product.discount_price
            else:
                item_price = item.product.price
                
                
            OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.quantity * Decimal(item_price)
            )
            # Reducing the available stock
            item.product.available_stock = F('available_stock') - item.quantity
            item.product.sold_count = F('sold_count') + item.quantity
            item.product.save()
            
            # Unlist the product if stock becomes 0
            if item.product.available_stock == 0:
                item.product.is_listed = False
                item.product.save()
            
        cart_item.delete()
        # Wallet balance and walletTransaction details
        cart_total_with_discount = request.session.get('cart_total_with_discount')
        payment_method = request.POST.get('payment_method')
        if payment_method == 'wallet':
            wallet = get_object_or_404(Wallet,user=user)
            
            wallet.balance = float(wallet.balance) - cart_total_with_discount
            wallet.save()
            
            print(cart_total_with_discount)
            print(wallet.balance)
            
            wallet_transaction = WalletTransation.objects.create(
                wallet = wallet,
                transaction_type = 'debited',
                amount = cart_total_with_discount,
            )
        elif payment_method == 'razorpay':
            payment_id = request.session.get('razor_payment')
            payment_obj = Payment.objects.create(
                order = order,
                total_price = cart_total_with_discount,
                payment_method = 'razorpay',
                razor_pay_order_id = payment_id['id'],
                
            )
            
        # Get the coupon code from the request
        coupon_code = request.session.get('coupon_code', '')
        print(coupon_code)
        coupon = None
        if coupon_code:
            try:
                coupon = Coupons.objects.get(code=coupon_code)
                coupon.used_limit = F('used_limit') - 1
                cart_total_with_discount -= float(coupon.discount_amount)
                coupon.save()
            except Coupons.DoesNotExist:
                coupon = None
                messages.error(request, "Coupon not found or expired.")
        
        # Check if a Checkout already exists
        checkout_exist = Checkout.objects.filter(cart=cart).first()
        
        if not checkout_exist:
            print(checkout_exist.id,checkout_exist.cart_id)
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
            print("Existing checkout updated with new values.")
            
        return redirect('order_app:order_view')

    
    orders = request.user.orders.all().order_by('-id')
    context = {
        'orders':orders,
    }
    return render(request,'order_app/orders.html',context)

# Razor pay method
# import razorpay
# from django.conf import settings
# def razor_pay(request,amount):
#     client = razorpay.Client(auth=(settings.razor_pay_key, settings.razor_pay_secret))

#     data = { "amount": amount, "currency": "INR", "receipt": "order_rcptid_11" }
#     payment = client.order.create(data=data)


@login_required
def order_details(request,order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    order = Order.objects.get(id = order_id)
    payment_method = request.session.get('payment_method')
    print(payment_method)
    request.session['order_id'] = order_id
    order_items = order.items.all()
    total_price = 0
    for item in order_items:
        if item.product.offer:
            total_price += item.product.discount_price * item.quantity
        else:
            total_price += item.price * item.quantity
    
    
    # Get the coupon code from the request
    coupon_code = request.session.get('coupon_code', '')
    print(coupon_code)
    coupon = None
    if coupon_code:
        try:
            coupon = Coupons.objects.get(code=coupon_code)
            total_price = float(total_price) - float(coupon.discount_amount)
        except Coupons.DoesNotExist:
            coupon = None
            messages.error(request, "Coupon not found or expired.")
        
        
    context = {
        'order':order,
        'total_price':total_price,
        'payment_method':payment_method,
    }
    
    return render(request,'order_app/order_details.html',context)

@login_required
def submit_review(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
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
    
    return render(request,'order_app/add_review.html',{'order_items':order_items,'order_id':order_id})

# {% url 'return_item' item.id %}
# {% url 'cancel_order' order.id %}
# {% url 'submit_review' order.id %}


@login_required
def cancel_order(request, order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        
        # Get cancellation reason from form
        cancel_reason = request.POST.get('cancel_reason')
        
        if cancel_reason:
            order.order_status = 'canceled'
            order.cancellation_reason = cancel_reason 
            
            # If order canceled then available stock is recalculated
            order_items = order.items.all()
            total_price = 0
            for item in order_items:
                item.product.available_stock = F('available_stock') + item.quantity
                item.product.save()
                total_price += item.price * item.quantity
            order.save()
            
            # Adding money to wallet when cancelling the order.
            
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance = F('balance') + total_price
            wallet.save()
            print(wallet.balance)
            
            wallet_transaction = WalletTransation.objects.create(
                wallet = wallet,
                transaction_type = 'cancellation',
                amount = total_price,
            )

            messages.success(request, "Order canceled successfully.")
        else:
            messages.error(request, "Cancellation reason is required.")
    
    return redirect('order_app:order_details', order_id=order_id)


@login_required
def return_item(request, item_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    if request.method == 'POST':
        order_item = OrderItems.objects.get(id=item_id)
        
        # Get return item reason from form
        return_reason = request.POST.get('return_reason')
        if return_reason:
            order_item.return_reason = return_reason
            order_item.return_date = timezone.now()
            order_item.save()
            
            # Adding money to wallet when returning the item.
            total_price = order_item.price * order_item.quantity
            print(order_item.price,order_item.quantity)
            print(total_price)
            wallet = Wallet.objects.get(user=request.user)
            wallet.balance = F('balance') + total_price
            wallet.save()
            print(wallet.balance)
            
            wallet_transaction = WalletTransation.objects.create(
                wallet = wallet,
                transaction_type = 'refund',
                amount = total_price,
            )

            messages.success(request, "Order item returned successfully.")
        else:
            messages.error(request, "Return reason is required.")
    
    return redirect('order_app:order_details', order_id=order_item.order.id)
