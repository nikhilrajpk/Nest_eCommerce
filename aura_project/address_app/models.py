from django.db import models
from authentication_app.models import CustomUser
# Create your models here.

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="addresses")
    country = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255, null=True, blank=True)
    postal_code = models.CharField(max_length=20)
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    ADDRESS_TYPE_CHOICES = [
        ('H','Home'),
        ('O','Office'),
        ('OT','Other')
    ]
    address_type = models.CharField(max_length=12,choices=ADDRESS_TYPE_CHOICES)

    def __str__(self):
        return f"{self.user.first_name} - {self.get_address_type_display()}"