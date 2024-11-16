from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from product_app.models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
# Create your views here.
from django.http import JsonResponse
@login_required
def add_to_wishlist(request, product_id):
    if request.user.is_authenticated and request.user.is_staff:
        return JsonResponse({'redirect_url': 'admin_app:admin_home'})
    if request.user.is_authenticated and request.user.is_block:
        return JsonResponse({'redirect_url': 'authentication_app:logout'})
    
    user = request.user
    product = get_object_or_404(Product, id=product_id)
    
    # Check if the user already has a wishlist or create a new one
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    
    # Check if the product is already in the wishlist
    wishlist_item, item_created = Wishlist_items.objects.get_or_create(wishlist=wishlist, product=product)
    
    if not item_created:
        # If the product already exists
        pass
    
    return JsonResponse({
        'status': 'success',
        'message': 'Product added to wishlist'
    })

@login_required
def wishlist_view(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    user = request.user
    wishlist, created = Wishlist.objects.get_or_create(user=user)
    wishlist_items = wishlist.wishlist_items_set.all()  # Access the related Wishlist_items
    
    for item in wishlist_items:
        # removing offers if it expires 
        if item.product.offer and item.product.offer.end_date < timezone.now():
            item.product.offer = None
            item.product.category.offer = None
            item.save()
    
    return render(request, 'wishlist_app/wishlist.html', {
        'wishlist': wishlist,
        'wishlist_items': wishlist_items,
    })

@login_required
def remove_from_wishlist(request, wishlist_id):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_app:admin_home')
    if request.user.is_authenticated and request.user.is_block:
        return redirect('authentication_app:logout')
    
    wishlist_item = Wishlist_items.objects.get(id = wishlist_id)
    wishlist_item.delete()
    
    return redirect('wishlist_app:wishlist')
