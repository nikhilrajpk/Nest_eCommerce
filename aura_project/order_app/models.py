from django.db import models
from authentication_app.models import CustomUser
from product_app.models import Product
from cart_app.models import *
from address_app.models import Address
from coupen_app.models import Coupons
from enum import unique
from pyexpat import model
from sys import prefix
from pyparsing import alphas
from shortuuid.django_fields import ShortUUIDField
# Create your models here.

STATUS = (
        ('pending','Pending'),
        ('confirmed','Confirmed'),
        ('shipped','Shipped'),
        ('delivered','Delivered'),
        ('canceled','Canceled'),
    )
CHECKOUT_STATUS = (
    ('in_progress','In_progress'),
    ('completed','Completed'),
    ('canceled','Canceled'),
)

class Order(models.Model):
    # oid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='ord', alphabet="abcdefgh12345")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="orders")
    order_status = models.CharField(max_length=20, choices=STATUS, default="pending")
    order_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self) -> str:
        return f'{self.user.first_name}-{self.order_status}'

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.product.product_name}-{self.quantity}'
    

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50)

class Checkout(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coupons = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    checkout_status = models.CharField(max_length=20, choices=CHECKOUT_STATUS, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    order = models.OneToOneField('Order', on_delete=models.CASCADE, null=True, blank=True)
