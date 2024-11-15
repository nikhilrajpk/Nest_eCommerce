from django.contrib import admin
from .models import CustomUser,UserReferral
# Register your models here.
admin.site.register(CustomUser)
admin.site.register(UserReferral)