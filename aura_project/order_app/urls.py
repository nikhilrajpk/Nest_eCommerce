from django.urls import path
from . import views

app_name = 'order_app'

urlpatterns = [
    path('confirm_order/',views.confirm_order,name='confirm_order'),
    path('order_view/',views.order_view,name='order_view'),
]