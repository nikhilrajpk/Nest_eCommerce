from django.db import models
from authentication_app.models import CustomUser
from product_app.models import Product

class Wishlist(models.Model):
    user = models.OneToOneField(CustomUser,on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
class Wishlist_items(models.Model):
    wishlist = models.ForeignKey(Wishlist,on_delete=models.CASCADE)
    product = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
