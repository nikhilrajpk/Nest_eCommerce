from django.db import models
from django.contrib.auth.models import AbstractUser

app_name = 'authentication_app'

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    is_block = models.BooleanField(default=False)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']