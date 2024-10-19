from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product_app.models import *
from django.contrib.auth.decorators import login_required
# Create your views here.

@login_required
def add_to_wishlist(request, product_id):
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the user already has a wishlist or create a new one
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    
    # Check if the product is already in the wishlist
    wishlist_item, item_created = Wishlist_items.objects.get_or_create(wishlist=wishlist, product=product)
    
    if not item_created:
        # If the product already exists
        pass
    
    return redirect('wishlist_app:wishlist')

@login_required
def wishlist_view(request):
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    wishlist_items = wishlist.wishlist_items_set.all()  # Access the related Wishlist_items
    
    return render(request, 'wishlist_app/wishlist.html', {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    })

@login_required
def remove_from_wishlist(request, wishlist_id):
    wishlist_item = Wishlist_items.objects.get(id = wishlist_id)
    wishlist_item.delete()
    
    return redirect('wishlist_app:wishlist')
