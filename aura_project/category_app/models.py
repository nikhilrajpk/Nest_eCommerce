from django.db import models
from enum import unique
from pyexpat import model
from sys import prefix
from pyparsing import alphas
from shortuuid.django_fields import ShortUUIDField
from django.utils.html import mark_safe

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)

class Category(models.Model):
    cid = ShortUUIDField(unique=True, length=10, max_length=20, prefix='cat', alphabet="abcdefgh12345")
    category_name = models.CharField(max_length=255)
    cat_image = models.ImageField(upload_to='category/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_listed = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return self.category_name
    
    def category_image(self):
        return mark_safe('<img src="%s" width="50" height="50" />' % (self.image.url))