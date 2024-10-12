from django.db import models

from django.core.exceptions import ValidationError
from django.utils import timezone

class Coupons(models.Model):
    code = models.CharField(max_length=50, unique=True)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    maximum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    used_limit = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expiry_date = models.DateTimeField()
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def clean(self):
        # Ensure expiry_date is in the future
        if self.expiry_date < timezone.now():
            raise ValidationError('The coupon has already expired.')

        # Ensure minimum order amount is less than maximum order amount
        if self.minimum_order_amount > self.maximum_order_amount:
            raise ValidationError('Minimum order amount cannot be greater than the maximum order amount.')

    def save(self, *args, **kwargs):
        # Call the clean method before saving to ensure validation is enforced
        self.clean()
        super().save(*args, **kwargs)