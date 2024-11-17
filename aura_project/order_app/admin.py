from django.contrib import admin
from .models import Order,OrderAddress,OrderItems
# Register your models here.

admin.site.register(Order)
admin.site.register(OrderAddress)
admin.site.register(OrderItems)