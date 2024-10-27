"""
URL configuration for aura_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('user_app.urls')),
    path('',include('authentication_app.urls')),
    path('accounts/',include('allauth.urls')),  # google sign in path
    path('',include('category_app.urls')),
    path('admin-panel/',include('admin_app.urls')),
    path('',include('address_app.urls')),
    path('',include('cart_app.urls')),
    path('',include('coupen_app.urls')),
    path('',include('order_app.urls')),
    path('',include('product_app.urls')),
    path('',include('profile_app.urls')),
    path('',include('wallet_app.urls')),
    path('',include('wishlist_app.urls')),
    
    
]

#setting urlpatterns for static and media files
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)