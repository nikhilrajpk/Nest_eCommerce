from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product_app.models import *
from django.contrib.auth.decorators import login_required

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
        
    return redirect('cart_app:cart')
    
@login_required
def cart_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    
    # Get the user's cart
    cart, created = Cart.objects.get_or_create(user = request.user)
    cart_items = cart.items.all()  # Related name from Cart_item
    
    
    cart_items_with_prices = []
    
    # Calculate the total price for each item
    for item in cart_items:
        if item.product.offer:
            item.total_price = item.product.discount_price * item.quantity
        else:
            item.total_price = item.product.price * item.quantity
    
        cart_items_with_prices.append(item)
    
    # Calculate total cart value
    cart_total = sum(item.total_price for item in cart_items_with_prices)
    
    return render(request,'cart_app/cart.html',{
        'cart': cart,
        'cart_items': cart_items,
        'cart_total':cart_total,
    })
    

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