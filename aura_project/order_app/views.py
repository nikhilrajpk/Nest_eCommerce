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
from django.db.models import F, Count
import razorpay
from django.conf import settings

# Create your views here.


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
        
        order_id = request.POST.get('order_id')
        
        discount = request.POST.get('discount',0)
        coupon_code = request.POST.get('coupon_code',None)
        print('discount amount of coupon if applied . confirm order line 42',discount)
        print('coupon_code  applied . confirm order line 42:',coupon_code)
        
        if request.POST.get('payment_retry') == 1:
            order = Order.objects.get(id = order_id)
            code = order.checkout.coupons.code
            discount_amount = order.checkout.coupons.discount_amount
    
    cart_items_with_prices = []
    # Calculate the total price for each item
    for item in cart_items:
        # checking if item and category is listed
        if not item.product.is_listed or not item.product.category.is_listed:
            # Set SweetAlert message in session
            request.session['swal_message'] = f"{item.product.product_name} is unavailable now. You need to remove it to proceed."
            request.session['swal_icon'] = "error"
            return redirect('cart_app:cart')
        else:
            # removing offers if it expires 
            if item.product.offer and item.product.offer.end_date < timezone.now():
                messages.error(request,f'Offer {item.product.offer.offer_title} is expired.')
                item.product.offer = None
                item.product.category.offer = None
                item.save()
                
            # Check if quantity exceeds available stock
            if item.quantity > item.product.available_stock:
                item.quantity = item.product.available_stock
                item.save()
                messages.warning(request, f'Quantity for {item.product.product_name} has been adjusted to match available stock ({item.product.available_stock}).')
                
            if item.product.offer:
                item.total_price = item.product.discount_price * item.quantity
            else:
                item.total_price = item.product.price * item.quantity
        
            cart_items_with_prices.append(item)

    # Get cart totals
    cart_total = sum(item.total_price for item in cart_items)
    cart_total_with_discount = float(cart_total) - float(discount)
    cart_total_with_discount += float(50)
    
    if cart_total_with_discount == 50:
        total_amount = request.POST.get('total_amount')
        cart_total_with_discount = total_amount
        print(cart_total_with_discount,'this is when retrying payment*********** line 90 cofirm order')
        
    request.session['cart_total_with_discount'] = cart_total_with_discount
    print('from confirm order line 93.  session cart_total_with_discount=',request.session['cart_total_with_discount'])
    
    context = {
        'cart_id':cart.id,
        'cart_items': cart_items,
        'address': address,
        'cart_total': float(cart_total),
        'cart_total_with_discount': cart_total_with_discount,
        'payment_method': payment_method,
        'order_id':order_id,
        'discount':discount,
        'coupon_code':coupon_code,
    }    
    
    if request.POST.get('payment_retry') == 1:
        context['discount'] = discount_amount
        context['coupon_code'] = code
    
    # Wallet payment
    wallet,created = Wallet.objects.get_or_create(user=user)
    wallet_balance = float(wallet.balance)
    
    if payment_method == 'wallet':
        
        if cart_total_with_discount > wallet_balance:
            messages.error(request,'Insufficient balance in wallet!')
            # Set SweetAlert message in session
            request.session['swal_message'] = f"Insufficient balance in wallet!"
            request.session['swal_icon'] = "error"
            return redirect('cart_app:checkout',cart_id=cart.id)
    
    # Razor pay ******************************
    elif payment_method == 'razorpay':
        try:
            client = razorpay.Client(auth=(settings.KEY, settings.SECRET))
            amount_in_paise = int(float(cart_total_with_discount) * 100)
            data = { "amount": amount_in_paise, "currency": "INR", "payment_capture": 1, "receipt": "order_rcptid_11" }
            payment = client.order.create(data=data)        
            request.session['razor_payment'] = payment
            # ***************
            print('razorpay payment details on line 133 : ',payment)
            #****************
            context['payment'] = payment
            context['payment_retry'] = request.POST.get('payment_retry')
            print('first continue payment value line 137 :',context['payment_retry'])
        except Exception as e:
            messages.error(request,'Razor pay server is currently down.',e)
    else:
        pass
        
    return render(request, 'order_app/order_confirmation.html', context)

@login_required
def order_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    orders = request.user.orders.all().order_by('-id')
    context = {
        'orders':orders,
    }
    if request.method == 'POST':
        user_id = request.user.id
        user = CustomUser.objects.get(id = user_id)
        cart = Cart.objects.get(user = user) # Getting the cart for the user
        cart_item = cart.items.all()    # Getting all cart items for the cart
           
        delivery_date = timezone.now() + timedelta(days=7)
        
        address_id = request.session.get('address_id')
        address = Address.objects.get(id = address_id)
        
        discount = request.POST.get('discount',0)
        coupon_code = request.POST.get('coupon_code',None)
        print('discount amount getting on : order view line 156 : ', discount)
        print('coupon_code getting on : order view line 157 : ', coupon_code)
        
        
        # Creating and saving the order
        order_obj = None
        if request.POST.get('payment_retry') == '1':
                order_id = request.POST.get('order_id')
                order_obj = Order.objects.get(id = order_id)
        if not order_obj:
            order = Order(
                user = user,
                order_status = 'confirmed',
                delivery_date = delivery_date,
                address = address
            )
            
            order.save()
            
            #creating orderAddress 
            OrderAddress.objects.create(
                order = order,
                address = address,
                country = address.country,
                street_address = address.street_address,
                state = address.state,
                landmark = address.landmark,
                postal_code = address.postal_code,
                phone = address.phone,
                alternative_phone = address.alternative_phone,
                address_field = address.address,
                address_type = address.get_address_type_display(),
            )
        total_price = 50
        # Creating order items for the items from cart.
        for item in cart_item:
            # product price if it has offer or not.
            item_price = 0                                      #######***********change needed************
            if item.product.offer:
                item_price = item.product.discount_price
            else:
                item_price = item.product.price
                
                
            order_items = OrderItems.objects.create(
                order = order,
                product = item.product,
                quantity = item.quantity,
                price = item.product.price,
                discount_price = item.product.discount_price,
                total_price = item.quantity * Decimal(item_price),
            )
            
            
            # calculating total order price
            if item.product.offer:
                total_price += item.product.discount_price * item.quantity          
            else:
                total_price += item.product.price * item.quantity
            
            
            
            # order.total_price = total_price
            print('order_total saving in order table is :',total_price, 'from order view line 206')
            
            
            
            # Reducing the available stock
            item.product.available_stock = F('available_stock') - item.quantity
            item.product.sold_count = F('sold_count') + item.quantity
            item.product.save()
            
            # Unlist the product if stock becomes 0
            if item.product.available_stock == 0:
                item.product.is_listed = False
                item.product.save()
        
        # if discount is applied on order, total price for order is calculated.  
        if not order_obj:      
            if discount:
                order.total_price = Decimal(total_price) - Decimal(discount)
            else:
                order.total_price = Decimal(total_price)
            order.save()
        else:
            order_obj.total_price = Decimal(order_obj.total_price)
            order_obj.save()
            
            
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
            payment_obj = Payment.objects.create(
                order = order,
                total_price = cart_total_with_discount,
                payment_method = 'wallet',  
                payment_status = 'success',     
            )
        elif payment_method == 'razorpay':
            payment_id = request.session.get('razor_payment')
            payment_status = request.POST.get('payment_status','success')
            print('payment status is :',payment_status)
            print(request.POST.get('payment_retry'),"payment retry on order view line 269")
            
            if payment_status == 'failed' and request.POST.get('payment_retry') != '1':
                order.order_status = 'pending'
                order.save()
                
                messages.error(request,'Payment is failed! You can continue the payment from here :)')
            elif request.POST.get('payment_retry') == '1' and payment_status == 'failed':
                print('payment failed 2nd time of order line 262:',order_id,request.POST.get('payment_failed'),)    
                messages.error(request,'Your order is canceled because payment failure!')
                order_obj.order_status = 'canceled'
                order_obj.save()
            
            # When retrying payment    
            if request.POST.get('payment_retry') == '1' and payment_status == 'success':
                # order_id = request.POST.get('order_id')
                # order_obj = Order.objects.get(id = order_id)
                payment_obj = Payment.objects.get(order = order_obj)
                payment_obj.payment_status = 'success'
                payment_obj.razor_pay_order_id = payment_id['id']
                payment_obj.save()
                order_obj.order_status = 'confirmed'
                order_obj.save()
            elif request.POST.get('payment_retry') != '1':
                payment_obj = Payment.objects.create(
                    order = order,
                    total_price = cart_total_with_discount,
                    payment_method = 'razorpay',
                    razor_pay_order_id = payment_id['id'],
                    payment_status = payment_status,
                )
        else:
            payment_obj = Payment.objects.create(
                order = order,
                total_price = cart_total_with_discount,
                payment_method = 'cod', 
                payment_status = 'success',       
            )
            
        # Get the coupon code from the request
        coupon = None
        if coupon_code:
            try:
                coupon = Coupons.objects.get(code=coupon_code)
                print(coupon.used_limit)
                coupon.used_limit = F('used_limit') - 1
                print('after',coupon.used_limit)
                cart_total_with_discount -= float(coupon.discount_amount)
                coupon.save()
            except Coupons.DoesNotExist:
                coupon = None
                if request.POST.get('payment_retry') == 1:
                    messages.error(request, "Coupon not found or expired.")
        
        if not order_obj:
            # Adding data to checkout
            checkout = Checkout(
                order=order,
                cart=cart,
                total_amount=cart_total_with_discount,
                coupons=coupon,  # Assign the coupon object
                address=address,
                checkout_status='completed',
            )
            checkout.save()
        
        # Removing coupon from checkout page 
        request.session['coupon_applied'] = False
        
        
        
            
        return redirect('order_app:order_view')

    
    return render(request,'order_app/orders.html',context)



@login_required
def order_details(request,order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    try:
        order = Order.objects.get(id = order_id)
    except Exception as e:
        messages.error(request,'Order details is not available. ')
        return redirect('order_app:order_view')
    
    if request.user != order.user:
        return redirect('authentication_app:logout')
        
    try:
        payment = Payment.objects.get(order = order)
        if payment:
            payment_method = payment.payment_method
            print(payment_method)
    except Exception as e:
            payment_method = 'COD'
            
    request.session['order_id'] = order_id
    order_items = order.items.all()
    total_price = order.total_price
    # for item in order_items:
    #     if item.product.offer:
    #         total_price += item.product.discount_price * item.quantity          ######**********
    #     else:
    #         total_price += item.price * item.quantity
    
    # total_price += 50
    # Get the coupon code from the request
    # coupon_code = request.session.get('coupon_code', '')
    coupon_discount = 0
    coupon_code = None
    try:
        coupon_code = order.checkout.coupons.code
        print('coupon code getting from order details line 369:',coupon_code)
        coupon = None
        if coupon_code:
            try:
                coupon = Coupons.objects.get(code=coupon_code)
                total_price = float(total_price) - float(coupon.discount_amount)
                coupon_discount = coupon.discount_amount
                request.session['discount_amount'] = 0
                request.session['coupon_code'] = ''
            except Coupons.DoesNotExist:
                coupon = None
                messages.error(request, "Coupon not found or expired.")
    except Exception as e:
        print('coupon does not exist on order details line 416',e)
        
    address = order.orderAddress.first()    
    context = {
        'order':order,
        'total_price':total_price,
        'payment_method':payment_method,
        'coupon_discount':coupon_discount,
        'coupon_code':coupon_code,
        'a':address,
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




@login_required
def cancel_order(request, order_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    if request.method == 'POST':
        order = Order.objects.get(id=order_id)
        if request.user != order.user:
            return redirect('authentication_app:logout')
        
        # If order is done by COD then in cancel order money should not be credited to the wallet.
        try:
            payment = Payment.objects.get(order = order)
            payment_method = payment.payment_method
        except Exception as e:
            payment_method = 'cod'
        
        # Get cancellation reason from form
        cancel_reason = request.POST.get('cancel_reason')
        
        if cancel_reason:
            order.order_status = 'canceled'
            order.cancellation_reason = cancel_reason 
            
            # If order canceled then available stock is recalculated
            order_items = order.items.all()
            total_price = order.total_price
            for item in order_items:
                item.product.available_stock = F('available_stock') + item.quantity
                item.product.save()
            order.save()
            
            # Adding money to wallet when cancelling the order.
            if not payment_method=='cod':
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
            

            messages.success(request, "Return request sent.")
        else:
            messages.error(request, "Return reason is required.")
    
    return redirect('order_app:order_details', order_id=order_item.order.id)

def return_confirm(request,item_id,order_id):
    # if request.user.is_authenticated and request.user.is_staff:
    #     return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    if request.method == 'POST':
        order_item = OrderItems.objects.get(id=item_id)
        
        # Adding money to wallet when returning the item.
        total_price = order_item.total_price
        print('total price of order item from return confirm line 557: ',total_price)
        
        # getting the user of the order.
        order = Order.objects.get(id = order_id)
        user_id = order.user.id
        user = CustomUser.objects.get(id=user_id)
        
        coupon_discount = 0
        coupon_code = None
        try:
            coupon_code = order.checkout.coupons.code
            print('coupon code getting from return confirm line 568:',coupon_code)
            coupon = None
            if coupon_code:
                try:
                    coupon = Coupons.objects.get(code=coupon_code)
                    coupon_discount = coupon.discount_amount
                except Coupons.DoesNotExist:
                    coupon = None
                    messages.error(request, "Coupon not found or expired.")
        except Exception as e:
            print('coupon does not exist on return confirm line 579',e)
        
        if coupon_code:
            item_count = order.items.count()
            if item_count:
                amount = coupon_discount / item_count
                shipping_amount = float(50) / item_count
                total_price = float(total_price) - float(amount) + float(shipping_amount)
        
        wallet,created = Wallet.objects.get_or_create(user=user)
        wallet.balance = F('balance') + total_price
        wallet.save()
        print('wallet balance after returning the order item line 566 : ',wallet.balance)
        
        wallet_transaction = WalletTransation.objects.create(
            wallet = wallet,
            transaction_type = 'refund',
            amount = total_price,
        )
        
        order_item.return_status = 'returned'
        order_item.save()
        
        return redirect('admin_app:show_order',order_id=order_id)
    else:
        return redirect('admin_app:show_order',order_id=order_id)
    
    
    
    
import weasyprint
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
import os

@login_required
def download_invoice_pdf(request, order_id):
    # Get order details
    order = Order.objects.get(id=order_id, user=request.user)
    order_items = order.items.all()

    try:
        payment = Payment.objects.get(order = order)
        if payment:
            payment_method = payment.payment_method
            print(payment_method)
    except Exception as e:
            payment_method = 'cod'
            
    # Calculate total price as in your order_details view
    total_price = order.total_price
    # for item in order_items:
    #     if item.product.offer:
    #         item_price = item.product.discount_price * item.quantity
    #     else:
    #         item_price = item.price * item.quantity
    #     total_price += item_price
    # total_price += 50

    address = order.orderAddress.first()
    
    # Get coupon and discount amount if any
    coupon_discount = 0
    coupon_code = None
    try:
        coupon_code = order.checkout.coupons.code
        print('coupon code getting from download invoice  line 619:',coupon_code)
        coupon = None
        if coupon_code:
            try:
                coupon = Coupons.objects.get(code=coupon_code)
                total_price = float(total_price) - float(coupon.discount_amount)
                coupon_discount = coupon.discount_amount
            except Coupons.DoesNotExist:
                coupon = None
                messages.error(request, "Coupon not found or expired.")
    except Exception as e:
        print('coupon does not exist on order details line 388',e)
        
    # Context for rendering the PDF template
    sub_total = order.total_price-50 + coupon_discount
    context = {
        'order': order,
        'order_items': order_items,
        'total_price': total_price,
        'coupon_discount': coupon_discount,
        'payment_method':payment_method,
        'sub_total':sub_total,
        'address':address,
        'coupon_discount':coupon_discount,
        'coupon_code':coupon_code,
    }

    # Render the template to HTML
    html = render_to_string('order_app/invoice_template.html', context)

    # Convert HTML to PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order_id}.pdf"'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response)

    return response
