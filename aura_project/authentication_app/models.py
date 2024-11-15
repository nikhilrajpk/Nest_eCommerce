from django.db import models
from django.contrib.auth.models import AbstractUser

app_name = 'authentication_app'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_block = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    
    
class UserReferral(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='referral')
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)

    def __str__(self):
        return self.user.first_name