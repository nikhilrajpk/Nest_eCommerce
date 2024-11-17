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
    delivery_date = models.DateTimeField()
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True)
    cancellation_reason = models.TextField(null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self) -> str:
        return f'{self.user.first_name}-{self.order_status}'

class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    return_reason = models.TextField(null=True, blank=True)
    return_date = models.DateTimeField(auto_now_add=True,null=True)
    return_status = models.CharField(max_length=10,default='pending',null=True,blank=True)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self) -> str:
        return f'{self.product.product_name}-{self.quantity}'
    
class OrderAddress(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="orderAddress")
    address = models.ForeignKey(Address,on_delete=models.SET_NULL, null=True,)
    country = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    address_field = models.TextField(default=None)
    address_type = models.CharField(max_length=12)
    

class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    total_price = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50)
    razor_pay_order_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_id = models.CharField(max_length=100, null=True, blank=True)
    razor_pay_payment_signature = models.CharField(max_length=100, null=True, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=50,null=True,blank=True,default='pending')

class Checkout(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE,related_name='checkout')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    coupons = models.ForeignKey(Coupons, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    checkout_status = models.CharField(max_length=20, choices=CHECKOUT_STATUS, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
# class CancelOrder(models.Model):
#     reason = models.TextField()
#     order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='cancel_order')
#     canceled_date = models.DateTimeField(auto_now_add=True)
    
# class ReturnItem(models.Model):
#     reason = models.TextField()
#     order = models.ForeignKey(Order,on_delete=models.CASCADE,related_name='return_item')
#     order_item = models.ForeignKey(OrderItems,on_delete=models.CASCADE,related_name='return_item')
#     return_date = models.DateTimeField(auto_now_add=True)