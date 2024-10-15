from django.db import models
from category_app.models import Category
from authentication_app.models import CustomUser
# Create your models here.


class Offer(models.Model):
    offer_title = models.CharField(max_length=255)
    offer_description = models.TextField()
    offer_percentage = models.IntegerField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    

class Product(models.Model):
    product_name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    offer = models.ForeignKey(Offer,on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='product')
    available_stock = models.PositiveIntegerField()
    image_1 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_2 = models.ImageField(upload_to='products/', null=True, blank=True)
    image_3 = models.ImageField(upload_to='products/', null=True, blank=True)
    offer = models.ForeignKey(Offer,on_delete=models.SET_NULL,null=True)
    is_listed = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    material = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    def discount_price(self):
        discount =  self.price - (self.offer.offer_percentage * self.price/100)
        return discount
    
    
RATING = (
    (1,"⭐☆☆☆☆"),
    (2,"⭐⭐☆☆☆"),
    (3,"⭐⭐⭐☆☆"),
    (4,"⭐⭐⭐⭐☆"),
    (5,"⭐⭐⭐⭐⭐"),
)
    
class ProductReview(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING, default=None)
    comment = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f'{self.user.first_name}-{self.product.product_name}-{self.rating}'


class Banner(models.Model):
    banner_name = models.CharField(max_length=255)
    banner_description = models.TextField()
    product = models.OneToOneField(Product,on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    deal_price = models.DecimalField(max_digits=10, decimal_places=2)
    banner_image = models.ImageField(upload_to='banner/')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_listed = models.BooleanField(default=True)