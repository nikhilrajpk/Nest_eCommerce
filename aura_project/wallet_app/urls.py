from django.urls import path
from . import views

app_name = 'wallet_app'

urlpatterns = [
    path('wallet/',views.wallet,name='wallet'),
]