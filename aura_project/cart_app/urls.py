from django.urls import path
from . import views

app_name = 'cart_app'

urlpatterns = [
    path('add_to_cart/<int:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('cart/',views.cart_view,name='cart'),
    path('cart/update/<int:product_id>/<str:action>/', views.update_cart_item_quantity, name='update_cart_item_quantity'),
    path('remove_cart_item/<int:cart_id>/',views.remove_cart_item,name='remove_cart_item'),
    path('check_coupon/',views.check_coupon,name='check_coupon'),
    path('checkout/<int:cart_id>/',views.checkout,name='checkout'),
]