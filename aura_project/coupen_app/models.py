from django.db import models

from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

class Coupons(models.Model):
    code = models.CharField(max_length=50, unique=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    maximum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    used_limit = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        
        if not isinstance(self.expiry_date, datetime):
            raise ValidationError('Invalid expiry date format.')
        
        if self.expiry_date < timezone.now():
            raise ValidationError('The coupon has already expired.')

        
        if self.minimum_order_amount > self.maximum_order_amount:
            raise ValidationError('Minimum order amount cannot be greater than the maximum order amount.')

    def save(self, *args, **kwargs):
        
        self.clean()
        super().save(*args, **kwargs)